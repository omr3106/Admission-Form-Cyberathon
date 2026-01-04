from tkinter import messagebox
from tkinter import *
from tkinter import ttk  # Import ttk for better styling capabilities
import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

# --- Configuration & Colors ---
APP_TITLE = "Student Admission System"
COLOR_BG = "#ecf0f1"          # Light Grey Background
COLOR_SIDEBAR = "#ffffff"     # White Sidebar
COLOR_PRIMARY = "#2980b9"     # Blue
COLOR_SUCCESS = "#27ae60"     # Green
COLOR_DANGER = "#c0392b"      # Red
COLOR_TEXT = "#2c3e50"        # Dark Blue/Grey
FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11)

# --- Firebase Setup (Kept Exact) ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if not firebase_admin._apps:
    key_path = resource_path("serviceAccountKey.json")
    try:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Could not find key at:\n{key_path}\n\nError: {e}")
        sys.exit()

db = firestore.client()
COLLECTION_NAME = "admissions"

# --- Logic Functions ---

def check_mail(email):
    if ("@" not in email) or ("." not in email):
        return False
    splitt = email.split(".")[-1]
    if splitt in ["com", 'in']:
        return True
    return False

def check_number(contact):
    if contact.startswith("+91") and contact[3:].isdigit() and len(contact) == 13:
        return True
    return False

def show_error_message(title, message):
    messagebox.showerror(title, message)

def submit():
    name = name_entry.get()
    email = email_entry.get()
    contact = contact_entry.get()
    gender = gender_var.get()
    stream = stream_var.get()

    if not check_mail(email):
        show_error_message("Error", "Please enter a valid email address ending with .com or .in")
        return
    if not check_number(contact):
        show_error_message("Error", "Please enter a valid phone number starting with +91")
        return

    if not name or not email or not contact or not gender or not stream:
        show_error_message("Error", "All fields are required!")
        return

    data = {
        "Name": name,
        "Email": email,
        "Contact": contact,
        "Gender": gender,
        "Stream": stream
    }
    
    try:
        db.collection(COLLECTION_NAME).add(data)
        messagebox.showinfo("Success", "Student Registered Successfully!")
    except Exception as e:
        show_error_message("Database Error", f"Could not upload: {e}")
        return

    # Clear fields
    name_entry.delete(0, END)
    email_entry.delete(0, END)
    contact_entry.delete(0, END)
    gender_var.set(None)
    stream_var.set(None)
    
    # Auto refresh list if visible
    view_records()

def view_records():
    display_entries()

def display_entries():
    # Clear current view
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Header
    Label(display_frame, text="Current Student Records", bg=COLOR_BG, fg=COLOR_TEXT, font=FONT_SUBHEADER).pack(pady=(0, 20), anchor="w")

    # Scrollable container (Simple Frame for now, can be upgraded to Canvas)
    list_container = Frame(display_frame, bg=COLOR_BG)
    list_container.pack(fill="both", expand=True)

    try:
        docs = db.collection(COLLECTION_NAME).stream()
        
        # Headers
        headers = ["Name", "Email", "Contact", "Gender", "Stream", "Actions"]
        header_row = Frame(list_container, bg="#bdc3c7")
        header_row.pack(fill="x", pady=2)
        for val in headers:
            Label(header_row, text=val, bg="#bdc3c7", fg=COLOR_TEXT, font=("Segoe UI", 10, "bold"), width=15).pack(side="left", padx=2)

        for doc in docs:
            doc_id = doc.id
            data = doc.to_dict()
            
            # Create a "Row" Frame
            row_frame = Frame(list_container, bg="white", pady=5)
            row_frame.pack(fill="x", pady=2)

            record_values = [
                data.get("Name", ""),
                data.get("Email", ""),
                data.get("Contact", ""),
                data.get("Gender", ""),
                data.get("Stream", "")
            ]

            # Data Columns
            for val in record_values:
                Label(row_frame, text=val, bg="white", fg=COLOR_TEXT, font=("Segoe UI", 10), width=15, anchor="center").pack(side="left", padx=2)

            # Action Buttons Container
            action_frame = Frame(row_frame, bg="white", width=200)
            action_frame.pack(side="left", padx=10)

            Button(action_frame, text="Edit", 
                   command=lambda d_id=doc_id, vals=record_values: update_record_ui(d_id, vals), 
                   bg=COLOR_PRIMARY, fg='white', font=("Segoe UI", 8), relief='flat', cursor="hand2", width=6).pack(side="left", padx=2)

            Button(action_frame, text="Del", 
                   command=lambda d_id=doc_id: delete_record(d_id), 
                   bg=COLOR_DANGER, fg='white', font=("Segoe UI", 8), relief='flat', cursor="hand2", width=6).pack(side="left", padx=2)
            
    except Exception as e:
        show_error_message("Connection Error", f"Could not fetch data: {e}")

def delete_record(doc_id):
    if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
        try:
            db.collection(COLLECTION_NAME).document(doc_id).delete()
            display_entries() 
        except Exception as e:
            show_error_message("Error", f"Could not delete: {e}")

def update_record_ui(doc_id, current_values):
    """ Switch the display frame to 'Edit Mode' """
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Populate variables
    updated_name_var.set(current_values[0])
    updated_email_var.set(current_values[1])
    updated_contact_var.set(current_values[2])
    updated_gender_var.set(current_values[3])
    updated_stream_var.set(current_values[4])

    # Edit Form UI
    Label(display_frame, text="Edit Student Record", bg=COLOR_BG, fg=COLOR_PRIMARY, font=FONT_HEADER).pack(pady=20)

    edit_form = Frame(display_frame, bg="white", padx=20, pady=20, relief="flat")
    edit_form.pack(pady=10)

    # Helper for grid entries
    def create_edit_row(lbl, var, r):
        Label(edit_form, text=lbl, bg="white", fg=COLOR_TEXT, font=FONT_BODY).grid(row=r, column=0, sticky="w", pady=10)
        Entry(edit_form, textvariable=var, font=FONT_BODY, bg="#f8f9fa", width=30).grid(row=r, column=1, pady=10, padx=10)

    create_edit_row("Name:", updated_name_var, 0)
    create_edit_row("Email:", updated_email_var, 1)
    create_edit_row("Contact:", updated_contact_var, 2)

    # Gender Edit
    Label(edit_form, text="Gender:", bg="white", font=FONT_BODY).grid(row=3, column=0, sticky="w", pady=10)
    g_frame = Frame(edit_form, bg="white")
    g_frame.grid(row=3, column=1, sticky="w", padx=10)
    Radiobutton(g_frame, text="Male", variable=updated_gender_var, value="Male", bg="white").pack(side="left")
    Radiobutton(g_frame, text="Female", variable=updated_gender_var, value="Female", bg="white").pack(side="left")

    # Stream Edit
    Label(edit_form, text="Stream:", bg="white", font=FONT_BODY).grid(row=4, column=0, sticky="w", pady=10)
    s_frame = Frame(edit_form, bg="white")
    s_frame.grid(row=4, column=1, sticky="w", padx=10)
    for s in ["Science", "Arts", "Commerce"]:
        Radiobutton(s_frame, text=s, variable=updated_stream_var, value=s, bg="white").pack(side="left")

    # Buttons
    btn_box = Frame(edit_form, bg="white")
    btn_box.grid(row=5, column=0, columnspan=2, pady=20)
    
    Button(btn_box, text="Save Changes", command=lambda: submit_update(doc_id), 
           bg=COLOR_SUCCESS, fg='white', font=FONT_BODY, relief='flat', padx=20, pady=5).pack(side="left", padx=10)
    
    Button(btn_box, text="Cancel", command=view_records, 
           bg="#95a5a6", fg='white', font=FONT_BODY, relief='flat', padx=20, pady=5).pack(side="left", padx=10)

def submit_update(doc_id):
    updated_data = {
        "Name": updated_name_var.get(),
        "Email": updated_email_var.get(),
        "Contact": updated_contact_var.get(),
        "Gender": updated_gender_var.get(),
        "Stream": updated_stream_var.get()
    }

    try:
        db.collection(COLLECTION_NAME).document(doc_id).update(updated_data)
        messagebox.showinfo("Success", "Record Updated!")
        display_entries()
    except Exception as e:
        show_error_message("Update Error", f"Could not update: {e}")

# --- Main UI Setup ---

root = Tk()
root.title("Student Admission Portal")
root.config(bg=COLOR_BG)
root.geometry('1200x700')

# -- Left Panel (Form) --
main_frame = Frame(root, bg=COLOR_SIDEBAR, padx=30, pady=30)
main_frame.place(relx=0, rely=0, relwidth=0.35, relheight=1)

# Header
Label(main_frame, text="Admission Form", bg=COLOR_SIDEBAR, fg=COLOR_PRIMARY, font=FONT_HEADER).pack(anchor="w", pady=(0, 20))

# Helper to create styled inputs
def create_input(label_text, row_idx):
    Label(main_frame, text=label_text, bg=COLOR_SIDEBAR, fg=COLOR_TEXT, font=FONT_BODY).pack(anchor="w", pady=(10, 5))
    ent = Entry(main_frame, relief='flat', font=FONT_BODY, bg=COLOR_BG, highlightbackground="#bdc3c7", highlightthickness=1)
    ent.pack(fill="x", ipady=5)
    return ent

# Inputs
name_entry = create_input("Full Name", 1)
email_entry = create_input("Email Address", 2)
contact_entry = create_input("Contact Number (+91)", 3)

# Gender
Label(main_frame, text="Gender", bg=COLOR_SIDEBAR, fg=COLOR_TEXT, font=FONT_BODY).pack(anchor="w", pady=(15, 5))
gender_var = StringVar()
gf = Frame(main_frame, bg=COLOR_SIDEBAR)
gf.pack(fill="x")
Radiobutton(gf, text="Male", variable=gender_var, value="Male", bg=COLOR_SIDEBAR, font=FONT_BODY).pack(side="left", padx=(0, 10))
Radiobutton(gf, text="Female", variable=gender_var, value="Female", bg=COLOR_SIDEBAR, font=FONT_BODY).pack(side="left")

# Stream
Label(main_frame, text="Stream", bg=COLOR_SIDEBAR, fg=COLOR_TEXT, font=FONT_BODY).pack(anchor="w", pady=(15, 5))
stream_var = StringVar()
sf = Frame(main_frame, bg=COLOR_SIDEBAR)
sf.pack(fill="x")
Radiobutton(sf, text="Sci", variable=stream_var, value="Science", bg=COLOR_SIDEBAR, font=FONT_BODY).pack(side="left", padx=(0, 10))
Radiobutton(sf, text="Arts", variable=stream_var, value="Arts", bg=COLOR_SIDEBAR, font=FONT_BODY).pack(side="left", padx=(0, 10))
Radiobutton(sf, text="Comm", variable=stream_var, value="Commerce", bg=COLOR_SIDEBAR, font=FONT_BODY).pack(side="left")

# Submit Button
Button(main_frame, text="Submit Registration", command=submit, 
       bg=COLOR_PRIMARY, fg='white', font=("Segoe UI", 12, "bold"), 
       activebackground="#3498db", activeforeground='white', relief='flat', cursor="hand2").pack(fill="x", pady=30, ipady=5)

# View Button
Button(main_frame, text="View All Records", command=view_records, 
       bg=COLOR_BG, fg=COLOR_TEXT, font=("Segoe UI", 11), 
       relief='flat', cursor="hand2").pack(fill="x", ipady=2)


# -- Right Panel (Display/Edit) --
display_frame = Frame(root, bg=COLOR_BG, padx=20, pady=20)
display_frame.place(relx=0.35, rely=0, relwidth=0.65, relheight=1)

# Variables for the Update Logic
updated_name_var = StringVar()
updated_email_var = StringVar()
updated_contact_var = StringVar()
updated_gender_var = StringVar()
updated_stream_var = StringVar()

# Initialize view
Label(display_frame, text="Select 'View All Records' to load data.", bg=COLOR_BG, fg="#95a5a6", font=FONT_BODY).pack(pady=50)

root.mainloop()