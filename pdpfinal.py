import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"C:\app\kamal\product\21c\dbhomeXE\bin")

import os
import datetime
from abc import ABC, abstractmethod
#Strategy Design Pattern
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, house_no, payment_date, amount_paid):
        pass
class CreditCardPayment(PaymentStrategy):
    def process_payment(self, house_no, payment_date, amount_paid):
        print(f"Processing credit card payment of {amount_paid} for house {house_no} on {payment_date}.")

class CashPayment(PaymentStrategy):
    def process_payment(self, house_no, payment_date, amount_paid):
        print(f"Processing cash payment of {amount_paid} for house {house_no} on {payment_date}.")

class BankTransferPayment(PaymentStrategy):
    def process_payment(self, house_no, payment_date, amount_paid):
        print(f"Processing bank transfer payment of {amount_paid} for house {house_no} on {payment_date}.")

# Singleton Pattern for database connection
class DatabaseConnection:
    _instance = None

    def __new__(cls, user, password, dsn):
        if cls._instance is None:
            try:
                cls._instance = super(DatabaseConnection, cls).__new__(cls)
                cls._instance.connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
                print("Connected to the database!")
            except cx_Oracle.DatabaseError as e:
                print(f"Database connection error: {e}")
                cls._instance = None
        return cls._instance

    @classmethod
    def get_connection(cls):
        return cls._instance.connection if cls._instance else None

# Command Pattern for database operations
class Command:
    def execute(self):
        raise NotImplementedError("Subclasses should implement this method")

class ListApartmentsCommand(Command):
    def __init__(self, connection):
        self.connection = connection

    def execute(self):
        if not self.connection:
            print("No database connection available.")
            return None
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT apartment_id, apartment_name, address, num_of_rooms, rent
                FROM Apartment
            """)
            apartments = cursor.fetchall()
            if apartments:
                return apartments  
            else:
                print("No apartments found.")
                return []
        except cx_Oracle.DatabaseError as e:
            print(f"Error listing apartments: {e}")
            return None
        finally:
            if cursor:
                cursor.close()


class AddTenantCommand(Command):
    def __init__(self, connection, house_no, tenant_name, phone_number, apartment_id, move_in_date):
        self.connection = connection
        self.house_no = house_no
        self.tenant_name = tenant_name
        self.phone_number = phone_number
        self.apartment_id = apartment_id
        self.move_in_date = move_in_date

    def execute(self):
        if not self.connection:
            print("No database connection available.")
            return
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Tenant (house_no, tenant_name, phone_number, apartment_id, move_in_date)
                VALUES (:1, :2, :3, :4, :5)
            """, (self.house_no, self.tenant_name, self.phone_number, self.apartment_id, self.move_in_date))
            self.connection.commit()
            print(f"Tenant '{self.tenant_name}' added successfully.")
        except cx_Oracle.DatabaseError as e:
            self.connection.rollback()
            print(f"Error adding tenant: {e}")
        finally:
            if cursor:
                cursor.close()

class UpdateTenantCommand(Command):
    def __init__(self, connection, house_no, tenant_name, phone_number, apartment_id, move_in_date):
        self.connection = connection
        self.house_no = house_no
        self.tenant_name = tenant_name
        self.phone_number = phone_number
        self.apartment_id = apartment_id
        self.move_in_date = move_in_date

    def execute(self):
        if not self.connection:
            print("No database connection available.")
            return
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE Tenant
                SET tenant_name = :1, phone_number = :2, apartment_id = :3, move_in_date = :4
                WHERE house_no = :5
            """, (self.tenant_name, self.phone_number, self.apartment_id, self.move_in_date, self.house_no))
            self.connection.commit()
            print(f"Tenant '{self.tenant_name}' updated successfully.")
        except cx_Oracle.DatabaseError as e:
            self.connection.rollback()
            print(f"Error updating tenant: {e}")
        finally:
            if cursor:
                cursor.close()

class DeleteTenantCommand(Command):
    def __init__(self, connection, house_no):
        self.connection = connection
        self.house_no = house_no
        

    def execute(self):
        if not self.connection:
            print("No database connection available.")
            return
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Tenant WHERE house_no = :1", (self.house_no,))
            self.connection.commit()
            print(f"Tenant Record in '{self.house_no}' deleted successfully.")
        except cx_Oracle.DatabaseError as e:
            self.connection.rollback()
            print(f"Error deleting tenant: {e}")
        finally:
            if cursor:
                cursor.close()

class ListTenantsCommand(Command):
    def __init__(self, connection):
        self.connection = connection

    def execute(self):
        if not self.connection:
            print("No database connection available.")
            return None 
        
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT house_no, tenant_name, phone_number, apartment_id, move_in_date, due_amount
                FROM Tenant
            """)
            tenants = cursor.fetchall()
            if tenants:
                print("List of Tenants:")
                for tenant in tenants:
                    print(f"House No: {tenant[0]}, Name: {tenant[1]}, Phone: {tenant[2]}, "
                          f"Apartment ID: {tenant[3]}, Move-In Date: {tenant[4]}, Due Amount: {tenant[5]}")
            else:
                print("No tenants found.")
            return tenants  
        except cx_Oracle.DatabaseError as e:
            print(f"Error listing tenants: {e}")
            return None
        finally:
            if cursor:
                cursor.close()


# Observer Pattern for audit logging
class Observer:
    def update(self, event_type, data):
        raise NotImplementedError("Subclasses should implement this method")

class AuditLogger(Observer):
    def __init__(self, connection):
        self.connection = connection

    def update(self, event_type, data):
        cursor = None
        try:
            cursor = self.connection.cursor()
            if event_type == 'DELETE':
                # Log only the house_no for DELETE event
                cursor.execute("""
                    INSERT INTO Audit_Tenant (house_no, action)
                    VALUES (:1, :2)
                """, (data['house_no'], event_type))
            else:
                # For other events, log full tenant details
                cursor.execute("""
                    INSERT INTO Audit_Tenant (house_no, tenant_name, phone_number, apartment_id, move_in_date, action)
                    VALUES (:1, :2, :3, :4, :5, :6)
                """, (data['house_no'], data['tenant_name'], data['phone_number'], data['apartment_id'], data['move_in_date'], event_type))

            self.connection.commit()
            print(f"Audit log added for {event_type} action.")
        except cx_Oracle.DatabaseError as e:
            print(f"Error logging audit: {e}")
        finally:
            if cursor:
                cursor.close()


# Subject class for notifying observers
class TenantManager:
    def __init__(self):
        self.observers = []
        

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data):
        for observer in self.observers:
            observer.update(event_type, data)

    def list_apartments(self, command):
        apartments = command.execute()  
        return apartments

    def add_tenant(self, command):
        command.execute()
        tenant_data = {
            'house_no': command.house_no,
            'tenant_name': command.tenant_name,
            'phone_number': command.phone_number,
            'apartment_id': command.apartment_id,
            'move_in_date': command.move_in_date
        }
        self.notify_observers('INSERT', tenant_data)

    def update_tenant(self, command):
        command.execute()
        tenant_data = {
            'house_no': command.house_no,
            'tenant_name': command.tenant_name,
            'phone_number': command.phone_number,
            'apartment_id': command.apartment_id,
            'move_in_date': command.move_in_date
        }
        self.notify_observers('UPDATE', tenant_data)

    def delete_tenant(self,command):
        command.execute()
        tenant_data = {
            'house_no': command.house_no,
        }
        self.notify_observers('DELETE', tenant_data)

# GUI code for login page
class LoginPage(tk.Tk):
    def __init__(self, tenant_manager, db_connection):
        super().__init__()
        self.tenant_manager = tenant_manager
        self.db_connection = db_connection
        self.title("Login Page")
        self.geometry("300x350")

        
        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login as Admin", command=self.admin_login).pack(pady=10)
        tk.Button(self, text="Login as Tenant", command=self.tenant_login).pack(pady=10)

    def admin_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin123":
            self.destroy()  
            admin_app = AdminApp(self.tenant_manager, self.db_connection) 
            admin_app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid admin credentials.")

    def tenant_login(self):
        house_no = self.username_entry.get()  
        password = self.password_entry.get()  

        cursor = self.db_connection.cursor()
        try:
            if password == "tenant123":
                cursor.execute("SELECT house_no FROM Tenant WHERE house_no = :house_no", {'house_no': house_no})
                tenant_data = cursor.fetchone()

            if tenant_data:                
                self.destroy() 
                tenant_app = TenantApp(self.tenant_manager, self.db_connection,house_no)  
                tenant_app.mainloop()
            else:
                messagebox.showerror("Login Failed", "Invalid house number.")
        except cx_Oracle.DatabaseError as e:
            print("Database error:", e)
            messagebox.showerror("Login Failed", "An error occurred while checking credentials.")

      

class TenantApp(tk.Tk):
    
    def __init__(self, tenant_manager, db_connection, house_no):
        super().__init__()
        self.tenant_manager = tenant_manager
        self.db_connection = db_connection
        self.house_no = house_no  
        self.title("Tenant Dashboard")
        self.geometry("400x400")

        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="MENU", menu=options_menu)

        options_menu.add_command(label="View Due Amount", command=self.view_due_amount)
        options_menu.add_command(label="View Payment History", command=self.view_payment_history_gui)
        options_menu.add_command(label="Make Payment", command=self.make_payment_gui)
        options_menu.add_command(label="Request Maintenance", command=self.request_maintenance_gui)
        options_menu.add_command(label="Logout", command=self.destroy)

    def view_due_amount(self):
        house_no = self.house_no 
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("SELECT due_amount FROM Tenant WHERE house_no = :house_no", {'house_no': house_no})
            due_amount_data = cursor.fetchone()

            if due_amount_data:
                due_amount = due_amount_data[0]
                messagebox.showinfo("Due Amount", f"The due amount for tenant with house number {house_no} is: {due_amount}")
            else:
                messagebox.showerror("No Data Found", f"No tenant found with house number {house_no}.")
        except cx_Oracle.DatabaseError as e:
            print("Database error:", e)
            messagebox.showerror("Database Error", "An error occurred while retrieving the due amount.")
        finally:
            cursor.close()

    def view_payment_history_gui(self):
        history_window = tk.Toplevel(self)
        history_window.title("Payment History")

        house_no = self.house_no  
        self.view_payment_history(house_no, history_window)  

    def view_payment_history(self, house_no, history_window):
        
        cursor = self.db_connection.cursor()
        try:
           
            for widget in history_window.winfo_children():
                widget.destroy()  

            cursor.execute("SELECT payment_id, payment_date, amount_paid, payment_method FROM SYSTEM.Payment WHERE house_no = :1", (house_no,))
            rows = cursor.fetchall()

            if rows:
                row_num = 0  
                for row in rows:
                    tk.Label(history_window, text=f"Payment ID: {row[0]}, Date: {row[1]}, Amount: {row[2]}, Method: {row[3]}").grid(row=row_num, column=0, padx=5, pady=5, columnspan=2, sticky="w")
                    row_num += 1
            else:
                tk.Label(history_window, text="No payment history found.").grid(row=0, column=0, padx=5, pady=5, columnspan=2, sticky="w")
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", "Error fetching payment history: " + str(e))
        finally:
            cursor.close()
    def make_payment_gui(self):
        payment_window = tk.Toplevel(self)
        payment_window.title("Make Payment")

        tk.Label(payment_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
        house_no_entry = tk.Entry(payment_window)
        house_no_entry.grid(row=0, column=1, padx=5, pady=5)
        house_no_entry.insert(0, self.house_no) 
        house_no_entry.config(state="readonly") 

        tk.Label(payment_window, text="Payment Date (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
        payment_date_entry = tk.Entry(payment_window)
        payment_date_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(payment_window, text="Amount Paid").grid(row=2, column=0, padx=5, pady=5)
        amount_paid_entry = tk.Entry(payment_window)
        amount_paid_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(payment_window, text="Payment Method").grid(row=3, column=0, padx=5, pady=5)
        payment_method_var = tk.StringVar(payment_window)
        payment_method_var.set("Credit Card")  
        payment_method_menu = tk.OptionMenu(payment_window, payment_method_var, "Credit Card", "Cash", "Bank Transfer")
        payment_method_menu.grid(row=3, column=1, padx=5, pady=5)

        def process_payment():
            payment_date = payment_date_entry.get()
            amount_paid = amount_paid_entry.get()
            payment_method = payment_method_var.get()

            if payment_method == "Credit Card":
                strategy = CreditCardPayment()
            elif payment_method == "Cash":
                strategy = CashPayment()
            elif payment_method == "Bank Transfer":
                strategy = BankTransferPayment()
            else:
                messagebox.showerror("Error", "Invalid payment method")
                return

            strategy.process_payment(self.house_no, payment_date, amount_paid)
            self.make_payment(self.house_no, payment_date, amount_paid, payment_method)

        tk.Button(payment_window, text="Submit Payment", command=process_payment).grid(row=4, columnspan=2, pady=10)

    def make_payment(self, house_no, payment_date, amount_paid, payment_method):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("SELECT * FROM SYSTEM.Tenant WHERE house_no = :1", (house_no,))
            result = cursor.fetchone()
            if result is not None:
                cursor.execute(
                    "INSERT INTO SYSTEM.Payment (house_no, payment_date, amount_paid, payment_method) "
                    "VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4)",
                    (house_no, payment_date, amount_paid, payment_method)
                )
                cursor.execute(
                    "UPDATE SYSTEM.Tenant "
                    "SET due_amount = due_amount - :1 "
                    "WHERE house_no = :2",
                    (amount_paid, house_no)
                )
                self.db_connection.commit()
                messagebox.showinfo("Success", "Payment recorded successfully!")
            else:
                messagebox.showwarning("Warning", "No tenant found with that house number.")
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", "Error recording payment: " + str(e))
            self.db_connection.rollback()
        finally:
            cursor.close()

    def request_maintenance_gui(self):
        maintenance_window = tk.Toplevel(self)
        maintenance_window.title("Request Maintenance")

        tk.Label(maintenance_window, text="Apartment ID").grid(row=0, column=0, padx=5, pady=5)
        apartment_id_entry = tk.Entry(maintenance_window)
        apartment_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(maintenance_window, text="House No").grid(row=1, column=0, padx=5, pady=5)
        house_no_entry = tk.Entry(maintenance_window)
        house_no_entry.grid(row=1, column=1, padx=5, pady=5)
        house_no_entry.insert(0, self.house_no)
        house_no_entry.config(state="readonly")

        tk.Label(maintenance_window, text="Issue Description").grid(row=2, column=0, padx=5, pady=5)
        issue_description_entry = tk.Entry(maintenance_window)
        issue_description_entry.grid(row=2, column=1, padx=5, pady=5)

        def submit_request():
            apartment_id = apartment_id_entry.get()
            issue_description = issue_description_entry.get()
            self.request_maintenance(apartment_id, self.house_no, issue_description)

            apartment_id_entry.delete(0, tk.END)
            issue_description_entry.delete(0, tk.END)

        tk.Button(maintenance_window, text="Submit Request", command=submit_request).grid(row=3, columnspan=2, pady=10)

    def request_maintenance(self, apartment_id, house_no, issue_description):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("SELECT * FROM SYSTEM.Tenant WHERE house_no = :1", (house_no,))
            result = cursor.fetchone()

            if result is not None:
                cursor.execute(
                    "INSERT INTO SYSTEM.Maintenance(apartment_id, house_no, issue_description, request_date) "
                    "VALUES (:1, :2, :3, SYSDATE)",
                    (apartment_id, house_no, issue_description)
                )
                self.db_connection.commit()
                messagebox.showinfo("Success", "Maintenance request submitted successfully!")
            else:
                messagebox.showwarning("Warning", "No tenant found with that house number.")
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", "Error executing query: " + str(e))
            self.db_connection.rollback()
        finally:
            cursor.close()



class AdminApp(tk.Tk):
    def __init__(self, tenant_manager,connection):
        self.connection = connection
        super().__init__()
        self.tenant_manager = tenant_manager
        self.title("Tenant Management System")
        self.geometry("400x350")
        
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        self.add_frame = tk.Frame(self)
        self.update_frame = tk.Frame(self)
        self.delete_frame = tk.Frame(self)
        self.list_frame = tk.Frame(self)
        self.tenant_frame = tk.Frame(self)
        self.provide_frame = tk.Frame(self)
        self.complaints_frame = tk.Frame(self)
        self.latest_frame = tk.Frame(self)

        tenant_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="MENU", menu=tenant_menu)
        tenant_menu.add_command(label="List Apartments", command=self.show_list_apartments)
        tenant_menu.add_command(label="Add Tenant", command=self.show_add_tenant)
        tenant_menu.add_command(label="Update Tenant", command=self.show_update_tenant)
        tenant_menu.add_command(label="Delete Tenant",command=self.show_delete_tenant)
        tenant_menu.add_command(label="Display Tenant Details", command=self.show_list_tenants)
        tenant_menu.add_command(label="Provide Maintenance Service", command=self.provide_service_gui)
        tenant_menu.add_command(label="Display All Complaints", command=self.display_complaints_gui)
        tenant_menu.add_command(label="Display Latest Modifications", command=self.display_latest_modifications_gui)
        tenant_menu.add_command(label="Logout", command=self.destroy)

    def show_list_apartments(self):
        self.add_frame.pack_forget()
        self.update_frame.pack_forget()
        self.delete_frame.pack_forget()
        self.provide_frame.pack_forget()
        self.tenant_frame.pack_forget()
        self.complaints_frame.pack_forget()
        self.latest_frame.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.treeview = ttk.Treeview(self.list_frame, columns=("Apartment ID", "Apartment Name", "Address", "Rooms", "Rent"), show="headings")
        self.treeview.heading("Apartment ID", text="Apartment ID")
        self.treeview.heading("Apartment Name", text="Apartment Name")
        self.treeview.heading("Address", text="Address")
        self.treeview.heading("Rooms", text="Rooms")
        self.treeview.heading("Rent", text="Rent")
        self.treeview.pack(fill="both", expand=True)

        list_apartments_cmd = ListApartmentsCommand(self.connection)
        apartments = list_apartments_cmd.execute() 
        if apartments:
            for apartment in apartments:
                self.treeview.insert("", "end", values=apartment)
        else:
            print("No apartments available to display.")


    def show_add_tenant(self):
        self.list_frame.pack_forget()
        self.latest_frame.pack_forget()
        self.update_frame.pack_forget()
        self.delete_frame.pack_forget()
        self.tenant_frame.pack_forget()
        self.provide_frame.pack_forget()
        self.complaints_frame.pack_forget()
        self.add_frame.pack(fill="both", expand=True)
        self.create_add_widgets()

    def show_update_tenant(self):
        self.latest_frame.pack_forget()
        self.list_frame.pack_forget()
        self.add_frame.pack_forget()
        self.delete_frame.pack_forget()
        self.provide_frame.pack_forget()
        self.tenant_frame.pack_forget()
        self.complaints_frame.pack_forget()
        self.update_frame.pack(fill="both", expand=True)
        self.create_update_widgets()
        
    def show_delete_tenant(self):
        self.latest_frame.pack_forget()
        self.list_frame.pack_forget()
        self.update_frame.pack_forget()
        self.add_frame.pack_forget()
        self.provide_frame.pack_forget()
        self.tenant_frame.pack_forget()
        self.complaints_frame.pack_forget()
        self.delete_frame.pack(fill="both",expand=True)
        self.create_delete_widgets()
    
    def create_add_widgets(self):
        for widget in self.add_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.add_frame, text="Add Tenant").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self.add_frame, text="House No:").grid(row=1, column=0, padx=10, pady=5)
        self.house_no_entry = tk.Entry(self.add_frame)
        self.house_no_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.add_frame, text="Tenant Name:").grid(row=2, column=0, padx=10, pady=5)
        self.tenant_name_entry = tk.Entry(self.add_frame)
        self.tenant_name_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.add_frame, text="Phone Number:").grid(row=3, column=0, padx=10, pady=5)
        self.phone_entry = tk.Entry(self.add_frame)
        self.phone_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self.add_frame, text="Apartment ID:").grid(row=4, column=0, padx=10, pady=5)
        self.apartment_id_entry = tk.Entry(self.add_frame)
        self.apartment_id_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self.add_frame, text="Move-in Date (YYYY-MM-DD):").grid(row=5, column=0, padx=10, pady=5)
        self.move_in_date_entry = tk.Entry(self.add_frame)
        self.move_in_date_entry.grid(row=5, column=1, padx=10, pady=5)

        tk.Button(self.add_frame, text="Add Tenant", command=self.add_tenant).grid(row=6, column=0, columnspan=2, pady=10)

    def create_update_widgets(self):
        for widget in self.update_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.update_frame, text="Update Tenant").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self.update_frame, text="House No:").grid(row=1, column=0, padx=10, pady=5)
        self.house_no_entry = tk.Entry(self.update_frame)
        self.house_no_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.update_frame, text="Tenant Name:").grid(row=2, column=0, padx=10, pady=5)
        self.tenant_name_entry = tk.Entry(self.update_frame)
        self.tenant_name_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.update_frame, text="Phone Number:").grid(row=3, column=0, padx=10, pady=5)
        self.phone_entry = tk.Entry(self.update_frame)
        self.phone_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self.update_frame, text="Apartment ID:").grid(row=4, column=0, padx=10, pady=5)
        self.apartment_id_entry = tk.Entry(self.update_frame)
        self.apartment_id_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self.update_frame, text="Move-in Date (YYYY-MM-DD):").grid(row=5, column=0, padx=10, pady=5)
        self.move_in_date_entry = tk.Entry(self.update_frame)
        self.move_in_date_entry.grid(row=5, column=1, padx=10, pady=5)

        tk.Button(self.update_frame, text="Update Tenant", command=self.update_tenant).grid(row=6, column=0, columnspan=2, pady=10)

    def create_delete_widgets(self):
        for widget in self.delete_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.delete_frame, text="Delete Tenant").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self.delete_frame, text="House No:").grid(row=1, column=0, padx=10, pady=5)
        self.house_no_entry = tk.Entry(self.delete_frame)
        self.house_no_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(self.delete_frame, text="Delete Tenant", command=self.delete_tenant).grid(row=6, column=0, columnspan=2, pady=10)
    
    def add_tenant(self):
        house_no = self.house_no_entry.get()
        tenant_name = self.tenant_name_entry.get()
        phone_number = self.phone_entry.get()
        apartment_id = self.apartment_id_entry.get()
        move_in_date_str = self.move_in_date_entry.get()

        if not (house_no and tenant_name and phone_number and apartment_id and move_in_date_str):
            messagebox.showwarning("Input Error", "All fields must be filled.")
            return

        try:
            move_in_date = datetime.datetime.strptime(move_in_date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Date Error", "Move-in date must be in the format YYYY-MM-DD.")
            return

        add_tenant_cmd = AddTenantCommand(
            db_connection_instance.get_connection(),
            house_no, tenant_name, phone_number, int(apartment_id), move_in_date
        )
        self.tenant_manager.add_tenant(add_tenant_cmd)
        messagebox.showinfo("Success", "Tenant added successfully")

    def update_tenant(self):
        house_no = self.house_no_entry.get()
        tenant_name = self.tenant_name_entry.get()
        phone_number = self.phone_entry.get()
        apartment_id = self.apartment_id_entry.get()
        move_in_date_str = self.move_in_date_entry.get()

        if not (house_no and tenant_name and phone_number and apartment_id and move_in_date_str):
            messagebox.showwarning("Input Error", "All fields must be filled.")
            return

        try:
            move_in_date = datetime.datetime.strptime(move_in_date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Date Error", "Move-in date must be in the format YYYY-MM-DD.")
            return

        update_tenant_cmd = UpdateTenantCommand(
            db_connection_instance.get_connection(),
            house_no, tenant_name, phone_number, int(apartment_id), move_in_date
        )
        self.tenant_manager.update_tenant(update_tenant_cmd)
        messagebox.showinfo("Success", "Tenant updated successfully")

    def delete_tenant(self):
        house_no = self.house_no_entry.get()

        if not house_no:
            messagebox.showwarning("Input Error", "Fields must not be empty")
            return

        tenant_data = self.fetch_tenant_details(house_no)
        if not tenant_data:
            messagebox.showwarning("Error", "Tenant not found")
            return

        delete_tenant_cmd = DeleteTenantCommand(
            db_connection_instance.get_connection(),
            house_no
        )

        observer = AuditLogger(db_connection_instance.get_connection())
        observer.update('DELETE', tenant_data) 

        try:
            self.tenant_manager.delete_tenant(delete_tenant_cmd)
            messagebox.showinfo('Success', 'Tenant deleted successfully')
        except Exception as e:
            messagebox.showerror('Error', f"Error deleting tenant: {str(e)}")

    def fetch_tenant_details(self, house_no):
        cursor = None
        try:
            cursor = db_connection_instance.get_connection().cursor()
            cursor.execute("""
                SELECT tenant_name, phone_number, apartment_id, move_in_date
                FROM Tenant WHERE house_no = :1
            """, (house_no,))
            tenant_data = cursor.fetchone()
            if tenant_data:
                return {
                    'house_no': house_no,
                    'tenant_name': tenant_data[0],
                    'phone_number': tenant_data[1],
                    'apartment_id': tenant_data[2],
                    'move_in_date': tenant_data[3]
                }
            return None 
        except cx_Oracle.DatabaseError as e:
            print(f"Error fetching tenant details: {e}")
        finally:
            if cursor:
                cursor.close()

    def show_list_tenants(self):
      
        self.latest_frame.pack_forget()
        self.complaints_frame.pack_forget()
        self.add_frame.pack_forget()
        self.update_frame.pack_forget()
        self.delete_frame.pack_forget()
        self.provide_frame.pack_forget()
        self.tenant_frame.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.treeview = ttk.Treeview(self.list_frame, columns=("House No", "Tenant Name", "Phone", "Apartment ID", "Move-In Date", "Due Amount"), show="headings")
        
        self.treeview.heading("House No", text="House No")
        self.treeview.heading("Tenant Name", text="Tenant Name")
        self.treeview.heading("Phone", text="Phone")
        self.treeview.heading("Apartment ID", text="Apartment ID")
        self.treeview.heading("Move-In Date", text="Move-In Date")
        self.treeview.heading("Due Amount", text="Due Amount")
        self.treeview.pack(fill="both", expand=True)

        list_tenants_cmd = ListTenantsCommand(self.connection)
        tenants = list_tenants_cmd.execute()

        if tenants is None:
            messagebox.showerror("Error", "Failed to fetch tenant data.")
            return

        for tenant in tenants:
            self.treeview.insert("", "end", values=tenant)


    # Maintenance Service GUI
    def provide_service_gui(self):
        frames = [
            self.list_frame,self.latest_frame, self.complaints_frame, self.add_frame,
            self.update_frame, self.delete_frame, self.tenant_frame
        ]
        for frame in frames:
            if frame.winfo_ismapped():
                frame.pack_forget()
        self.provide_frame.pack(fill="both", expand=True)

        for widget in self.provide_frame.winfo_children():
            widget.destroy()

        tk.Label(self.provide_frame, text="Apartment ID").grid(row=0, column=0, padx=5, pady=5)
        apartment_id_entry = tk.Entry(self.provide_frame)
        apartment_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.provide_frame, text="House No").grid(row=1, column=0, padx=5, pady=5)
        house_no_entry = tk.Entry(self.provide_frame)
        house_no_entry.grid(row=1, column=1, padx=5, pady=5)

        def provide():
            apartment_id = apartment_id_entry.get()
            house_no = house_no_entry.get()

            result_message = self.provide_service(self.connection, apartment_id, house_no, lambda msg: messagebox.showerror("Error", msg))
            if result_message:
                messagebox.showinfo("Success", result_message)

        tk.Button(self.provide_frame, text="Provide Service", command=provide).grid(row=2, columnspan=2, pady=10)

    def provide_service(self, connection, apartment_id, house_no, error_callback):
        cursor = connection.cursor()
        try:
            if self.check_complaint(connection, apartment_id, house_no):
                if self.incomplete_complaint(connection, apartment_id, house_no):
                    issues_fixed = []
                    cursor.execute("SELECT issue_description FROM SYSTEM.Maintenance WHERE apartment_id = :1 AND house_no = :2", (apartment_id, house_no))
                    rows = cursor.fetchall()
                    for row in rows:
                        issues_fixed.append(row[0])
                    if issues_fixed:
                        cursor.execute(
                            "UPDATE SYSTEM.Maintenance "
                            "SET status ='Completed' WHERE apartment_id = :1 AND house_no = :2",
                            (apartment_id, house_no)
                        )
                        cursor.execute(
                            "UPDATE SYSTEM.Tenant "
                            "SET due_amount = due_amount + 100 "
                            "WHERE house_no = :1",
                            (house_no,)
                        )
                        connection.commit()
                        return f"Maintenance Service Completed for Apartment ID: {apartment_id}, House No: {house_no}. Issues Fixed: {', '.join(issues_fixed)}"
                    else:
                        return "No issues found to fix."
                else:
                    return "Maintenance service already completed."
            else:
                return "No complaint registered for this apartment."
        except cx_Oracle.DatabaseError as e:
            connection.rollback()
            error_callback(f"Error submitting maintenance request: {e}")
            return None
        except cx_Oracle.InterfaceError as e:
            connection.rollback()
            error_callback(f"Database interface error: {e}")
            return None
        finally:
            cursor.close()

    def check_complaint(self, connection, apartment_id, house_no):
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM Maintenance WHERE apartment_id = :1 AND house_no = :2", (apartment_id, house_no))
            count = cursor.fetchone()[0]
            return count > 0
        except cx_Oracle.DatabaseError as e:
            print(f"Error checking complaint: {e}")
            return False
        finally:
            cursor.close()

    def incomplete_complaint(self, connection, apartment_id, house_no):
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM Maintenance WHERE apartment_id = :1 AND house_no = :2 AND status != 'Completed'", (apartment_id, house_no))
            count = cursor.fetchone()[0]
            return count > 0
        except cx_Oracle.DatabaseError as e:
            print(f"Error checking incomplete complaint: {e}")
            return False
        finally:
            cursor.close()


    def display_complaints_gui(self):
        
        infos = []

        frames = [
            self.list_frame, self.update_frame, self.provide_frame,
            self.add_frame, self.delete_frame, self.tenant_frame, self.latest_frame
        ]
        
        for frame in frames:
            if frame.winfo_ismapped():
                frame.pack_forget()
        self.complaints_frame.pack(fill="both", expand=True)

        columns = ("Apartment Name", "House No", "Issue Description", "Request Date", "Status", "Tenant Name", "Tenant Phone", "Apartment Address")
        
        if hasattr(self, 'complaint_tree') and self.complaint_tree.winfo_exists():
            self.complaint_tree.destroy()
        
        if hasattr(self, 'tree_scroll') and self.tree_scroll.winfo_exists():
            self.tree_scroll.destroy()
        
        self.complaint_tree = ttk.Treeview(self.complaints_frame, columns=columns, show="headings")
        
        for col in columns:
            self.complaint_tree.heading(col, text=col)
            self.complaint_tree.column(col, width=150, anchor="w")  
       
        self.complaint_tree.pack(padx=10, pady=10)

        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT m.issue_description, m.request_date, m.status, t.tenant_name, t.phone_number, 
                                    a.apartment_name, a.address, m.house_no
                            FROM Maintenance m
                            JOIN Tenant t ON m.house_no = t.house_no
                            JOIN Apartment a ON m.apartment_id = a.apartment_id""")
            rows = cursor.fetchall()

            if len(rows) == 0:
                self.complaint_tree.insert("", "end", values=("No complaints registered.",) * len(columns))  
            else:
                for row in rows:
                    self.complaint_tree.insert("", "end", values=(row[5], row[7], row[0], row[1], row[2], row[3], row[4], row[6]))

        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", f"Error displaying complaints: {e}")
        finally:
            cursor.close()
    
    
    def display_latest_modifications_gui(self): 
        infos = []

        frames = [
            self.list_frame, self.update_frame, self.provide_frame,
            self.add_frame, self.delete_frame, self.tenant_frame, self.complaints_frame
        ]
        
        for frame in frames:
            if frame.winfo_ismapped():
                frame.pack_forget()
        
        self.latest_frame.pack(fill="both", expand=True)

        columns = ("Audit ID", "House No", "Action", "Change Date")
        
        if hasattr(self, 'latest_tree') and self.latest_tree.winfo_exists():
            self.latest_tree.destroy()
        
        if hasattr(self, 'tree_scroll') and self.tree_scroll.winfo_exists():
            self.tree_scroll.destroy()

        self.latest_tree = ttk.Treeview(self.latest_frame, columns=columns, show="headings")
        
        for col in columns:
            self.latest_tree.heading(col, text=col)
            self.latest_tree.column(col, width=150, anchor="w")  

        self.tree_scroll = tk.Scrollbar(self.latest_frame, orient="vertical", command=self.latest_tree.yview)
        self.latest_tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.pack(side="right", fill="y")

        self.latest_tree.pack(padx=10, pady=10)

        cursor = self.connection.cursor()
        try:
            cursor.execute('''SELECT audit_id, house_no, action, change_date 
                            FROM Audit_Tenant 
                            WHERE change_date = (SELECT MAX(change_date) FROM Audit_Tenant)''')
            rows = cursor.fetchall()

            if len(rows) == 0:
                messagebox.showwarning("Warning", "No modifications made yet")
            else:
                for row in rows:
                    self.latest_tree.insert("", "end", values=row)
                    infos.append({
                        "Audit ID": row[0],
                        "House No": row[1],
                        "Action": row[2],
                        "Change Date": row[3],
                    })
            return infos  

        except cx_Oracle.DatabaseError as e:
            print("Error executing query:", e)
            return []  
        except cx_Oracle.InterfaceError as e:
            print(f"Database interface error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

# Main application setup
if __name__ == "__main__":
    DB_USER = os.getenv('DB_USER', 'system')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'lotus')
    DB_DSN = os.getenv('DB_DSN', 'localhost:1522/XE')

    db_connection_instance = DatabaseConnection(DB_USER, DB_PASSWORD, DB_DSN)
    db_connection = db_connection_instance.get_connection()

    if db_connection:
        audit_logger = AuditLogger(db_connection)
        tenant_manager = TenantManager()
        tenant_manager.register_observer(audit_logger)

        login_app = LoginPage(tenant_manager, db_connection)
        login_app.mainloop()
    else:
        print("Failed to create a valid database connection.")




