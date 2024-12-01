import sqlite3

def setup_database():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY,
            bus_number TEXT NOT NULL,
            route TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            bus_id INTEGER,
            customer_name TEXT NOT NULL,
            seats_reserved INTEGER NOT NULL,
            FOREIGN KEY (bus_id) REFERENCES buses (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_bus(bus_number, route, total_seats):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO buses (bus_number, route, total_seats, available_seats)
        VALUES (?, ?, ?, ?)
    ''', (bus_number, route, total_seats, total_seats))
    
    conn.commit()
    conn.close()

def view_buses():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM buses')
    buses = cursor.fetchall()
    
    conn.close()
    return buses

def make_reservation(bus_id, customer_name, seats_reserved):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT available_seats FROM buses WHERE id = ?', (bus_id,))
    available_seats = cursor.fetchone()[0]
    
    if available_seats >= int(seats_reserved):
        cursor.execute('''
            INSERT INTO reservations (bus_id, customer_name, seats_reserved)
            VALUES (?, ?, ?)
        ''', (bus_id, customer_name, seats_reserved))
        
        cursor.execute('''
            UPDATE buses SET available_seats = available_seats - ?
            WHERE id = ?
        ''', (seats_reserved, bus_id))
        
        conn.commit()
        print("Reservation made successfully!")
    else:
        print("Not enough available seats!")
    
    conn.close()

def view_reservations():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT reservations.id, buses.bus_number, reservations.customer_name, reservations.seats_reserved
        FROM reservations
        JOIN buses ON reservations.bus_id = buses.id
    ''')
    reservations = cursor.fetchall()
    
    conn.close()
    return reservations

def reverse_seats(bus_id, seats_to_reverse):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT available_seats FROM buses WHERE id = ?', (bus_id,))
    available_seats = cursor.fetchone()[0]
    
    if available_seats - seats_to_reverse >= 0:
        cursor.execute('''
            UPDATE buses SET available_seats = available_seats + ?
            WHERE id = ?
        ''', (seats_to_reverse, bus_id))
        
        conn.commit()
        print("Seats reversed successfully!")
    else:
        print("Not enough available seats to reverse!")
    
    conn.close()