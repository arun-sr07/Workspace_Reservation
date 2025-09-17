import tkinter as tk
from tkcalendar import DateEntry
from tkinter import messagebox, ttk
from datetime import date,datetime
from services.workspace_service import (
    list_workspaces,
    list_available_seats,
    list_all_seats,
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

from db import get_connection
import pymysql


# ---------- Login ----------
def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def login():
    user_id = entry_user_id.get()
    password = entry_password.get()

    user = get_user_by_id(user_id)
    if not user:
        messagebox.showerror("Error", "Invalid User ID")
        return
    if user["password"] != password:
        messagebox.showerror("Error", "Invalid Password")
        return

    login_frame.pack_forget()
    open_main_menu(user)


# ---------- Main Menu ----------
def open_main_menu(user):
    main_frame = tk.Frame(root, padx=10, pady=10)
    main_frame.pack()

    tk.Label(main_frame, text=f"Welcome {user['username']} ({user['role']})", font=("Arial", 14)).pack(pady=5)

    
    
    tk.Button(main_frame, text="Workspace Reservations", width=30,
              command=lambda: open_workspace_menu(user)).pack(pady=5)
    tk.Button(main_frame, text="Meeting Room Reservations", width=30,
              command=lambda: open_meeting_menu(user)).pack(pady=5)
    if user["role"].lower() == "management":
        tk.Button(main_frame, text="Training Room Reservations", width=30,
                  command=lambda: open_training_room_menu(user)).pack(pady=5)

    tk.Button(main_frame, text="Exit", width=30, command=root.quit).pack(pady=5)


# ---------- Workspace ----------


def open_workspace_menu(user):
    ws_win = tk.Toplevel(root)
    ws_win.title("Workspace Reservations")
    ws_win.geometry("700x600")

    tk.Label(ws_win, text="Select Workspace:").pack()
    workspaces = list_workspaces()
    workspace_map = {w['name']: w['resource_id'] for w in workspaces}

    ws_var = tk.StringVar()
    ws_dropdown = ttk.Combobox(ws_win, textvariable=ws_var, values=list(workspace_map.keys()))
    ws_dropdown.pack(pady=5)

    tk.Label(ws_win, text="Select Date:").pack()
    date_picker = DateEntry(ws_win, width=12, background='darkblue',
                            foreground='white', borderwidth=2,
                            date_pattern='yyyy-mm-dd', mindate=date.today())
    date_picker.pack(pady=5)

    

    recommendation_label = tk.Label(ws_win, text="", fg="purple", font=("Arial", 11, "bold"))
    recommendation_label.pack(pady=5)

    seat_frame = tk.Frame(ws_win)
    seat_frame.pack(fill="both", expand=True)

    def refresh_seats():
        for widget in seat_frame.winfo_children():
            widget.destroy()

        workspace_id = workspace_map.get(ws_var.get())
        if not workspace_id:
            return

        reservation_date = date_picker.get_date().strftime("%Y-%m-%d")
        seats = list_all_seats(workspace_id, reservation_date)  # must return {seat_id, seat_number, is_reserved}

        cols = 4
        for idx, seat in enumerate(seats):
            seat_id = seat["seat_id"]
            seat_num = seat["seat_number"]
            is_reserved = seat.get("is_reserved", False)

            btn_color = "red" if is_reserved else "lightgreen"
            btn_state = "disabled" if is_reserved else "normal"

            btn = tk.Button(
                seat_frame,
                text=seat_num,
                width=6, height=2,
                bg=btn_color,
                state=btn_state,
                command=lambda sid=seat_id: reserve_selected_seat(user['user_id'], sid, reservation_date, workspace_id)
            )
            btn.grid(row=idx // cols, column=idx % cols, padx=5, pady=5)

    def reserve_selected_seat(user_id, seat_id, reservation_date, workspace_id):
        result = reserve_seat(user_id, seat_id, reservation_date, workspace_id)
        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Reservation Failed", result["error"])
        else:
            messagebox.showinfo("Success", f"Seat {seat_id} reserved for {reservation_date}")
            refresh_seats()

    def open_cancel_window():
        workspace_id = workspace_map.get(ws_var.get())
        if not workspace_id:
            messagebox.showwarning("Warning", "Select a workspace first!")
            return

        reservation_date = date_picker.get_date().strftime("%Y-%m-%d")
        all_reservations = get_user_reservationss(user['user_id'])
        reservations_today = [
            r for r in all_reservations
            
            if str(r["reservation_date"]) == reservation_date
        ]

        if not reservations_today:
            messagebox.showinfo("Info", "You have no reservations for this date.")
            return

        cancel_win = tk.Toplevel(ws_win)
        cancel_win.title("Cancel Reservations")
        cancel_win.geometry("400x300")

        cancel_frame = tk.Frame(cancel_win)
        cancel_frame.pack(expand=True, fill="both", pady=10)

        cols = 4
        for idx, res in enumerate(reservations_today):
            seat_id = res["seat_number"]
            seat_num = res.get("seat_number", seat_id)
            reservation_id = res["reservation_id"]

            btn = tk.Button(
                cancel_frame,
                text=f"{seat_num}\n(#{reservation_id})",
                width=8, height=3,
                bg="red", fg="white",
                command=lambda rid=reservation_id, sid=seat_id: cancel_selected_seat(rid, sid, cancel_win)
            )
            btn.grid(row=idx // cols, column=idx % cols, padx=5, pady=5)

    def cancel_selected_seat(reservation_id, seat_id, cancel_window):
        result = cancel_reservation(reservation_id, user['user_id'])
        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Cancel Failed", result["error"])
        else:
            messagebox.showinfo("Success", f"Seat {seat_id} cancelled.")
            cancel_window.destroy()
            refresh_seats()

    # 🔥 NEW: View all reservations (scrollable)
    def open_all_reservations_window():
        all_res = get_user_reservationss(user['user_id'])
        if not all_res:
            messagebox.showinfo("Info", "You have no reservations.")
            return

        all_win = tk.Toplevel(ws_win)
        all_win.title("My Reservations (All Dates)")
        all_win.geometry("600x350")

        columns = ("Id",  "Seat_id", "Date")
        tree = ttk.Treeview(all_win, columns=columns, show="headings", height=10)
        tree.heading("reservation_id", text="Reservation ID")
        
        tree.heading("seat_id", text="Seat")
        tree.heading("date", text="Date")
        tree.pack(fill="both", expand=True)

        for res in all_res:
            tree.insert("", "end", values=(res["reservation_id"], res["seat_number"], res["reservation_date"]))

        def cancel_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select a reservation to cancel.")
                return
            values = tree.item(selected[0], "values")
            reservation_id = values[0]
            seat_id = values[2]
            result = cancel_reservation(reservation_id, user['user_id'])
            if isinstance(result, dict) and "error" in result:
                messagebox.showerror("Cancel Failed", result["error"])
            else:
                messagebox.showinfo("Success", f"Seat {seat_id} cancelled.")
                tree.delete(selected[0])
                refresh_seats()

        cancel_btn = tk.Button(all_win, text="Cancel Selected Reservation", command=cancel_selected)
        cancel_btn.pack(pady=5)

    def fetch_seats():
        if not ws_var.get():
            messagebox.showwarning("Warning", "Select a workspace first!")
            return
        workspace_id = workspace_map[ws_var.get()]
        reservation_date = date_picker.get_date().strftime("%Y-%m-%d")
        try:
            recs = list_recommended_seats(user['user_id'], workspace_id, reservation_date)
            if recs:
                recommendation_label.config(
                    text="Recommended: " + ", ".join([f"Seat {s} ({p*100:.0f}%)" for s, p in recs])
                )
            else:
                recommendation_label.config(text="No recommendations available.")
        except Exception as e:
            recommendation_label.config(text=f"Error: {e}")

        refresh_seats()

    tk.Button(ws_win, text="Load Seats & Recommendations", command=fetch_seats).pack(pady=5)
    tk.Button(ws_win, text="Cancel My Reservations (Today)", command=open_cancel_window).pack(pady=5)
    tk.Button(ws_win, text="View My Reservations (All Dates)", command=open_all_reservations_window).pack(pady=5)

# ---------- Meeting Room ----------

def open_meeting_menu(user):
    mr_win = tk.Toplevel(root)
    mr_win.title("Meeting Room Reservations")
    mr_win.geometry("850x500")

    tk.Label(mr_win, text="Meeting Rooms", font=("Arial", 14, "bold")).pack(pady=5)

    # --- Meeting Room Table with all columns ---
    columns = ("resource_id", "floor_id", "name", "resource_type", "capacity", "project_name")
    tree = ttk.Treeview(mr_win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=120, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_meeting_rooms():
        tree.delete(*tree.get_children())
        rooms = list_meeting_rooms()
        for room in rooms:
            tree.insert("", "end", values=(
                room["resource_id"],
                room["floor_id"],
                room["name"],
                room["resource_type"],
                room["capacity"],
                room["project_name"]
            ))

    load_meeting_rooms()

    # --- Reservation Form ---
    form_frame = tk.Frame(mr_win, relief="groove", borderwidth=2, padx=10, pady=10)
    form_frame.pack(fill="x", pady=10)

    tk.Label(form_frame, text="Reservation Date:").grid(row=0, column=0, sticky="e")
    date_picker = DateEntry(form_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2,
                            date_pattern='yyyy-mm-dd')
    date_picker.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="Start Hour (0-23):").grid(row=1, column=0, sticky="e")
    start_hour_var = tk.IntVar()
    tk.Spinbox(form_frame, from_=0, to=23, textvariable=start_hour_var, width=5).grid(row=1, column=1, sticky="w")

    tk.Label(form_frame, text="End Hour (0-23):").grid(row=2, column=0, sticky="e")
    end_hour_var = tk.IntVar()
    tk.Spinbox(form_frame, from_=0, to=23, textvariable=end_hour_var, width=5).grid(row=2, column=1, sticky="w")

    def reserve_selected_room():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Room", "Please select a meeting room first!")
            return
        room_id = tree.item(selected[0])["values"][0]  # resource_id

        reservation_date = date_picker.get_date().strftime("%Y-%m-%d")
        start_time = f"{start_hour_var.get()}:00:00"
        end_time = f"{end_hour_var.get()}:00:00"

        result = reserve_room(user['user_id'], room_id, reservation_date, start_time, end_time)
        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Reservation Failed", result["error"])
        else:
            messagebox.showinfo("Success", "Meeting Room Reserved Successfully!")

    def open_cancel_window():
        reservations = get_meeting_reservations(user['user_id'])
        cancel_win = tk.Toplevel(mr_win)
        cancel_win.title("Cancel Meeting Room Reservation")
        cancel_win.geometry("650x350")

        cols = ("Id",  "Date", "Name","Start Time", "End Time")
        tree_cancel = ttk.Treeview(cancel_win, columns=cols, show="headings")
        for col in cols:
            tree_cancel.heading(col, text=col.capitalize())
            tree_cancel.column(col, width=120, anchor="center")
        tree_cancel.pack(fill="both", expand=True)

        for res in reservations:
            tree_cancel.insert("", "end", values=(
                res["reservation_id"], 
                res["reservation_date"],res["office_name"] ,res["start_time"], res["end_time"]
            ))

        def cancel_selected_reservation():
            selected = tree_cancel.selection()
            if not selected:
                messagebox.showwarning("Select Reservation", "Please select a reservation to cancel.")
                return
            reservation_id = tree_cancel.item(selected[0])["values"][0]
            result = cancel_meeting_reservation(reservation_id, user['user_id'])
            if isinstance(result, dict) and "error" in result:
                messagebox.showerror("Cancel Failed", result["error"])
            else:
                messagebox.showinfo("Success", "Reservation Cancelled!")
                cancel_win.destroy()
                load_meeting_rooms()

        tk.Button(cancel_win, text="Cancel Selected Reservation", command=cancel_selected_reservation).pack(pady=5)

    def open_all_reservations_window():
        reservations = get_meeting_reservations(user['user_id'])
        print(reservations)
        all_res_win = tk.Toplevel(mr_win)
        all_res_win.title("My Meeting Room Reservations")
        all_res_win.geometry("650x350")

        cols = ("Id",  "Date", "Name","Start Time", "End Time")
        tree_all = ttk.Treeview(all_res_win, columns=cols, show="headings")
        for col in cols:
            tree_all.heading(col, text=col.capitalize())
            tree_all.column(col, width=120, anchor="center")
        tree_all.pack(fill="both", expand=True)

        for res in reservations:
            tree_all.insert("", "end", values=(
                res["reservation_id"], 
                res["reservation_date"],res["office_name"], res["start_time"], res["end_time"]
            ))

    # --- Buttons ---
    tk.Button(form_frame, text="Reserve Selected Room", command=reserve_selected_room).grid(row=3, column=0, columnspan=2, pady=5)
    tk.Button(mr_win, text="Cancel My Reservations", command=open_cancel_window).pack(pady=3)
    tk.Button(mr_win, text="View My Reservations", command=open_all_reservations_window).pack(pady=3)

    


def open_training_room_menu(user):
    if user["role"].lower() != "management":
        messagebox.showerror("Access Denied", "Only management can reserve training rooms.")
        return

    tr_win = tk.Toplevel(root)
    tr_win.title("Training Room Reservations")
    tr_win.geometry("750x500")

    tk.Label(tr_win, text="Training Rooms", font=("Arial", 14, "bold")).pack(pady=5)

    # --- Table of training rooms ---
    columns = ("Id", "Name", "Capacity", "Floor", "Type")
    tree = ttk.Treeview(tr_win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_training_rooms():
        tree.delete(*tree.get_children())
        rooms = list_training_rooms()
        for room in rooms:
            tree.insert("", "end", values=(
                room["resource_id"],
                room["name"],
                room["capacity"],
                room.get("floor", ""),
                room.get("type", "")
            ))

    load_training_rooms()

    # --- Reservation Form ---
    form_frame = tk.Frame(tr_win, relief="groove", borderwidth=2, padx=10, pady=10)
    form_frame.pack(fill="x", pady=10)

    tk.Label(form_frame, text="Start Date:").grid(row=0, column=0, sticky="e")
    start_date_picker = DateEntry(form_frame, width=12, date_pattern='yyyy-mm-dd')
    start_date_picker.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="End Date:").grid(row=1, column=0, sticky="e")
    end_date_picker = DateEntry(form_frame, width=12, date_pattern='yyyy-mm-dd')
    end_date_picker.grid(row=1, column=1, padx=5)

    tk.Label(form_frame, text="Batch:").grid(row=2, column=0, sticky="e")
    batch_entry = tk.Entry(form_frame, width=20)
    batch_entry.grid(row=2, column=1, padx=5)

    def reserve_selected_room():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Room", "Please select a training room first!")
            return
        room_id = tree.item(selected[0])["values"][0]  # training_room_id
        start_date = start_date_picker.get_date().strftime("%Y-%m-%d")
        end_date = end_date_picker.get_date().strftime("%Y-%m-%d")
        batch = batch_entry.get() or None

        result = reserve_training_room(user['user_id'], room_id, start_date, end_date, batch)
        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Reservation Failed", result["error"])
        else:
            messagebox.showinfo("Success", "Training Room Reserved Successfully!")

    def open_cancel_window(user_id):
        cancel_win = tk.Toplevel(root)
        cancel_win.title("Cancel My Training Reservations")

        # This should return a list of dicts with keys:
        # training_reservation_id, resource_id, start_date, end_date, batch
        reservations = get_user_training_reservations(user_id)

        if not reservations:
            tk.Label(cancel_win, text="No training reservations found.", fg="red").pack()
            return

        tk.Label(cancel_win, text="Click a reservation to cancel it:", font=("Arial", 12, "bold")).pack(pady=5)

        for res in reservations:
            btn_text = (
                f"ID #{res['training_reservation_id']} | "
                f"Room: {res['resource_id']} | "
                f"{res['start_date']} → {res['end_date']} | "
                f"Batch: {res['batch'] or '-'}"
            )
            tk.Button(
                cancel_win,
                text=btn_text,
                command=lambda r=res: cancel_reservation_and_refresh(r, cancel_win)
            ).pack(fill="x", pady=2, padx=5)


    def cancel_reservation_and_refresh(reservation, window):
        result = cancel_training_reservation(reservation["training_reservation_id"])
        if "error" in result:
            messagebox.showerror("Error", f"Cancel Failed: {result['error']}")
        else:
            messagebox.showinfo("Success", "Training Reservation cancelled successfully.")
            window.destroy()
  
              

    def view_reservations():
        reservations = get_user_training_reservations(user['user_id'])
        if not reservations:
            messagebox.showinfo("Info", "No training reservations found.")
            return

        view_win = tk.Toplevel(tr_win)
        view_win.title("My Training Reservations")
        view_win.geometry("600x300")

        columns = ("Id", "Room", "Start", "End", "Batch")
        tree_view = ttk.Treeview(view_win, columns=columns, show="headings")
        for col in columns:
            tree_view.heading(col, text=col)
            tree_view.column(col, anchor="center", width=100)
        tree_view.pack(fill="both", expand=True)

        for res in reservations:
            tree_view.insert("", "end", values=(
                res["training_reservation_id"],
                res.get("room_name", ""),
                res["start_date"],
                res["end_date"],
                res.get("batch", "")
            ))

    # --- Buttons ---
    tk.Button(form_frame, text="Reserve Selected Training Room", command=reserve_selected_room).grid(row=3, column=0, columnspan=2, pady=5)
    tk.Button(
    tr_win,
    text="Cancel Reservation",
    command=lambda: open_cancel_window(user["user_id"])
).pack(pady=5)
    tk.Button(tr_win, text="View My Reservations", command=view_reservations).pack(pady=5)




# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Workspace Reservation System")
root.geometry("400x250")

login_frame = tk.Frame(root, padx=20, pady=20)
login_frame.pack()

tk.Label(login_frame, text="Employee ID:").pack()
entry_user_id = tk.Entry(login_frame)
entry_user_id.pack()

tk.Label(login_frame, text="Password:").pack()
entry_password = tk.Entry(login_frame, show="*")
entry_password.pack()

tk.Button(login_frame, text="Login", command=login).pack(pady=10)

root.mainloop()
