import pytest
import mysql.connector
from main import reserve_seat, cancel_reservation, list_available_seats

# Test MySQL connection (use a test database ideally)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="workspace_reservation"
)
cursor = db.cursor(dictionary=True)

@pytest.fixture
def setup_user_seat():
    # Create a test user
    cursor.execute("INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com')")
    user_id = cursor.lastrowid
    cursor.execute("INSERT INTO seats (seat_number) VALUES ('T1')")
    seat_id = cursor.lastrowid
    db.commit()
    yield user_id, seat_id
    # Cleanup
    cursor.execute("DELETE FROM reservations WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    cursor.execute("DELETE FROM seats WHERE id=%s", (seat_id,))
    db.commit()


def test_reserve_and_cancel(setup_user_seat):
    user_id, seat_id = setup_user_seat
    
    reserve_seat(user_id, seat_id)
    cursor.execute("SELECT status FROM seats WHERE id=%s", (seat_id,))
    status = cursor.fetchone()['status']
    assert status == 'reserved'
    
    cancel_reservation(user_id, seat_id)
    cursor.execute("SELECT status FROM seats WHERE id=%s", (seat_id,))
    status = cursor.fetchone()['status']
    assert status == 'available'
