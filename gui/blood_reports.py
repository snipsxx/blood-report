import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from utils.pdf_generator import PDFGenerator, create_pdf_directory, generate_filename
from typing import Dict, List, Any

class BloodReportsManagement:
    def __init__(self, parent, database, status_callback):
        self.parent = parent
        self.db = database
        self.status_callback = status_callback
        self.current_report_id = None
        self.selected_tests = {}  # test_type_id -> test_data
        self.setup_ui()
        self.load_patients()
        self.load_test_types()
        self.load_reports()
    
    def setup_ui(self):
        """Setup blood reports management interface"""
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_new_report_tab()
        self.create_reports_list_tab()
    
    def create_new_report_tab(self):
        """Create new report creation tab"""
        new_report_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(new_report_frame, text="Create New Report")
        
        new_report_frame.columnconfigure(0, weight=1)
        new_report_frame.columnconfigure(1, weight=1)
        new_report_frame.rowconfigure(2, weight=1)
        
        # Report Details Section
        details_frame = ttk.LabelFrame(new_report_frame, text="Report Details", padding="10")
        details_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.setup_report_details(details_frame)
        
        # Test Selection Section
        tests_frame = ttk.LabelFrame(new_report_frame, text="Select Tests", padding="10")
        tests_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5), pady=(0, 10))
        self.setup_test_selection(tests_frame)
        
        # Selected Tests Section
        selected_frame = ttk.LabelFrame(new_report_frame, text="Selected Tests", padding="10")
        selected_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=(0, 10))
        self.setup_selected_tests(selected_frame)
        
        # Test Results Section
        results_frame = ttk.LabelFrame(new_report_frame, text="Enter Test Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.setup_test_results(results_frame)
    
    def setup_report_details(self, parent):
        """Setup report details form"""
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)
        
        # Patient Selection
        ttk.Label(parent, text="Patient*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(parent, textvariable=self.patient_var, state="readonly", width=30)
        self.patient_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 10))
        
        # Test Date
        ttk.Label(parent, text="Test Date*:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.test_date_var = tk.StringVar()
        self.test_date_var.set(date.today().strftime('%Y-%m-%d'))
        ttk.Entry(parent, textvariable=self.test_date_var, width=20).grid(
            row=0, column=3, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Doctor Name
        ttk.Label(parent, text="Doctor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.doctor_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.doctor_var, width=30).grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 10))
        
        # Lab Technician
        ttk.Label(parent, text="Lab Technician:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.technician_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.technician_var, width=20).grid(
            row=1, column=3, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
    
    def setup_test_selection(self, parent):
        """Setup test selection interface"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Available tests list
        columns = ('Code', 'Name', 'Price')
        self.available_tests_tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)
        
        self.available_tests_tree.heading('Code', text='Code')
        self.available_tests_tree.heading('Name', text='Test Name')
        self.available_tests_tree.heading('Price', text='Price (₹)')
        
        self.available_tests_tree.column('Code', width=80, minwidth=60)
        self.available_tests_tree.column('Name', width=200, minwidth=150)
        self.available_tests_tree.column('Price', width=100, minwidth=80)
        
        # Scrollbar for available tests
        available_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.available_tests_tree.yview)
        self.available_tests_tree.configure(yscrollcommand=available_scrollbar.set)
        
        self.available_tests_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        available_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Add Test button
        ttk.Button(parent, text="Add Selected Test →", command=self.add_selected_test).grid(
            row=1, column=0, columnspan=2, pady=10)
        
        # Double-click to add test
        self.available_tests_tree.bind('<Double-1>', lambda e: self.add_selected_test())
    
    def setup_selected_tests(self, parent):
        """Setup selected tests display"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Selected tests list
        columns = ('Code', 'Name', 'Price')
        self.selected_tests_tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)
        
        self.selected_tests_tree.heading('Code', text='Code')
        self.selected_tests_tree.heading('Name', text='Test Name')
        self.selected_tests_tree.heading('Price', text='Price (₹)')
        
        self.selected_tests_tree.column('Code', width=80, minwidth=60)
        self.selected_tests_tree.column('Name', width=200, minwidth=150)
        self.selected_tests_tree.column('Price', width=100, minwidth=80)
        
        # Scrollbar for selected tests
        selected_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.selected_tests_tree.yview)
        self.selected_tests_tree.configure(yscrollcommand=selected_scrollbar.set)
        
        self.selected_tests_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        selected_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Remove Test button
        ttk.Button(parent, text="← Remove Selected", command=self.remove_selected_test).grid(
            row=1, column=0, columnspan=2, pady=10)
        
        # Create Report button
        ttk.Button(parent, text="Create Report", command=self.create_report, 
                  style='Accent.TButton').grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # Double-click to remove test
        self.selected_tests_tree.bind('<Double-1>', lambda e: self.remove_selected_test())
    
    def setup_test_results(self, parent):
        """Setup test results entry interface"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Results frame with scrollable canvas
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.results_frame = ttk.Frame(canvas)
        
        self.results_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Save Results button
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save Results", command=self.save_test_results,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT)
    
    def create_reports_list_tab(self):
        """Create reports list and management tab"""
        reports_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(reports_frame, text="View Reports")
        
        # Configure grid
        reports_frame.columnconfigure(0, weight=1)
        reports_frame.rowconfigure(1, weight=1)
        
        # Search frame
        search_frame = ttk.Frame(reports_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search Reports:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.reports_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.reports_search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.search_reports)
        
        ttk.Button(search_frame, text="Refresh", command=self.load_reports).grid(row=0, column=2)
        
        # Reports list
        list_frame = ttk.Frame(reports_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ('ID', 'Date', 'Patient', 'Phone', 'Doctor', 'Status')
        self.reports_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        self.reports_tree.heading('ID', text='Report ID')
        self.reports_tree.heading('Date', text='Test Date')
        self.reports_tree.heading('Patient', text='Patient Name')
        self.reports_tree.heading('Phone', text='Phone')
        self.reports_tree.heading('Doctor', text='Doctor')
        self.reports_tree.heading('Status', text='Status')
        
        self.reports_tree.column('ID', width=80, minwidth=60)
        self.reports_tree.column('Date', width=100, minwidth=80)
        self.reports_tree.column('Patient', width=200, minwidth=150)
        self.reports_tree.column('Phone', width=120, minwidth=100)
        self.reports_tree.column('Doctor', width=150, minwidth=100)
        self.reports_tree.column('Status', width=100, minwidth=80)
        
        # Scrollbars
        reports_v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.reports_tree.yview)
        reports_h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.reports_tree.xview)
        self.reports_tree.configure(yscrollcommand=reports_v_scrollbar.set, xscrollcommand=reports_h_scrollbar.set)
        
        self.reports_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        reports_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        reports_h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons
        action_frame = ttk.Frame(reports_frame)
        action_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(action_frame, text="View Details", command=self.view_report_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Generate Bill", command=self.generate_bill_from_report).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Download PDF", command=self.download_report_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Print Report", command=self.print_report).pack(side=tk.LEFT)
        
        # Double-click to view details
        self.reports_tree.bind('<Double-1>', lambda e: self.view_report_details())
    
    def load_patients(self):
        """Load patients for selection"""
        try:
            patients = self.db.search_patients("")
            self.patients_data = {f"{p['first_name']} {p['last_name']} ({p['phone_number']})": p['patient_id'] 
                                  for p in patients}
            self.patient_combo['values'] = list(self.patients_data.keys())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load patients: {e}")
    
    def load_test_types(self):
        """Load available test types"""
        try:
            self.test_types = self.db.get_all_test_types()
            self.populate_available_tests()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load test types: {e}")
    
    def populate_available_tests(self):
        """Populate available tests tree"""
        # Clear existing items
        for item in self.available_tests_tree.get_children():
            self.available_tests_tree.delete(item)
        
        for test_type in self.test_types:
            values = (
                test_type['test_code'],
                test_type['test_name'],
                f"₹{test_type['price']:.2f}"
            )
            self.available_tests_tree.insert('', tk.END, values=values, tags=(test_type['test_type_id'],))
    
    def add_selected_test(self):
        """Add selected test to the selected tests list"""
        selection = self.available_tests_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a test to add")
            return
        
        item = self.available_tests_tree.item(selection[0])
        test_type_id = int(item['tags'][0])
        
        # Check if already selected
        if test_type_id in self.selected_tests:
            messagebox.showwarning("Already Selected", "This test is already selected")
            return
        
        # Find test data
        test_data = next((t for t in self.test_types if t['test_type_id'] == test_type_id), None)
        if test_data:
            self.selected_tests[test_type_id] = test_data
            self.update_selected_tests_display()
    
    def remove_selected_test(self):
        """Remove selected test from the selected tests list"""
        selection = self.selected_tests_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a test to remove")
            return
        
        item = self.selected_tests_tree.item(selection[0])
        test_type_id = int(item['tags'][0])
        
        if test_type_id in self.selected_tests:
            del self.selected_tests[test_type_id]
            self.update_selected_tests_display()
    
    def update_selected_tests_display(self):
        """Update the selected tests tree display"""
        # Clear existing items
        for item in self.selected_tests_tree.get_children():
            self.selected_tests_tree.delete(item)
        
        for test_type_id, test_data in self.selected_tests.items():
            values = (
                test_data['test_code'],
                test_data['test_name'],
                f"₹{test_data['price']:.2f}"
            )
            self.selected_tests_tree.insert('', tk.END, values=values, tags=(test_type_id,))
    
    def create_report(self):
        """Create a new blood report"""
        # Validate inputs
        if not self.patient_var.get():
            messagebox.showerror("Validation Error", "Please select a patient")
            return
        
        if not self.test_date_var.get():
            messagebox.showerror("Validation Error", "Please enter test date")
            return
        
        if not self.selected_tests:
            messagebox.showerror("Validation Error", "Please select at least one test")
            return
        
        try:
            # Validate date format
            datetime.strptime(self.test_date_var.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        try:
            # Get patient ID
            patient_id = self.patients_data[self.patient_var.get()]
            
            # Create report
            report_data = {
                'patient_id': patient_id,
                'test_date': self.test_date_var.get(),
                'doctor_name': self.doctor_var.get().strip(),
                'lab_technician': self.technician_var.get().strip(),
                'status': 'pending',
                'notes': ''
            }
            
            self.current_report_id = self.db.create_blood_report(report_data)
            
            # Create placeholder test results
            for test_type_id in self.selected_tests:
                result_data = {
                    'report_id': self.current_report_id,
                    'test_type_id': test_type_id,
                    'result_value': '',
                    'is_normal': None,
                    'remarks': ''
                }
                self.db.add_test_result(result_data)
            
            messagebox.showinfo("Success", f"Blood report created successfully!\nReport ID: {self.current_report_id}")
            self.status_callback(f"Blood report {self.current_report_id} created")
            
            # Switch to results entry
            self.setup_results_entry_fields()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create report: {e}")
    
    def setup_results_entry_fields(self):
        """Setup dynamic fields for entering test results"""
        # Clear existing fields
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_tests:
            return
        
        # Header
        ttk.Label(self.results_frame, text=f"Enter Results for Report ID: {self.current_report_id}", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Column headers
        ttk.Label(self.results_frame, text="Test", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Label(self.results_frame, text="Result Value", font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(self.results_frame, text="Normal?", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=5)
        ttk.Label(self.results_frame, text="Remarks", font=('Arial', 10, 'bold')).grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Create result entry fields
        self.result_vars = {}
        row = 2
        
        for test_type_id, test_data in self.selected_tests.items():
            # Test name and normal range
            test_info = f"{test_data['test_name']} ({test_data['test_code']})"
            if test_data.get('normal_range'):
                test_info += f"\nNormal: {test_data['normal_range']}"
            
            ttk.Label(self.results_frame, text=test_info).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            
            # Result value entry
            result_var = tk.StringVar()
            ttk.Entry(self.results_frame, textvariable=result_var, width=15).grid(row=row, column=1, padx=5, pady=5)
            
            # Normal/Abnormal selection
            normal_var = tk.StringVar()
            normal_combo = ttk.Combobox(self.results_frame, textvariable=normal_var, 
                                       values=["Normal", "Abnormal"], state="readonly", width=10)
            normal_combo.grid(row=row, column=2, padx=5, pady=5)
            
            # Remarks entry
            remarks_var = tk.StringVar()
            ttk.Entry(self.results_frame, textvariable=remarks_var, width=20).grid(row=row, column=3, padx=5, pady=5)
            
            # Store variables
            self.result_vars[test_type_id] = {
                'result': result_var,
                'normal': normal_var,
                'remarks': remarks_var
            }
            
            row += 1
    
    def save_test_results(self):
        """Save entered test results"""
        if not self.current_report_id or not self.result_vars:
            messagebox.showwarning("No Data", "No report or results to save")
            return
        
        try:
            # Update test results
            for test_type_id, vars_dict in self.result_vars.items():
                result_value = vars_dict['result'].get().strip()
                normal_status = vars_dict['normal'].get()
                remarks = vars_dict['remarks'].get().strip()
                
                # Convert normal status to boolean
                is_normal = None
                if normal_status == "Normal":
                    is_normal = True
                elif normal_status == "Abnormal":
                    is_normal = False
                
                # Update result in database
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE test_results 
                    SET result_value = ?, is_normal = ?, remarks = ?
                    WHERE report_id = ? AND test_type_id = ?
                ''', (result_value, is_normal, remarks, self.current_report_id, test_type_id))
                conn.commit()
                conn.close()
            
            # Update report status to completed
            self.db.update_report_status(self.current_report_id, 'completed')
            
            messagebox.showinfo("Success", "Test results saved successfully!")
            self.status_callback(f"Results saved for report {self.current_report_id}")
            
            # Refresh reports list and clear form
            self.load_reports()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {e}")
    
    def load_reports(self):
        """Load and display blood reports"""
        try:
            reports = self.db.get_blood_reports()
            self.populate_reports_list(reports)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reports: {e}")
    
    def populate_reports_list(self, reports):
        """Populate reports list"""
        # Clear existing items
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)
        
        for report in reports:
            patient_name = f"{report['first_name']} {report['last_name']}"
            values = (
                report['report_id'],
                report['test_date'],
                patient_name,
                report['phone_number'],
                report.get('doctor_name', ''),
                report['status'].title()
            )
            self.reports_tree.insert('', tk.END, values=values, tags=(report['report_id'],))
    
    def search_reports(self, event=None):
        """Search reports based on search term"""
        search_term = self.reports_search_var.get().lower()
        if not search_term:
            self.load_reports()
            return
        
        # Filter reports
        all_reports = self.db.get_blood_reports()
        filtered_reports = []
        
        for report in all_reports:
            if (search_term in f"{report['first_name']} {report['last_name']}".lower() or
                search_term in report['phone_number'] or
                search_term in str(report['report_id']) or
                search_term in report.get('doctor_name', '').lower()):
                filtered_reports.append(report)
        
        self.populate_reports_list(filtered_reports)
    
    def view_report_details(self):
        """View detailed report information"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a report to view")
            return
        
        item = self.reports_tree.item(selection[0])
        report_id = int(item['tags'][0])
        
        try:
            report_details = self.db.get_report_details(report_id)
            if report_details:
                self.show_report_details_window(report_details)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load report details: {e}")
    
    def show_report_details_window(self, report_details):
        """Show detailed report in a new window"""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Report Details - ID: {report_details['report_id']}")
        detail_window.geometry("800x600")
        
        # Create scrollable text widget
        text_frame = ttk.Frame(detail_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format report details
        content = f"""
BLOOD TEST REPORT
================

Report ID: {report_details['report_id']}
Date: {report_details['test_date']}
Status: {report_details['status'].upper()}

PATIENT INFORMATION
-------------------
Name: {report_details['first_name']} {report_details['last_name']}
Phone: {report_details['phone_number']}
Date of Birth: {report_details.get('date_of_birth', 'N/A')}
Gender: {report_details.get('gender', 'N/A')}

MEDICAL INFORMATION
-------------------
Doctor: {report_details.get('doctor_name', 'N/A')}
Lab Technician: {report_details.get('lab_technician', 'N/A')}
Notes: {report_details.get('notes', 'N/A')}

TEST RESULTS
============
"""
        
        for test_result in report_details.get('test_results', []):
            status = "NORMAL" if test_result.get('is_normal') else "ABNORMAL" if test_result.get('is_normal') is False else "PENDING"
            content += f"""
{test_result['test_name']} ({test_result['test_code']})
Normal Range: {test_result.get('normal_range', 'N/A')} {test_result.get('unit', '')}
Result: {test_result.get('result_value', 'PENDING')} {test_result.get('unit', '')}
Status: {status}
Remarks: {test_result.get('remarks', 'None')}
---------------------------------------------------
"""
        
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
    
    def generate_bill_from_report(self):
        """Generate bill from selected report"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a report to generate bill")
            return
        
        item = self.reports_tree.item(selection[0])
        report_id = int(item['tags'][0])
        
        try:
            bill_id = self.db.create_bill_from_report(report_id)
            messagebox.showinfo("Success", f"Bill generated successfully!\nBill ID: {bill_id}")
            self.status_callback(f"Bill {bill_id} generated from report {report_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {e}")
    
    def download_report_pdf(self):
        """Download selected report as PDF"""
        try:
            selected_item = self.reports_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a report to download.")
                return
            
            report_id = self.reports_tree.item(selected_item[0])['values'][0]
            
            # Get complete report details
            report_details = self.db.get_complete_report_details(report_id)
            if not report_details:
                messagebox.showerror("Error", "Failed to get report details.")
                return
            
            # Ask for save location
            pdf_dir = create_pdf_directory()
            suggested_filename = generate_filename("blood_report", report_id)
            
            filename = filedialog.asksaveasfilename(
                initialdir=pdf_dir,
                initialfile=suggested_filename,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Blood Report PDF"
            )
            
            if not filename:
                return
            
            # Generate PDF
            pdf_generator = PDFGenerator()
            success = pdf_generator.generate_blood_report_pdf(report_details, filename)
            
            if success:
                messagebox.showinfo("Success", f"Report PDF saved successfully!\nLocation: {filename}")
            else:
                messagebox.showerror("Error", "Failed to generate PDF report.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download PDF: {e}")

    def print_report(self):
        """Print selected report (placeholder)"""
        messagebox.showinfo("Print Report", "Print functionality will be implemented with PDF generation in the next update.")
    
    def clear_form(self):
        """Clear all form fields"""
        self.patient_var.set("")
        self.test_date_var.set(date.today().strftime('%Y-%m-%d'))
        self.doctor_var.set("")
        self.technician_var.set("")
        self.selected_tests.clear()
        self.update_selected_tests_display()
        self.current_report_id = None
        self.result_vars = {}
        
        # Clear results entry fields
        for widget in self.results_frame.winfo_children():
            widget.destroy() 