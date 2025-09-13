# services/meeting_room_service.py

from datetime import date
from models import resources, reservations

def list_meeting_rooms():
    """
    List all meeting rooms.
    """
    return resources.get_resources_by_type("MeetingRoom")

def reserve_room(user_id: int, room_id: int, reservation_date: date, start_time: str, end_time: str):
    """
    Reserve a meeting room for a given time range.
    """

    # 1. Validate: room exists and is a MeetingRoom
    room = resources.get_meeting_room_by_id(room_id)
    if not room:
        return {"error": "Invalid resource or not a meeting room."}

    # 2. Check overlapping reservations
    conflict = reservations.get_conflicting_reservation(room_id, reservation_date, start_time, end_time)
    if conflict:
        return {"error": "Meeting room already booked during this time."}

    # 3. Insert reservation
    reservation_id = reservations.insert_meeting_reservation(
        user_id=user_id,
        resource_id=room_id,
        reservation_date=reservation_date,
        start_time=start_time,
        end_time=end_time
    )

    return {"success": True, "reservation_id": reservation_id}


def cancel_reservation(reservation_id: int, user_id: int):
    """
    Cancel a meeting room reservation (only by owner).
    """
    reservation = reservations.get_user_reservation_by_id(reservation_id, user_id)
    if not reservation:
        return {"error": "Reservation not found or not owned by user."}

    reservations.delete_reservation(reservation_id)
    return {"success": True}


def get_user_reservation(user_id: int):
    """
    Get all meeting room reservations of a user.
    """
    return reservations.get_meeting_room_reservations_by_user(user_id)
