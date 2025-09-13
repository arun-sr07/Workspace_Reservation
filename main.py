from datetime import date
from tabulate import tabulate
from db import get_connection
import pymysql
import stdiomask
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from colorama import Fore, Style
console = Console()
# ---- Services ----
from services.workspace_service import (
    list_workspaces,
    list_available_seats,
    reserve_seat,
    cancel_reservation,
    get_user_reservationss,
    list_recommended_seats
)
from services.meeting_service import (
    list_meeting_rooms,
    reserve_room,
    cancel_reservation as cancel_meeting_reservation,
    get_user_reservation as get_meeting_reservations
)
from services.training_service import (
    list_training_rooms,
    reserve_training_room,
    cancel_training_reservation,
    get_user_training_reservations
)
reserved_seats_map = {
    "workspace": set(),
    "meeting": set(),
    "training": set()
}

def show_seat_layout(room_type: str, rows: int, cols: int):
    """Display seat layout with reserved seats in color"""
    reserved = reserved_seats_map[room_type]

    print(Fore.CYAN + f"\n--- {room_type.capitalize()} Seat Layout ---" + Style.RESET_ALL)

    seat_number = 1
    for r in range(rows):
        row_str = ""
        for c in range(cols):
            if seat_number in reserved:
                row_str += Fore.RED + "[X]" + Style.RESET_ALL + " "
            else:
                row_str += Fore.GREEN + f"[{seat_number}]" + Style.RESET_ALL + " "
            seat_number += 1
        print(row_str)

    print(Fore.YELLOW + "\nLegend: [X] Reserved | [n] Available" + Style.RESET_ALL)
# ---------- Helper Printers ----------
def print_table(data, headers=None):
    if not data:
        console.print("[yellow]⚠️ No records found.[/yellow]")
        return

    if isinstance(data[0], dict):
        if headers == "keys" or headers is None:
            headers = list(data[0].keys())
        table = Table(title="Results", box=box.ROUNDED, show_lines=True, style="cyan")
        for h in headers:
            table.add_column(h, style="bold green")
        for row in data:
            table.add_row(*[str(row.get(h, "")) for h in headers])
        console.print(table)
    else:
        # fallback to tabulate
        print("\n" + tabulate(data, headers=headers, tablefmt="fancy_grid"))

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


# ---------- Workspace ----------
def workspace_menu(user_id: int):
    while True:
        console.print(Panel.fit(" [bold cyan]Workspace Seat Reservation[/bold cyan]", style="magenta", box=box.ROUNDED))
        console.print("1.  List Workspaces")
        console.print("2. 🔙 Back to Main Menu")

        choice = input(" Enter choice: ")

        if choice == '1':
            workspaces = list_workspaces()
            print_table(workspaces, headers="keys")

            workspace_id = int(input(" Enter Workspace ID (or 0 to go back): "))
            if workspace_id == 0:
                continue

            reservation_date = input(" Enter Date (YYYY-MM-DD): ")
            try:
                recommended = list_recommended_seats(user_id, workspace_id, reservation_date)
                if recommended:
                    console.print("\n[bold magenta]🔮 Recommended Seats for You:[/bold magenta]")
                    for seat, prob in recommended:
                        console.print(f" Seat {seat} → [green]{prob*100:.0f}% match[/green]")
                else:
                    console.print("[yellow]⚠️ No recommendations available yet. Try reserving a few times first![/yellow]")
            except Exception as e:
                console.print(f"[red]Recommendation Error: {e}[/red]")

            
            seats = list_available_seats(workspace_id, reservation_date)
            print_table(seats, headers="keys")

            while True:
                console.print(Panel.fit("🎯 [bold cyan]Seat Actions[/bold cyan]", style="blue", box=box.SQUARE))
                console.print("1.  Reserve a Seat")
                console.print("2.  Cancel Reservation")
                console.print("3.  View My Reservations")
                console.print("4.  Back to Workspace Menu")
                console.print("5. View Seat Layout")

                sub_choice = input(" Enter choice: ")

                if sub_choice == '1':
                    seat_id = int(input("💺 Enter Seat ID: "))
                    result = reserve_seat(user_id, seat_id, reservation_date, workspace_id)
                    if isinstance(result, dict) and "error" in result:
                        console.print(f"[red] Reservation Failed: {result['error']}[/red]")
                    else:
                        reserved_seats_map["workspace"].add(seat_id)  # update ASCII layout
                        console.print("[green] Reservation Successful ![/green]")
                        show_seat_layout("workspace", 3, 4)  # show updated layout

                elif sub_choice == '2':
                    reservation_id = int(input(" Enter Reservation ID to cancel: "))
                    result = cancel_reservation(reservation_id, user_id)
                    if isinstance(result, dict) and "error" in result:
                        console.print(f"[red] Cancel Failed: {result['error']}[/red]")
                    else:
                        seat_id = int(input("Enter Seat ID to free: "))
                        if seat_id in reserved_seats_map["workspace"]:
                            reserved_seats_map["workspace"].remove(seat_id)  # free seat
                        print("✅ Reservation Cancelled Successfully!")
                        show_seat_layout("workspace", 3, 4)

                elif sub_choice == '3':
                    reservations = get_user_reservationss(user_id)
                    print_table(reservations, headers="keys")

                elif sub_choice == '4':
                    break
                elif sub_choice == '5':
                    show_seat_layout("workspace", 3, 4)
                else:
                    console.print("[yellow] Invalid choice, try again.[/yellow]")

        elif choice == '2':
            break
        else:
            console.print("[yellow] Invalid choice, try again.[/yellow]")


# ---------- Meeting ----------
def meeting_menu(user_id: int):
    while True:
        console.print(Panel.fit(" [bold cyan]Meeting Room Reservation[/bold cyan]", style="magenta", box=box.ROUNDED))
        console.print("1.  List Meeting Rooms")
        console.print("2.  Back to Main Menu")

        choice = input(" Enter choice: ")

        if choice == '1':
            rooms = list_meeting_rooms()
            print_table(rooms, headers="keys")

            room_id = int(input(" Enter Room ID (or 0 to go back): "))
            if room_id == 0:
                continue

            while True:
                console.print(Panel.fit(f"🎯 [bold cyan]Actions for Meeting Room {room_id}[/bold cyan]", style="blue", box=box.SQUARE))
                console.print("1.  Reserve Meeting Room")
                console.print("2.  Cancel Reservation")
                console.print("3.  View My Reservations")
                console.print("4.  Back to Meeting Rooms")

                sub_choice = input(" Enter choice: ")

                if sub_choice == '1':
                    reservation_date = input(" Enter Date (YYYY-MM-DD): ")
                    start_hour = input(" Start Hour (0-23): ")
                    end_hour = input(" End Hour (0-23): ")
                    start_time = f"{start_hour}:00:00"
                    end_time = f"{end_hour}:00:00"

                    result = reserve_room(user_id, room_id, reservation_date, start_time, end_time)
                    if isinstance(result, dict) and "error" in result:
                        console.print(f"[red] Reservation Failed: {result['error']}[/red]")
                    else:
                        console.print("[green] Reservation Successful![/green]")

                elif sub_choice == '2':
                    reservation_id = int(input("🆔 Enter Reservation ID to cancel: "))
                    result = cancel_meeting_reservation(reservation_id, user_id)
                    if isinstance(result, dict) and "error" in result:
                        console.print(f"[red] Cancel Failed: {result['error']}[/red]")
                    else:
                        console.print("[green] Reservation Cancelled![/green]")

                elif sub_choice == '3':
                    reservations = get_meeting_reservations(user_id)
                    print_table(reservations, headers="keys")

                elif sub_choice == '4':
                    break
                else:
                    console.print("[yellow] Invalid choice, try again.[/yellow]")

        elif choice == '2':
            break
        else:
            console.print("[yellow] Invalid choice, try again.[/yellow]")


# ---------- Training ----------
def training_menu(user_id: int):
    while True:
        console.print(Panel.fit(" [bold cyan]Training Room Reservation[/bold cyan]", style="magenta", box=box.ROUNDED))
        console.print("1.  List Training Rooms")
        console.print("2.  Back to Main Menu")

        choice = input(" Enter choice: ")

        if choice == '1':
            rooms = list_training_rooms()
            print_table(rooms, headers="keys")

            room_id = int(input(" Enter Training Room ID (or 0 to go back): "))
            if room_id == 0:
                continue

            while True:
                console.print(Panel.fit(f" [bold cyan]Actions for Training Room {room_id}[/bold cyan]", style="blue", box=box.SQUARE))
                console.print("1.  Reserve Training Room")
                console.print("2.  Cancel Reservation")
                console.print("3.  View My Reservations")
                console.print("4.  Back to Training Rooms")

                sub_choice = input(" Enter choice: ")

                if sub_choice == '1':
                    start_date = input(" Enter Start Date (YYYY-MM-DD): ")
                    end_date = input(" Enter End Date (YYYY-MM-DD): ")
                    batch = input(" Enter Batch : ") or None

                    result = reserve_training_room(user_id, room_id, start_date, end_date, batch)
                    if isinstance(result, dict) and "error" in result:
                        console.print(f"[red] Reservation Failed: {result['error']}[/red]")
                    else:
                        console.print("[green] Training Room Reserved Successfully![/green]")

                elif sub_choice == '2':
                    reservation_id = int(input(" Enter Reservation ID to cancel: "))
                    result = cancel_training_reservation(reservation_id)
                    if isinstance(result, dict) and "error" in result:
                        console.print(f"[red] Cancel Failed: {result['error']}[/red]")
                    else:
                        console.print("[green] Reservation Cancelled![/green]")

                elif sub_choice == '3':
                    reservations = get_user_training_reservations(user_id)
                    if reservations:
                        print_table(reservations, headers="keys")
                    else:
                        console.print("[yellow] No training reservations found.[/yellow]")

                elif sub_choice == '4':
                    break
                else:
                    console.print("[yellow] Invalid choice, try again.[/yellow]")

        elif choice == '2':
            break
        else:
            console.print("[yellow] Invalid choice, try again.[/yellow]")


# ---------- Main ----------
def main():
    console.print(Panel.fit("🏢 [bold cyan]Workspace Reservation System[/bold cyan] 🏢", style="bold magenta", box=box.DOUBLE_EDGE))

    user_id = input(" Enter your Employee ID: ")
    password = stdiomask.getpass(" Enter Password: ", mask="*")
    user = get_user_by_id(user_id)

    if not user:
        console.print("[red] Invalid User ID.[/red]")
        return
    if user["password"] != password:
        console.print("[red] Invalid Password.[/red]")
        return None

    console.print(f"[bold green] Welcome {user['username']}![/bold green] Role: [cyan]{user['role']}[/cyan]")
    while True:
        print(Fore.CYAN + "\n=== Main Menu ===" + Style.RESET_ALL)
        print(Fore.YELLOW + "1." + Style.RESET_ALL + "  Workspace Reservations")
        print(Fore.YELLOW + "2." + Style.RESET_ALL + "  Meeting Room Reservations")

        # Show Training Room option only for management
        if user["role"].lower() == "management":
            print(Fore.YELLOW + "3." + Style.RESET_ALL + "  Training Room Reservations")
            print(Fore.RED + "4." + Style.RESET_ALL + "  Exit")
            choice = input("Enter choice: ")
        else:
            print(Fore.RED + "3." + Style.RESET_ALL + "  Exit")
            choice = input("Enter choice: ")

        if choice == '1':
            workspace_menu(user_id)

        elif choice == '2':
            meeting_menu(user_id)

        elif choice == '3' and user["role"].lower() == "management":
            training_menu(user_id)

        elif (choice == '3' and user["role"].lower() != "management") or \
             (choice == '4' and user["role"].lower() == "management"):
            print(" Exiting. Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
