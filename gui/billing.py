import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from utils.pdf_generator import PDFGenerator, create_pdf_directory, generate_filename

class BillingManagement:
    def __init__(self, parent, database, status_callback):
        self.parent = parent
        self.db = database
        self.status_callback = status_callback
        self.setup_ui()
        self.load_bills()
    
    def setup_ui(self):
        """Setup billing management interface"""
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_bills_list_tab()
        self.create_payment_tab()
    
    def create_bills_list_tab(self):
        """Create bills list tab"""
        bills_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(bills_frame, text="View Bills")
        
        bills_frame.columnconfigure(0, weight=1)
        bills_frame.rowconfigure(1, weight=1)
        
        # Search and filter frame
        search_frame = ttk.Frame(bills_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search Bills:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.bills_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.bills_search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.search_bills)
        
        # Payment status filter
        ttk.Label(search_frame, text="Status:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.status_filter_var = tk.StringVar()
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_filter_var,
                                   values=["All", "Unpaid", "Partial", "Paid"], state="readonly", width=12)
        status_combo.grid(row=0, column=3, padx=(0, 10))
        status_combo.set("All")
        status_combo.bind('<<ComboboxSelected>>', self.filter_bills)
        
        ttk.Button(search_frame, text="Refresh", command=self.load_bills).grid(row=0, column=4)
        
        # Bills list
        list_frame = ttk.Frame(bills_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ('ID', 'Date', 'Patient', 'Phone', 'Total', 'Paid', 'Status')
        self.bills_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        self.bills_tree.heading('ID', text='Bill ID')
        self.bills_tree.heading('Date', text='Bill Date')
        self.bills_tree.heading('Patient', text='Patient Name')
        self.bills_tree.heading('Phone', text='Phone')
        self.bills_tree.heading('Total', text='Total Amount')
        self.bills_tree.heading('Paid', text='Paid Amount')
        self.bills_tree.heading('Status', text='Status')
        
        self.bills_tree.column('ID', width=80, minwidth=60)
        self.bills_tree.column('Date', width=100, minwidth=80)
        self.bills_tree.column('Patient', width=200, minwidth=150)
        self.bills_tree.column('Phone', width=120, minwidth=100)
        self.bills_tree.column('Total', width=120, minwidth=100)
        self.bills_tree.column('Paid', width=120, minwidth=100)
        self.bills_tree.column('Status', width=100, minwidth=80)
        
        # Scrollbars
        bills_v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.bills_tree.yview)
        self.bills_tree.configure(yscrollcommand=bills_v_scrollbar.set)
        
        self.bills_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        bills_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Action buttons
        action_frame = ttk.Frame(bills_frame)
        action_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(action_frame, text="View Details", command=self.view_bill_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Record Payment", command=self.record_payment).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Download PDF", command=self.download_bill_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Print Receipt", command=self.print_receipt).pack(side=tk.LEFT)
        
        self.bills_tree.bind('<Double-1>', lambda e: self.view_bill_details())
    
    def create_payment_tab(self):
        """Create payment recording tab"""
        payment_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(payment_frame, text="Record Payment")
        
        payment_frame.columnconfigure(1, weight=1)
        
        # Payment form
        form_frame = ttk.LabelFrame(payment_frame, text="Payment Details", padding="20")
        form_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        form_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Bill ID
        ttk.Label(form_frame, text="Bill ID*:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.payment_bill_id_var = tk.StringVar()
        bill_id_entry = ttk.Entry(form_frame, textvariable=self.payment_bill_id_var, width=20)
        bill_id_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        bill_id_entry.bind('<Return>', self.load_bill_for_payment)
        ttk.Button(form_frame, text="Load Bill", command=self.load_bill_for_payment).grid(
            row=row, column=2, pady=5, padx=(10, 0))
        row += 1
        
        # Bill Information Display
        self.bill_info_frame = ttk.LabelFrame(form_frame, text="Bill Information", padding="10")
        self.bill_info_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.bill_info_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Payment Amount
        ttk.Label(form_frame, text="Payment Amount*:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.payment_amount_var = tk.StringVar()
        payment_entry = ttk.Entry(form_frame, textvariable=self.payment_amount_var, width=20)
        payment_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        payment_entry.bind('<KeyRelease>', self.validate_payment_amount)
        row += 1
        
        # Payment Method
        ttk.Label(form_frame, text="Payment Method*:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.payment_method_var = tk.StringVar()
        method_combo = ttk.Combobox(form_frame, textvariable=self.payment_method_var,
                                   values=["Cash", "Card", "UPI", "Bank Transfer", "Cheque"], 
                                   state="readonly", width=17)
        method_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Record Payment", command=self.save_payment).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Form", command=self.clear_payment_form).pack(side=tk.LEFT)
        
        # Initialize bill info frame
        self.setup_empty_bill_info()
    
    def setup_empty_bill_info(self):
        """Setup empty bill information display"""
        for widget in self.bill_info_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.bill_info_frame, text="Enter Bill ID and click 'Load Bill' to view details",
                 font=('Arial', 10, 'italic')).grid(row=0, column=0, pady=20)
    
    def load_bills(self):
        """Load and display all bills"""
        try:
            bills = self.db.get_bills()
            self.populate_bills_list(bills)
            self.status_callback(f"Loaded {len(bills)} bills")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bills: {e}")
    
    def populate_bills_list(self, bills):
        """Populate bills list"""
        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)
        
        for bill in bills:
            patient_name = f"{bill['first_name']} {bill['last_name']}"
            values = (
                bill['bill_id'],
                bill['bill_date'],
                patient_name,
                bill['phone_number'],
                f"₹{bill['total_amount']:.2f}",
                f"₹{bill['paid_amount']:.2f}",
                bill['payment_status'].title()
            )
            self.bills_tree.insert('', tk.END, values=values, tags=(bill['bill_id'],))
    
    def search_bills(self, event=None):
        """Search bills based on search term"""
        search_term = self.bills_search_var.get().lower()
        self.filter_and_display_bills(search_term)
    
    def filter_bills(self, event=None):
        """Filter bills by payment status"""
        search_term = self.bills_search_var.get().lower()
        self.filter_and_display_bills(search_term)
    
    def filter_and_display_bills(self, search_term=""):
        """Filter and display bills based on search term and status"""
        try:
            all_bills = self.db.get_bills()
            filtered_bills = []
            
            status_filter = self.status_filter_var.get().lower()
            
            for bill in all_bills:
                # Text search filter
                if search_term and not (
                    search_term in f"{bill['first_name']} {bill['last_name']}".lower() or
                    search_term in bill['phone_number'] or
                    search_term in str(bill['bill_id'])):
                    continue
                
                # Status filter
                if status_filter != "all" and bill['payment_status'] != status_filter:
                    continue
                
                filtered_bills.append(bill)
            
            self.populate_bills_list(filtered_bills)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter bills: {e}")
    
    def view_bill_details(self):
        """View detailed bill information"""
        selection = self.bills_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bill to view")
            return
        
        item = self.bills_tree.item(selection[0])
        bill_id = int(item['tags'][0])
        
        try:
            bill_details = self.db.get_bill_details(bill_id)
            if bill_details:
                self.show_bill_details_window(bill_details)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bill details: {e}")
    
    def show_bill_details_window(self, bill_details):
        """Show detailed bill in a new window"""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Bill Details - ID: {bill_details['bill_id']}")
        detail_window.geometry("700x600")
        
        text_frame = ttk.Frame(detail_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format bill details
        subtotal = sum(item['total_price'] for item in bill_details.get('items', []))
        content = f"""LABORATORY BILL
===============

Bill ID: {bill_details['bill_id']}
Date: {bill_details['bill_date']}
Status: {bill_details['payment_status'].upper()}

PATIENT INFORMATION
-------------------
Name: {bill_details['first_name']} {bill_details['last_name']}
Phone: {bill_details['phone_number']}
Address: {bill_details.get('address', 'N/A')}

BILL ITEMS
==========
"""
        
        for item in bill_details.get('items', []):
            content += f"""
{item['test_name']} ({item['test_code']})
Quantity: {item['quantity']}
Unit Price: ₹{item['unit_price']:.2f}
Total: ₹{item['total_price']:.2f}
---------------------------------------------------
"""
        
        content += f"""

PAYMENT SUMMARY
===============
Subtotal: ₹{subtotal:.2f}
Tax (18% GST): ₹{bill_details.get('tax_amount', 0):.2f}
Discount: ₹{bill_details.get('discount', 0):.2f}
---------------------------------------------------
Total Amount: ₹{bill_details['total_amount']:.2f}
Paid Amount: ₹{bill_details['paid_amount']:.2f}
Balance: ₹{bill_details['total_amount'] - bill_details['paid_amount']:.2f}

Payment Method: {bill_details.get('payment_method', 'N/A')}
"""
        
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
    
    def record_payment(self):
        """Record payment for selected bill"""
        selection = self.bills_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bill to record payment")
            return
        
        item = self.bills_tree.item(selection[0])
        bill_id = int(item['tags'][0])
        
        # Switch to payment tab and load the bill
        self.notebook.select(1)
        self.payment_bill_id_var.set(str(bill_id))
        self.load_bill_for_payment()
    
    def load_bill_for_payment(self, event=None):
        """Load bill details for payment recording"""
        bill_id_str = self.payment_bill_id_var.get().strip()
        if not bill_id_str:
            messagebox.showwarning("No Bill ID", "Please enter a bill ID")
            return
        
        try:
            bill_id = int(bill_id_str)
            bill_details = self.db.get_bill_details(bill_id)
            
            if not bill_details:
                messagebox.showerror("Bill Not Found", f"No bill found with ID: {bill_id}")
                self.setup_empty_bill_info()
                return
            
            self.display_bill_info(bill_details)
            
        except ValueError:
            messagebox.showerror("Invalid Bill ID", "Please enter a valid numeric bill ID")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bill: {e}")
    
    def display_bill_info(self, bill_details):
        """Display bill information in payment form"""
        for widget in self.bill_info_frame.winfo_children():
            widget.destroy()
        
        self.current_bill = bill_details
        balance = bill_details['total_amount'] - bill_details['paid_amount']
        
        ttk.Label(self.bill_info_frame, text="Patient:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.bill_info_frame, text=f"{bill_details['first_name']} {bill_details['last_name']}").grid(
            row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        ttk.Label(self.bill_info_frame, text="Total Amount:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.bill_info_frame, text=f"₹{bill_details['total_amount']:.2f}").grid(
            row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        ttk.Label(self.bill_info_frame, text="Paid Amount:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.bill_info_frame, text=f"₹{bill_details['paid_amount']:.2f}").grid(
            row=2, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        ttk.Label(self.bill_info_frame, text="Balance:").grid(row=3, column=0, sticky=tk.W, pady=2)
        balance_label = ttk.Label(self.bill_info_frame, text=f"₹{balance:.2f}", font=('Arial', 10, 'bold'))
        balance_label.grid(row=3, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        ttk.Label(self.bill_info_frame, text="Status:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(self.bill_info_frame, text=bill_details['payment_status'].title()).grid(
            row=4, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        if balance > 0:
            self.payment_amount_var.set(f"{balance:.2f}")
    
    def validate_payment_amount(self, event=None):
        """Validate payment amount input"""
        amount = self.payment_amount_var.get()
        valid_chars = '0123456789.'
        filtered_amount = ''.join(c for c in amount if c in valid_chars)
        
        if filtered_amount.count('.') > 1:
            parts = filtered_amount.split('.')
            filtered_amount = parts[0] + '.' + ''.join(parts[1:])
        
        if filtered_amount != amount:
            self.payment_amount_var.set(filtered_amount)
    
    def save_payment(self):
        """Save payment record"""
        if not hasattr(self, 'current_bill'):
            messagebox.showerror("No Bill Loaded", "Please load a bill first")
            return
        
        amount_str = self.payment_amount_var.get().strip()
        if not amount_str:
            messagebox.showerror("Validation Error", "Please enter payment amount")
            return
        
        try:
            payment_amount = float(amount_str)
            if payment_amount <= 0:
                messagebox.showerror("Validation Error", "Payment amount must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid payment amount")
            return
        
        if not self.payment_method_var.get():
            messagebox.showerror("Validation Error", "Please select payment method")
            return
        
        current_balance = self.current_bill['total_amount'] - self.current_bill['paid_amount']
        if payment_amount > current_balance:
            if not messagebox.askyesno("Overpayment", 
                                     f"Payment amount exceeds balance. Continue?"):
                return
        
        try:
            new_paid_amount = self.current_bill['paid_amount'] + payment_amount
            total_amount = self.current_bill['total_amount']
            
            if new_paid_amount >= total_amount:
                payment_status = 'paid'
            elif new_paid_amount > 0:
                payment_status = 'partial'
            else:
                payment_status = 'unpaid'
            
            payment_data = {
                'paid_amount': new_paid_amount,
                'payment_status': payment_status,
                'payment_method': self.payment_method_var.get()
            }
            
            self.db.update_payment(self.current_bill['bill_id'], payment_data)
            
            messagebox.showinfo("Success", f"Payment of ₹{payment_amount:.2f} recorded successfully!")
            self.status_callback(f"Payment recorded for bill {self.current_bill['bill_id']}")
            
            self.load_bills()
            self.clear_payment_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record payment: {e}")
    
    def clear_payment_form(self):
        """Clear payment form"""
        self.payment_bill_id_var.set("")
        self.payment_amount_var.set("")
        self.payment_method_var.set("")
        self.setup_empty_bill_info()
        if hasattr(self, 'current_bill'):
            delattr(self, 'current_bill')
    
    def download_bill_pdf(self):
        """Download selected bill as PDF"""
        try:
            selected_item = self.bills_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a bill to download.")
                return
            
            bill_id = self.bills_tree.item(selected_item[0])['values'][0]
            
            # Get complete bill details
            bill_details = self.db.get_complete_bill_details(bill_id)
            if not bill_details:
                messagebox.showerror("Error", "Failed to get bill details.")
                return
            
            # Ask for save location
            pdf_dir = create_pdf_directory()
            suggested_filename = generate_filename("bill", bill_id)
            
            filename = filedialog.asksaveasfilename(
                initialdir=pdf_dir,
                initialfile=suggested_filename,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Bill PDF"
            )
            
            if not filename:
                return
            
            # Generate PDF
            pdf_generator = PDFGenerator()
            success = pdf_generator.generate_bill_pdf(bill_details, filename)
            
            if success:
                messagebox.showinfo("Success", f"Bill PDF saved successfully!\nLocation: {filename}")
            else:
                messagebox.showerror("Error", "Failed to generate PDF bill.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download PDF: {e}")
    
    def print_receipt(self):
        """Generate and save a payment receipt PDF"""
        try:
            selected_item = self.bills_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a bill to print receipt.")
                return
            
            bill_id = self.bills_tree.item(selected_item[0])['values'][0]
            
            # Get bill details
            bill_details = self.db.get_complete_bill_details(bill_id)
            if not bill_details:
                messagebox.showerror("Error", "Failed to get bill details.")
                return
            
            # Check if any payment has been made
            if bill_details['paid_amount'] <= 0:
                messagebox.showwarning("Warning", "No payments have been made for this bill.")
                return
            
            # Ask for save location
            pdf_dir = create_pdf_directory()
            suggested_filename = generate_filename("receipt", bill_id)
            
            filename = filedialog.asksaveasfilename(
                initialdir=pdf_dir,
                initialfile=suggested_filename,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Receipt PDF"
            )
            
            if not filename:
                return
            
            # Add receipt flag to indicate this is a payment receipt
            bill_details['is_receipt'] = True
            
            # Generate PDF receipt
            pdf_generator = PDFGenerator()
            success = pdf_generator.generate_bill_pdf(bill_details, filename)
            
            if success:
                messagebox.showinfo("Success", f"Receipt PDF saved successfully!\nLocation: {filename}")
            else:
                messagebox.showerror("Error", "Failed to generate receipt.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print receipt: {e}") 