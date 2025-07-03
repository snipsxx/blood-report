import tkinter as tk
from tkinter import ttk, messagebox
from .patient_forms_2 import PatientRegistrationForm, PatientSearchForm
from .test_management import TestTypeManagement
from .blood_reports import BloodReportsManagement
from .billing import BillingManagement
from .analytics_dashboard import AnalyticsDashboard

class MainWindow:
    def __init__(self, root, database):
        self.root = root
        self.db = database
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')  # Modern looking theme
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Laboratory Billing System", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Initialize status bar variable first (needed by tabs)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_patient_tab()
        self.create_test_management_tab()
        self.create_reports_tab()
        self.create_billing_tab()
        self.create_analytics_tab()
        
        # Status bar
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_patient_tab(self):
        """Create patient management tab"""
        patient_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(patient_frame, text="Patient Management")
        
        # Configure grid
        patient_frame.columnconfigure(0, weight=1)
        patient_frame.columnconfigure(1, weight=1)
        patient_frame.rowconfigure(1, weight=1)
        
        # Patient Registration Section
        reg_frame = ttk.LabelFrame(patient_frame, text="Patient Registration", padding="10")
        reg_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 5), pady=(0, 10))
        
        self.patient_registration = PatientRegistrationForm(reg_frame, self.db, self.update_status)
        
        # Patient Search Section
        search_frame = ttk.LabelFrame(patient_frame, text="Patient Search", padding="10")
        search_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=(5, 0), pady=(0, 10))
        
        # Patient List Section (spans both columns)
        list_frame = ttk.LabelFrame(patient_frame, text="Patient List", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        self.patient_search = PatientSearchForm(search_frame, list_frame, self.db, self.update_status)
    
    def create_test_management_tab(self):
        """Create test management tab"""
        test_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(test_frame, text="Test Management")
        
        self.test_management = TestTypeManagement(test_frame, self.db, self.update_status)
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(reports_frame, text="Blood Reports")
        
        self.blood_reports = BloodReportsManagement(reports_frame, self.db, self.update_status)
    
    def create_billing_tab(self):
        """Create billing tab"""
        billing_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(billing_frame, text="Billing")
        
        self.billing = BillingManagement(billing_frame, self.db, self.update_status)
    
    def create_analytics_tab(self):
        """Create analytics dashboard tab"""
        analytics_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(analytics_frame, text="Analytics")
        
        self.analytics = AnalyticsDashboard(analytics_frame, self.db)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.after(3000, lambda: self.status_var.set("Ready"))  # Clear after 3 seconds 