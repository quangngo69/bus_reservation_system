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
            gender TEXT,
            balance REAL DEFAULT 0.0,
            name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY,
            bus_number TEXT NOT NULL,
            route TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            time TEXT,
            price REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            bus_id INTEGER,
            customer_name TEXT NOT NULL,
            seats_reserved INTEGER NOT NULL,
            plan TEXT NOT NULL,
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
    if 'balance' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0.0")
    if 'name' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
    
    # Add new columns to the buses table if they don't exist
    cursor.execute("PRAGMA table_info(buses)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'time' not in columns:
        cursor.execute("ALTER TABLE buses ADD COLUMN time TEXT")
    if 'price' not in columns:
        cursor.execute("ALTER TABLE buses ADD COLUMN price REAL NOT NULL")
    if 'available_seats' not in columns:
        cursor.execute("ALTER TABLE buses ADD COLUMN available_seats INTEGER NOT NULL")
    
    # Add new columns to the reservations table if they don't exist
    cursor.execute("PRAGMA table_info(reservations)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'plan' not in columns:
        cursor.execute("ALTER TABLE reservations ADD COLUMN plan TEXT NOT NULL DEFAULT 'one_time'")
    
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

def update_user(user_id, username, email, phone_number, gender, name):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users
        SET username = ?, email = ?, phone_number = ?, gender = ?, name = ?
        WHERE id = ?
    ''', (username, email, phone_number, gender, name, user_id))
    
    conn.commit()
    conn.close()

def add_bus(bus_number, route, total_seats, time, price):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buses (bus_number, route, total_seats, available_seats, time, price)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (bus_number, route, total_seats, total_seats, time, price))
    conn.commit()
    conn.close()

def view_buses():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM buses')
    buses = cursor.fetchall()
    
    conn.close()
    return buses

def make_reservation(bus_id, customer_name, seats_reserved, plan):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT available_seats FROM buses WHERE id = ?', (bus_id,))
    available_seats = cursor.fetchone()[0]
    
    if available_seats >= seats_reserved:
        cursor.execute('''
            INSERT INTO reservations (bus_id, customer_name, seats_reserved, plan)
            VALUES (?, ?, ?, ?)
        ''', (bus_id, customer_name, seats_reserved, plan))
        
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
            SELECT reservations.id, buses.bus_number, buses.route, reservations.customer_name, reservations.seats_reserved, buses.time, buses.price, reservations.plan
            FROM reservations
            JOIN buses ON reservations.bus_id = buses.id
        ''')
    else:
        cursor.execute('''
            SELECT reservations.id, buses.bus_number, buses.route, reservations.customer_name, reservations.seats_reserved, buses.time, buses.price, reservations.plan
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

def update_bus(bus_id, bus_number, route, total_seats, available_seats, time, price):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE buses
        SET bus_number = ?, route = ?, total_seats = ?, available_seats = ?, time = ?, price = ?
        WHERE id = ?
    ''', (bus_number, route, total_seats, available_seats, time, price, bus_id))
    
    conn.commit()
    conn.close()

def delete_bus_from_db(bus_id):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
    
    conn.commit()
    conn.close()

def update_balance(user_id, amount):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users
        SET balance = balance + ?
        WHERE id = ?
    ''', (amount, user_id))
    
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, phone_number, balance FROM users')
    users = cursor.fetchall()
    
    conn.close()
    return users

def update_password(user_id, new_password):
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    password_hash = generate_password_hash(new_password)
    
    cursor.execute('''
        UPDATE users
        SET password_hash = ?
        WHERE id = ?
    ''', (password_hash, user_id))
    
    conn.commit()
    conn.close()