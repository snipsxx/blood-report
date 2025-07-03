import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

class PatientRegistrationForm:
    def __init__(self, parent, database, status_callback):
        self.parent = parent
        self.db = database
        self.status_callback = status_callback
        self.setup_form()
    
    def setup_form(self):
        """Setup patient registration form"""
        self.parent.columnconfigure(1, weight=1)
        
        row = 0
        
        # First Name
        ttk.Label(self.parent, text="First Name*:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.first_name_var = tk.StringVar()
        ttk.Entry(self.parent, textvariable=self.first_name_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        row += 1
        
        # Last Name
        ttk.Label(self.parent, text="Last Name*:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.last_name_var = tk.StringVar()
        ttk.Entry(self.parent, textvariable=self.last_name_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        row += 1
        
        # Phone Number
        ttk.Label(self.parent, text="Phone Number*:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(self.parent, textvariable=self.phone_var, width=30)
        phone_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        phone_entry.bind('<KeyRelease>', self.validate_phone)
        row += 1
        
        # Email
        ttk.Label(self.parent, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(self.parent, textvariable=self.email_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        row += 1
        
        # Date of Birth
        ttk.Label(self.parent, text="Date of Birth:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.dob_var = tk.StringVar()
        ttk.Entry(self.parent, textvariable=self.dob_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(self.parent, text="(YYYY-MM-DD)", font=('Arial', 8)).grid(
            row=row+1, column=1, sticky=tk.W, padx=(5, 0))
        row += 2
        
        # Gender
        ttk.Label(self.parent, text="Gender:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(
            self.parent, textvariable=self.gender_var, 
            values=["Male", "Female", "Other"], state="readonly", width=27)
        gender_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        row += 1
        
        # Address
        ttk.Label(self.parent, text="Address:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.address_var = tk.StringVar()
        ttk.Entry(self.parent, textvariable=self.address_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        row += 1
        
        # Emergency Contact
        ttk.Label(self.parent, text="Emergency Contact:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.emergency_contact_var = tk.StringVar()
        ttk.Entry(self.parent, textvariable=self.emergency_contact_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        row += 1
        
        # Emergency Phone
        ttk.Label(self.parent, text="Emergency Phone:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.emergency_phone_var = tk.StringVar()
        ttk.Entry(self.parent, textvariable=self.emergency_phone_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Register Patient", command=self.register_patient).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT)
    
    def validate_phone(self, event=None):
        """Validate phone number format"""
        phone = self.phone_var.get()
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) > 10:
            self.phone_var.set(phone[:-1])
    
    def validate_form(self):
        """Validate form data"""
        errors = []
        if not self.first_name_var.get().strip():
            errors.append("First name is required")
        if not self.last_name_var.get().strip():
            errors.append("Last name is required")
        
        phone = self.phone_var.get().strip()
        if not phone:
            errors.append("Phone number is required")
        elif len(re.sub(r'\D', '', phone)) < 10:
            errors.append("Phone number must be at least 10 digits")
        
        email = self.email_var.get().strip()
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append("Invalid email format")
        
        dob = self.dob_var.get().strip()
        if dob:
            try:
                datetime.strptime(dob, '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD")
        
        return errors
    
    def register_patient(self):
        """Register a new patient"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        patient_data = {
            'first_name': self.first_name_var.get().strip(),
            'last_name': self.last_name_var.get().strip(),
            'phone_number': self.phone_var.get().strip(),
            'email': self.email_var.get().strip(),
            'date_of_birth': self.dob_var.get().strip() or None,
            'gender': self.gender_var.get(),
            'address': self.address_var.get().strip(),
            'emergency_contact': self.emergency_contact_var.get().strip(),
            'emergency_phone': self.emergency_phone_var.get().strip()
        }
        
        try:
            patient_id = self.db.add_patient(patient_data)
            messagebox.showinfo("Success", f"Patient registered successfully!\nPatient ID: {patient_id}")
            self.status_callback(f"Patient {patient_data['first_name']} {patient_data['last_name']} registered")
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Registration Error", str(e))
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to register patient: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.dob_var.set("")
        self.gender_var.set("")
        self.address_var.set("")
        self.emergency_contact_var.set("")
        self.emergency_phone_var.set("")


class PatientSearchForm:
    def __init__(self, search_parent, list_parent, database, status_callback):
        self.search_parent = search_parent
        self.list_parent = list_parent
        self.db = database
        self.status_callback = status_callback
        self.setup_search_form()
        self.setup_patient_list()
        self.load_all_patients()
    
    def setup_search_form(self):
        """Setup patient search form"""
        ttk.Label(self.search_parent, text="Search:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self.search_parent, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        self.search_parent.columnconfigure(1, weight=1)
        
        ttk.Button(self.search_parent, text="Search", command=self.search_patients).grid(row=1, column=0, pady=5)
        ttk.Button(self.search_parent, text="Show All", command=self.load_all_patients).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
    
    def setup_patient_list(self):
        """Setup patient list with treeview"""
        self.list_parent.columnconfigure(0, weight=1)
        self.list_parent.rowconfigure(0, weight=1)
        
        tree_frame = ttk.Frame(self.list_parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ('ID', 'Name', 'Phone', 'Email', 'Gender', 'Address')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Phone', text='Phone')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Gender', text='Gender')
        self.tree.heading('Address', text='Address')
        
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Name', width=200, minwidth=150)
        self.tree.column('Phone', width=120, minwidth=100)
        self.tree.column('Email', width=180, minwidth=120)
        self.tree.column('Gender', width=80, minwidth=60)
        self.tree.column('Address', width=200, minwidth=150)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.tree.bind('<Double-1>', self.on_patient_select)
    
    def on_search_change(self, event=None):
        """Handle search as user types"""
        search_term = self.search_var.get()
        if len(search_term) >= 2 or search_term == "":
            self.search_patients()
    
    def search_patients(self):
        """Search patients based on search term"""
        search_term = self.search_var.get().strip()
        try:
            patients = self.db.search_patients(search_term)
            self.populate_patient_list(patients)
            
            if search_term:
                self.status_callback(f"Found {len(patients)} patients matching '{search_term}'")
            else:
                self.status_callback(f"Showing all {len(patients)} patients")
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search patients: {e}")
    
    def load_all_patients(self):
        """Load all patients"""
        self.search_var.set("")
        self.search_patients()
    
    def populate_patient_list(self, patients):
        """Populate the patient list treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for patient in patients:
            full_name = f"{patient['first_name']} {patient['last_name']}"
            values = (
                patient['patient_id'],
                full_name,
                patient['phone_number'],
                patient.get('email', ''),
                patient.get('gender', ''),
                patient.get('address', '')
            )
            self.tree.insert('', tk.END, values=values, tags=(patient['patient_id'],))
    
    def on_patient_select(self, event):
        """Handle patient selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            patient_id = item['values'][0]
            patient_name = item['values'][1]
            messagebox.showinfo("Patient Selected", f"Selected: {patient_name}\nID: {patient_id}\n\n(Detail view coming in next phase)") 