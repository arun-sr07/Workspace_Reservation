from db import get_connection,fetch_one
import pymysql


def get_resource_by_id(resource_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM resources WHERE resource_id = %s", (resource_id,))
    resource = cursor.fetchone()
    cursor.close()
    conn.close()
    return resource

def get_resources_by_floor(floor_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM resources WHERE floor_id = %s", (floor_id,))
    resources = cursor.fetchall()
    cursor.close()
    conn.close()
    return resources

def get_resources_by_type(resource_type):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM resources WHERE resource_type = %s", (resource_type,))
    resources = cursor.fetchall()
    cursor.close()
    conn.close()
    return resources

def get_seats_by_resource(resource_id: int):
    """
    Get all seats for a given resource (e.g., workspace).
    """
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT s.seat_id, s.seat_number
        FROM seats s
        WHERE s.resource_id = %s
    """, (resource_id,))
    seats = cursor.fetchall()
    cursor.close()
    conn.close()
    return seats

def get_seat_with_resource(seat_id: int):
    """
    Fetch seat details along with its resource.
    """
    return fetch_one("""
        SELECT s.seat_id, s.seat_number, r.resource_id, r.resource_type, r.name AS resource_name
        FROM seats s
        JOIN resources r ON s.resource_id = r.resource_id
        WHERE s.seat_id = %s
    """, (seat_id,))

def get_meeting_room_by_id(resource_id: int):
    return fetch_one("""
        SELECT resource_id, name
        FROM resources
        WHERE resource_id = %s AND resource_type = 'MeetingRoom'
    """, (resource_id,))

