import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class LabDatabase:
    def __init__(self, db_path: str = "lab_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL UNIQUE,
                    email TEXT,
                    date_of_birth DATE,
                    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
                    address TEXT,
                    emergency_contact TEXT,
                    emergency_phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Test types table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_types (
                    test_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    test_code TEXT UNIQUE,
                    normal_range TEXT,
                    unit TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    description TEXT
                )
            ''')
            
            # Blood reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blood_reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    test_date DATE NOT NULL,
                    doctor_name TEXT,
                    lab_technician TEXT,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'reviewed')),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
                )
            ''')
            
            # Test results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    test_type_id INTEGER NOT NULL,
                    result_value TEXT,
                    is_normal BOOLEAN,
                    remarks TEXT,
                    FOREIGN KEY (report_id) REFERENCES blood_reports (report_id),
                    FOREIGN KEY (test_type_id) REFERENCES test_types (test_type_id)
                )
            ''')
            
            # Bills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    report_id INTEGER,
                    bill_date DATE NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    paid_amount DECIMAL(10,2) DEFAULT 0,
                    payment_status TEXT DEFAULT 'unpaid' CHECK(payment_status IN ('unpaid', 'partial', 'paid')),
                    payment_method TEXT,
                    discount DECIMAL(10,2) DEFAULT 0,
                    tax_amount DECIMAL(10,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                    FOREIGN KEY (report_id) REFERENCES blood_reports (report_id)
                )
            ''')
            
            # Bill items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bill_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL,
                    test_type_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    unit_price DECIMAL(10,2),
                    total_price DECIMAL(10,2),
                    FOREIGN KEY (bill_id) REFERENCES bills (bill_id),
                    FOREIGN KEY (test_type_id) REFERENCES test_types (test_type_id)
                )
            ''')
            
            # Insert some default test types
            self._insert_default_test_types(cursor)
            
            conn.commit()
            print("Database initialized successfully!")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _insert_default_test_types(self, cursor):
        """Insert default blood test types"""
        default_tests = [
            ('Complete Blood Count', 'CBC', '4.5-11.0 x10³/μL', '10³/μL', 500.00, 'Basic blood count test'),
            ('Blood Sugar Fasting', 'BSF', '70-100 mg/dL', 'mg/dL', 200.00, 'Fasting blood glucose test'),
            ('Blood Sugar Random', 'BSR', '<140 mg/dL', 'mg/dL', 150.00, 'Random blood glucose test'),
            ('Hemoglobin', 'HGB', '12-16 g/dL', 'g/dL', 300.00, 'Hemoglobin level test'),
            ('Cholesterol Total', 'CHOL', '<200 mg/dL', 'mg/dL', 400.00, 'Total cholesterol test'),
            ('Liver Function Test', 'LFT', 'Various', 'Various', 800.00, 'Complete liver function panel'),
            ('Kidney Function Test', 'KFT', 'Various', 'Various', 700.00, 'Complete kidney function panel'),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO test_types 
            (test_name, test_code, normal_range, unit, price, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', default_tests)
    
    # Patient operations
    def add_patient(self, patient_data: Dict[str, Any]) -> int:
        """Add a new patient and return patient_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO patients 
                (first_name, last_name, phone_number, email, date_of_birth, 
                 gender, address, emergency_contact, emergency_phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_data['first_name'],
                patient_data['last_name'],
                patient_data['phone_number'],
                patient_data.get('email', ''),
                patient_data.get('date_of_birth', ''),
                patient_data.get('gender', ''),
                patient_data.get('address', ''),
                patient_data.get('emergency_contact', ''),
                patient_data.get('emergency_phone', '')
            ))
            
            patient_id = cursor.lastrowid
            conn.commit()
            return patient_id
            
        except sqlite3.IntegrityError as e:
            if "phone_number" in str(e):
                raise ValueError("Phone number already exists")
            raise e
        finally:
            conn.close()
    
    def search_patients(self, search_term: str = "") -> List[Dict[str, Any]]:
        """Search patients by name or phone number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if search_term:
                cursor.execute('''
                    SELECT * FROM patients 
                    WHERE first_name LIKE ? OR last_name LIKE ? OR phone_number LIKE ?
                    ORDER BY last_name, first_name
                ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('SELECT * FROM patients ORDER BY last_name, first_name')
            
            columns = [description[0] for description in cursor.description]
            patients = []
            
            for row in cursor.fetchall():
                patient = dict(zip(columns, row))
                patients.append(patient)
            
            return patients
            
        finally:
            conn.close()
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """Get patient by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        finally:
            conn.close()
    
    # Test type operations
    def add_test_type(self, test_data: Dict[str, Any]) -> int:
        """Add a new test type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO test_types (test_name, test_code, normal_range, unit, price, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                test_data['test_name'],
                test_data['test_code'],
                test_data.get('normal_range', ''),
                test_data.get('unit', ''),
                test_data['price'],
                test_data.get('description', '')
            ))
            
            test_type_id = cursor.lastrowid
            conn.commit()
            return test_type_id
            
        finally:
            conn.close()
    
    def get_all_test_types(self) -> List[Dict[str, Any]]:
        """Get all test types"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM test_types ORDER BY test_name')
            columns = [description[0] for description in cursor.description]
            test_types = []
            
            for row in cursor.fetchall():
                test_type = dict(zip(columns, row))
                test_types.append(test_type)
            
            return test_types
            
        finally:
            conn.close()
    
    # Blood report operations
    def create_blood_report(self, report_data: Dict[str, Any]) -> int:
        """Create a new blood report and return report_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO blood_reports 
                (patient_id, test_date, doctor_name, lab_technician, status, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                report_data['patient_id'],
                report_data['test_date'],
                report_data.get('doctor_name', ''),
                report_data.get('lab_technician', ''),
                report_data.get('status', 'pending'),
                report_data.get('notes', '')
            ))
            
            report_id = cursor.lastrowid
            conn.commit()
            return report_id
            
        finally:
            conn.close()
    
    def add_test_result(self, result_data: Dict[str, Any]) -> int:
        """Add a test result to a blood report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO test_results 
                (report_id, test_type_id, result_value, is_normal, remarks)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                result_data['report_id'],
                result_data['test_type_id'],
                result_data.get('result_value', ''),
                result_data.get('is_normal', None),
                result_data.get('remarks', '')
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            return result_id
            
        finally:
            conn.close()
    
    def get_blood_reports(self, patient_id: int = None) -> List[Dict[str, Any]]:
        """Get blood reports, optionally filtered by patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if patient_id:
                cursor.execute('''
                    SELECT br.*, p.first_name, p.last_name, p.phone_number
                    FROM blood_reports br
                    JOIN patients p ON br.patient_id = p.patient_id
                    WHERE br.patient_id = ?
                    ORDER BY br.test_date DESC
                ''', (patient_id,))
            else:
                cursor.execute('''
                    SELECT br.*, p.first_name, p.last_name, p.phone_number
                    FROM blood_reports br
                    JOIN patients p ON br.patient_id = p.patient_id
                    ORDER BY br.test_date DESC
                ''')
            
            columns = [description[0] for description in cursor.description]
            reports = []
            
            for row in cursor.fetchall():
                report = dict(zip(columns, row))
                reports.append(report)
            
            return reports
            
        finally:
            conn.close()
    
    def get_report_details(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Get complete report details including test results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get report header
            cursor.execute('''
                SELECT br.*, p.first_name, p.last_name, p.phone_number, p.date_of_birth, p.gender
                FROM blood_reports br
                JOIN patients p ON br.patient_id = p.patient_id
                WHERE br.report_id = ?
            ''', (report_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [description[0] for description in cursor.description]
            report = dict(zip(columns, row))
            
            # Get test results
            cursor.execute('''
                SELECT tr.*, tt.test_name, tt.test_code, tt.normal_range, tt.unit, tt.price
                FROM test_results tr
                JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                WHERE tr.report_id = ?
                ORDER BY tt.test_name
            ''', (report_id,))
            
            test_columns = [description[0] for description in cursor.description]
            test_results = []
            
            for row in cursor.fetchall():
                test_result = dict(zip(test_columns, row))
                test_results.append(test_result)
            
            report['test_results'] = test_results
            return report
            
        finally:
            conn.close()
    
    def get_complete_report_details(self, report_id: int) -> Dict[str, Any]:
        """Get complete report details for PDF generation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get report with patient details
            cursor.execute('''
                SELECT br.*, p.first_name, p.last_name, p.phone_number, 
                       p.date_of_birth, p.gender, p.address
                FROM blood_reports br
                JOIN patients p ON br.patient_id = p.patient_id
                WHERE br.report_id = ?
            ''', (report_id,))
            
            report = cursor.fetchone()
            if not report:
                return None
            
            # Get test results with test details
            cursor.execute('''
                SELECT tr.*, tt.test_name, tt.test_code, tt.price, 
                       tt.normal_range, tt.unit
                FROM test_results tr
                JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                WHERE tr.report_id = ?
                ORDER BY tt.test_name
            ''', (report_id,))
            
            test_results = cursor.fetchall()
            
            # Get column names for report
            report_columns = [description[0] for description in cursor.description]
            report_details = dict(zip(report_columns, report))
            
            # Get test results with proper column mapping
            if test_results:
                cursor.execute('''
                    SELECT tr.*, tt.test_name, tt.test_code, tt.price, 
                           tt.normal_range, tt.unit
                    FROM test_results tr
                    JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                    WHERE tr.report_id = ?
                    ORDER BY tt.test_name
                    LIMIT 1
                ''', (report_id,))
                
                # Get column names for test results
                test_columns = [description[0] for description in cursor.description]
                
                # Re-execute to get all results
                cursor.execute('''
                    SELECT tr.*, tt.test_name, tt.test_code, tt.price, 
                           tt.normal_range, tt.unit
                    FROM test_results tr
                    JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                    WHERE tr.report_id = ?
                    ORDER BY tt.test_name
                ''', (report_id,))
                
                test_results = cursor.fetchall()
                report_details['test_results'] = [dict(zip(test_columns, result)) for result in test_results]
            else:
                report_details['test_results'] = []
            
            return report_details
            
        finally:
            conn.close()
    
    def get_complete_bill_details(self, bill_id: int) -> Dict[str, Any]:
        """Get complete bill details for PDF generation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get bill with patient details
            cursor.execute('''
                SELECT b.*, p.first_name, p.last_name, p.phone_number, 
                       p.address, p.gender, p.date_of_birth
                FROM bills b
                JOIN patients p ON b.patient_id = p.patient_id
                WHERE b.bill_id = ?
            ''', (bill_id,))
            
            bill = cursor.fetchone()
            if not bill:
                return None
            
            # Get bill items with test details
            cursor.execute('''
                SELECT bi.*, tt.test_name, tt.test_code
                FROM bill_items bi
                JOIN test_types tt ON bi.test_type_id = tt.test_type_id
                WHERE bi.bill_id = ?
                ORDER BY tt.test_name
            ''', (bill_id,))
            
            bill_items = cursor.fetchall()
            
            # Get column names for bill
            bill_columns = [description[0] for description in cursor.description]
            bill_details = dict(zip(bill_columns, bill))
            
            # Get bill items with proper column mapping
            if bill_items:
                cursor.execute('''
                    SELECT bi.*, tt.test_name, tt.test_code
                    FROM bill_items bi
                    JOIN test_types tt ON bi.test_type_id = tt.test_type_id
                    WHERE bi.bill_id = ?
                    ORDER BY tt.test_name
                    LIMIT 1
                ''', (bill_id,))
                
                # Get column names for bill items
                item_columns = [description[0] for description in cursor.description]
                
                # Re-execute to get all results
                cursor.execute('''
                    SELECT bi.*, tt.test_name, tt.test_code
                    FROM bill_items bi
                    JOIN test_types tt ON bi.test_type_id = tt.test_type_id
                    WHERE bi.bill_id = ?
                    ORDER BY tt.test_name
                ''', (bill_id,))
                
                bill_items = cursor.fetchall()
                bill_details['items'] = [dict(zip(item_columns, item)) for item in bill_items]
            else:
                bill_details['items'] = []
            
            return bill_details
            
        finally:
            conn.close()
    
    def update_report_status(self, report_id: int, status: str):
        """Update report status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE blood_reports 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE report_id = ?
            ''', (status, report_id))
            
            conn.commit()
            
        finally:
            conn.close()
    
    # Billing operations
    def create_bill(self, bill_data: Dict[str, Any]) -> int:
        """Create a new bill and return bill_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO bills 
                (patient_id, report_id, bill_date, total_amount, paid_amount, 
                 payment_status, payment_method, discount, tax_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bill_data['patient_id'],
                bill_data.get('report_id'),
                bill_data['bill_date'],
                bill_data['total_amount'],
                bill_data.get('paid_amount', 0),
                bill_data.get('payment_status', 'unpaid'),
                bill_data.get('payment_method', ''),
                bill_data.get('discount', 0),
                bill_data.get('tax_amount', 0)
            ))
            
            bill_id = cursor.lastrowid
            conn.commit()
            return bill_id
            
        finally:
            conn.close()
    
    def add_bill_item(self, item_data: Dict[str, Any]) -> int:
        """Add an item to a bill"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO bill_items 
                (bill_id, test_type_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item_data['bill_id'],
                item_data['test_type_id'],
                item_data.get('quantity', 1),
                item_data['unit_price'],
                item_data['total_price']
            ))
            
            item_id = cursor.lastrowid
            conn.commit()
            return item_id
            
        finally:
            conn.close()
    
    def get_bills(self, patient_id: int = None) -> List[Dict[str, Any]]:
        """Get bills, optionally filtered by patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if patient_id:
                cursor.execute('''
                    SELECT b.*, p.first_name, p.last_name, p.phone_number
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    WHERE b.patient_id = ?
                    ORDER BY b.bill_date DESC
                ''', (patient_id,))
            else:
                cursor.execute('''
                    SELECT b.*, p.first_name, p.last_name, p.phone_number
                    FROM bills b
                    JOIN patients p ON b.patient_id = p.patient_id
                    ORDER BY b.bill_date DESC
                ''')
            
            columns = [description[0] for description in cursor.description]
            bills = []
            
            for row in cursor.fetchall():
                bill = dict(zip(columns, row))
                bills.append(bill)
            
            return bills
            
        finally:
            conn.close()
    
    def get_bill_details(self, bill_id: int) -> Optional[Dict[str, Any]]:
        """Get complete bill details including items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get bill header
            cursor.execute('''
                SELECT b.*, p.first_name, p.last_name, p.phone_number, p.address
                FROM bills b
                JOIN patients p ON b.patient_id = p.patient_id
                WHERE b.bill_id = ?
            ''', (bill_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [description[0] for description in cursor.description]
            bill = dict(zip(columns, row))
            
            # Get bill items
            cursor.execute('''
                SELECT bi.*, tt.test_name, tt.test_code
                FROM bill_items bi
                JOIN test_types tt ON bi.test_type_id = tt.test_type_id
                WHERE bi.bill_id = ?
                ORDER BY tt.test_name
            ''', (bill_id,))
            
            item_columns = [description[0] for description in cursor.description]
            bill_items = []
            
            for row in cursor.fetchall():
                item = dict(zip(item_columns, row))
                bill_items.append(item)
            
            bill['items'] = bill_items
            return bill
            
        finally:
            conn.close()
    
    def update_payment(self, bill_id: int, payment_data: Dict[str, Any]):
        """Update payment information for a bill"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE bills 
                SET paid_amount = ?, payment_status = ?, payment_method = ?
                WHERE bill_id = ?
            ''', (
                payment_data['paid_amount'],
                payment_data['payment_status'],
                payment_data.get('payment_method', ''),
                bill_id
            ))
            
            conn.commit()
            
        finally:
            conn.close()
    
    def create_bill_from_report(self, report_id: int) -> int:
        """Create a bill automatically from a blood report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get report details
            cursor.execute('''
                SELECT patient_id, test_date FROM blood_reports WHERE report_id = ?
            ''', (report_id,))
            
            report_row = cursor.fetchone()
            if not report_row:
                raise ValueError("Report not found")
            
            patient_id, test_date = report_row
            
            # Get test results and prices
            cursor.execute('''
                SELECT tr.test_type_id, tt.price
                FROM test_results tr
                JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                WHERE tr.report_id = ?
            ''', (report_id,))
            
            test_results = cursor.fetchall()
            if not test_results:
                raise ValueError("No test results found for this report")
            
            # Calculate total
            total_amount = sum(price for _, price in test_results)
            tax_amount = total_amount * 0.18  # 18% GST
            final_amount = total_amount + tax_amount
            
            # Create bill
            bill_data = {
                'patient_id': patient_id,
                'report_id': report_id,
                'bill_date': test_date,
                'total_amount': final_amount,
                'tax_amount': tax_amount,
                'payment_status': 'unpaid'
            }
            
            bill_id = self.create_bill(bill_data)
            
            # Add bill items
            for test_type_id, price in test_results:
                item_data = {
                    'bill_id': bill_id,
                    'test_type_id': test_type_id,
                    'quantity': 1,
                    'unit_price': price,
                    'total_price': price
                }
                self.add_bill_item(item_data)
            
            return bill_id
            
        finally:
            conn.close() 