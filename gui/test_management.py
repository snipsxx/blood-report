import tkinter as tk
from tkinter import ttk, messagebox

class TestTypeManagement:
    def __init__(self, parent, database, status_callback):
        self.parent = parent
        self.db = database
        self.status_callback = status_callback
        self.setup_ui()
        self.load_test_types()
    
    def setup_ui(self):
        """Setup test management interface"""
        # Configure grid
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=2)
        self.parent.rowconfigure(0, weight=1)
        
        # Add new test type section
        add_frame = ttk.LabelFrame(self.parent, text="Add New Test Type", padding="10")
        add_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        self.setup_add_form(add_frame)
        
        # Test types list section
        list_frame = ttk.LabelFrame(self.parent, text="Available Test Types", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_test_list(list_frame)
    
    def setup_add_form(self, parent):
        """Setup form to add new test types"""
        parent.columnconfigure(1, weight=1)
        
        row = 0
        
        # Test Name
        ttk.Label(parent, text="Test Name*:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.test_name_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.test_name_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0)
        )
        row += 1
        
        # Test Code
        ttk.Label(parent, text="Test Code*:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.test_code_var = tk.StringVar()
        code_entry = ttk.Entry(parent, textvariable=self.test_code_var, width=30)
        code_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        code_entry.bind('<KeyRelease>', self.format_test_code)
        row += 1
        
        # Price
        ttk.Label(parent, text="Price (₹)*:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.StringVar()
        price_entry = ttk.Entry(parent, textvariable=self.price_var, width=30)
        price_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        price_entry.bind('<KeyRelease>', self.validate_price)
        row += 1
        
        # Normal Range
        ttk.Label(parent, text="Normal Range:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.normal_range_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.normal_range_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0)
        )
        row += 1
        
        # Unit
        ttk.Label(parent, text="Unit:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(
            parent, 
            textvariable=self.unit_var,
            values=["mg/dL", "g/dL", "μL", "10³/μL", "mmol/L", "IU/L", "ng/mL", "pg/mL", "%"],
            width=27
        )
        unit_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        # Description
        ttk.Label(parent, text="Description:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.description_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0)
        )
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=15)
        
        ttk.Button(
            button_frame, 
            text="Add Test Type", 
            command=self.add_test_type
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Clear Form", 
            command=self.clear_form
        ).pack(side=tk.LEFT)
    
    def setup_test_list(self, parent):
        """Setup test types list display"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create treeview
        columns = ('Code', 'Name', 'Price', 'Range', 'Unit')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Define headings
        self.tree.heading('Code', text='Code')
        self.tree.heading('Name', text='Test Name')
        self.tree.heading('Price', text='Price (₹)')
        self.tree.heading('Range', text='Normal Range')
        self.tree.heading('Unit', text='Unit')
        
        # Define column widths
        self.tree.column('Code', width=80, minwidth=60)
        self.tree.column('Name', width=200, minwidth=150)
        self.tree.column('Price', width=100, minwidth=80)
        self.tree.column('Range', width=150, minwidth=100)
        self.tree.column('Unit', width=80, minwidth=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Refresh button
        ttk.Button(
            parent, 
            text="Refresh List", 
            command=self.load_test_types
        ).grid(row=1, column=0, pady=10)
    
    def format_test_code(self, event=None):
        """Format test code to uppercase"""
        code = self.test_code_var.get().upper()
        self.test_code_var.set(code)
    
    def validate_price(self, event=None):
        """Validate price input to allow only numbers and decimal point"""
        price = self.price_var.get()
        # Remove invalid characters
        valid_chars = '0123456789.'
        filtered_price = ''.join(c for c in price if c in valid_chars)
        
        # Ensure only one decimal point
        if filtered_price.count('.') > 1:
            parts = filtered_price.split('.')
            filtered_price = parts[0] + '.' + ''.join(parts[1:])
        
        if filtered_price != price:
            self.price_var.set(filtered_price)
    
    def validate_form(self):
        """Validate the add test form"""
        errors = []
        
        # Required fields
        if not self.test_name_var.get().strip():
            errors.append("Test name is required")
        
        if not self.test_code_var.get().strip():
            errors.append("Test code is required")
        
        price_str = self.price_var.get().strip()
        if not price_str:
            errors.append("Price is required")
        else:
            try:
                price = float(price_str)
                if price <= 0:
                    errors.append("Price must be greater than 0")
            except ValueError:
                errors.append("Invalid price format")
        
        return errors
    
    def add_test_type(self):
        """Add a new test type"""
        # Validate form
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        # Prepare test data
        test_data = {
            'test_name': self.test_name_var.get().strip(),
            'test_code': self.test_code_var.get().strip().upper(),
            'price': float(self.price_var.get().strip()),
            'normal_range': self.normal_range_var.get().strip(),
            'unit': self.unit_var.get().strip(),
            'description': self.description_var.get().strip()
        }
        
        try:
            test_type_id = self.db.add_test_type(test_data)
            messagebox.showinfo(
                "Success", 
                f"Test type '{test_data['test_name']}' added successfully!\nTest ID: {test_type_id}"
            )
            self.status_callback(f"Test type '{test_data['test_name']}' added")
            self.clear_form()
            self.load_test_types()  # Refresh the list
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Error", "Test code already exists. Please use a different code.")
            else:
                messagebox.showerror("Database Error", f"Failed to add test type: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.test_name_var.set("")
        self.test_code_var.set("")
        self.price_var.set("")
        self.normal_range_var.set("")
        self.unit_var.set("")
        self.description_var.set("")
    
    def load_test_types(self):
        """Load and display all test types"""
        try:
            test_types = self.db.get_all_test_types()
            self.populate_test_list(test_types)
            self.status_callback(f"Loaded {len(test_types)} test types")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load test types: {e}")
    
    def populate_test_list(self, test_types):
        """Populate the test types list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add test types
        for test_type in test_types:
            values = (
                test_type['test_code'],
                test_type['test_name'],
                f"₹{test_type['price']:.2f}",
                test_type.get('normal_range', ''),
                test_type.get('unit', '')
            )
            self.tree.insert('', tk.END, values=values) 