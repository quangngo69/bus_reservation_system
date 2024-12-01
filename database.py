import sqlite3
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

def setup_database():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT,
            phone_number TEXT,
            gender TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY,
            bus_number TEXT NOT NULL,
            route TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            time TEXT
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
    
    # Add new columns to the users table if they don't exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'email' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if 'phone_number' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")
    if 'gender' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT")
    
    # Add new columns to the buses table if they don't exist
    cursor.execute("PRAGMA table_info(buses)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'time' not in columns:
        cursor.execute("ALTER TABLE buses ADD COLUMN time TEXT")
    
    conn.commit()
    conn.close()

def add_user(username, password, email=None, phone_number=None, gender=None):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    password_hash = generate_password_hash(password)
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, email, phone_number, gender)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, password_hash, email, phone_number, gender))
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user

def check_password(stored_password_hash, password):
    return check_password_hash(stored_password_hash, password)

def update_user(user_id, username, email, phone_number, gender):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users
        SET username = ?, email = ?, phone_number = ?, gender = ?
        WHERE id = ?
    ''', (username, email, phone_number, gender, user_id))
    
    conn.commit()
    conn.close()

def add_bus(bus_number, route, total_seats, time):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buses (bus_number, route, total_seats, available_seats, time)
        VALUES (?, ?, ?, ?, ?)
    ''', (bus_number, route, total_seats, total_seats, time))
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
    
    if available_seats >= seats_reserved:
        cursor.execute('''
            INSERT INTO reservations (bus_id, customer_name, seats_reserved)
            VALUES (?, ?, ?)
        ''', (bus_id, customer_name, seats_reserved))
        
        cursor.execute('''
            UPDATE buses SET available_seats = available_seats - ?
            WHERE id = ?
        ''', (seats_reserved, bus_id))
        
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def view_reservations(user_id, is_admin):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    if is_admin:
        cursor.execute('''
            SELECT reservations.id, buses.bus_number, buses.route, reservations.customer_name, reservations.seats_reserved, buses.time
            FROM reservations
            JOIN buses ON reservations.bus_id = buses.id
        ''')
    else:
        cursor.execute('''
            SELECT reservations.id, buses.bus_number, buses.route, reservations.customer_name, reservations.seats_reserved, buses.time
            FROM reservations
            JOIN buses ON reservations.bus_id = buses.id
            WHERE reservations.customer_name = (SELECT username FROM users WHERE id = ?)
        ''', (user_id,))
    
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

def get_bus(bus_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
    bus = cursor.fetchone()
    
    conn.close()
    return bus

def view_user_tickets(user_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT buses.id, buses.route, reservations.seats_reserved, reservations.customer_name
        FROM reservations
        JOIN buses ON reservations.bus_id = buses.id
        WHERE reservations.customer_name = (SELECT username FROM users WHERE id = ?)
    ''', (user_id,))
    tickets = cursor.fetchall()
    
    conn.close()
    return tickets

def update_bus(bus_id, bus_number, route, total_seats, available_seats, time):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE buses
        SET bus_number = ?, route = ?, total_seats = ?, available_seats = ?, time = ?
        WHERE id = ?
    ''', (bus_number, route, total_seats, available_seats, time, bus_id))
    
    conn.commit()
    conn.close()

def delete_bus_from_db(bus_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
    
    conn.commit()
    conn.close()