import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Tuple
import calendar

class LabAnalytics:
    def __init__(self, database):
        self.db = database
    
    def get_revenue_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get revenue summary for date range"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Default to current month if no dates provided
            if not start_date or not end_date:
                today = date.today()
                start_date = date(today.year, today.month, 1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            
            # Total revenue
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) as total_revenue,
                       COALESCE(SUM(paid_amount), 0) as collected_revenue,
                       COALESCE(SUM(total_amount - paid_amount), 0) as outstanding_amount,
                       COUNT(*) as total_bills
                FROM bills 
                WHERE bill_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            revenue_data = cursor.fetchone()
            
            # Payment status breakdown
            cursor.execute('''
                SELECT payment_status, COUNT(*) as count, SUM(total_amount) as amount
                FROM bills 
                WHERE bill_date BETWEEN ? AND ?
                GROUP BY payment_status
            ''', (start_date, end_date))
            
            payment_breakdown = {}
            for row in cursor.fetchall():
                payment_breakdown[row[0]] = {'count': row[1], 'amount': row[2]}
            
            return {
                'period': f"{start_date} to {end_date}",
                'total_revenue': revenue_data[0],
                'collected_revenue': revenue_data[1],
                'outstanding_amount': revenue_data[2],
                'total_bills': revenue_data[3],
                'collection_rate': (revenue_data[1] / revenue_data[0] * 100) if revenue_data[0] > 0 else 0,
                'payment_breakdown': payment_breakdown
            }
            
        finally:
            conn.close()
    
    def get_test_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get test volume and popularity statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Default to current month
            if not start_date or not end_date:
                today = date.today()
                start_date = date(today.year, today.month, 1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            
            # Total tests performed
            cursor.execute('''
                SELECT COUNT(*) as total_tests
                FROM test_results tr
                JOIN blood_reports br ON tr.report_id = br.report_id
                WHERE br.test_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            total_tests = cursor.fetchone()[0]
            
            # Most popular tests
            cursor.execute('''
                SELECT tt.test_name, tt.test_code, COUNT(*) as test_count,
                       SUM(tt.price) as revenue_generated
                FROM test_results tr
                JOIN blood_reports br ON tr.report_id = br.report_id
                JOIN test_types tt ON tr.test_type_id = tt.test_type_id
                WHERE br.test_date BETWEEN ? AND ?
                GROUP BY tt.test_type_id, tt.test_name, tt.test_code, tt.price
                ORDER BY test_count DESC
                LIMIT 10
            ''', (start_date, end_date))
            
            popular_tests = []
            for row in cursor.fetchall():
                popular_tests.append({
                    'test_name': row[0],
                    'test_code': row[1],
                    'count': row[2],
                    'revenue': row[3]
                })
            
            # Test abnormality rates
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN tr.is_normal = 1 THEN 1 ELSE 0 END) as normal_results,
                    SUM(CASE WHEN tr.is_normal = 0 THEN 1 ELSE 0 END) as abnormal_results,
                    SUM(CASE WHEN tr.is_normal IS NULL THEN 1 ELSE 0 END) as pending_results
                FROM test_results tr
                JOIN blood_reports br ON tr.report_id = br.report_id
                WHERE br.test_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            result_stats = cursor.fetchone()
            
            return {
                'period': f"{start_date} to {end_date}",
                'total_tests': total_tests,
                'popular_tests': popular_tests,
                'result_distribution': {
                    'normal': result_stats[0] or 0,
                    'abnormal': result_stats[1] or 0,
                    'pending': result_stats[2] or 0
                },
                'abnormality_rate': (result_stats[1] / total_tests * 100) if total_tests > 0 else 0
            }
            
        finally:
            conn.close()
    
    def get_patient_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get patient-related statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Default to current month
            if not start_date or not end_date:
                today = date.today()
                start_date = date(today.year, today.month, 1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            
            # New patients in period
            cursor.execute('''
                SELECT COUNT(*) FROM patients 
                WHERE DATE(created_at) BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            new_patients = cursor.fetchone()[0]
            
            # Total active patients (patients with reports in period)
            cursor.execute('''
                SELECT COUNT(DISTINCT patient_id) 
                FROM blood_reports 
                WHERE test_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            active_patients = cursor.fetchone()[0]
            
            # Patient gender distribution
            cursor.execute('''
                SELECT 
                    p.gender,
                    COUNT(*) as count
                FROM patients p
                WHERE EXISTS (
                    SELECT 1 FROM blood_reports br 
                    WHERE br.patient_id = p.patient_id 
                    AND br.test_date BETWEEN ? AND ?
                )
                GROUP BY p.gender
            ''', (start_date, end_date))
            
            gender_distribution = {}
            for row in cursor.fetchall():
                gender_distribution[row[0] or 'Unknown'] = row[1]
            
            # Repeat patients (more than one visit)
            cursor.execute('''
                SELECT COUNT(*) 
                FROM (
                    SELECT patient_id, COUNT(*) as visit_count
                    FROM blood_reports 
                    WHERE test_date BETWEEN ? AND ?
                    GROUP BY patient_id
                    HAVING visit_count > 1
                ) repeat_patients
            ''', (start_date, end_date))
            
            repeat_patients = cursor.fetchone()[0]
            
            return {
                'period': f"{start_date} to {end_date}",
                'new_patients': new_patients,
                'active_patients': active_patients,
                'repeat_patients': repeat_patients,
                'repeat_rate': (repeat_patients / active_patients * 100) if active_patients > 0 else 0,
                'gender_distribution': gender_distribution
            }
            
        finally:
            conn.close()
    
    def get_daily_revenue_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily revenue trend for specified number of days"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            cursor.execute('''
                SELECT 
                    bill_date,
                    COALESCE(SUM(total_amount), 0) as daily_revenue,
                    COALESCE(SUM(paid_amount), 0) as daily_collection,
                    COUNT(*) as bills_count
                FROM bills 
                WHERE bill_date BETWEEN ? AND ?
                GROUP BY bill_date
                ORDER BY bill_date
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            revenue_data = []
            for row in cursor.fetchall():
                revenue_data.append({
                    'date': row[0],
                    'revenue': row[1],
                    'collection': row[2],
                    'bills': row[3]
                })
            
            return revenue_data
            
        finally:
            conn.close()
    
    def get_monthly_comparison(self, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly comparison data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            monthly_data = []
            
            for i in range(months):
                # Calculate month start and end dates
                today = date.today()
                month_date = today.replace(day=1) - timedelta(days=i*30)
                month_start = month_date.replace(day=1)
                
                # Get last day of month
                last_day = calendar.monthrange(month_start.year, month_start.month)[1]
                month_end = month_start.replace(day=last_day)
                
                cursor.execute('''
                    SELECT 
                        COALESCE(SUM(b.total_amount), 0) as revenue,
                        COALESCE(SUM(b.paid_amount), 0) as collection,
                        COUNT(DISTINCT b.bill_id) as bills,
                        COUNT(DISTINCT br.report_id) as reports,
                        COUNT(DISTINCT b.patient_id) as patients
                    FROM bills b
                    LEFT JOIN blood_reports br ON b.report_id = br.report_id
                    WHERE b.bill_date BETWEEN ? AND ?
                ''', (month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
                
                result = cursor.fetchone()
                
                monthly_data.append({
                    'month': month_start.strftime('%Y-%m'),
                    'month_name': month_start.strftime('%B %Y'),
                    'revenue': result[0],
                    'collection': result[1],
                    'bills': result[2],
                    'reports': result[3],
                    'patients': result[4]
                })
            
            return list(reversed(monthly_data))  # Most recent first
            
        finally:
            conn.close()
    
    def get_outstanding_analysis(self) -> Dict[str, Any]:
        """Get analysis of outstanding payments"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Outstanding by age
            today = date.today()
            
            aging_buckets = [
                ('0-30 days', 30),
                ('31-60 days', 60),
                ('61-90 days', 90),
                ('90+ days', float('inf'))
            ]
            
            aging_analysis = []
            
            for bucket_name, days in aging_buckets:
                if days == float('inf'):
                    # More than 90 days
                    cutoff_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
                    cursor.execute('''
                        SELECT COUNT(*), COALESCE(SUM(total_amount - paid_amount), 0)
                        FROM bills 
                        WHERE payment_status != 'paid' 
                        AND bill_date < ?
                    ''', (cutoff_date,))
                else:
                    # Within range
                    start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
                    end_date = today.strftime('%Y-%m-%d') if days == 30 else (today - timedelta(days=days-30)).strftime('%Y-%m-%d')
                    
                    cursor.execute('''
                        SELECT COUNT(*), COALESCE(SUM(total_amount - paid_amount), 0)
                        FROM bills 
                        WHERE payment_status != 'paid' 
                        AND bill_date BETWEEN ? AND ?
                    ''', (start_date, end_date))
                
                result = cursor.fetchone()
                aging_analysis.append({
                    'period': bucket_name,
                    'count': result[0],
                    'amount': result[1]
                })
            
            # Top outstanding patients
            cursor.execute('''
                SELECT 
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.phone_number,
                    COALESCE(SUM(b.total_amount - b.paid_amount), 0) as outstanding_amount,
                    COUNT(*) as unpaid_bills
                FROM bills b
                JOIN patients p ON b.patient_id = p.patient_id
                WHERE b.payment_status != 'paid'
                GROUP BY b.patient_id, p.first_name, p.last_name, p.phone_number
                HAVING outstanding_amount > 0
                ORDER BY outstanding_amount DESC
                LIMIT 10
            ''')
            
            top_outstanding = []
            for row in cursor.fetchall():
                top_outstanding.append({
                    'patient_name': row[0],
                    'phone': row[1],
                    'amount': row[2],
                    'bills': row[3]
                })
            
            return {
                'aging_analysis': aging_analysis,
                'top_outstanding': top_outstanding
            }
            
        finally:
            conn.close()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get key performance indicators"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            today = date.today()
            current_month_start = today.replace(day=1).strftime('%Y-%m-%d')
            last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
            last_month_end = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Current month metrics
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT b.bill_id) as bills,
                    COUNT(DISTINCT br.report_id) as reports,
                    COUNT(DISTINCT b.patient_id) as patients,
                    COALESCE(SUM(b.total_amount), 0) as revenue
                FROM bills b
                LEFT JOIN blood_reports br ON b.report_id = br.report_id
                WHERE b.bill_date >= ?
            ''', (current_month_start,))
            
            current_metrics = cursor.fetchone()
            
            # Last month metrics for comparison
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT b.bill_id) as bills,
                    COUNT(DISTINCT br.report_id) as reports,
                    COUNT(DISTINCT b.patient_id) as patients,
                    COALESCE(SUM(b.total_amount), 0) as revenue
                FROM bills b
                LEFT JOIN blood_reports br ON b.report_id = br.report_id
                WHERE b.bill_date BETWEEN ? AND ?
            ''', (last_month_start, last_month_end))
            
            last_metrics = cursor.fetchone()
            
            # Calculate growth rates
            def calculate_growth(current, previous):
                if previous == 0:
                    return 100 if current > 0 else 0
                return ((current - previous) / previous) * 100
            
            return {
                'current_month': {
                    'bills': current_metrics[0],
                    'reports': current_metrics[1],
                    'patients': current_metrics[2],
                    'revenue': current_metrics[3]
                },
                'last_month': {
                    'bills': last_metrics[0],
                    'reports': last_metrics[1],
                    'patients': last_metrics[2],
                    'revenue': last_metrics[3]
                },
                'growth_rates': {
                    'bills': calculate_growth(current_metrics[0], last_metrics[0]),
                    'reports': calculate_growth(current_metrics[1], last_metrics[1]),
                    'patients': calculate_growth(current_metrics[2], last_metrics[2]),
                    'revenue': calculate_growth(current_metrics[3], last_metrics[3])
                }
            }
            
        finally:
            conn.close() 