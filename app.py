from flask import Flask, render_template, request, redirect, url_for
from database import setup_database, add_bus, view_buses, make_reservation, view_reservations

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_bus', methods=['GET', 'POST'])
def add_bus_route():
    if request.method == 'POST':
        bus_number = request.form['bus_number']
        route = request.form['route']
        total_seats = request.form['total_seats']
        add_bus(bus_number, route, total_seats)
        return redirect(url_for('view_buses'))
    return render_template('add_bus.html')

@app.route('/view_buses')
def view_buses_route():
    buses = view_buses()
    return render_template('view_buses.html', buses=buses)

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

@app.route('/view_reservations')
def view_reservations_route():
    reservations = view_reservations()
    return render_template('view_reservations.html', reservations=reservations)

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)