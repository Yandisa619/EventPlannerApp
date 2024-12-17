import os

# Paths for Tcl and Tk libraries
os.environ['TCL_LIBRARY'] = r'C:\Users\yndub\tcl8.6.15\library'
os.environ['TK_LIBRARY'] = r'C:\Users\yndub\tk8.6.15\library'

import customtkinter as ctk
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, StringVar, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Configure CustomTkinter theme
ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue")  

def create_database():

    connection = sqlite3.connect("event_planner.db")
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS events")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT,
            attendees INTEGER DEFAULT 0,
            status TEXT CHECK(status IN ('upcoming', 'completed')) NOT NULL,
            price REAL DEFAULT 0,
            revenue REAL DEFAULT 0
        )
    """)
    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_database()

class EventPlannerApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill = "both", expand = True)

    
        self.frames = {}
        for F in (LoginFrame, RegisterFrame, DashboardFrame, AnalyticsFrame, SearchFrame, CreateEventFrame, ManageEventsFrame):
            frame = F(parent = self.container, controller = self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")  

        self.show_frame(LoginFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()  

    def update_stats_periodically(self):
        self.load_statistics()
        self.after(6000, self.update_stats_periodically)
        

        # Main window settings
        self.title("Event Planner")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.9)} x {int(screen_height * 0.9)}")
        self.resizable(False, False)  

        #Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.init_frames()

    
    def initialize_database():
     connection = sqlite3.connect("event_planner.db")
     cursor = connection.cursor()

    
     cursor.execute('''
         CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT UNIQUE NOT NULL,
             email TEXT UNIQUE NOT NULL,
             password TEXT NOT NULL
         )
     ''' )  
    
     connection.commit()
     connection.close()
    


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller 

        # Background Theme
        self.configure(fg_color = "#1a1a1a")

        # Login form
        ctk.CTkLabel(self, text="Login", font=("Poppins", 24, "bold"), text_color = "#ffffff",).pack(pady=30)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", height = 40, corner_radius = 10, fg_color = "#333333", text_color = "#ffffff", placeholder_text_color = "#aaaaaa",)
        self.username_entry.pack(pady=10, fill="x", padx=40)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", height = 40, corner_radius = 10, fg_color = "#333333", text_color = "#ffffff", placeholder_text_color = "#aaaaaa",)
        self.password_entry.pack(pady=10, fill="x", padx=40)

        self.show_password_var = ctk.StringVar(value = "*")
        ctk.CTkCheckBox(
            self,
            text = "Show Password",
            variable = self.show_password_var,
            onvalue = "on",
            offvalue = "off",
            text_color = "#ffffff",
            command = lambda: self.password_entry.configure(show = "" if self.show_password_var.get() == "on" else "*")
        ).pack(pady = 5)

        login_button = ctk.CTkButton(
            self,
            text = "Login",
            height = 50,
            corner_radius = 20,
            fg_color = "#1e90ff",
            hover_color = "#1c86ee",
            text_color = "#ffffff",
            command = self.login_user  
        )
        login_button.pack(pady=10, padx = 40, fill = "x")

        register_button = ctk.CTkButton(
            self,
            text = "Register",
            height = 50,
            corner_radius = 20,
            fg_color = "#1e90ff",
            hover_color = "#1c86ee",
            text_color = "#ffffff",
            command= lambda: controller.show_frame(RegisterFrame) 
        )
        register_button.pack(pady=10, padx = 40, fill = "x")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        connection = sqlite3.connect("event_planner.db")
        cursor = connection.cursor()
       
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            messagebox.showinfo("Success", "Login successful")
            self.controller.show_frame(DashboardFrame)
        else:
            messagebox.showerror("Error", "Invalid username or password")

    
    
class RegisterFrame(ctk.CTkFrame):
    def register_user(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

    

        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        connection = sqlite3.connect("event_planner.db")
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, password))
            connection.commit()
            messagebox.showinfo("Success", "Registration successful")
            self.controller.show_frame(LoginFrame)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or Email already exists")
        finally:
            connection.close()
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent,*args,**kwargs)
        self.controller = controller

        self.configure(fg_color = "#1a1a1a")

        # Registration form
        ctk.CTkLabel(self, text="Register", font=("Poppins", 24, "bold"), text_color = "#ffffff").pack(pady=30)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", height = 40, corner_radius = 10, fg_color = "#333333", text_color = "#ffffff", placeholder_text_color = "#aaaaaa",)
        self.username_entry.pack(pady=10, fill="x", padx=40)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", height = 40, corner_radius = 10, fg_color = "#333333", text_color = "#ffffff", placeholder_text_color = "#aaaaaa",)
        self.email_entry.pack(pady=10, fill="x", padx=40)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", height = 40, corner_radius = 10, fg_color = "#333333", text_color = "#ffffff", placeholder_text_color = "#aaaaaa",)
        self.password_entry.pack(pady=10, fill="x", padx=40)

        self.show_password_var = ctk.StringVar(value = "*")
        ctk.CTkCheckBox(
            self,
            text = "Show Password",
            variable = self.show_password_var,
            onvalue = "on",
            offvalue = "off",
            text_color = "#ffffff",
            command = lambda: self.password_entry.configure(show = "" if self.show_password_var.get() == "on" else "*")  
        ) .pack(pady = 5)

        register_button = ctk.CTkButton(
            self,
            text = "Submit",
            height = 50, 
            corner_radius = 20,
            fg_color = "#1e90ff",
            hover_color = "#1c86ee",
            text_color = "#ffffff",
            command = self.register_user
        )
        register_button.pack(pady = 10, padx = 40, fill = "x")

   
        back_button = ctk.CTkButton(
            self,
            text = "Back",
            height = 50,
            corner_radius = 20,
            fg_color = "#1e90ff",
            hover_color = "#1c86ee",
            text_color = "#ffffff", 
            command = lambda: controller.show_frame(LoginFrame)
        )
        back_button.pack(pady = 10, padx = 40, fill = "x")
    
class AnalyticsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        self.configure(fg_color = "#1a1a1a")

        title_label = ctk.CTkLabel(self, text = "Analytics Dashboard", font = ("Poppins", 20, "bold"), text_color = "#aaaaaa")
        title_label.grid(row = 0, column = 0, pady = 20, sticky = "n")

        stats_frame = ctk.CTkFrame(self, fg_color="#333333", corner_radius=10)
        stats_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.stat_labels = {
            "Upcoming Events": ctk.CTkLabel(stats_frame, text = "0",font=("Poppins", 14), text_color="#ffffff"),
             "Completed Events": ctk.CTkLabel(stats_frame, text="0", font = ("Poppins", 14), text_color = "#ffffff"),
             "Revenue": ctk.CTkLabel(stats_frame, text="R0.00", font = ("Poppins", 14), text_color = "#ffffff"),
             "Total Attendees": ctk.CTkLabel(stats_frame, text="0", font=("Poppins", 14), text_color="#ffffff"),
             "Upcoming Locations": ctk.CTkLabel(stats_frame, text="No upcoming locations", font=("Poppins", 14), text_color="#ffffff"),
        }

        for i, (key, label) in enumerate(self.stat_labels.items()):
            key_label = ctk.CTkLabel(stats_frame, text = f"{key}:", font = ("Poppins", 14, "bold"), text_color = "#cccccc")
            key_label.grid(row = i, column = 0, padx = 10, pady = 5, sticky = "w")
            label.grid(row = i, column = 1, padx = 10, pady = 5, sticky = "e")

        stats_frame.columnconfigure(1, weight = 1)

        self.graph_frame = ctk.CTkFrame(self, fg_color="#262626", corner_radius=10)
        self.graph_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        

        # Placeholder data'
        revenue_data, months = self.get_revenue_data()

        if revenue_data and months:
           self.plot_revenue_trends(revenue_data, months)
        else:
            self.show_no_data_message()

        back_button = ctk.CTkButton(self, text = "Back to Dashboard", height = 40, corner_radius = 10, fg_color = "#ff4d4d", hover_color = "#ff6666", text_color = "#ffffff", command = lambda: self.controller.show_frame(DashboardFrame))
        back_button.grid(row=3, column=0, pady=20, sticky="ew", padx=20)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def get_revenue_data(self):
        """
        Fetches revenue trends data from the database.
        Returns:
            revenue_data(list): List of revenue values.
            months (list): Corresponding months for the revenue data.
        """
        try:
            connection = sqlite3.connect("event_planner.db")
            cursor = connection.cursor()

            cursor.execute("""
                SELECT strftime('%Y-%m', date) AS month, COALESCE(SUM(revenue), 0) AS monthly_revenue
                FROM events
                GROUP BY month
                ORDER BY month
                """)
            data = cursor.fetchall()
            
            revenue_data = [row[0] for row in data]
            months = [row[1] for row in data]
            
            connection.close()

            return revenue_data, months
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return [], []

    def plot_revenue_trends(self, revenue_data, months):
        """
        Plots revenue trends on the graph.

        """
        fig = Figure(figsize = (6,4), dpi = 100)
        ax = fig.add_subplot(111)
        ax.plot(months, revenue_data, marker = "o", linestyle = "-", color = "b", label = "Revenue")
        ax.set_title("Revenue Trends")
        ax.set_xlabel("Months")
        ax.set_ylabel("Revenue (R)")
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master = self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill = ctk.BOTH,expand = True)

    def show_no_data_message(self):
        """
        Displays a message when no data is available for the graph.

        """
        no_data_label = ctk.CTkLabel(self.graph_frame, text = "No data available to display.", font = ("Poppins", 14))
        no_data_label.pack(pady = 20)

    def go_back(self):
        """
        Navigates back to the main dashboard.
        
        """

        lambda: self.controller.show_frame(DashboardFrame)


        

class SearchFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller


        self.grid_columnconfigure(1, weight = 1)

        title_label = ctk.CTkLabel(self, text="Search Events", font=("Poppins", 16, "bold"))
        title_label.grid(row = 0, column = 0, columnspan = 2, pady = 10)

        location_label = ctk.CTkLabel(self, text = "Location:")
        location_label.grid(row = 1, column = 0, sticky = "w", padx = 10, pady = 5)

        self.location_var = StringVar()
        location_entry = ctk.CTkEntry(self, textvariable=self.location_var, placeholder_text="Enter location")
        location_entry.grid(row = 1, column = 1, sticky = "ew", padx = 10, pady = 5)

        date_label = ctk.CTkLabel(self, text = "Date (YYYY-MM-DD):")
        date_label.grid(row = 2, column = 0, sticky = "w", padx = 10, pady = 5)

        self.date_var = StringVar()
        date_entry = ctk.CTkEntry(self, textvariable = self.date_var, placeholder_text = "Enter date")
        date_entry.grid(row = 2, column = 1, sticky = "ew", padx = 10, pady = 5)

        search_button = ctk.CTkButton(self, text = "Search", command = self.perform_search)
        search_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.results_frame = ctk.CTkFrame(self, fg_color = "transparent")
        self.results_frame.grid(row = 4, column = 0, columnspan = 2, sticky = "nsew", padx = 10, pady = 10)

        self.grid_rowconfigure(4, weight = 1)

    def perform_search(self):

       location = self.location_var.get().strip()
       date = self.date_var.get().strip()

       connection = sqlite3.connect("event_planner.db")
       cursor = connection.cursor()

       query = "SELECT name, date, location, status FROM events WHERE 1=1"
       params = []

       if location:
           query += "AND LOWER(location) LIKE ?"
           params.append(f"%{location.lower()}%")

       if date:
           query += " AND date = ?"
           params.append(date)

       try: 
           
           cursor.execute(query, params)
           filtered_events = cursor.fetchall()

           for widget in self.results_frame.winfo_children():
               widget.destroy()

           if filtered_events:
               for event in filtered_events:
                   name, event_date, loc, status = event
                   result_label = ctk.CTkLabel(
                       self.results_frame,
                       text = f"{name} - {loc} on {event_date} ({status})",
                       anchor = "w"
                   )
                   result_label.pack(fill = ctk.X, padx = 5, pady = 2)
           else:
               messagebox.showerror("No Results", "No events match the given criteria")
        
       except sqlite3.Error as e:
          messagebox.showerror("Database Error", f"An error occurred: {e}")
       finally:

           connection.close() 
           
class ManageEventsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        self.configure(fg_color = "#1a1a1a")

        ctk.CTkLabel(self, text = "Manage Events", font = ("Poppins", 24, "bold"), text_color = "#ffffff").pack(pady = 30)

        table_frame = ctk.CTkFrame(self, fg_color="#262626", corner_radius=15)
        table_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.events_table = ttk.Treeview(table_frame, columns = ("ID", "Title", "Date", "Location", "Price"), show = "headings",)
        self.events_table.heading("ID", text = "ID")
        self.events_table.heading("Title", text="Title")
        self.events_table.heading("Date", text="Date")
        self.events_table.heading("Location", text="Location")
        self.events_table.heading("Price", text="Price")
        self.events_table.pack(pady=10, padx=10, fill="both", expand=True)

        self.load_events()

        action_frame = ctk.CTkFrame(self, fg_color="#262626", corner_radius=15)
        action_frame.pack(pady=20, padx=20, fill="x")

        buttons = [
                   ("Add Event", self.add_events),
                   ("Edit Event", self.edit_event),
                   ("Delete Event", self.delete_event),
                   ("Back to Dashboard",lambda: controller.show_frame(DashboardFrame))
        ]

        for btn_text, btn_command in buttons:
            ctk.CTkButton(action_frame, text = btn_text, height = 40, corner_radius = 10, fg_color = "#333333", hover_color = "#444444", text_color = "#ffffff", command = btn_command,).pack(pady = 10, padx = 40, fill = "x")
            

    def load_events(self):
        for row in self.events_table.get_children():
            self.events_table.delete(row)

        connection = sqlite3.connect("event_planner.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        connection.close()

        for event in events:
            self.events_table.insert("", "end", values = event)

    def add_events(self):
        self.controller.show_frame(CreateEventFrame)

    def edit_event(self):
        selected_item = self.events_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an event to edit.")
            return
        event_data = self.events_table.item(selected_item, "values")
        self.controller.frames["EditEventFrame"].load_event(event_data)
        self.controller.show_frame(EditEventFrame)

    def delete_event(self):
        selected_item = self.events_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an event to delete.")
            return
        
        event_id = self.events_table.item(selected_item, "values")[0]

        connection = sqlite3.connect("event_planner.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        connection.commit()
        connection.close()

        messagebox.showinfo("Success", "Event deleted successfully.")
        self.load_events()

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        self.configure(fg_color = "#1a1a1a")

        

        # Dashboard (placeholder)
        ctk.CTkLabel(self, text="Dashboard", font=("Poppins", 24, "bold"), text_color = "#ffffff").pack(pady=30)
      
        # Statistics Section (Cards)
        self.stats_frame = ctk.CTkFrame(self, fg_color = "#262626", corner_radius = 15)
        self.stats_frame.pack(pady = 20, padx = 20, fill = "x")
        
        self.stat_labels = {}
        stats = ["Upcoming Events","Completed Events","Revenue", "Attendees", "Upcoming Locations"]
        for stat in stats:
            card = ctk.CTkFrame(self.stats_frame, fg_color = "#333333", corner_radius = 10, width = 150, height = 100 )
            card.pack(side = "left", padx = 10, pady = 10, expand = True, fill = "both" )
            
            
            ctk.CTkLabel(card, text = stat, font = ("Poppins", 14, "bold"), text_color = "#ffffff").pack(pady = (10, 5))
            self.stat_labels[stat] = ctk.CTkLabel(card, text = "Loading ...", font = ("Poppins", 20, "bold"), text_color = "#00ff00")
            self.stat_labels[stat].pack(pady = (0, 10))
            
        
        self.load_statistics()




        # Navigation Buttons
        nav_frame = ctk.CTkFrame(self, fg_color = "#262626", corner_radius = 15)
        nav_frame.pack(pady = 20, padx = 20, fill = "x")

        nav_buttons = [
            ("Create Event", lambda: controller.show_frame(CreateEventFrame)),
            ("Manage Events", lambda: controller.show_frame(ManageEventsFrame)),
            ("View Analytics", lambda: controller.show_frame(AnalyticsFrame)),
        ]
        for btn_text, btn_command in nav_buttons:
            ctk.CTkButton(nav_frame, text = btn_text, height = 40, corner_radius = 10, fg_color = "#333333", hover_color = "#444444", text_color = "#ffffff", command = btn_command).pack(pady = 10, padx = 40, fill = "x")



        ctk.CTkButton(
            self,
            text = "Logout",
            height = 40,
            corner_radius = 10,
            fg_color = "#ff4d4d",
            hover_color = "#ff6666",
            text_color = "#ffffff",
            command = lambda: controller.show_frame(LoginFrame)  
        ).pack(pady = 20, padx = 40, fill = "x")

    def load_statistics(self):

     try: 

        connection = sqlite3.connect("event_planner.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM events WHERE status = 'upcoming') AS upcoming_count,
                (SELECT COUNT(*) FROM events WHERE status = 'completed') AS completed_count,
                (SELECT COALESCE(SUM(attendees), 0) FROM events) AS total_attendees,
                (SELECT COALESCE(SUM(revenue), 0) FROM events) AS total_revenue
            
        """)
        results = cursor.fetchone()

        if results:
            upcoming_events, completed_events, total_attendees, revenue = results
        else:
            upcoming_events = completed_events = total_attendees = revenue = 0

        cursor.execute("SELECT DISTINCT location FROM events WHERE status = 'upcoming'")
        locations = cursor.fetchall()
        upcoming_locations = ", ".join([loc[0] for loc in locations]) if locations else "No upcoming locations"

        self.stat_labels["Upcoming Events"].configure(text=str(upcoming_events))
        self.stat_labels["Completed Events"].configure(text=str(completed_events))
        self.stat_labels["Revenue"].configure(text=f"R{revenue:,.2f}" if revenue else "R0.00")
        self.stat_labels["Total Attendees"].configure(text=str(total_attendees or 0))
        self.stat_labels["Upcoming Locations"].configure(text=upcoming_locations)

        connection.close()
     except Exception as e:
      print(f"Error loading statistics: {e}")
      for key in self.stat_labels:
          self.stat_labels[key].configure(text = "Error")

        
           
       
class CreateEventFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, user_id = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.user_id = user_id or "guest"

        self.configure(fg_color = "#1a1a1a")

        title_label = ctk.CTkLabel(self, text = "Create Event", font = ("Poppins", 20, "bold"), text_color = "#aaaaaa")
        title_label.grid(row = 0, column = 0, columnspan = 2, pady = (20, 10), sticky = "n")

        self.name_entry = ctk.CTkEntry(self, placeholder_text = "Event Name", font = ("Poppins", 14))
        self.name_entry.grid(row = 1, column = 0, columnspan = 2, padx = 20, pady = (10,5), sticky = "ew")

        self.date_entry = ctk.CTkEntry(self, placeholder_text = "Date (YYYY-MM-DD)", font = ("Poppins", 14))
        self.date_entry.grid(row = 2, column = 0, columnspan = 2, padx = 20, pady = (10, 5), sticky = "ew")

        self.location_entry = ctk.CTkEntry(self, placeholder_text = "Location", font = ("Poppins", 14))
        self.location_entry.grid(row = 3, column = 0, columnspan = 2, padx = 20, pady = (10, 5), sticky = "ew")

        self.attendees_entry = ctk.CTkEntry(self, placeholder_text="Number of Attendees", font = ("Poppins", 14))
        self.attendees_entry.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 5), sticky = ("ew"))

        self.status_entry = ctk.CTkEntry(self, placeholder_text="Status (upcoming/completed)", font = ("Poppins", 14))
        self.status_entry.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 5), sticky = "ew")

        self.revenue_entry = ctk.CTkEntry(self, placeholder_text="Revenue", font = ("Poppins", 14))
        self.revenue_entry.grid(row=6, column=0, columnspan=2, padx=20, pady=(10, 5), sticky = "ew")

        submit_button = ctk.CTkButton(self, text="Submit", height = 40, corner_radius = 10, fg_color = "#28a745", hover_color = "#5cb85c", text_color = "#ffffff", command= lambda: self.add_event(self.user_id),)
        submit_button.grid(row=7, column=0, columnspan=2, pady= (10, 20), padx = 20)

        back_button = ctk.CTkButton(self, text = "Back to Dashboard", height = 40, corner_radius = 10, fg_color = "#ff4d4d", hover_color = "#ff6666", text_color = "#ffffff", command = lambda: self.controller.show_frame(DashboardFrame),)
        back_button.grid(row = 8, column = 0, columnspan = 2, pady = (10, 20), padx = 20)

        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

    def add_event(self, user_id):

        name = self.name_entry.get()
        date = self.date_entry.get()
        location = self.location_entry.get()
        attendees = self.attendees_entry.get()
        status = self.status_entry.get().lower()
        revenue = self.revenue_entry.get()

        if not name or not date or not status:
            messagebox.showwarning("Warning", "Name, date, and status are required fields.")
            return 
        
        if status not in ('upcoming', 'completed'):
           messagebox.showwarning("Warning","Status must be either 'upcoming' or 'completed'.")
           return 
        
        try:
            attendees = int(attendees) if attendees else 0
            revenue = float(revenue) if revenue else 0.0
        except ValueError:
            messagebox.showerror("Error","Attendees must be an integer and revenue must be a number.")
            return
        
        try:

            connection = sqlite3.connect("event_planner.db")
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO events (user_id, event_name, event_date, location, attendees, status, revenue)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, date, location, attendees, status, revenue))
            connection.commit()
            connection.close()
            
            self.clear_form()
            messagebox.showinfo("Success","Event added successfully.")
        except sqlite3.Error as e:
            (f"Database error: {e}")

        

    def clear_form(self):
        self.name_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.location_entry.delete(0, 'end')
        self.attendees_entry.delete(0, 'end')
        self.status_entry.delete(0, 'end')
        self.revenue_entry.delete(0, 'end')


if __name__ == "__main__":
    app = EventPlannerApp()
    app.mainloop()


