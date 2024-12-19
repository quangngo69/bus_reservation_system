import sqlite3

class ReservationDAO:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
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