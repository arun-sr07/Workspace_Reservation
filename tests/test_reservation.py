# tests/test_reservation.py

from datetime import date
from services.workspace_service import reserve_seat, cancel_reservation, get_user_reservations
from services.meeting_service import reserve_room, cancel_reservation as cancel_room_reservation, get_user_reservations as get_room_reservations
from services.training_service import (
    reserve_training_room,
    get_user_training_reservations,
    cancel_training_reservation
)
from models import reservations


from db import execute

def reset_db():
    execute("DELETE FROM reservations")
    execute("ALTER TABLE reservations AUTO_INCREMENT = 1")

users = {
    1: {"user_id": 1, "role": "Employee"},
    6: {"user_id": 6, "role": "Management"},
}

def run_tests():
    print("---- Workspace Reservation Tests ----")

    # 1. Reserve a seat
    print("\nTest 1: Reserve Seat")
    result = reserve_seat(user_id=1, seat_id=1, reservation_date=date.today(),resource_id=1)
    print("Result:", result)

    # 2. Try reserving the same seat again (should fail)
    print("\nTest 2: Reserve Same Seat Again")
    result = reserve_seat(user_id=2, seat_id=1, reservation_date=date.today(),resource_id=1)
    print("Result:", result)

    # 3. Get user reservations
    print("\nTest 3: Get User Reservations (User 1)")
    reservations = get_user_reservations(user_id=1)
    print("Reservations:", reservations)

    # 4. Cancel reservation
    if reservations:
        reservation_id = reservations[0]["reservation_id"]
        print("\nTest 4: Cancel Reservation")
        result = cancel_reservation(reservation_id, user_id=1)
        print("Result:", result)

    # 5. Check reservations again
    print("\nTest 5: Get Reservations After Cancel (User 1)")
    reservations = get_user_reservations(user_id=1)
    print("Reservations:", reservations)


def run_meeting_room_tests():
    print("\n---- Meeting Room Reservation Tests ----")

    # 1. Reserve a meeting room
    print("\nTest 1: Reserve Meeting Room")
    result = reserve_room(
        user_id=1,
        room_id=2,
        reservation_date=date.today(),
        start_time="10:00:00",
        end_time="11:00:00"
    )
    print("Result:", result)

    # 2. Try reserving same room overlapping time
    print("\nTest 2: Reserve Overlapping Meeting Room")
    result = reserve_room(
        user_id=2,
        room_id=2,
        reservation_date=date.today(),
        start_time="10:30:00",
        end_time="11:30:00"
    )
    print("Result:", result)

    # 3. Get user reservations
    print("\nTest 3: Get Meeting Room Reservations (User 1)")
    reservations = get_room_reservations(user_id=1)
    print("Reservations:", reservations)

    # 4. Cancel reservation
    if reservations:
        reservation_id = reservations[0]["reservation_id"]
        print("\nTest 4: Cancel Meeting Room Reservation")
        result = cancel_room_reservation(reservation_id, user_id=1)
        print("Result:", result)

    # 5. Check reservations again
    print("\nTest 5: Get Meeting Room Reservations After Cancel (User 1)")
    reservations = get_room_reservations(user_id=1)
    print("Reservations:", reservations)



def run_training_room_tests():
    print("\n---- Training Room Reservation Tests ----")

    # 1. Non-management user should fail
    print("\nTest 1: Non-Management User Reserve Training Room (should fail)")
    result = reserve_training_room(
        user=users[1],
        resource_id=4,
        reservation_date=date.today(),
        start_time="09:00:00",
        end_time="12:00:00",
        batch="Python"
    )
    print("Result:", result)

    # 2. Management user should succeed
    print("\nTest 2: Management User Reserve Training Room")
    result = reserve_training_room(
        user=users[6],
        resource_id=4,
        reservation_date=date.today(),
        start_time="09:00:00",
        end_time="12:00:00",
        batch="Python"
    )
    print("Result:", result)

    # 3. Exceeding capacity
    print("\nTest 3: Exceed Training Room Capacity")
    for i in range(5):  # simulate multiple bookings
        result = reserve_training_room(
            user=users[6],
            resource_id=4,
            reservation_date=date.today(),
            start_time="09:00:00",
            end_time="12:00:00",
            batch="Python"
        )
        print(f"Attempt {i+1}:", result)

    # 4. Get reservations for Management user
    print("\nTest 4: Get Training Room Reservations (User 6)")
    user_reservations = get_user_training_reservations(6)
    print("Reservations:", user_reservations)

    # 5. Cancel reservation (if any exists)
    if user_reservations:
        reservation_id = user_reservations[0]["reservation_id"]
        print("\nTest 5: Cancel Training Room Reservation")
        result = cancel_training_reservation(reservation_id)
        print("Result:", result)

    # 6. Verify cancellation
    print("\nTest 6: Get Reservations After Cancel (User 6)")
    user_reservations = get_user_training_reservations(6)
    print("Reservations:", user_reservations)

if __name__ == "__main__":
    run_tests()
    run_meeting_room_tests()
    reset_db()
    run_training_room_tests()
