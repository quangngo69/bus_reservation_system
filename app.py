from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import setup_database, add_user, get_user_by_username, get_user_by_id, check_password, update_user, add_bus, view_buses, make_reservation, view_reservations, reverse_seats, get_bus, view_user_tickets, update_bus, delete_bus_from_db
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from flask import send_file
import qrcode

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus_reservation.db'  # Change to your database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Custom Jinja2 filter to check if the user is admin
@app.template_filter('is_admin')
def is_admin(user_id):
    user = get_user_by_id(user_id)
    return user and user[1] == 'admin'

# Route for the index page
@app.route('/')
def index():
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = get_user_by_id(user_id)
    return render_template('index.html', user=user)

# Route for adding a bus
@app.route('/add_bus', methods=['GET', 'POST'])
def add_bus_route():
    if request.method == 'POST':
        bus_number = request.form['bus_number']
        route = request.form['route']
        total_seats = request.form['total_seats']
        add_bus(bus_number, route, total_seats)
        return redirect(url_for('view_buses_route'))
    return render_template('add_bus.html')

# Route for viewing buses
@app.route('/view_buses')
def view_buses_route():
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = get_user_by_id(user_id)
    buses = view_buses()
    return render_template('view_buses.html', buses=buses, user=user)

# Route for making a reservation
@app.route('/make_reservation', methods=['GET', 'POST'])
def make_reservation_route():
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = get_user_by_id(user_id)
    if request.method == 'POST':
        bus_id = request.form['bus_id']
        customer_name = request.form['customer_name']
        seats_reserved = request.form['seats_reserved']
        make_reservation(bus_id, customer_name, seats_reserved)
        return redirect(url_for('view_reservations'))
    buses = view_buses()
    return render_template('make_reservation.html', buses=buses, user=user)

# Route for viewing reservations
@app.route('/view_reservations')
def view_reservations_route():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view reservations.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('login'))
    
    is_admin = user[1] == 'admin'
    
    reservations = view_reservations(user_id, is_admin)
    return render_template('view_reservations.html', reservations=reservations, is_admin=is_admin, user=user)

# Route for reversing seats
@app.route('/reverse_seats/<int:bus_id>/<int:seats_to_reverse>')
def reverse_seats_route(bus_id, seats_to_reverse):
    reverse_seats(bus_id, seats_to_reverse)
    return redirect(url_for('view_buses_route'))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        existing_user = get_user_by_username(username)
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Create a new user
        add_user(username, password)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        if user and check_password(user[2], password):
            session['user_id'] = user[0]  # Store user ID in session
            flash('Login successful!')
            return redirect(url_for('home'))  # Redirect to a home page or dashboard
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Home route (after login)
@app.route('/home')
def home():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view the home page.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('login'))
    
    username = user[1]  # Assuming the username is the second field in the user tuple
    return render_template('home.html', username=username, user=user)

# Route to log out
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Route for buying a ticket
@app.route('/buy_ticket/<int:bus_id>', methods=['GET', 'POST'])
def buy_ticket(bus_id):
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        seats_reserved = int(request.form['seats_reserved'])
        
        # Make reservation and update available seats
        if make_reservation(bus_id, customer_name, seats_reserved):
            # Generate QR code
            qr_data = f"Bus ID: {bus_id}, Customer: {customer_name}, Seats: {seats_reserved}"
            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, 'PNG')
            buffer.seek(0)
            
            return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='ticket_qr.png')
        else:
            flash('Not enough available seats!')
            return redirect(url_for('buy_ticket', bus_id=bus_id))
    
    bus = get_bus(bus_id)
    if bus is None:
        flash('Bus not found.')
        return redirect(url_for('view_buses_route'))
    
    return render_template('buy_ticket.html', bus=bus)

@app.route('/generate_qr_code/<int:bus_id>/<customer_name>/<int:seats_reserved>')
def generate_qr_code(bus_id, customer_name, seats_reserved):
    qr_data = f"Bus ID: {bus_id}, Customer: {customer_name}, Seats: {seats_reserved}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, 'PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

# Route for viewing user's tickets
@app.route('/my_tickets')
def my_tickets():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view your tickets.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    tickets = view_user_tickets(user_id)
    return render_template('my_tickets.html', tickets=tickets, user=user)

@app.route('/edit_bus/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to edit buses.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('login'))
    
    if user[1] != 'admin':
        flash('You do not have permission to edit buses.')
        return redirect(url_for('home'))
    
    bus = get_bus(bus_id)
    if bus is None:
        flash('Bus not found.')
        return redirect(url_for('view_buses_route'))
    
    if request.method == 'POST':
        bus_number = request.form['bus_number']
        route = request.form['route']
        total_seats = int(request.form['total_seats'])
        available_seats = int(request.form['available_seats'])
        time = request.form['time']
        
        update_bus(bus_id, bus_number, route, total_seats, available_seats, time)
        flash('Bus details updated successfully!')
        return redirect(url_for('view_buses_route'))
    
    return render_template('edit_bus.html', bus=bus)

@app.route('/delete_bus/<int:bus_id>', methods=['POST'])
def delete_bus(bus_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to delete buses.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('login'))
    
    if user[1] != 'admin':
        flash('You do not have permission to delete buses.')
        return redirect(url_for('home'))
    
    delete_bus_from_db(bus_id)
    flash('Bus deleted successfully!')
    return redirect(url_for('view_buses_route'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view your profile.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        update_user(user_id, username, email, phone_number, gender)
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    with app.app_context():
        setup_database()  # Call your existing database setup function
    app.run(debug=True)