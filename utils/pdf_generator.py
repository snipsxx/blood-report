from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E4057')
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2E4057')
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.black
        )
        
        # Body style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        )

    def generate_blood_report_pdf(self, report_details, filename):
        """Generate PDF for blood report"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch)
            story = []
            
            # Header with lab info
            self.add_lab_header(story)
            
            # Report title
            story.append(Paragraph("BLOOD TEST REPORT", self.title_style))
            story.append(Spacer(1, 20))
            
            # Report information
            report_info = [
                ['Report ID:', str(report_details['report_id'])],
                ['Report Date:', report_details['test_date']],
                ['Status:', report_details['status'].upper()],
                ['Generated On:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            report_table = Table(report_info, colWidths=[2*inch, 3*inch])
            report_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(report_table)
            story.append(Spacer(1, 20))
            
            # Patient information
            story.append(Paragraph("PATIENT INFORMATION", self.subtitle_style))
            
            patient_info = [
                ['Name:', f"{report_details['first_name']} {report_details['last_name']}"],
                ['Phone:', report_details['phone_number']],
                ['Date of Birth:', report_details.get('date_of_birth', 'N/A')],
                ['Gender:', report_details.get('gender', 'N/A')]
            ]
            
            patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 20))
            
            # Medical information
            story.append(Paragraph("MEDICAL INFORMATION", self.subtitle_style))
            
            medical_info = [
                ['Doctor:', report_details.get('doctor_name', 'N/A')],
                ['Lab Technician:', report_details.get('lab_technician', 'N/A')],
                ['Notes:', report_details.get('notes', 'N/A')]
            ]
            
            medical_table = Table(medical_info, colWidths=[2*inch, 4*inch])
            medical_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(medical_table)
            story.append(Spacer(1, 30))
            
            # Test results
            story.append(Paragraph("TEST RESULTS", self.subtitle_style))
            
            # Test results table
            test_data = [['Test Name', 'Result', 'Normal Range', 'Status', 'Remarks']]
            
            for test_result in report_details.get('test_results', []):
                status = "NORMAL" if test_result.get('is_normal') else "ABNORMAL" if test_result.get('is_normal') is False else "PENDING"
                test_data.append([
                    f"{test_result['test_name']}\n({test_result['test_code']})",
                    f"{test_result.get('result_value', 'PENDING')} {test_result.get('unit', '')}".strip(),
                    f"{test_result.get('normal_range', 'N/A')} {test_result.get('unit', '')}".strip(),
                    status,
                    test_result.get('remarks', 'None')
                ])
            
            test_table = Table(test_data, colWidths=[2.2*inch, 1.5*inch, 1.5*inch, 1*inch, 1.3*inch])
            test_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            # Color code abnormal results
            for i, test_result in enumerate(report_details.get('test_results', []), 1):
                if test_result.get('is_normal') is False:
                    test_table.setStyle(TableStyle([
                        ('BACKGROUND', (3, i), (3, i), colors.HexColor('#FFE6E6')),
                        ('TEXTCOLOR', (3, i), (3, i), colors.red),
                        ('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'),
                    ]))
            
            story.append(test_table)
            story.append(Spacer(1, 30))
            
            # Footer
            self.add_report_footer(story)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

    def generate_bill_pdf(self, bill_details, filename):
        """Generate PDF for bill"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch)
            story = []
            
            # Header with lab info
            self.add_lab_header(story)
            
            # Bill title
            story.append(Paragraph("LABORATORY BILL", self.title_style))
            story.append(Spacer(1, 20))
            
            # Bill information
            bill_info = [
                ['Bill ID:', str(bill_details['bill_id'])],
                ['Bill Date:', bill_details['bill_date']],
                ['Payment Status:', bill_details['payment_status'].upper()],
                ['Generated On:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            bill_table = Table(bill_info, colWidths=[2*inch, 3*inch])
            bill_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(bill_table)
            story.append(Spacer(1, 20))
            
            # Patient information
            story.append(Paragraph("BILL TO", self.subtitle_style))
            
            patient_info = [
                ['Name:', f"{bill_details['first_name']} {bill_details['last_name']}"],
                ['Phone:', bill_details['phone_number']],
                ['Address:', bill_details.get('address', 'N/A')]
            ]
            
            patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 30))
            
            # Bill items
            story.append(Paragraph("SERVICES", self.subtitle_style))
            
            # Items table
            items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
            subtotal = 0
            
            for item in bill_details.get('items', []):
                items_data.append([
                    f"{item['test_name']}\n({item['test_code']})",
                    str(item['quantity']),
                    f"₹{item['unit_price']:.2f}",
                    f"₹{item['total_price']:.2f}"
                ])
                subtotal += item['total_price']
            
            items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 20))
            
            # Summary
            summary_data = [
                ['Subtotal:', f"₹{subtotal:.2f}"],
                ['Tax (18% GST):', f"₹{bill_details.get('tax_amount', 0):.2f}"],
                ['Discount:', f"₹{bill_details.get('discount', 0):.2f}"]
            ]
            
            # Add total with bold styling
            summary_data.append(['TOTAL AMOUNT:', f"₹{bill_details['total_amount']:.2f}"])
            summary_data.append(['PAID AMOUNT:', f"₹{bill_details['paid_amount']:.2f}"])
            
            balance = bill_details['total_amount'] - bill_details['paid_amount']
            summary_data.append(['BALANCE DUE:', f"₹{balance:.2f}"])
            
            summary_table = Table(summary_data, colWidths=[4*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0F0F0') if balance > 0 else colors.HexColor('#E6FFE6')),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Payment method
            if bill_details.get('payment_method'):
                story.append(Paragraph(f"Payment Method: {bill_details['payment_method']}", self.body_style))
                story.append(Spacer(1, 10))
            
            # Footer
            self.add_bill_footer(story)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating bill PDF: {e}")
            return False

    def generate_analytics_report_pdf(self, analytics_data, filename):
        """Generate comprehensive analytics PDF report"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch)
            story = []
            
            # Header with lab info
            self.add_lab_header(story)
            
            # Report title
            story.append(Paragraph("LABORATORY ANALYTICS REPORT", self.title_style))
            story.append(Spacer(1, 20))
            
            # Report period
            story.append(Paragraph(f"Report Period: {analytics_data['report_period']}", self.subtitle_style))
            story.append(Spacer(1, 20))
            
            # Revenue Summary
            story.append(Paragraph("REVENUE SUMMARY", self.subtitle_style))
            
            revenue_data = analytics_data['revenue']
            revenue_summary = [
                ['Metric', 'Amount'],
                ['Total Revenue', f"₹{revenue_data['total_revenue']:,.2f}"],
                ['Collected Revenue', f"₹{revenue_data['collected_revenue']:,.2f}"],
                ['Outstanding Amount', f"₹{revenue_data['outstanding_amount']:,.2f}"],
                ['Collection Rate', f"{revenue_data['collection_rate']:.1f}%"],
                ['Total Bills', str(revenue_data['total_bills'])]
            ]
            
            revenue_table = Table(revenue_summary, colWidths=[3*inch, 2*inch])
            revenue_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(revenue_table)
            story.append(Spacer(1, 20))
            
            # Test Statistics
            story.append(Paragraph("TEST STATISTICS", self.subtitle_style))
            
            test_data = analytics_data['tests']
            test_summary = [
                ['Metric', 'Value'],
                ['Total Tests Performed', str(test_data['total_tests'])],
                ['Normal Results', str(test_data['result_distribution']['normal'])],
                ['Abnormal Results', str(test_data['result_distribution']['abnormal'])],
                ['Pending Results', str(test_data['result_distribution']['pending'])],
                ['Abnormality Rate', f"{test_data['abnormality_rate']:.1f}%"]
            ]
            
            test_table = Table(test_summary, colWidths=[3*inch, 2*inch])
            test_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(test_table)
            story.append(Spacer(1, 20))
            
            # Popular Tests
            story.append(Paragraph("MOST POPULAR TESTS", self.subtitle_style))
            
            popular_tests_data = [['Test Name', 'Test Code', 'Count', 'Revenue']]
            for test in test_data.get('popular_tests', [])[:10]:  # Top 10
                popular_tests_data.append([
                    test['test_name'],
                    test['test_code'],
                    str(test['count']),
                    f"₹{test['revenue']:,.2f}"
                ])
            
            if len(popular_tests_data) > 1:
                popular_table = Table(popular_tests_data, colWidths=[2*inch, 1*inch, 1*inch, 1.5*inch])
                popular_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                
                story.append(popular_table)
            else:
                story.append(Paragraph("No test data available for this period.", self.body_style))
            
            story.append(Spacer(1, 20))
            
            # Patient Statistics
            story.append(Paragraph("PATIENT STATISTICS", self.subtitle_style))
            
            patient_data = analytics_data['patients']
            patient_summary = [
                ['Metric', 'Count'],
                ['New Patients', str(patient_data['new_patients'])],
                ['Active Patients', str(patient_data['active_patients'])],
                ['Repeat Patients', str(patient_data['repeat_patients'])],
                ['Repeat Rate', f"{patient_data['repeat_rate']:.1f}%"]
            ]
            
            patient_table = Table(patient_summary, colWidths=[3*inch, 2*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 20))
            
            # Performance Metrics
            story.append(Paragraph("PERFORMANCE COMPARISON", self.subtitle_style))
            
            performance = analytics_data['performance']
            performance_data = [
                ['Metric', 'Current Month', 'Last Month', 'Growth %'],
                ['Revenue', f"₹{performance['current_month']['revenue']:,.2f}", 
                 f"₹{performance['last_month']['revenue']:,.2f}", 
                 f"{performance['growth_rates']['revenue']:.1f}%"],
                ['Bills', str(performance['current_month']['bills']), 
                 str(performance['last_month']['bills']), 
                 f"{performance['growth_rates']['bills']:.1f}%"],
                ['Reports', str(performance['current_month']['reports']), 
                 str(performance['last_month']['reports']), 
                 f"{performance['growth_rates']['reports']:.1f}%"],
                ['Patients', str(performance['current_month']['patients']), 
                 str(performance['last_month']['patients']), 
                 f"{performance['growth_rates']['patients']:.1f}%"]
            ]
            
            performance_table = Table(performance_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
            performance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            # Color code growth rates
            for i in range(1, len(performance_data)):
                growth_rate = performance['growth_rates'][list(performance['growth_rates'].keys())[i-1]]
                color = colors.HexColor('#E6FFE6') if growth_rate >= 0 else colors.HexColor('#FFE6E6')
                performance_table.setStyle(TableStyle([
                    ('BACKGROUND', (3, i), (3, i), color),
                ]))
            
            story.append(performance_table)
            story.append(Spacer(1, 30))
            
            # Footer
            story.append(Paragraph("This report was generated automatically by the Laboratory Management System.", 
                                 self.body_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                 self.body_style))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating analytics PDF: {e}")
            return False

    def add_lab_header(self, story):
        """Add laboratory header to PDF"""
        # Lab name and info
        lab_info = [
            ["ADVANCED MEDICAL LABORATORY", ""],
            ["123 Medical Center Drive", "Phone: +91 98765 43210"],
            ["City, State 123456", "Email: info@advancedlab.com"],
            ["", "License: LAB/2024/001"]
        ]
        
        header_table = Table(lab_info, colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#2E4057')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 30))

    def add_report_footer(self, story):
        """Add footer to blood report"""
        story.append(Spacer(1, 30))
        
        footer_text = [
            "This report is computer generated and does not require signature.",
            "For any queries, please contact the laboratory.",
            "Keep this report safe for future reference."
        ]
        
        for text in footer_text:
            story.append(Paragraph(text, self.body_style))
        
        # Signature lines
        story.append(Spacer(1, 40))
        signature_data = [
            ["_____________________", "_____________________"],
            ["Lab Technician", "Doctor"],
            ["Date: _______________", "Date: _______________"]
        ]
        
        signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(signature_table)

    def add_bill_footer(self, story):
        """Add footer to bill"""
        story.append(Spacer(1, 30))
        
        footer_text = [
            "Thank you for choosing our laboratory services.",
            "Please retain this bill for your records.",
            "For any billing queries, contact our billing department."
        ]
        
        for text in footer_text:
            story.append(Paragraph(text, self.body_style))
        
        # Terms and conditions
        story.append(Spacer(1, 20))
        terms_title = Paragraph("TERMS & CONDITIONS", self.subtitle_style)
        story.append(terms_title)
        
        terms = [
            "1. Payment is due within 30 days of bill date.",
            "2. Late payment charges may apply after due date.",
            "3. All reports are confidential and property of the patient.",
            "4. Laboratory reserves the right to charge for duplicate reports."
        ]
        
        for term in terms:
            story.append(Paragraph(term, self.body_style))

def create_pdf_directory():
    """Create PDF output directory if it doesn't exist"""
    pdf_dir = "generated_pdfs"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    return pdf_dir

def generate_filename(prefix, id_number, extension=".pdf"):
    """Generate filename for PDF"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{id_number}_{timestamp}{extension}" 