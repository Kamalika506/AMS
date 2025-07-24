import tkinter as tk
from tkinter import messagebox, scrolledtext
import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"C:\app\kamal\product\21c\dbhomeXE\bin")

from PIL import Image, ImageTk

# Hardcoded credentials for admin and tenant
USER_CREDENTIALS = {
    "admin": {"username": "admin", "password": "admin123"},
    "tenant": {"username": "tenant", "password": "tenant123"}
}

# Hardcoded database connection credentials
DB_USER = "system"
DB_PASSWORD = "lotus"
DB_DSN = "localhost:1522/XE"

# Global variable for database connection
connection = None


# ========================= Database Connection ==========================
def connect_db():
    global connection
    try:
        connection = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        print("Connected to the database!")
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Database Error", f"Unable to connect to the database: {e}")
        return False
    return True


# ========================= Login =================================
def verify_login():
    username = username_entry.get()
    password = password_entry.get()

    if username == USER_CREDENTIALS["admin"]["username"] and password == USER_CREDENTIALS["admin"]["password"]:
        login_status_label.config(text="Admin login successful!", fg="green")
        if connect_db():
            open_main_window("admin")
    elif username == USER_CREDENTIALS["tenant"]["username"] and password == USER_CREDENTIALS["tenant"]["password"]:
        login_status_label.config(text="Tenant login successful!", fg="green")
        if connect_db():
            open_main_window("tenant")
    else:
        login_status_label.config(text="Login failed", fg="red")
        messagebox.showerror("Error", "Invalid username or password.")


# Function to open the main window with role-specific features
def open_main_window(role):
    login_window.destroy()  # Close the login window

    # Main window
    main_window = tk.Tk()
    main_window.title("Apartment Management System")
    main_window.geometry("500x600")

    if role == "admin":
        tk.Label(main_window, text="Admin Menu", font=("Arial", 14), fg="blue").pack(pady=5)

        # Admin buttons
        tk.Button(main_window, text="List Apartments", command=list_apartments_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Add Tenant", command=add_tenant_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Update Tenant", command=update_tenant_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Delete Tenant", command=delete_tenant_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Display Tenant Details", command=display_tenant_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Provide Maintenance Service", command=provide_service_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Display All Complaints", command=display_complaints_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Display latest modifications", command=display_latest_modifications_gui).pack(
            fill="x", pady=2)
        tk.Button(main_window, text="Logout", command=main_window.destroy).pack(fill="x", pady=2)

    if role == "tenant":
        tk.Label(main_window, text="Tenant Menu", font=("Arial", 14), fg="blue").pack(pady=5)

        # Tenant buttons
        tk.Button(main_window, text="View Apartment Details", command=view_apt_details_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Make Payment", command=make_payment_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Request Maintenance", command=request_maintenance_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="View Payment History", command=view_payment_history_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="View Due Amount", command=view_due_gui).pack(fill="x", pady=2)
        tk.Button(main_window, text="Logout", command=main_window.destroy).pack(fill="x", pady=2)

    main_window.mainloop()


# =========================  Admin-List all Apartments  ==========================
def list_apartments_gui():
    apartment_window = tk.Toplevel()
    apartment_window.title("List of Apartments")

    # Fetch the apartments
    apartments = list_apartments(connection)

    # Create a text widget to display the apartments
    text_area = tk.Text(apartment_window, width=60, height=20)
    text_area.pack(pady=10)

    if not apartments:
        text_area.insert(tk.END, "No apartments found.")
    else:
        for apartment in apartments:
            text_area.insert(tk.END, f"Apartment ID: {apartment['Apartment ID']}\n")
            text_area.insert(tk.END, f"Apartment Name: {apartment['Apartment Name']}\n")
            text_area.insert(tk.END, f"Address: {apartment['Address']}\n")
            text_area.insert(tk.END, f"Number of Rooms: {apartment['Number of Rooms']}\n")
            text_area.insert(tk.END, f"Rent: {apartment['Rent']}\n")
            text_area.insert(tk.END, "-" * 40 + "\n")

    # Make the text area read-only
    text_area.config(state=tk.DISABLED)


def list_apartments(connection):
    cursor = connection.cursor()
    apartments = []
    try:
        cursor.execute('SELECT * FROM "SYSTEM"."APARTMENT"')
        rows = cursor.fetchall()

        if len(rows) == 0:
            print("No apartments found.")
        else:
            for row in rows:
                apartments.append({
                    'Apartment ID': row[0],
                    'Apartment Name': row[1],
                    'Address': row[2],
                    'Number of Rooms': row[3],
                    'Rent': row[4]
                })
        return apartments  # Return the list of apartments
    except cx_Oracle.DatabaseError as e:
        print("Error executing query:", e)
        return []  # Return an empty list in case of error
    finally:
        cursor.close()


# =========================  Admin - Add Tenant  ==========================
def add_tenant_gui():
    tenant_window = tk.Toplevel()
    tenant_window.title("Add Tenant")

    tk.Label(tenant_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(tenant_window)
    house_no_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(tenant_window, text="Tenant Name").grid(row=1, column=0, padx=5, pady=5)
    tenant_name_entry = tk.Entry(tenant_window)
    tenant_name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(tenant_window, text="Phone Number").grid(row=2, column=0, padx=5, pady=5)
    phone_number_entry = tk.Entry(tenant_window)
    phone_number_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(tenant_window, text="Apartment ID").grid(row=3, column=0, padx=5, pady=5)
    apartment_id_entry = tk.Entry(tenant_window)
    apartment_id_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(tenant_window, text="Move-in Date (YYYY-MM-DD)").grid(row=4, column=0, padx=5, pady=5)
    move_in_date_entry = tk.Entry(tenant_window)
    move_in_date_entry.grid(row=4, column=1, padx=5, pady=5)

    def add_tenant_to_db():
        house_no = house_no_entry.get()
        tenant_name = tenant_name_entry.get()
        phone_number = phone_number_entry.get()
        apartment_id = apartment_id_entry.get()
        move_in_date = move_in_date_entry.get()

        try:
            cursor = connection.cursor()
            # Check if a tenant already exists for the specified house number
            cursor.execute(
                "SELECT COUNT(*) FROM SYSTEM.Tenant WHERE house_no = :1",
                (house_no,)
            )
            result = cursor.fetchone()

            if result[0] > 0:
                messagebox.showerror("Error", f"A tenant already exists for house number {house_no}.")
            else:
                # If no tenant exists, insert the new tenant record
                cursor.execute(
                    "INSERT INTO SYSTEM.Tenant (house_no, tenant_name, phone_number, apartment_id, move_in_date) "
                    "VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'))",
                    (house_no, tenant_name, phone_number, apartment_id, move_in_date)
                )
                connection.commit()
                messagebox.showinfo("Success", "Tenant added successfully!")
                tenant_window.destroy()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", f"Failed to add tenant: {e}")
            connection.rollback()
        finally:
            cursor.close()

    tk.Button(tenant_window, text="Save Tenant", command=add_tenant_to_db).grid(row=5, columnspan=2, pady=10)


# =========================  Admin - Update Tenant  ==========================
def update_tenant_gui():
    update_window = tk.Toplevel()
    update_window.title("Update Tenant")

    tk.Label(update_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(update_window)
    house_no_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(update_window, text="Tenant Name").grid(row=1, column=0, padx=5, pady=5)
    tenant_name_entry = tk.Entry(update_window)
    tenant_name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(update_window, text="Phone Number").grid(row=2, column=0, padx=5, pady=5)
    phone_number_entry = tk.Entry(update_window)
    phone_number_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(update_window, text="Apartment ID").grid(row=3, column=0, padx=5, pady=5)
    apartment_id_entry = tk.Entry(update_window)
    apartment_id_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(update_window, text="Move-in Date (YYYY-MM-DD)").grid(row=4, column=0, padx=5, pady=5)
    move_in_date_entry = tk.Entry(update_window)
    move_in_date_entry.grid(row=4, column=1, padx=5, pady=5)

    def update_tenant_in_db():
        house_no = house_no_entry.get()
        tenant_name = tenant_name_entry.get()
        phone_number = phone_number_entry.get()
        apartment_id = apartment_id_entry.get()
        move_in_date = move_in_date_entry.get()

        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE SYSTEM.Tenant SET tenant_name = :1, phone_number = :2, "
                "apartment_id = :3, move_in_date = TO_DATE(:4, 'YYYY-MM-DD') WHERE house_no = :5",
                (tenant_name, phone_number, apartment_id, move_in_date, house_no)
            )
            connection.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Tenant updated successfully!")
            else:
                messagebox.showwarning("Warning", "No tenant found with that house number.")
            update_window.destroy()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", f"Failed to update tenant: {e}")
            connection.rollback()
        finally:
            cursor.close()

    tk.Button(update_window, text="Update Tenant", command=update_tenant_in_db).grid(row=5, columnspan=2, pady=10)


# =========================  Admin - Delete Tenant  ==========================
def delete_tenant_gui():
    delete_window = tk.Toplevel()
    delete_window.title("Delete Tenant")

    tk.Label(delete_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(delete_window)
    house_no_entry.grid(row=0, column=1, padx=5, pady=5)

    def delete_tenant_from_db():
        house_no = house_no_entry.get()

        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM SYSTEM.Tenant WHERE house_no = :1", (house_no,))
            connection.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Tenant deleted successfully!")
            else:
                messagebox.showwarning("Warning", "No tenant found with that house number.")
            delete_window.destroy()
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", f"Failed to delete tenant: {e}")
            connection.rollback()
        finally:
            cursor.close()

    tk.Button(delete_window, text="Delete Tenant", command=delete_tenant_from_db).grid(row=1, columnspan=2, pady=10)


# =========================  Admin - Display Tenant Details  ==========================
def display_tenant_gui():
    display_window = tk.Toplevel()
    display_window.title("Display Tenant Details")

    tk.Label(display_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(display_window)
    house_no_entry.grid(row=0, column=1, padx=5, pady=5)

    def display_tenant_details():
        house_no = house_no_entry.get()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM SYSTEM.Tenant WHERE house_no = :1", (house_no,))
            tenant = cursor.fetchone()

            if tenant:
                details_window = tk.Toplevel()
                details_window.title("Tenant Details")
                details = f"House No: {tenant[0]}\nTenant Name: {tenant[1]}\nPhone Number: {tenant[2]}\nApartment ID: {tenant[3]}\nMove-in Date: {tenant[4]}"
                tk.Label(details_window, text=details).pack(padx=10, pady=10)
            else:
                messagebox.showwarning("Warning", "No tenant found with that house number.")
        except cx_Oracle.DatabaseError as e:
            messagebox.showerror("Error", f"Failed to fetch tenant details: {e}")
        finally:
            cursor.close()

    tk.Button(display_window, text="Display Tenant", command=display_tenant_details).grid(row=1, columnspan=2, pady=10)


# =========================  Admin - Maintenance Request Management =========================
def provide_service_gui():
    service_window = tk.Toplevel()
    service_window.title("Provide Maintenance Service")

    tk.Label(service_window, text="Apartment ID").grid(row=0, column=0, padx=5, pady=5)
    apartment_id_entry = tk.Entry(service_window)
    apartment_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(service_window, text="House No").grid(row=1, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(service_window)
    house_no_entry.grid(row=1, column=1, padx=5, pady=5)

    def provide():
        apartment_id = apartment_id_entry.get()
        house_no = house_no_entry.get()

        result_message = provide_service(connection, apartment_id, house_no,
                                         lambda msg: messagebox.showerror("Error", msg))
        if result_message:
            messagebox.showinfo("Success", result_message)
            service_window.destroy()

    tk.Button(service_window, text="Provide Service", command=provide).grid(row=2, columnspan=2, pady=10)


def provide_service(connection, apartment_id, house_no, error_callback):
    cursor = connection.cursor()
    try:
        if check_complaint(connection, apartment_id, house_no):
            if incomplete_complaint(connection, apartment_id, house_no):
                issues_fixed = []
                cursor.execute(
                    "SELECT issue_description FROM SYSTEM.Maintenance WHERE apartment_id = :1 AND house_no = :2",
                    (apartment_id, house_no))
                rows = cursor.fetchall()
                for row in rows:
                    issues_fixed.append(row[0])
                if issues_fixed:
                    cursor.execute(
                        "UPDATE SYSTEM.Maintenance "
                        "SET status ='Completed' WHERE apartment_id = :1 AND house_no = :2",
                        (apartment_id, house_no)
                    )
                    cursor.callproc('update_due_amount_proc', [house_no, 100])
                    
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
    finally:
        cursor.close()


# =========================  Admin - Displaying all maintenance requests complaints  ==========================
def display_complaints_gui():
    complaints_window = tk.Toplevel()
    complaints_window.title("Display Complaints")

    complaints_display = scrolledtext.ScrolledText(complaints_window, width=60, height=20, wrap=tk.WORD)
    complaints_display.pack(padx=10, pady=10)

    cursor = connection.cursor()
    try:
        # Execute the query to fetch maintenance complaints along with tenant and apartment details
        cursor.execute("""SELECT m.issue_description, m.request_date, m.status, t.tenant_name, t.phone_number, a.apartment_name, a.address,m.house_no
                        FROM Maintenance m
                        JOIN Tenant t ON m.house_no = t.house_no
                        JOIN Apartment a ON m.apartment_id = a.apartment_id""")
        rows = cursor.fetchall()

        if len(rows) == 0:
            complaints_display.insert(tk.END, "No complaints registered.\n")
        else:
            # Display each complaint with the relevant details
            for row in rows:
                complaints_display.insert(tk.END, f"Apartment Name: {row[5]}\n")
                complaints_display.insert(tk.END, f"House No: {row[7]}\n")
                complaints_display.insert(tk.END, f"Issue Description: {row[0]}\n")
                complaints_display.insert(tk.END, f"Request Date: {row[1]}\n")
                complaints_display.insert(tk.END, f"Status: {row[2]}\n")
                complaints_display.insert(tk.END, f"Tenant Name: {row[3]}\n")
                complaints_display.insert(tk.END, f"Tenant Phone: {row[4]}\n")
                complaints_display.insert(tk.END, f"Apartment Address: {row[6]}\n")
                complaints_display.insert(tk.END, "-" * 30 + "\n")
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Error", f"Error displaying complaints: {e}")
    finally:
        cursor.close()


# =========================  Admin-display_latest_modifications  ==========================
def display_latest_modifications_gui():
    latest_window = tk.Toplevel()
    latest_window.title("Display latest modifications")

    ext_area = tk.Text(latest_window, width=60, height=20)
    ext_area.pack(pady=10)

    infos = display_latest_modifications(connection)
    if not infos:
        ext_area.insert(tk.END, "No modifications done.")
    else:
        for info in infos:
            ext_area.insert(tk.END, f"Audit ID: {info['Audit ID']}\n")
            ext_area.insert(tk.END, f"House No: {info['House No']}\n")
            ext_area.insert(tk.END, f"Tenant Name: {info['Tenant Name']}\n")
            ext_area.insert(tk.END, f"Phone Number: {info['Phone Number']}\n")
            ext_area.insert(tk.END, f"Apartment ID: {info['Apartment ID']}\n")
            ext_area.insert(tk.END, f"Move-In Date: {info['Move-In Date']}\n")
            ext_area.insert(tk.END, f"Action: {info['Action']}\n")
            ext_area.insert(tk.END, f"Change Date: {info['Change Date']}\n")
            ext_area.insert(tk.END, "-" * 40 + "\n")

    # Make the text area read-only
    ext_area.config(state=tk.DISABLED)


def display_latest_modifications(connection):
    cursor = connection.cursor()
    infos = []
    try:
        cursor.execute(
            'SELECT audit_id, house_no, tenant_name, phone_number, apartment_id, move_in_date, action, change_date '
            'FROM Audit_Tenant WHERE change_date = (SELECT MAX(change_date) FROM Audit_Tenant)')
        rows = cursor.fetchall()

        if len(rows) == 0:
            print("No modifcations found.")
        else:
            for row in rows:
                infos.append({
                    "Audit ID": row[0],
                    "House No": row[1],
                    "Tenant Name": row[2],
                    "Phone Number": row[3],
                    "Apartment ID": row[4],
                    "Move-In Date": row[5],
                    "Action": row[6],
                    "Change Date": row[7],
                })
        return infos  # Return the list of apartments
    except cx_Oracle.DatabaseError as e:
        print("Error executing query:", e)
        return []  # Return an empty list in case of error
    finally:
        cursor.close()


# Function to check if there are any complaints registered for the apartment
def check_complaint(connection, apartment_id, house_no):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM SYSTEM.Maintenance WHERE apartment_id = :1 AND house_no = :2",
                       (apartment_id, house_no))
        count = cursor.fetchone()[0]
        return count > 0
    except cx_Oracle.DatabaseError as e:
        print("Error checking complaints:", e)
        return False
    finally:
        cursor.close()


# Function to check if the complaint is incomplete
def incomplete_complaint(connection, apartment_id, house_no):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT status FROM SYSTEM.Maintenance WHERE apartment_id = :1 AND house_no = :2",
                       (apartment_id, house_no))
        status = cursor.fetchone()
        if status and status[0] == 'Pending':
            return True
        return False
    except cx_Oracle.DatabaseError as e:
        print("Error checking complaint status:", e)
        return False
    finally:
        cursor.close()


# =========================  Tenant - View Apartment Details  ==========================
def view_apt_details_gui():
    details_window = tk.Toplevel()
    details_window.title("View Apartment Details")

    tk.Label(details_window, text="Apartment ID").grid(row=0, column=0, padx=5, pady=5)
    apartment_id_entry = tk.Entry(details_window)
    apartment_id_entry.grid(row=0, column=1, padx=5, pady=5)

    def fetch_apartment_details():
        apartment_id = apartment_id_entry.get()
        view_apt_details(connection, apartment_id)

    tk.Button(details_window, text="View Details", command=fetch_apartment_details).grid(row=1, columnspan=2, pady=10)


def view_apt_details(connection, apartment_id):
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT * FROM "SYSTEM"."APARTMENT" WHERE apartment_id = :1', (apartment_id,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            messagebox.showwarning("Warning", "Invalid Apartment ID")
        else:
            details_window = tk.Toplevel()
            details_window.title("Apartment Details")
            for row in rows:
                tk.Label(details_window, text=f"Apartment ID: {row[0]}").pack()
                tk.Label(details_window, text=f"Apartment Name: {row[1]}").pack()
                tk.Label(details_window, text=f"Address: {row[2]}").pack()
                tk.Label(details_window, text=f"Number of Rooms: {row[3]}").pack()
                tk.Label(details_window, text=f"Rent: {row[4]}").pack()
                tk.Label(details_window, text="-" * 40).pack()
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Error", "Error executing query: " + str(e))
    finally:
        cursor.close()


# =========================  Tenant - Make Payment  ==========================
def make_payment_gui():
    payment_window = tk.Toplevel()
    payment_window.title("Make Payment")

    tk.Label(payment_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(payment_window)
    house_no_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(payment_window, text="Payment Date (YYYY-MM-DD)").grid(row=1, column=0, padx=5, pady=5)
    payment_date_entry = tk.Entry(payment_window)
    payment_date_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(payment_window, text="Amount Paid").grid(row=2, column=0, padx=5, pady=5)
    amount_paid_entry = tk.Entry(payment_window)
    amount_paid_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(payment_window, text="Payment Method").grid(row=3, column=0, padx=5, pady=5)
    payment_method_entry = tk.Entry(payment_window)
    payment_method_entry.grid(row=3, column=1, padx=5, pady=5)

    def process_payment():
        house_no = house_no_entry.get()
        payment_date = payment_date_entry.get()
        amount_paid = amount_paid_entry.get()
        payment_method = payment_method_entry.get()

        make_payment(connection, house_no, payment_date, amount_paid, payment_method)

    tk.Button(payment_window, text="Submit Payment", command=process_payment).grid(row=4, columnspan=2, pady=10)


def make_payment(connection, house_no, payment_date, amount_paid, payment_method):
    cursor = connection.cursor()
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
            connection.commit()
            messagebox.showinfo("Success", "Payment recorded successfully!")
        else:
            messagebox.showwarning("Warning", "No tenant found with that house number.")
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Error", "Error recording payment: " + str(e))
        connection.rollback()
    finally:
        cursor.close()


# =========================  Tenant - Submit  Maintenance Complaints  ==========================
def request_maintenance_gui():
    maintenance_window = tk.Toplevel()
    maintenance_window.title("Request Maintenance")

    tk.Label(maintenance_window, text="Apartment ID").grid(row=0, column=0, padx=5, pady=5)
    apartment_id_entry = tk.Entry(maintenance_window)
    apartment_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(maintenance_window, text="House No").grid(row=1, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(maintenance_window)
    house_no_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(maintenance_window, text="Issue Description").grid(row=2, column=0, padx=5, pady=5)
    issue_description_entry = tk.Entry(maintenance_window)
    issue_description_entry.grid(row=2, column=1, padx=5, pady=5)

    def submit_request():
        apartment_id = apartment_id_entry.get()
        house_no = house_no_entry.get()
        issue_description = issue_description_entry.get()

        # Call the request_maintenance function
        request_maintenance(connection, apartment_id, house_no, issue_description)

        # Clear the fields after submission
        apartment_id_entry.delete(0, tk.END)
        house_no_entry.delete(0, tk.END)
        issue_description_entry.delete(0, tk.END)

    tk.Button(maintenance_window, text="Submit Request", command=submit_request).grid(row=3, columnspan=2, pady=10)


def request_maintenance(connection, apartment_id, house_no, issue_description):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM SYSTEM.Tenant WHERE house_no = :1", (house_no,))
        result = cursor.fetchone()

        if result is not None:

            cursor.execute(
                "INSERT INTO SYSTEM.Maintenance(apartment_id, house_no, issue_description, request_date) "
                "VALUES (:1, :2, :3, SYSDATE)",
                (apartment_id, house_no, issue_description)
            )
            connection.commit()
            messagebox.showinfo("Success", "Maintenance request submitted!!")
        # print("")
        else:
            messagebox.showwarning("Warning", "No tenant found with that house number.")
    except cx_Oracle.DatabaseError as e:
        print()
        messagebox.showerror("Error", "Error executing query: " + str(e))
        connection.rollback()
    finally:
        cursor.close()


# =========================  Tenant - View Payment History ==========================
def view_payment_history_gui():
    history_window = tk.Toplevel()
    history_window.title("View Payment History")

    tk.Label(history_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(history_window)
    house_no_entry.grid(row=0, column=1, padx=5, pady=5)

    def fetch_payment_history():
        house_no = house_no_entry.get()
        view_payment_history(connection, house_no)

    tk.Button(history_window, text="View History", command=fetch_payment_history).grid(row=1, columnspan=2, pady=10)


def view_payment_history(connection, house_no):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT payment_id, payment_date, amount_paid, payment_method FROM SYSTEM.Payment WHERE house_no = :1",
            (house_no,))
        rows = cursor.fetchall()
        if rows:
            history_window = tk.Toplevel()
            history_window.title("Payment History")
            for row in rows:
                tk.Label(history_window,
                         text=f"Payment ID: {row[0]}, Date: {row[1]}, Amount: {row[2]}, Method: {row[3]}").pack()
        else:
            messagebox.showinfo("Info", "No payment history found.")
    except cx_Oracle.DatabaseError as e:
        messagebox.showerror("Error", "Error fetching payment history: " + str(e))
    finally:
        cursor.close()


# =========================  Tenant - View Due Amount  ==========================
def view_due_gui():
    due_window = tk.Toplevel()
    due_window.title("View Due Amount")

    tk.Label(due_window, text="House No").grid(row=0, column=0, padx=5, pady=5)
    house_no_entry = tk.Entry(due_window)
    house_no_entry.grid(row=0, column=1, padx=5, pady=5)

    def check_due():
        house_no = house_no_entry.get()

        # Call the view_due function
        due_amount = view_due(connection, house_no)

        # Display the result
        if due_amount is not None:
            tk.messagebox.showinfo("Due Amount", f"The due amount for House No {house_no} is: {due_amount}")
        # else:
        # tk.messagebox.showwarning("No Due Amount", "No due amount found for this house number.")

    tk.Button(due_window, text="Check Due Amount", command=check_due).grid(row=1, columnspan=2, pady=10)


def view_due(connection, house_no):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM SYSTEM.Tenant WHERE house_no = :1", (house_no,))
        result = cursor.fetchone()

        if result is not None:
            cursor.execute("SELECT due_amount FROM Tenant WHERE house_no = :1", (house_no,))
            rows = cursor.fetchall()

            if rows:
                return rows[0][0]  # Return the first row's due_amount
            else:
                return None  # Return None if no due amount is found
        else:
            messagebox.showwarning("Warning", "No tenant found with that house number.")
    except cx_Oracle.DatabaseError as e:
        print("Error fetching due amount:", e)
        connection.rollback()
        return None  # Return None in case of error
    finally:
        cursor.close()


# ===========================================================================
# GUI for Login
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("600x500")

# Load the background image
background_image = Image.open(r'C:\Users\kamal\OneDrive\Desktop\DB project\aptimg.jpg')  # Update this path
background_photo = ImageTk.PhotoImage(background_image)

# Create a label to hold the background image
background_label = tk.Label(login_window, image=background_photo)
background_label.place(relwidth=1, relheight=1)  # Make the label fill the entire window

# Create a frame for the login form
frame = tk.Frame(login_window, bg="linen", bd=5, width=300, height=275)
frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame
frame.pack_propagate(False)

tk.Label(frame, text="Username").pack(pady=(10, 0))
username_entry = tk.Entry(frame)
username_entry.pack(pady=5)

tk.Label(frame, text="Password").pack(pady=(10, 0))
password_entry = tk.Entry(frame, show="*")
password_entry.pack(pady=5)

login_status_label = tk.Label(frame, bg="linen", text="")
login_status_label.pack(pady=(10, 0))

tk.Button(frame, text="Login", command=verify_login).pack(pady=20)

login_window.mainloop()



