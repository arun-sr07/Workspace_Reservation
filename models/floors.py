from db import get_connection
import pymysql
def get_floor_by_id(floor_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM floors WHERE floor_id = %s", (floor_id,))
    floor = cursor.fetchone()
    cursor.close()
    conn.close()
    return floor

def get_floors_by_office(office_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM floors WHERE office_id = %s", (office_id,))
    floors = cursor.fetchall()
    cursor.close()
    conn.close()
    return floors
