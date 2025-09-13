from db import get_connection
import pymysql
def create_reservation(user_id, resource_id, start_date, end_date, batch=None):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        INSERT INTO training_reservations (user_id, resource_id, start_date, end_date, batch)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, resource_id, start_date, end_date, batch))
    conn.commit()
    reservation_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return reservation_id


def get_reservations_for_resource(resource_id, start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM training_reservations
        WHERE resource_id = %s
        AND (start_date <= %s AND end_date >= %s)
    """, (resource_id, end_date, start_date))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_reservations_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM training_reservations WHERE user_id = %s", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def cancel_reservation(reservation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM training_reservations WHERE training_reservation_id = %s", (reservation_id,))
    conn.commit()
    cursor.close()
    conn.close()
