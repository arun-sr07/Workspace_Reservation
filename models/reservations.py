from db import get_connection
from db import fetch_one, fetch_all, execute, execute_return_id
import pymysql
def create_reservation(user_id, resource_id, start_date, end_date, batch=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO training_reservations (user_id, resource_id, start_date, end_date, batch)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, resource_id, start_date, end_date, batch))

    conn.commit()
    reservation_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return reservation_id

def get_reservation_by_id(reservation_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,))
    reservation = cursor.fetchone()
    cursor.close()
    conn.close()
    return reservation

def get_reservations_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
    reservations = cursor.fetchall()
    cursor.close()
    conn.close()
    return reservations

def get_reservations_for_resource(resource_id, reservation_date):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM reservations
        WHERE resource_id = %s AND reservation_date = %s
    """, (resource_id, reservation_date))
    reservations = cursor.fetchall()
    cursor.close()
    conn.close()
    return reservations

def cancel_reservation(reservation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))
    conn.commit()
    cursor.close()
    conn.close()

def clear_reservations_for_resource(resource_id, reservation_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservations WHERE resource_id = %s AND reservation_date = %s", (resource_id, reservation_date))
        conn.commit()
    finally:
        conn.close()



def get_by_seat_and_date(seat_id: int, reservation_date):
    return fetch_one("""
        SELECT reservation_id FROM reservations
        WHERE seat_id = %s AND reservation_date = %s
    """, (seat_id, reservation_date))

def insert_reservation(user_id: int, resource_id: int, seat_id: int, reservation_date):
    return execute_return_id("""
        INSERT INTO reservations (user_id, resource_id, seat_id, reservation_date)
        VALUES (%s, %s, %s, %s)
    """, (user_id, resource_id, seat_id, reservation_date))

def get_by_id_and_user(reservation_id: int, user_id: int):
    return fetch_one("""
        SELECT reservation_id FROM reservations
        WHERE reservation_id = %s AND user_id = %s
    """, (reservation_id, user_id))

def delete_reservation(reservation_id: int):
    execute("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))

def get_user_workspace_reservations(user_id: int):
    return fetch_all("""
        SELECT r.reservation_id, r.reservation_date,
               s.seat_number, res.name AS resource_name, o.name AS office_name
        FROM reservations r
        JOIN seats s ON r.seat_id = s.seat_id
        JOIN resources res ON s.resource_id = res.resource_id
        JOIN floors f ON res.floor_id = f.floor_id
        JOIN offices o ON f.office_id = o.office_id
        WHERE r.user_id = %s
        ORDER BY r.reservation_date DESC
    """, (user_id,))


from db import fetch_one, fetch_all, execute, execute_return_id

def get_conflicting_reservation(resource_id: int, reservation_date, start_time, end_time):
    return fetch_one("""
        SELECT reservation_id
        FROM reservations
        WHERE resource_id = %s
          AND reservation_date = %s
          AND NOT (end_time <= %s OR start_time >= %s)
    """, (resource_id, reservation_date, start_time, end_time))

def insert_meeting_reservation(user_id: int, resource_id: int, reservation_date, start_time, end_time):
    return execute_return_id("""
        INSERT INTO reservations (user_id, resource_id, reservation_date, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, resource_id, reservation_date, start_time, end_time))

def get_user_reservation_by_id(reservation_id: int, user_id: int):
    return fetch_one("""
        SELECT reservation_id
        FROM reservations
        WHERE reservation_id = %s AND user_id = %s
    """, (reservation_id, user_id))



def get_meeting_room_reservations_by_user(user_id: int):
    return fetch_all("""
        SELECT r.reservation_id, r.reservation_date, r.start_time, r.end_time,
               res.name AS room_name, o.name AS office_name, f.floor_number
        FROM reservations r
        JOIN resources res ON r.resource_id = res.resource_id
        JOIN floors f ON res.floor_id = f.floor_id
        JOIN offices o ON f.office_id = o.office_id
        WHERE r.user_id = %s AND res.resource_type = 'MeetingRoom'
        ORDER BY r.reservation_date DESC, r.start_time
    """, (user_id,))
