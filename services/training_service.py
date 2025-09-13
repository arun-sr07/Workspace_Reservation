from models import training_reservations, resources
from db import get_connection
import pymysql
def get_user_role(user_id):
    """
    Fetch role of a user from users table.
    """
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row["role"] if row else None


def list_training_rooms():
    """
    List all training rooms.
    """
    return resources.get_resources_by_type("TrainingRoom")


def reserve_training_room(user_id, resource_id, start_date, end_date, batch=None):
    """
    Reserve a training room (only Management users allowed).
    """
    # 1. Verify resource exists & is training room
    resource = resources.get_resource_by_id(resource_id)
    if not resource or resource["resource_type"] != "TrainingRoom":
        return {"error": "Invalid resource or not a training room."}

    # 2. Fetch role from DB
    role = get_user_role(user_id)
    if not role:
        return {"error": "User not found."}

    if role.lower() != "management":
        return {"error": "Only Management users can reserve training rooms."}

    # 3. Check existing reservations for overlap
    existing_reservations = training_reservations.get_reservations_for_resource(
        resource_id, start_date, end_date
    )
    if len(existing_reservations) >= resource["capacity"]:
        return {"error": "Training room capacity exceeded."}

    # 4. Create reservation
    reservation_id = training_reservations.create_reservation(
        user_id=user_id,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        batch=batch
    )

    return {"success": True, "reservation_id": reservation_id}


def get_user_training_reservations(user_id):
    """
    Get all training room reservations for a user.
    """
    user_reservations = training_reservations.get_reservations_by_user(user_id)
    return [
        r for r in user_reservations
        if resources.get_resource_by_id(r["resource_id"])["resource_type"] == "TrainingRoom"
    ]


def cancel_training_reservation(reservation_id):
    """
    Cancel a training room reservation.
    """
    training_reservations.cancel_reservation(reservation_id)
    return {"success": True}
