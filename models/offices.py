from db import get_connection
import pymysql
def get_office_by_id(office_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM offices WHERE office_id = %s", (office_id,))
    office = cursor.fetchone()
    cursor.close()
    conn.close()
    return office

def get_all_offices():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM offices", )
    offices = cursor.fetchall()
    cursor.close()
    conn.close()
    return offices
