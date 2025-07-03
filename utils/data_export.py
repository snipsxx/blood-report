import csv
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import pandas as pd

class DataExporter:
    def __init__(self, database):
        self.db = database
    
    def export_patients_to_csv(self, filename: str, search_term: str = "") -> bool:
        """Export patients data to CSV"""
        try:
            patients = self.db.search_patients(search_term)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Patient ID', 'First Name', 'Last Name', 'Phone Number', 
                            'Date of Birth', 'Gender', 'Address', 'Created Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for patient in patients:
                    writer.writerow({
                        'Patient ID': patient['patient_id'],
                        'First Name': patient['first_name'],
                        'Last Name': patient['last_name'],
                        'Phone Number': patient['phone_number'],
                        'Date of Birth': patient.get('date_of_birth', ''),
                        'Gender': patient.get('gender', ''),
                        'Address': patient.get('address', ''),
                        'Created Date': patient.get('created_at', '')
                    })
            
            return True
            
        except Exception as e:
            print(f"Error exporting patients to CSV: {e}")
            return False
    
    def export_reports_to_csv(self, filename: str, start_date: str = None, end_date: str = None) -> bool:
        """Export blood reports to CSV"""
        try:
            reports = self.db.get_blood_reports()
            
            # Filter by date if provided
            if start_date and end_date:
                reports = [r for r in reports if start_date <= r['test_date'] <= end_date]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Report ID', 'Test Date', 'Patient Name', 'Phone Number', 
                            'Doctor', 'Lab Technician', 'Status', 'Notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for report in reports:
                    writer.writerow({
                        'Report ID': report['report_id'],
                        'Test Date': report['test_date'],
                        'Patient Name': f"{report['first_name']} {report['last_name']}",
                        'Phone Number': report['phone_number'],
                        'Doctor': report.get('doctor_name', ''),
                        'Lab Technician': report.get('lab_technician', ''),
                        'Status': report['status'],
                        'Notes': report.get('notes', '')
                    })
            
            return True
            
        except Exception as e:
            print(f"Error exporting reports to CSV: {e}")
            return False
    
    def export_bills_to_csv(self, filename: str, start_date: str = None, end_date: str = None) -> bool:
        """Export bills data to CSV"""
        try:
            bills = self.db.get_bills()
            
            # Filter by date if provided
            if start_date and end_date:
                bills = [b for b in bills if start_date <= b['bill_date'] <= end_date]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Bill ID', 'Bill Date', 'Patient Name', 'Phone Number', 
                            'Total Amount', 'Paid Amount', 'Balance', 'Payment Status', 'Payment Method']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for bill in bills:
                    balance = bill['total_amount'] - bill['paid_amount']
                    writer.writerow({
                        'Bill ID': bill['bill_id'],
                        'Bill Date': bill['bill_date'],
                        'Patient Name': f"{bill['first_name']} {bill['last_name']}",
                        'Phone Number': bill['phone_number'],
                        'Total Amount': f"₹{bill['total_amount']:.2f}",
                        'Paid Amount': f"₹{bill['paid_amount']:.2f}",
                        'Balance': f"₹{balance:.2f}",
                        'Payment Status': bill['payment_status'],
                        'Payment Method': bill.get('payment_method', '')
                    })
            
            return True
            
        except Exception as e:
            print(f"Error exporting bills to CSV: {e}")
            return False
    
    def export_test_results_to_csv(self, filename: str, start_date: str = None, end_date: str = None) -> bool:
        """Export detailed test results to CSV"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Query for detailed test results
            query = '''
                SELECT br.report_id, br.test_date, 
                       p.first_name, p.last_name, p.phone_number,
                       tt.test_code, tt.test_name, tt.normal_range, tt.unit,
                       tr.result_value, tr.is_normal, tr.remarks
                FROM blood_reports br
                JOIN patients p ON br.patient_id = p.patient_id
                JOIN test_results tr ON br.report_id = tr.report_id
                JOIN test_types tt ON tr.test_type_id = tt.test_type_id
            '''
            
            params = []
            if start_date and end_date:
                query += ' WHERE br.test_date BETWEEN ? AND ?'
                params = [start_date, end_date]
            
            query += ' ORDER BY br.test_date, br.report_id, tt.test_name'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Report ID', 'Test Date', 'Patient Name', 'Phone Number',
                            'Test Code', 'Test Name', 'Result Value', 'Normal Range', 
                            'Unit', 'Status', 'Remarks']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in results:
                    status = "Normal" if result[10] == 1 else "Abnormal" if result[10] == 0 else "Pending"
                    
                    writer.writerow({
                        'Report ID': result[0],
                        'Test Date': result[1],
                        'Patient Name': f"{result[2]} {result[3]}",
                        'Phone Number': result[4],
                        'Test Code': result[5],
                        'Test Name': result[6],
                        'Result Value': result[9] or '',
                        'Normal Range': result[7] or '',
                        'Unit': result[8] or '',
                        'Status': status,
                        'Remarks': result[11] or ''
                    })
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error exporting test results to CSV: {e}")
            return False
    
    def export_to_excel(self, filename: str, start_date: str = None, end_date: str = None) -> bool:
        """Export all data to Excel with multiple sheets"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Export patients
                patients = self.db.search_patients("")
                patients_df = pd.DataFrame([{
                    'Patient ID': p['patient_id'],
                    'First Name': p['first_name'],
                    'Last Name': p['last_name'],
                    'Phone Number': p['phone_number'],
                    'Date of Birth': p.get('date_of_birth', ''),
                    'Gender': p.get('gender', ''),
                    'Address': p.get('address', ''),
                    'Created Date': p.get('created_at', '')
                } for p in patients])
                patients_df.to_excel(writer, sheet_name='Patients', index=False)
                
                # Export reports
                reports = self.db.get_blood_reports()
                if start_date and end_date:
                    reports = [r for r in reports if start_date <= r['test_date'] <= end_date]
                
                reports_df = pd.DataFrame([{
                    'Report ID': r['report_id'],
                    'Test Date': r['test_date'],
                    'Patient Name': f"{r['first_name']} {r['last_name']}",
                    'Phone Number': r['phone_number'],
                    'Doctor': r.get('doctor_name', ''),
                    'Lab Technician': r.get('lab_technician', ''),
                    'Status': r['status'],
                    'Notes': r.get('notes', '')
                } for r in reports])
                reports_df.to_excel(writer, sheet_name='Blood Reports', index=False)
                
                # Export bills
                bills = self.db.get_bills()
                if start_date and end_date:
                    bills = [b for b in bills if start_date <= b['bill_date'] <= end_date]
                
                bills_df = pd.DataFrame([{
                    'Bill ID': b['bill_id'],
                    'Bill Date': b['bill_date'],
                    'Patient Name': f"{b['first_name']} {b['last_name']}",
                    'Phone Number': b['phone_number'],
                    'Total Amount': b['total_amount'],
                    'Paid Amount': b['paid_amount'],
                    'Balance': b['total_amount'] - b['paid_amount'],
                    'Payment Status': b['payment_status'],
                    'Payment Method': b.get('payment_method', '')
                } for b in bills])
                bills_df.to_excel(writer, sheet_name='Bills', index=False)
                
                # Export test results
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                query = '''
                    SELECT br.report_id, br.test_date, 
                           p.first_name, p.last_name, p.phone_number,
                           tt.test_code, tt.test_name, tt.normal_range, tt.unit,
                           tr.result_value, tr.is_normal, tr.remarks
                    FROM blood_reports br
                    JOIN patients p ON br.patient_id = p.patient_id
                    JOIN test_results tr ON br.report_id = tr.report_id
                    JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                '''
                
                params = []
                if start_date and end_date:
                    query += ' WHERE br.test_date BETWEEN ? AND ?'
                    params = [start_date, end_date]
                
                query += ' ORDER BY br.test_date, br.report_id, tt.test_name'
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                test_results_data = []
                for result in results:
                    status = "Normal" if result[10] == 1 else "Abnormal" if result[10] == 0 else "Pending"
                    test_results_data.append({
                        'Report ID': result[0],
                        'Test Date': result[1],
                        'Patient Name': f"{result[2]} {result[3]}",
                        'Phone Number': result[4],
                        'Test Code': result[5],
                        'Test Name': result[6],
                        'Result Value': result[9] or '',
                        'Normal Range': result[7] or '',
                        'Unit': result[8] or '',
                        'Status': status,
                        'Remarks': result[11] or ''
                    })
                
                test_results_df = pd.DataFrame(test_results_data)
                test_results_df.to_excel(writer, sheet_name='Test Results', index=False)
                
                conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
    
    def create_backup_data(self, backup_dir: str) -> bool:
        """Create complete data backup in multiple formats"""
        try:
            # Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export to Excel
            excel_filename = os.path.join(backup_dir, f"lab_data_backup_{timestamp}.xlsx")
            excel_success = self.export_to_excel(excel_filename)
            
            # Export individual CSV files
            csv_dir = os.path.join(backup_dir, f"csv_backup_{timestamp}")
            os.makedirs(csv_dir, exist_ok=True)
            
            patients_csv = os.path.join(csv_dir, "patients.csv")
            reports_csv = os.path.join(csv_dir, "blood_reports.csv")
            bills_csv = os.path.join(csv_dir, "bills.csv")
            test_results_csv = os.path.join(csv_dir, "test_results.csv")
            
            csv_success = (
                self.export_patients_to_csv(patients_csv) and
                self.export_reports_to_csv(reports_csv) and
                self.export_bills_to_csv(bills_csv) and
                self.export_test_results_to_csv(test_results_csv)
            )
            
            return excel_success and csv_success
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

def create_export_directory():
    """Create export output directory if it doesn't exist"""
    export_dir = "data_exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    return export_dir

def generate_export_filename(prefix: str, extension: str = ".csv") -> str:
    """Generate filename for export"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{extension}" 