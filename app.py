from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import setup_database, add_bus, view_buses, make_reservation, view_reservations, reverse_seats
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Change to your database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

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
    buses = view_buses()
    return render_template('view_buses.html', buses=buses)

# Route for making a reservation
@app.route('/make_reservation', methods=['GET', 'POST'])
def make_reservation_route():
    if request.method == 'POST':
        bus_id = request.form['bus_id']
        customer_name = request.form['customer_name']
        seats_reserved = request.form['seats_reserved']
        make_reservation(bus_id, customer_name, seats_reserved)
        return redirect(url_for('view_reservations'))
    buses = view_buses()
    return render_template('make_reservation.html', buses=buses)

# Route for viewing reservations
@app.route('/view_reservations')
def view_reservations_route():
    reservations = view_reservations()
    return render_template('view_reservations.html', reservations=reservations)

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
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id  # Store user ID in session
            flash('Login successful!')
            return redirect(url_for('home'))  # Redirect to a home page or dashboard
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Home route (after login)
@app.route('/home')
def home():
    return render_template('home.html')  # You can create a simple home page template

# Route to log out
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    setup_database()  # Call your existing database setup function
    app.run(debug=True)