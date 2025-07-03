# Laboratory Billing System

A comprehensive desktop application for managing laboratory operations including patient management, blood test types, billing, and report generation.

## Features

### Phase 1 ✅ COMPLETED

### ✅ Patient Management
- **Patient Registration**: Add new patients with complete details
- **Patient Search**: Search by name or phone number with real-time filtering
- **Patient List**: View all registered patients in an organized table
- **Validation**: Form validation with proper error handling
- **Phone Number Uniqueness**: Prevents duplicate phone numbers

### ✅ Test Type Management
- **Add Test Types**: Create new blood test types with pricing
- **Test Catalog**: View all available tests with prices and normal ranges
- **Price Management**: Set individual prices for each test
- **Test Codes**: Unique test codes for easy identification

### ✅ Database System
- **SQLite Database**: Local database with complete schema
- **Data Integrity**: Foreign key relationships and constraints
- **Default Data**: Pre-loaded with common blood tests

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Windows 10/11 (tested)

### Installation Steps

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

## Database Schema

The system uses SQLite with the following main tables:

- **patients**: Patient information with unique phone numbers
- **test_types**: Available blood tests with pricing
- **blood_reports**: Test reports and results
- **bills**: Billing information and payment tracking
- **test_results**: Individual test results linked to reports
- **bill_items**: Detailed bill line items

## Usage Guide

### Adding a New Patient

1. Go to the **Patient Management** tab
2. Fill in the **Patient Registration** form:
   - **Required fields**: First Name, Last Name, Phone Number
   - **Optional fields**: Email, Date of Birth, Gender, Address, Emergency Contact
3. Click **Register Patient**
4. The patient will appear in the patient list

### Creating Blood Reports

1. Go to the **Blood Reports** tab → **Create New Report**
2. Select patient from dropdown
3. Set test date and optional doctor/technician names
4. In **Select Tests** section, double-click tests to add them
5. Click **Create Report** to generate the report
6. Enter test results in the **Enter Test Results** section
7. Set result values and normal/abnormal status
8. Click **Save Results** to complete the report

### Managing Bills

1. Go to the **Billing** tab → **View Bills**
2. Generate bills automatically from reports using **Generate Bill** button
3. View detailed bill information with **View Details**
4. Record payments using **Record Payment** button
5. Filter bills by payment status (All, Unpaid, Partial, Paid)
6. Search bills by patient name, phone, or bill ID

### Recording Payments

1. Go to **Billing** tab → **Record Payment**
2. Enter Bill ID and click **Load Bill**
3. Enter payment amount (auto-filled with balance)
4. Select payment method (Cash, Card, UPI, etc.)
5. Click **Record Payment** to save

### Managing Test Types

1. Go to the **Test Management** tab
2. In the **Add New Test Type** section:
   - Enter test name (e.g., "Complete Blood Count")
   - Enter unique test code (e.g., "CBC")
   - Set price in rupees
   - Add normal range and units (optional)
   - Add description (optional)
3. Click **Add Test Type**
4. The test will appear in the available tests list

## File Structure

```
bloodreport/
├── main.py                 # Application entry point
├── database.py             # Database operations and models
├── requirements.txt        # Python dependencies
├── lab_database.db        # SQLite database (created automatically)
├── gui/
│   ├── __init__.py
│   ├── main_window.py     # Main application window with tabs
│   ├── patient_forms_2.py # Patient registration and search
│   ├── test_management.py # Test type management
│   ├── blood_reports.py   # Blood report creation and management
│   └── billing.py         # Billing and payment management
└── README.md              # This documentation
```

## Default Test Types

The application comes pre-loaded with common blood tests:

- **CBC** (Complete Blood Count) - ₹500.00
- **BSF** (Blood Sugar Fasting) - ₹200.00
- **BSR** (Blood Sugar Random) - ₹150.00
- **HGB** (Hemoglobin) - ₹300.00
- **CHOL** (Cholesterol Total) - ₹400.00
- **LFT** (Liver Function Test) - ₹800.00
- **KFT** (Kidney Function Test) - ₹700.00

## System Workflow

### Complete Patient Journey

1. **Patient Registration**: Add patient details in Patient Management
2. **Report Creation**: Create blood report and select required tests
3. **Result Entry**: Lab technician enters test results and marks normal/abnormal
4. **Bill Generation**: Automatically generate bill from completed report
5. **Payment Processing**: Record patient payments and track balances
6. **Report Viewing**: View detailed reports and bill history

### Key Features Highlights

- **Patient Phone Uniqueness**: Prevents duplicate patients using phone numbers
- **Automatic Tax Calculation**: 18% GST automatically calculated on bills
- **Real-time Search**: Instant search and filtering across all modules
- **Data Integrity**: Foreign key relationships ensure data consistency
- **Status Tracking**: Track report and payment statuses in real-time
- **Professional Interface**: Clean, modern GUI with intuitive navigation

### Phase 2 ✅ COMPLETED

### ✅ Blood Report Management
- **Create Reports**: Select patients and tests for new blood reports
- **Test Selection**: Choose from available test types with pricing
- **Result Entry**: Enter test results with normal/abnormal indicators
- **Report Viewing**: Detailed report viewer with patient and test information
- **Status Tracking**: Track report status (pending, completed, reviewed)
- **Search Reports**: Find reports by patient name, phone, or report ID

### ✅ Advanced Billing System
- **Automatic Bill Generation**: Generate bills directly from blood reports
- **Bill Management**: View and search all bills with filtering options
- **Payment Tracking**: Record payments with multiple payment methods
- **Payment Status**: Track unpaid, partial, and fully paid bills
- **Bill Details**: Detailed bill viewer with itemized test costs
- **GST Calculation**: Automatic 18% tax calculation
- **Balance Tracking**: Real-time balance calculations

### ✅ Enhanced Database Operations
- **Blood Reports Storage**: Complete report and result data management
- **Billing Integration**: Seamless integration between reports and bills
- **Payment History**: Full payment tracking and history
- **Data Relationships**: Proper foreign key relationships and data integrity

## Upcoming Features (Phase 3)

- 🔄 **PDF Generation**: Print professional reports and bills
- 🔄 **Report Templates**: Customizable report layouts with letterhead
- 🔄 **Analytics Dashboard**: Revenue and test volume statistics
- 🔄 **Data Export**: Export data to Excel and CSV formats
- 🔄 **Backup/Restore**: Automated data backup functionality
- 🔄 **User Management**: Multiple user roles and permissions

## Technical Details

- **Framework**: Python Tkinter (built-in GUI framework)
- **Database**: SQLite (serverless, local storage)
- **Architecture**: Modular design with separate GUI components
- **Validation**: Comprehensive form validation and error handling
- **Responsive**: Resizable windows with proper grid layouts

## Support

For issues or questions about this laboratory billing system, please check:

1. Error messages in the status bar (bottom of the window)
2. Validation messages in popup dialogs
3. Console output for technical details

## Development Notes

- Phone numbers are used as unique patient identifiers
- All monetary values are stored as DECIMAL(10,2)
- Dates are stored in YYYY-MM-DD format
- The application automatically creates the database on first run
- All forms include proper validation and error handling 