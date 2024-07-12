import enum
import logging
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import bcrypt

# Initialize logging
logging.basicConfig(filename='st_marys_logistics.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define Enums
class TransportationStatus(enum.Enum):
    SCHEDULED = 'Scheduled'
    IN_TRANSIT = 'In Transit'
    DELIVERED = 'Delivered'

# Database Initialization
def initialize_database():
    try:
        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()

        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS warehouses (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        location TEXT NOT NULL
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY,
                        warehouse_id INTEGER,
                        item_name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS transportation (
                         id INTEGER PRIMARY KEY,
                         vehicle_number TEXT NOT NULL,
                         driver_name TEXT NOT NULL,
                         destination TEXT NOT NULL,
                         status TEXT NOT NULL,
                         transport_type TEXT,
                         CONSTRAINT valid_status CHECK (status IN ('Scheduled', 'In Transit', 'Delivered'))
                     )''')

        # Create users table for data security
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL
                    )''')

        # Check if the admin user already exists
        c.execute('''SELECT COUNT(*) FROM users WHERE username = ?''', ('admin',))
        if c.fetchone()[0] == 0:
            admin_password = 'admin'  # Set a default password for the admin user
            admin_password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            c.execute('''INSERT INTO users (username, password_hash) VALUES (?, ?)''',
                      ('admin', admin_password_hash))
            logging.info('Admin user created with default password.')
        else:
            logging.info('Admin user already exists.')

        conn.commit()
        logging.info('Database initialized successfully.')
    except sqlite3.Error as e:
        logging.error(f'Database initialization error: {e}')
    finally:
        conn.close()

# Inventory Management Functions
def add_inventory_item(self, warehouse_id, item_name, quantity):
    try:
        conn = sqlite3.connect('st_marys_logistics.db', check_same_thread=False)
        c = conn.cursor()

        c.execute('''INSERT INTO inventory (warehouse_id, item_name, quantity) VALUES (?, ?, ?)''',
                  (warehouse_id, item_name, quantity))

        conn.commit()
        logging.info(f'Added {quantity} units of {item_name} to warehouse {warehouse_id}.')
    except sqlite3.Error as e:
        logging.error(f'Error adding inventory item: {e}')
    finally:
        conn.close()

def update_inventory_item(self, item_id, warehouse_id, item_name, quantity):
    try:
        conn = sqlite3.connect('st_marys_logistics.db', check_same_thread=False)
        c = conn.cursor()

        c.execute('''UPDATE inventory SET warehouse_id=?, item_name=?, quantity=? WHERE id=?''',
                  (warehouse_id, item_name, quantity, item_id))

        conn.commit()
        logging.info(f'Updated inventory item ID {item_id}.')
    except sqlite3.Error as e:
        logging.error(f'Error updating inventory item: {e}')
    finally:
        conn.close()

def delete_inventory_items(self, item_id):
    try:
        conn = sqlite3.connect('st_marys_logistics.db', check_same_thread=False)
        c = conn.cursor()

        c.execute('''DELETE FROM inventory WHERE id=?''', (item_id,))

        conn.commit()
        logging.info(f'Deleted inventory item ID {item_id}.')
    except sqlite3.Error as e:
        logging.error(f'Error deleting inventory item: {e}')
    finally:
        conn.close()

# Transportation Management Functions
def add_transportation(vehicle_number, driver_name, destination, status):
    pool = ConnectionPool()
    conn = pool.acquire_connection()
    try:
        c = conn.cursor()

        c.execute(
            '''INSERT INTO transportation (vehicle_number, driver_name, destination, status) 
               VALUES (?, ?, ?, ?)''',
            (vehicle_number, driver_name, destination, status.value))  # Ensure status is stored as string

        conn.commit()
        logging.info(f'Added transportation with vehicle number {vehicle_number} to {destination}. Status: {status}')
    except sqlite3.Error as e:
        logging.error(f'Error adding transportation: {e}')
        raise e
    finally:
        pool.release_connection(conn)


def update_transportation_status(transport_id, new_status):
    try:
        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()
        c.execute('''UPDATE transportation SET status = ? WHERE id = ?''', (new_status, transport_id))

        conn.commit()
        logging.info(f'Updated transportation ID {transport_id} to status {new_status}.')
    except sqlite3.Error as e:
        logging.error(f'Error updating transportation status: {e}')
    finally:
        conn.close()

def delete_transportation(transport_id):
    try:
        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()
        c.execute('''DELETE FROM transportation WHERE id = ?''', (transport_id,))

        conn.commit()
        logging.info(f'Deleted transportation ID {transport_id}.')
    except sqlite3.Error as e:
        logging.error(f'Error deleting transportation: {e}')
    finally:
        conn.close()

def delete_transportation(transport_id):
    pool = ConnectionPool()
    conn = pool.acquire_connection()
    try:
        c = conn.cursor()
        c.execute('''DELETE FROM transportation WHERE id = ?''', (transport_id,))

        conn.commit()
        logging.info(f'Deleted transportation id {transport_id}.')
    except sqlite3.Error as e:
        logging.error(f'Error deleting transportation: {e}')
        raise e
    finally:
        pool.release_connection(conn)

# User Management Functions
def create_user(username, password):
    try:
        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        c.execute('''INSERT INTO users (username, password_hash) VALUES (?, ?)''', (username, password_hash))

        conn.commit()
        logging.info(f'Created user {username}.')
    except sqlite3.Error as e:
        logging.error(f'Error creating user: {e}')
    finally:
        conn.close()


def authenticate_user(username, password):
    try:
        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()

        # Check if the user exists
        c.execute('''SELECT password_hash FROM users WHERE username = ?''', (username,))
        result = c.fetchone()

        if result:
            stored_hash = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                logging.debug('Password check passed.')
                return True
            else:
                logging.debug('Password mismatch.')
                return False
        else:
            logging.debug('User not found.')
            return False
    except sqlite3.Error as e:
        logging.error(f'Error authenticating user: {e}')
        return False
    finally:
        conn.close()

# Thread-safe Singleton Connection Pool
class ConnectionPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.connections = []
        return cls._instance

    def acquire_connection(self):
        try:
            conn = sqlite3.connect('st_marys_logistics.db', check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            logging.error(f'Error acquiring database connection: {e}')
            raise RuntimeError('Failed to acquire database connection.')

    def release_connection(self, conn):
        try:
            conn.close()
        except sqlite3.Error as e:
            logging.error(f'Error releasing database connection: {e}')

# User-Friendly Interface (Tkinter)
class StMarysLogisticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("St. Mary's Logistics")
        self.root.geometry("800x600")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(self.login_frame, textvariable=self.username_var).grid(row=0, column=1, padx=10, pady=5)
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(self.login_frame, textvariable=self.password_var, show='*').grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, columnspan=2, pady=10)

        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        self.inventory_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Inventory", menu=self.inventory_menu)
        self.inventory_menu.add_command(label="View Inventory Items", command=self.view_inventory_items)

        self.transportation_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Transportation", menu=self.transportation_menu)
        self.transportation_menu.add_command(label="View Transportation Record", command=self.view_transportation_record)

        # Hide menus initially
        self.menu_bar.entryconfig("Inventory", state="disabled")
        self.menu_bar.entryconfig("Transportation", state="disabled")

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if authenticate_user(username, password):
            messagebox.showinfo("Success", "Login Successful!")
            self.show_menu()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def show_menu(self):
        self.menu_bar.entryconfig("Inventory", state="normal")
        self.menu_bar.entryconfig("Transportation", state="normal")

    def view_inventory_items(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Inventory Items")
        self.set_window_size(view_window)

        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()

        c.execute('''SELECT id, warehouse_id, item_name, quantity FROM inventory''')
        records = c.fetchall()
        conn.close()

        cols = ('ID', 'Warehouse ID', 'Item Name', 'Quantity')
        tree = ttk.Treeview(view_window, columns=cols, show='headings')

        for col in cols:
            tree.heading(col, text=col)
        tree.grid(row=0, column=0, columnspan=5)

        for record in records:
            tree.insert("", "end", values=record)

        def add_item():
            add_window = tk.Toplevel(view_window)
            add_window.title("Add Inventory Item")
            self.set_window_size(add_window)

            warehouse_id_var = tk.IntVar()  # Use IntVar for numeric input
            item_name_var = tk.StringVar()
            quantity_var = tk.IntVar()

            tk.Label(add_window, text="Warehouse ID:").grid(row=0, column=0, padx=10, pady=5)
            tk.Entry(add_window, textvariable=warehouse_id_var).grid(row=0, column=1, padx=10, pady=5)
            tk.Label(add_window, text="Item Name:").grid(row=1, column=0, padx=10, pady=5)
            tk.Entry(add_window, textvariable=item_name_var).grid(row=1, column=1, padx=10, pady=5)
            tk.Label(add_window, text="Quantity:").grid(row=2, column=0, padx=10, pady=5)
            tk.Entry(add_window, textvariable=quantity_var).grid(row=2, column=1, padx=10, pady=5)

            def add_to_database():
                warehouse_id = warehouse_id_var.get()
                item_name = item_name_var.get()
                quantity = quantity_var.get()

                conn = sqlite3.connect('st_marys_logistics.db')
                c = conn.cursor()

                c.execute('''INSERT INTO inventory (warehouse_id, item_name, quantity) VALUES (?, ?, ?)''',
                          (warehouse_id, item_name, quantity))

                conn.commit()
                conn.close()

                # Update the Treeview with the new item
                tree.insert("", "end", values=(None, warehouse_id, item_name, quantity))

                add_window.destroy()
                messagebox.showinfo("Success", "Item added successfully.")

            tk.Button(add_window, text="Add", command=add_to_database).grid(row=3, columnspan=2, pady=10)

        def edit_item():
            selected_item = tree.selection()[0]
            item_id = tree.item(selected_item, 'values')[0]
            warehouse_id = tree.item(selected_item, 'values')[1]
            item_name = tree.item(selected_item, 'values')[2]
            quantity = tree.item(selected_item, 'values')[3]

            edit_window = tk.Toplevel(view_window)
            edit_window.title("Edit Inventory Item")
            self.set_window_size(edit_window)

            tk.Label(edit_window, text="Warehouse ID:").grid(row=0, column=0, padx=10, pady=5)
            tk.Entry(edit_window, textvariable=tk.IntVar(value=warehouse_id)).grid(row=0, column=1, padx=10, pady=5)
            tk.Label(edit_window, text="Item Name:").grid(row=1, column=0, padx=10, pady=5)
            tk.Entry(edit_window, textvariable=tk.StringVar(value=item_name)).grid(row=1, column=1, padx=10, pady=5)
            tk.Label(edit_window, text="Quantity:").grid(row=2, column=0, padx=10, pady=5)
            tk.Entry(edit_window, textvariable=tk.IntVar(value=quantity)).grid(row=2, column=1, padx=10, pady=5)

            def update_to_database():
                new_warehouse_id = int(edit_window.winfo_children()[1].get())
                new_item_name = edit_window.winfo_children()[3].get()
                new_quantity = int(edit_window.winfo_children()[5].get())

                conn = sqlite3.connect('st_marys_logistics.db')
                c = conn.cursor()

                c.execute('''UPDATE inventory SET warehouse_id=?, item_name=?, quantity=? WHERE id=?''',
                          (new_warehouse_id, new_item_name, new_quantity, item_id))

                conn.commit()
                conn.close()

                # Update the Treeview with the updated item
                tree.item(selected_item, values=(item_id, new_warehouse_id, new_item_name, new_quantity))

                edit_window.destroy()
                messagebox.showinfo("Success", "Item updated successfully.")

            tk.Button(edit_window, text="Update", command=update_to_database).grid(row=3, columnspan=2, pady=10)

        def delete_item():
            selected_item = tree.selection()[0]
            item_id = tree.item(selected_item, 'values')[0]

            conn = sqlite3.connect('st_marys_logistics.db')
            c = conn.cursor()

            c.execute('''DELETE FROM inventory WHERE id=?''', (item_id,))
            conn.commit()
            conn.close()

            # Remove item from Treeview
            tree.delete(selected_item)
            messagebox.showinfo("Success", "Item deleted successfully.")

        tk.Button(view_window, text="Add Item", command=add_item).grid(row=1, column=0, pady=10)
        tk.Button(view_window, text="Edit Item", command=edit_item).grid(row=1, column=1, pady=10)
        tk.Button(view_window, text="Delete Item", command=delete_item).grid(row=1, column=2, pady=10)
        tk.Button(view_window, text="Close", command=view_window.destroy).grid(row=1, column=3, pady=10)

    def view_transportation_record(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Transportation Record")
        self.set_window_size(view_window)

        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()

        c.execute('''SELECT id, vehicle_number, driver_name, destination, status 
                     FROM transportation''')
        records = c.fetchall()
        conn.close()

        cols = ('ID', 'Vehicle Number', 'Driver Name', 'Destination', 'Status')
        tree = ttk.Treeview(view_window, columns=cols, show='headings')

        for col in cols:
            tree.heading(col, text=col)
        tree.grid(row=0, column=0, columnspan=6)

        for record in records:
            tree.insert("", "end", values=record)

        def add_transportation_record():
            add_window = tk.Toplevel(view_window)
            add_window.title("Add Transportation Record")
            self.set_window_size(add_window)

            vehicle_number_var = tk.StringVar()
            driver_name_var = tk.StringVar()
            destination_var = tk.StringVar()
            status_var = tk.StringVar()

            tk.Label(add_window, text="Vehicle Number:").grid(row=0, column=0, padx=10, pady=5)
            tk.Entry(add_window, textvariable=vehicle_number_var).grid(row=0, column=1, padx=10, pady=5)
            tk.Label(add_window, text="Driver Name:").grid(row=1, column=0, padx=10, pady=5)
            tk.Entry(add_window, textvariable=driver_name_var).grid(row=1, column=1, padx=10, pady=5)
            tk.Label(add_window, text="Destination:").grid(row=2, column=0, padx=10, pady=5)
            tk.Entry(add_window, textvariable=destination_var).grid(row=2, column=1, padx=10, pady=5)
            tk.Label(add_window, text="Status:").grid(row=3, column=0, padx=10, pady=5)
            tk.Entry(add_window, textvariable=status_var).grid(row=3, column=1, padx=10, pady=5)

            tk.Button(add_window, text="Add", command=lambda: self.add_transportation_record(vehicle_number_var.get(), driver_name_var.get(), destination_var.get(), status_var.get())).grid(row=4, columnspan=2, pady=10)

        def edit_transportation_record():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showerror("Error", "Please select an item to edit.")
                return

            selected_item = selected_items[0]
            item_id = tree.item(selected_item, 'values')[0]
            vehicle_number = tree.item(selected_item, 'values')[1]
            driver_name = tree.item(selected_item, 'values')[2]
            destination = tree.item(selected_item, 'values')[3]
            status = tree.item(selected_item, 'values')[4]

            edit_window = tk.Toplevel(view_window)
            edit_window.title("Edit Transportation Record")
            self.set_window_size(edit_window)

            tk.Label(edit_window, text="Vehicle Number:").grid(row=0, column=0, padx=10, pady=5)
            tk.Entry(edit_window, textvariable=tk.StringVar(value=vehicle_number)).grid(row=0, column=1, padx=10,
                                                                                        pady=5)
            tk.Label(edit_window, text="Driver Name:").grid(row=1, column=0, padx=10, pady=5)
            tk.Entry(edit_window, textvariable=tk.StringVar(value=driver_name)).grid(row=1, column=1, padx=10, pady=5)
            tk.Label(edit_window, text="Destination:").grid(row=2, column=0, padx=10, pady=5)
            tk.Entry(edit_window, textvariable=tk.StringVar(value=destination)).grid(row=2, column=1, padx=10, pady=5)
            tk.Label(edit_window, text="Status:").grid(row=3, column=0, padx=10, pady=5)
            tk.Entry(edit_window, textvariable=tk.StringVar(value=status)).grid(row=3, column=1, padx=10, pady=5)

            def update_transportation_record():
                new_vehicle_number = edit_window.winfo_children()[1].get()
                new_driver_name = edit_window.winfo_children()[3].get()
                new_destination = edit_window.winfo_children()[5].get()
                new_status = edit_window.winfo_children()[7].get()

                self.update_transportation_record(item_id, new_vehicle_number, new_driver_name, new_destination,
                                                  new_status)

                tree.item(selected_item, text="",
                          values=(item_id, new_vehicle_number, new_driver_name, new_destination, new_status))

                edit_window.destroy()
                messagebox.showinfo("Success", "Record updated successfully.")

            tk.Button(edit_window, text="Update", command=update_transportation_record).grid(row=4, columnspan=2, pady=10)

        def delete_transportation_record():
            selected_item = tree.selection()[0]
            item_id = tree.item(selected_item, 'values')[0]

            self.delete_transportation_record(item_id)

            tree.delete(selected_item)
            messagebox.showinfo("Success", "Record deleted successfully.")

        tk.Button(view_window, text="Add Record", command=add_transportation_record).grid(row=1, column=0, pady=10)
        tk.Button(view_window, text="Edit Record", command=edit_transportation_record).grid(row=1, column=1, pady=10)
        tk.Button(view_window, text="Delete Record", command=delete_transportation_record).grid(row=1, column=2, pady=10)
        tk.Button(view_window, text="Close", command=view_window.destroy).grid(row=1, column=3, pady=10)


    def add_transportation_record(self, vehicle_number, driver_name, destination, status):
        pool = ConnectionPool()
        conn = pool.acquire_connection()
        try:
            c = conn.cursor()

            c.execute('''INSERT INTO transportation (vehicle_number, driver_name, destination, status) 
                         VALUES (?, ?, ?, ?)''', (vehicle_number, driver_name, destination, status))

            conn.commit()
            logging.info(f'Added transportation record with vehicle number {vehicle_number} to {destination}. Status: {status}')

        except sqlite3.Error as e:
            logging.error(f'Error adding transportation record: {e}')
            messagebox.showerror("Error", f"Error adding transportation record: {e}")
        finally:
            pool.release_connection(conn)

    def show_add_transportation_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Transportation Record")
        self.set_window_size(add_window)

        vehicle_number_var = tk.StringVar()
        driver_name_var = tk.StringVar()
        destination_var = tk.StringVar()
        status_var = tk.StringVar()

        tk.Label(add_window, text="Vehicle Number:").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(add_window, textvariable=vehicle_number_var).grid(row=0, column=1, padx=10, pady=5)
        tk.Label(add_window, text="Driver Name:").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(add_window, textvariable=driver_name_var).grid(row=1, column=1, padx=10, pady=5)
        tk.Label(add_window, text="Destination:").grid(row=2, column=0, padx=10, pady=5)
        tk.Entry(add_window, textvariable=destination_var).grid(row=2, column=1, padx=10, pady=5)
        tk.Label(add_window, text="Status:").grid(row=3, column=0, padx=10, pady=5)
        tk.Entry(add_window, textvariable=status_var).grid(row=3, column=1, padx=10, pady=5)

        tk.Button(add_window, text="Add", command=lambda: self.add_transportation_record(
            vehicle_number_var.get(), driver_name_var.get(), destination_var.get(), status_var.get())).grid(row=4, columnspan=2, pady=10)

    def setup_menus(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.transportation_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Transportation", menu=self.transportation_menu)
        self.transportation_menu.add_command(label="Add Transportation Record", command=self.show_add_transportation_window)
        self.transportation_menu.add_command(label="View Transportation Record", command=self.view_transportation_record)

    def update_transportation_record(self, item_id, vehicle_number, driver_name, destination, status):
        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()

        c.execute('''UPDATE transportation SET vehicle_number=?, driver_name=?, destination=?, status=? WHERE id=?''',
                  (vehicle_number, driver_name, destination, status, item_id))

        conn.commit()
        conn.close()

    def delete_transportation_record(self, item_id):
        conn = sqlite3.connect('st_marys_logistics.db')
        c = conn.cursor()

        c.execute('''DELETE FROM transportation WHERE id=?''', (item_id,))

        conn.commit()
        conn.close()

    def set_window_size(self, window):
        window.update_idletasks()
        width = 800
        height = 600
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    root = tk.Tk()
    app = StMarysLogisticsApp(root)
    root.mainloop()
