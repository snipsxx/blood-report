# Laboratory Management System - Flask Web Application

A comprehensive web-based laboratory management system for blood testing, patient management, billing, and analytics.

## 🚀 Features

### 🏥 Core Functionality
- **Patient Management**: Register, search, and manage patient information
- **Test Management**: Define blood test types with pricing and normal ranges
- **Blood Reports**: Create, manage, and track test reports with results
- **Billing System**: Generate bills, track payments, and manage revenue
- **Analytics Dashboard**: Comprehensive reporting and data visualization
- **PDF Generation**: Professional reports and bills with download capability
- **Data Export**: Excel and CSV export functionality

### 🎨 Modern Web Interface
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Professional UI**: Medical-themed design with modern aesthetics
- **Interactive Charts**: Real-time data visualization with Chart.js
- **Intuitive Navigation**: Easy-to-use interface with clear workflow
- **Real-time Updates**: AJAX-powered interactions for smooth user experience

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd blood-report
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
The database will be automatically created when you first run the application.

### 5. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 🌐 Application Structure

```
blood-report/
├── app.py                      # Main Flask application
├── database.py                 # Database operations and models
├── requirements.txt            # Python dependencies
├── README_FLASK.md            # This documentation
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── dashboard.html         # Main dashboard
│   ├── patients.html          # Patient management
│   ├── tests.html             # Test type management
│   ├── reports.html           # Blood reports
│   ├── billing.html           # Billing management
│   ├── analytics.html         # Analytics dashboard
│   ├── 404.html               # Error pages
│   └── 500.html
├── static/                     # Static files
│   ├── css/
│   │   └── main.css           # Custom styles
│   └── js/
│       ├── main.js            # Common utilities
│       ├── dashboard.js       # Dashboard functionality
│       ├── patients.js        # Patient management
│       ├── tests.js           # Test management
│       ├── reports.js         # Report management
│       ├── billing.js         # Billing functionality
│       └── analytics.js       # Analytics charts
├── utils/                      # Utility modules
│   ├── pdf_generator.py       # PDF generation
│   ├── analytics.py           # Analytics engine
│   └── data_export.py         # Data export functionality
└── lab_database.db            # SQLite database (created automatically)
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production configuration:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///lab_database.db
```

### Security Settings
For production deployment:
1. Change the `SECRET_KEY` in `app.py`
2. Set `debug=False` 
3. Configure proper HTTPS
4. Set up database backups

## 📊 Database Schema

### Main Tables
- **patients**: Patient information and demographics
- **test_types**: Blood test definitions with pricing
- **blood_reports**: Test reports and status tracking
- **test_results**: Individual test results and values
- **bills**: Billing information and payment tracking
- **bill_items**: Detailed bill line items

### Key Relationships
- Patients → Blood Reports (One-to-Many)
- Blood Reports → Test Results (One-to-Many)
- Test Types → Test Results (One-to-Many)
- Blood Reports → Bills (One-to-One)
- Bills → Bill Items (One-to-Many)

## 🎯 Usage Guide

### 1. Patient Management
1. Navigate to **Patients** page
2. Click **Add New Patient** to register patients
3. Use search and filters to find patients
4. View patient details and create reports

### 2. Test Management
1. Go to **Tests** page
2. Add new test types with pricing
3. Define normal ranges and units
4. Manage test catalog

### 3. Blood Reports
1. Visit **Reports** page
2. Create new reports by selecting patients
3. Add test types to reports
4. Enter test results and mark as normal/abnormal
5. Generate and download PDF reports

### 4. Billing
1. Access **Billing** page
2. Generate bills from completed reports
3. Track payment status
4. Record payments with different methods
5. Download bill PDFs

### 5. Analytics
1. Open **Analytics** dashboard
2. View revenue trends and statistics
3. Analyze test popularity and results
4. Monitor outstanding payments
5. Export data for external analysis

## 🔒 Security Features

- **CSRF Protection**: Prevents cross-site request forgery
- **Input Validation**: Server-side validation for all forms
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Template auto-escaping
- **File Upload Security**: Restricted file types and sizes

## 🚀 Production Deployment

### Using Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/your/app/static;
        expires 30d;
    }
}
```

## 📱 API Endpoints

### Patient Management
- `GET /api/patients` - List all patients
- `POST /api/patients` - Create new patient
- `GET /api/patients/<id>` - Get patient details
- `PUT /api/patients/<id>` - Update patient

### Test Management
- `GET /api/tests` - List all test types
- `POST /api/tests` - Create new test type
- `GET /api/tests/<id>` - Get test details

### Reports
- `GET /api/reports` - List all reports
- `POST /api/reports` - Create new report
- `GET /api/reports/<id>` - Get report details
- `GET /api/reports/<id>/pdf` - Download report PDF

### Billing
- `GET /api/bills` - List all bills
- `POST /api/bills` - Create new bill
- `GET /api/bills/<id>` - Get bill details
- `POST /api/bills/<id>/payment` - Record payment
- `GET /api/bills/<id>/pdf` - Download bill PDF

### Analytics
- `GET /api/analytics/overview` - Dashboard overview
- `GET /api/analytics/revenue` - Revenue analytics
- `GET /api/analytics/tests` - Test analytics

## 🔧 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check if database file exists and has proper permissions
ls -la lab_database.db
```

**Port Already in Use**
```bash
# Change port in app.py or kill existing process
lsof -ti:5000 | xargs kill -9
```

**Module Import Errors**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

**Template Not Found**
```bash
# Check if templates directory exists
ls -la templates/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the code documentation

## 🔄 Version History

### v2.0.0 - Flask Web Application
- Complete web-based interface
- Modern responsive design
- Real-time analytics dashboard
- PDF generation and downloads
- Advanced search and filtering
- Professional medical theme

### v1.0.0 - Desktop Application
- Basic Tkinter desktop interface
- Core functionality implemented
- SQLite database integration

---

**Built with ❤️ for healthcare professionals** 