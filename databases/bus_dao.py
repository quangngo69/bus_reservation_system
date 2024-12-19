import sqlite3

class BusDAO:
    @staticmethod
    def add_bus(bus_number, route, total_seats, time, price):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO buses (bus_number, route, total_seats, available_seats, time, price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bus_number, route, total_seats, total_seats, time, price))
        conn.commit()
        conn.close()

    @staticmethod
    def view_buses(sort_by=None, search_query=None):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        query = 'SELECT * FROM buses'
        params = []
        
        if search_query:
            query += ' WHERE route LIKE ?'
            params.append(f'%{search_query}%')
        
        if sort_by:
            query += f' ORDER BY {sort_by}'
        
        cursor.execute(query, params)
        buses = cursor.fetchall()
        
        conn.close()
        return buses

    @staticmethod
    def get_bus(bus_id):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
        bus = cursor.fetchone()
        
        conn.close()
        return bus

    @staticmethod
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

    @staticmethod
    def delete_bus_from_db(bus_id):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
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