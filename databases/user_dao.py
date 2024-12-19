import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class UserDAO:
    @staticmethod
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

    @staticmethod
    def get_user_by_username(username):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        conn.close()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user

    @staticmethod
    def check_password(stored_password_hash, password):
        return check_password_hash(stored_password_hash, password)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_all_users():
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, phone_number, balance FROM users')
        users = cursor.fetchall()
        
        conn.close()
        return users

    @staticmethod
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