import mysql.connector
from datetime import datetime
from tabulate import tabulate

# ----------------------
# MySQL Connection
# ----------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arunsr2003@.",
    database="workspace_reservation"
)
cursor = db.cursor(dictionary=True)

# ----------------------
# Core Functions
# ----------------------

def list_workspaces():
    cursor.execute("SELECT * FROM workspaces")
    workspaces = cursor.fetchall()
    print(tabulate(workspaces, headers="keys", tablefmt="grid"))

def list_available_seats(workspace_id, reservation_date, time_slot):
    query = """
        SELECT s.id, s.seat_number
        FROM seats s
        WHERE s.workspace_id=%s
        AND s.id NOT IN (
            SELECT seat_id FROM reservations 
            WHERE reservation_date=%s AND time_slot=%s
        )
    """
    cursor.execute(query, (workspace_id, reservation_date, time_slot))
    seats = cursor.fetchall()
    if not seats:
        print("No seats available.")
    else:
        print(tabulate(seats, headers="keys", tablefmt="grid"))
    return seats

def reserve_seat(user_id, seat_id, reservation_date, time_slot):
    # Check if seat already reserved
    cursor.execute("""
        SELECT * FROM reservations 
        WHERE seat_id=%s AND reservation_date=%s AND time_slot=%s
    """, (seat_id, reservation_date, time_slot))
    if cursor.fetchone():
        print("Seat already reserved for this slot.")
        return
    cursor.execute("""
        INSERT INTO reservations (user_id, seat_id, reservation_date, time_slot)
        VALUES (%s, %s, %s, %s)
    """, (user_id, seat_id, reservation_date, time_slot))
    db.commit()
    print("Seat reserved successfully!")

def cancel_reservation(user_id, reservation_id):
    cursor.execute("DELETE FROM reservations WHERE id=%s AND user_id=%s", (reservation_id, user_id))
    if cursor.rowcount == 0:
        print("❌ No reservation found for that ID.")
    else:
        db.commit()
        print("✅ Reservation cancelled successfully!")


def view_user_reservations(user_id):
    cursor.execute("""
        SELECT r.id as reservation_id, s.seat_number, w.name as workspace, r.reservation_date, r.time_slot
        FROM reservations r
        JOIN seats s ON r.seat_id = s.id
        JOIN workspaces w ON s.workspace_id = w.id
        WHERE r.user_id=%s
    """, (user_id,))
    reservations = cursor.fetchall()
    if not reservations:
        print("No reservations found.")
    else:
        print(tabulate(reservations, headers="keys", tablefmt="grid"))

# ----------------------
# Console Menu
# ----------------------
def main():
    user_id = int(input("Enter your User ID: "))

    while True:
        print("\n--- Workspace Seat Reservation ---")
        print("1. List workspaces")
        print("2. List available seats")
        print("3. Reserve a seat")
        print("4. Cancel a reservation")
        print("5. View my reservations")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            list_workspaces()
        elif choice == '2':
            workspace_id = int(input("Enter Workspace ID: "))
            date = input("Enter reservation date (YYYY-MM-DD): ")
            slot = input("Enter time slot (Morning/Afternoon/Evening): ")
            list_available_seats(workspace_id, date, slot)
        elif choice == '3':
            workspace_id = int(input("Enter Workspace ID: "))
            date = input("Enter reservation date (YYYY-MM-DD): ")
            slot = input("Enter time slot (Morning/Afternoon/Evening): ")
            available_seats = list_available_seats(workspace_id, date, slot)
            if available_seats:
                seat_id = int(input("Enter Seat ID to reserve: "))
                reserve_seat(user_id, seat_id, date, slot)
        elif choice == '4':
            reservation_id = int(input("Enter Reservation ID to cancel: "))
            cancel_reservation(user_id, reservation_id)
        elif choice == '5':
            view_user_reservations(user_id)
        elif choice == '6':
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
