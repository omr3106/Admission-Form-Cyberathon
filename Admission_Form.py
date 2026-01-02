from tkinter import messagebox
from tkinter import *
import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys


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
    except Exception as e:
        show_error_message("Database Error", f"Could not upload: {e}")
        return

    name_entry.delete(0, END)
    email_entry.delete(0, END)
    contact_entry.delete(0, END)
    gender_var.set(None)
    stream_var.set(None)

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
    top = Toplevel(root)
    top.title(title)
    top.geometry("500x110")
    Label(top, text=message, font="Bahnschrift 14", bg='white', fg='black').pack(pady=20)
    Button(top, text="OK", command=top.destroy, bg='dark sea green', fg='white', font='Bahnschrift 16', relief='solid').pack()

def view_records():
    display_entries()

def display_entries():
    for widget in display_frame.winfo_children():
        widget.destroy()

    Label(display_frame, text="Admission Details", bg='dark sea green', fg='navy', font='Bahnschrift 24 underline').grid(row=0, column=0, columnspan=3, pady=20)

    try:
        docs = db.collection(COLLECTION_NAME).stream()
        
        for i, doc in enumerate(docs):
            doc_id = doc.id
            data = doc.to_dict()
            
            record_values = [
                data.get("Name", ""),
                data.get("Email", ""),
                data.get("Contact", ""),
                data.get("Gender", ""),
                data.get("Stream", "")
            ]

            for j, val in enumerate(record_values):
                label = Label(display_frame, text=val, bg='dark sea green', fg='black', font='Bahnschrift 16')
                label.grid(row=i + 1, column=j, padx=5, pady=5)

            delete_button = Button(display_frame, text="Delete", 
                                   command=lambda d_id=doc_id: delete_record(d_id), 
                                   bg='red', fg='yellow', font='Bahnschrift 16', relief='solid')
            delete_button.grid(row=i + 1, column=len(record_values), padx=5, pady=5)

            update_button = Button(display_frame, text="Update", 
                                   command=lambda d_id=doc_id, vals=record_values: update_record(d_id, vals), 
                                   bg='lime green', fg='Dark blue', font='Bahnschrift 16', relief='solid')
            update_button.grid(row=i + 1, column=len(record_values) + 1, padx=5, pady=5)
            
    except Exception as e:
        show_error_message("Connection Error", f"Could not fetch data: {e}")

def delete_record(doc_id):
    try:
        db.collection(COLLECTION_NAME).document(doc_id).delete()
        display_entries() 
    except Exception as e:
        show_error_message("Error", f"Could not delete: {e}")

def update_record(doc_id, current_values):
    for widget in display_frame.winfo_children():
        widget.destroy()

    updated_name_var.set(current_values[0])
    updated_email_var.set(current_values[1])
    updated_contact_var.set(current_values[2])
    updated_gender_var.set(current_values[3])
    updated_stream_var.set(current_values[4])

    Label(display_frame, text="Updated Name:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=6, column=0, pady=5)
    Entry(display_frame, textvariable=updated_name_var, font='Bahnschrift 16').grid(row=6, column=1, pady=5)

    Label(display_frame, text="Updated Email:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=7, column=0, pady=5)
    Entry(display_frame, textvariable=updated_email_var, font='Bahnschrift 16').grid(row=7, column=1, pady=5)

    Label(display_frame, text="Updated Contact:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=8, column=0, pady=5)
    Entry(display_frame, textvariable=updated_contact_var, font='Bahnschrift 16').grid(row=8, column=1, pady=5)

    Label(display_frame, text="Updated Gender:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=9, column=0, pady=5)
    Radiobutton(display_frame, text="Male", variable=updated_gender_var, value="Male", bg='dark sea green', fg='black',
                font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=9, column=1, pady=5)
    Radiobutton(display_frame, text="Female", variable=updated_gender_var, value="Female", bg='dark sea green', fg='black',
                font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=9, column=2, pady=5)

    Label(display_frame, text="Updated Stream:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=10, column=0, pady=5)
    Radiobutton(display_frame, text="Science", variable=updated_stream_var, value="Science", bg='dark sea green', fg='black',
                font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=10, column=1, pady=5)
    Radiobutton(display_frame, text="Arts", variable=updated_stream_var, value="Arts", bg='dark sea green', fg='black',
                font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=10, column=2, pady=5)
    Radiobutton(display_frame, text="Commerce", variable=updated_stream_var, value="Commerce", bg='dark sea green', fg='black',
                font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=10, column=3, pady=5)

    update_button = Button(display_frame, text="Submit Update", command=lambda: submit_update(doc_id), bg='lime green', fg='black',
                           font='Bahnschrift 16', relief='solid')
    update_button.grid(row=11, columnspan=3, pady=10)

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
        display_entries()
    except Exception as e:
        show_error_message("Update Error", f"Could not update: {e}")

root = Tk()
root.title("Registration Form")
root.config(bg='dark sea green')
root.geometry('1500x1000')

main_frame = Frame(root, bg='dark sea green')
main_frame.place(relwidth=0.5, relheight=1)

Label(main_frame, text="Admission Form", bg='dark sea green', fg='navy', font='Bahnschrift 36 underline').grid(row=0, column=0, columnspan=3, pady=20)

Label(main_frame, text="Name:", bg='dark sea green', fg='black', font='Bahnschrift 16 ').grid(row=1, column=0, pady=5)
name_entry = Entry(main_frame, relief='sunken', font='Bahnschrift 16', bg='mint cream')
name_entry.grid(row=1, column=1, pady=5)

Label(main_frame, text="Email:", bg='dark sea green', fg='black', font='Bahnschrift 16 ').grid(row=2, column=0, pady=5)
email_entry = Entry(main_frame, font='Bahnschrift 16', bg='mint cream')
email_entry.grid(row=2, column=1, pady=5)

Label(main_frame, text="Contact:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=3, column=0, pady=5)
contact_entry = Entry(main_frame, font='Bahnschrift 16', bg='mint cream')
contact_entry.grid(row=3, column=1, pady=5)

Label(main_frame, text="Gender:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=4, column=0, pady=5)
gender_var = StringVar()
gender_var.set(None)
Radiobutton(main_frame, text="Male", variable=gender_var, value="Male", bg='dark sea green', fg='black',
            font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=4, column=1, pady=5)
Radiobutton(main_frame, text="Female", variable=gender_var, value="Female", bg='dark sea green', fg='black',
            font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=4, column=2, pady=5)

Label(main_frame, text="Stream:", bg='dark sea green', fg='black', font='Bahnschrift 16').grid(row=5, column=0, pady=5)
stream_var = StringVar()
stream_var.set(None)
Radiobutton(main_frame, text="Science", variable=stream_var, value="Science", bg='dark sea green', fg='black',
            font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=5, column=1, pady=5)
Radiobutton(main_frame, text="Arts", variable=stream_var, value="Arts", bg='dark sea green', fg='black',
            font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=5, column=2, pady=5)
Radiobutton(main_frame, text="Commerce", variable=stream_var, value="Commerce", bg='dark sea green', fg='black',
            font='Bahnschrift 16', activebackground='dark sea green', activeforeground='black').grid(row=5, column=3, pady=5)

submit_button = Button(main_frame, text="Submit", command=submit, bg='lime green', fg='black', font='Bahnschrift 16',
                       activebackground='dark sea green', activeforeground='white', relief='solid')
submit_button.grid(row=6, columnspan=3, pady=10)

view_button = Button(main_frame, text="View Records", command=view_records, bg='dark slate gray3', fg='dark slate gray', font='Bahnschrift 16',
                     activebackground='dark sea green', activeforeground='white', relief='solid')
view_button.grid(row=7, columnspan=3)

display_frame = Frame(root, bg='dark sea green')
display_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

updated_name_var = StringVar()
updated_email_var = StringVar()
updated_contact_var = StringVar()
updated_gender_var = StringVar()
updated_stream_var = StringVar()

updated_name_entry = Entry(display_frame, textvariable=updated_name_var, font='Bahnschrift 16')
updated_email_entry = Entry(display_frame, textvariable=updated_email_var, font='Bahnschrift 16')
updated_contact_entry = Entry(display_frame, textvariable=updated_contact_var, font='Bahnschrift 16')

root.mainloop()