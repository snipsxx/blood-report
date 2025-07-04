from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
import os
import json
from datetime import datetime, date
import io
from werkzeug.utils import secure_filename

from database import LabDatabase
from utils.pdf_generator import PDFGenerator
from utils.analytics import AnalyticsEngine
from utils.data_export import DataExporter

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize database
db = LabDatabase()

# Custom JSON encoder to handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

# Patient Management Routes
@app.route('/patients')
def patients():
    """Patient management page"""
    return render_template('patients.html')

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients with optional search"""
    search_term = request.args.get('search', '')
    try:
        patients = db.search_patients(search_term)
        return jsonify({'success': True, 'data': patients})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
def add_patient():
    """Add new patient"""
    try:
        data = request.get_json()
        patient_id = db.add_patient(data)
        return jsonify({'success': True, 'patient_id': patient_id})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>')
def get_patient(patient_id):
    """Get patient by ID"""
    try:
        patient = db.get_patient_by_id(patient_id)
        if patient:
            return jsonify({'success': True, 'data': patient})
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Test Management Routes
@app.route('/tests')
def tests():
    """Test management page"""
    return render_template('tests.html')

@app.route('/api/tests', methods=['GET'])
def get_tests():
    """Get all test types"""
    try:
        tests = db.get_all_test_types()
        return jsonify({'success': True, 'data': tests})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tests', methods=['POST'])
def add_test():
    """Add new test type"""
    try:
        data = request.get_json()
        test_id = db.add_test_type(data)
        return jsonify({'success': True, 'test_id': test_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Blood Reports Routes
@app.route('/reports')
def reports():
    """Blood reports page"""
    return render_template('reports.html')

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get blood reports with optional patient filter"""
    patient_id = request.args.get('patient_id', type=int)
    try:
        reports = db.get_blood_reports(patient_id)
        return jsonify({'success': True, 'data': reports})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports', methods=['POST'])
def create_report():
    """Create new blood report"""
    try:
        data = request.get_json()
        report_id = db.create_blood_report(data)
        
        # Add test results if provided
        if 'test_results' in data:
            for result in data['test_results']:
                result['report_id'] = report_id
                db.add_test_result(result)
        
        return jsonify({'success': True, 'report_id': report_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/<int:report_id>')
def get_report_details(report_id):
    """Get detailed report information"""
    try:
        report = db.get_complete_report_details(report_id)
        return jsonify({'success': True, 'data': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/<int:report_id>/results', methods=['POST'])
def add_test_results(report_id):
    """Add test results to a report"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        for result in results:
            result['report_id'] = report_id
            db.add_test_result(result)
        
        # Update report status to completed
        db.update_report_status(report_id, 'completed')
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Billing Routes
@app.route('/billing')
def billing():
    """Billing management page"""
    return render_template('billing.html')

@app.route('/api/bills', methods=['GET'])
def get_bills():
    """Get bills with optional filters"""
    patient_id = request.args.get('patient_id', type=int)
    status = request.args.get('status')
    try:
        bills = db.get_bills(patient_id)
        if status and status != 'all':
            bills = [bill for bill in bills if bill['payment_status'] == status]
        return jsonify({'success': True, 'data': bills})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bills', methods=['POST'])
def create_bill():
    """Create new bill"""
    try:
        data = request.get_json()
        if 'report_id' in data:
            # Create bill from report
            bill_id = db.create_bill_from_report(data['report_id'])
        else:
            # Create manual bill
            bill_id = db.create_bill(data)
        return jsonify({'success': True, 'bill_id': bill_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bills/<int:bill_id>')
def get_bill_details(bill_id):
    """Get detailed bill information"""
    try:
        bill = db.get_complete_bill_details(bill_id)
        return jsonify({'success': True, 'data': bill})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bills/<int:bill_id>/payment', methods=['POST'])
def record_payment(bill_id):
    """Record payment for a bill"""
    try:
        data = request.get_json()
        db.update_payment(bill_id, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Analytics Routes
@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    return render_template('analytics.html')

@app.route('/api/analytics/overview')
def analytics_overview():
    """Get analytics overview data"""
    try:
        analytics = AnalyticsEngine(db)
        data = {
            'revenue_summary': analytics.get_revenue_summary(),
            'patient_stats': analytics.get_patient_statistics(),
            'test_stats': analytics.get_test_statistics()
        }
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/revenue')
def analytics_revenue():
    """Get revenue analytics data"""
    try:
        analytics = AnalyticsEngine(db)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        data = {
            'daily_revenue': analytics.get_daily_revenue_trend(start_date, end_date),
            'payment_methods': analytics.get_payment_method_distribution(),
            'collection_rate': analytics.get_collection_vs_revenue()
        }
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/tests')
def analytics_tests():
    """Get test analytics data"""
    try:
        analytics = AnalyticsEngine(db)
        data = {
            'popular_tests': analytics.get_popular_tests(),
            'test_results_distribution': analytics.get_test_results_distribution(),
            'abnormality_rates': analytics.get_abnormality_rates()
        }
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# PDF Generation Routes
@app.route('/api/reports/<int:report_id>/pdf')
def download_report_pdf(report_id):
    """Download PDF report"""
    try:
        report_data = db.get_complete_report_details(report_id)
        if not report_data:
            return jsonify({'error': 'Report not found'}), 404
        
        pdf_generator = PDFGenerator()
        pdf_buffer = pdf_generator.generate_blood_report(report_data)
        
        filename = f"blood_report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<int:bill_id>/pdf')
def download_bill_pdf(bill_id):
    """Download PDF bill"""
    try:
        bill_data = db.get_complete_bill_details(bill_id)
        if not bill_data:
            return jsonify({'error': 'Bill not found'}), 404
        
        pdf_generator = PDFGenerator()
        pdf_buffer = pdf_generator.generate_bill(bill_data)
        
        filename = f"bill_{bill_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Data Export Routes
@app.route('/api/export/excel')
def export_excel():
    """Export data to Excel"""
    try:
        export_type = request.args.get('type', 'all')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        exporter = DataExporter(db)
        excel_buffer = exporter.export_to_excel(export_type, start_date, end_date)
        
        filename = f"lab_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('generated_pdfs', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 