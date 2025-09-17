# services/workspace_service.py

from datetime import date
from models import reservations, resources,offices, floors
from ml.recommendation_service import get_recommended_seats

def list_recommended_seats(user_id, resource_id, reservation_date):
    recommendations = get_recommended_seats(user_id, resource_id, reservation_date)
    return recommendations


def list_workspaces():
    """
    List all workspaces (resources of type Workspace).
    """
    return resources.get_resources_by_type("Workspace")

def list_all_seats(resource_id: int, reservation_date: str):
    """
    Return ALL seats for a workspace, with a flag whether each seat is reserved.
    """
    all_seats = resources.get_seats_by_resource(resource_id)
    reserved_seats = reservations.get_reservations_for_resource(resource_id, reservation_date)

    reserved_ids = {r["seat_id"] for r in reserved_seats if r.get("seat_id")}

    for seat in all_seats:
        seat["is_reserved"] = seat["seat_id"] in reserved_ids

    return all_seats
def list_available_seats(resource_id: int, reservation_date: date):
    """
    List available seats for a workspace on a specific date.
    """
    all_seats = resources.get_seats_by_resource(resource_id)
    reserved_seats = reservations.get_reservations_for_resource(resource_id, reservation_date)

    reserved_ids = {r["seat_id"] for r in reserved_seats if r.get("seat_id")}
    available = [s for s in all_seats if s["seat_id"] not in reserved_ids]

    return available

def reserve_seat(user_id: int, seat_id: int, reservation_date: date, resource_id: int):
    """
    Reserve a workspace seat for a whole day.
    """

    # 1. Check if seat belongs to a workspace
    seat = resources.get_seat_with_resource(seat_id)
    if not seat or seat["resource_type"] != "Workspace":
        return {"error": "Invalid seat or not a workspace seat."}

    # 2. Check if already booked
    existing = reservations.get_by_seat_and_date(seat_id, reservation_date)
    if existing:
        return {"error": "Seat already booked for this date."}

    # 3. Create reservation
    reservation_id = reservations.insert_reservation(
        user_id=user_id,
        resource_id=resource_id,
        seat_id=seat_id,
        reservation_date=reservation_date
    )

    return {"success": True, "reservation_id": reservation_id}


def cancel_reservation(reservation_id: int, user_id: int):
    """
    Cancel a reservation (only by owner).
    """
    res = reservations.get_by_id_and_user(reservation_id, user_id)
    if not res:
        return {"error": "Reservation not found or not owned by user."}

    reservations.delete_reservation(reservation_id)
    return {"success": True}


def get_user_reservationss(user_id: int):
    """
    Get all reservations of a user.
    """
    return reservations.get_user_workspace_reservations(user_id)
