// ===== PATIENTS MANAGEMENT =====
const Patients = {
    dataTable: null,
    currentPatients: [],
    
    // Initialize patients page
    init: function() {
        this.loadPatients();
        this.initializeDataTable();
        this.bindEvents();
    },
    
    // Load all patients
    loadPatients: function() {
        LabSystem.ajax({
            url: '/api/patients',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    Patients.currentPatients = response.data;
                    Patients.updatePatientsTable(response.data);
                    Patients.updatePatientCount(response.data.length);
                }
            }
        });
    },
    
    // Initialize DataTable
    initializeDataTable: function() {
        this.dataTable = TableHelper.initialize('patientsTable', {
            columns: [
                { data: 'patient_id', width: '80px' },
                { 
                    data: null,
                    render: function(data) {
                        return `${data.first_name} ${data.last_name}`;
                    }
                },
                { data: 'phone_number' },
                { data: 'email', defaultContent: '-' },
                { data: 'gender', defaultContent: '-' },
                { 
                    data: 'date_of_birth',
                    render: function(data) {
                        return data ? LabSystem.formatDate(data) : '-';
                    }
                },
                {
                    data: null,
                    orderable: false,
                    width: '120px',
                    render: function(data) {
                        return TableHelper.getActionButtons(data.patient_id, [
                            {
                                icon: 'fas fa-eye',
                                color: 'primary',
                                onclick: `Patients.viewPatient(${data.patient_id})`,
                                tooltip: 'View Details'
                            },
                            {
                                icon: 'fas fa-file-medical',
                                color: 'success',
                                onclick: `Patients.createReport(${data.patient_id})`,
                                tooltip: 'Create Report'
                            },
                            {
                                icon: 'fas fa-edit',
                                color: 'warning',
                                onclick: `Patients.editPatient(${data.patient_id})`,
                                tooltip: 'Edit Patient'
                            }
                        ]);
                    }
                }
            ]
        });
    },
    
    // Update patients table
    updatePatientsTable: function(patients) {
        if (this.dataTable) {
            this.dataTable.clear().rows.add(patients).draw();
        }
    },
    
    // Update patient count
    updatePatientCount: function(count) {
        $('#totalPatientsCount').text(count);
    },
    
    // Search patients
    searchPatients: function(searchTerm) {
        LabSystem.ajax({
            url: '/api/patients',
            method: 'GET',
            data: { search: searchTerm },
            success: function(response) {
                if (response.success) {
                    Patients.updatePatientsTable(response.data);
                    Patients.updatePatientCount(response.data.length);
                }
            }
        });
    },
    
    // Filter patients by gender
    filterByGender: function(gender) {
        let filteredPatients = this.currentPatients;
        
        if (gender) {
            filteredPatients = this.currentPatients.filter(patient => 
                patient.gender === gender
            );
        }
        
        this.updatePatientsTable(filteredPatients);
        this.updatePatientCount(filteredPatients.length);
    },
    
    // Add new patient
    addPatient: function(formData) {
        LabSystem.ajax({
            url: '/api/patients',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    LabSystem.showToast('Patient added successfully!', 'success');
                    $('#addPatientModal').modal('hide');
                    FormHelper.clearForm('addPatientForm');
                    Patients.loadPatients();
                }
            },
            error: function(xhr) {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    LabSystem.showToast(xhr.responseJSON.error, 'error');
                }
            }
        });
    },
    
    // View patient details
    viewPatient: function(patientId) {
        LabSystem.ajax({
            url: `/api/patients/${patientId}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    Patients.showPatientDetails(response.data);
                }
            }
        });
    },
    
    // Show patient details modal
    showPatientDetails: function(patient) {
        const detailsHtml = `
            <div class="row g-3">
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Patient ID</h6>
                    <p class="mb-0">#${patient.patient_id}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Full Name</h6>
                    <p class="mb-0">${patient.first_name} ${patient.last_name}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Phone Number</h6>
                    <p class="mb-0">${patient.phone_number}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Email</h6>
                    <p class="mb-0">${patient.email || '-'}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Date of Birth</h6>
                    <p class="mb-0">${patient.date_of_birth ? LabSystem.formatDate(patient.date_of_birth) : '-'}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Gender</h6>
                    <p class="mb-0">${patient.gender || '-'}</p>
                </div>
                <div class="col-12">
                    <h6 class="text-muted mb-1">Address</h6>
                    <p class="mb-0">${patient.address || '-'}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Emergency Contact</h6>
                    <p class="mb-0">${patient.emergency_contact || '-'}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Emergency Phone</h6>
                    <p class="mb-0">${patient.emergency_phone || '-'}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Created</h6>
                    <p class="mb-0">${LabSystem.formatDateTime(patient.created_at)}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted mb-1">Last Updated</h6>
                    <p class="mb-0">${LabSystem.formatDateTime(patient.updated_at)}</p>
                </div>
            </div>
        `;
        
        $('#patientDetailsContent').html(detailsHtml);
        $('#editPatientBtn').data('patient-id', patient.patient_id);
        $('#patientDetailsModal').modal('show');
    },
    
    // Edit patient
    editPatient: function(patientId) {
        // Close details modal if open
        $('#patientDetailsModal').modal('hide');
        
        // Load patient data and populate form
        LabSystem.ajax({
            url: `/api/patients/${patientId}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    FormHelper.populateForm('addPatientForm', response.data);
                    $('#addPatientModal .modal-title').text('Edit Patient');
                    $('#addPatientForm').data('mode', 'edit').data('patient-id', patientId);
                    $('#addPatientModal').modal('show');
                }
            }
        });
    },
    
    // Create report for patient
    createReport: function(patientId) {
        window.location.href = `/reports?patient=${patientId}`;
    },
    
    // Bind event handlers
    bindEvents: function() {
        // Add patient form submission
        $('#addPatientForm').on('submit', function(e) {
            e.preventDefault();
            
            if (FormHelper.validateForm('addPatientForm')) {
                const formData = FormHelper.serializeToObject('addPatientForm');
                
                const mode = $(this).data('mode');
                if (mode === 'edit') {
                    const patientId = $(this).data('patient-id');
                    Patients.updatePatient(patientId, formData);
                } else {
                    Patients.addPatient(formData);
                }
            } else {
                LabSystem.showToast('Please fill in all required fields correctly', 'warning');
            }
        });
        
        // Modal hide event - reset form
        $('#addPatientModal').on('hidden.bs.modal', function() {
            FormHelper.clearForm('addPatientForm');
            $('#addPatientModal .modal-title').text('Add New Patient');
            $('#addPatientForm').removeData('mode').removeData('patient-id');
        });
        
        // Search input
        $('#patientSearch').on('input', function() {
            const searchTerm = $(this).val();
            clearTimeout($(this).data('timeout'));
            
            $(this).data('timeout', setTimeout(function() {
                Patients.searchPatients(searchTerm);
            }, 300));
        });
        
        // Gender filter
        $('#genderFilter').on('change', function() {
            const gender = $(this).val();
            Patients.filterByGender(gender);
        });
        
        // Clear filters
        $('#clearFilters').on('click', function() {
            $('#patientSearch').val('');
            $('#genderFilter').val('');
            Patients.updatePatientsTable(Patients.currentPatients);
            Patients.updatePatientCount(Patients.currentPatients.length);
        });
        
        // Edit patient button in details modal
        $('#editPatientBtn').on('click', function() {
            const patientId = $(this).data('patient-id');
            Patients.editPatient(patientId);
        });
        
        // Phone number formatting
        $('#phoneNumber').on('input', function() {
            this.value = this.value.replace(/[^\d+\-\s()]/g, '');
        });
        
        // Emergency phone formatting
        $('#emergencyPhone').on('input', function() {
            this.value = this.value.replace(/[^\d+\-\s()]/g, '');
        });
    },
    
    // Update patient
    updatePatient: function(patientId, formData) {
        LabSystem.ajax({
            url: `/api/patients/${patientId}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    LabSystem.showToast('Patient updated successfully!', 'success');
                    $('#addPatientModal').modal('hide');
                    FormHelper.clearForm('addPatientForm');
                    Patients.loadPatients();
                }
            },
            error: function(xhr) {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    LabSystem.showToast(xhr.responseJSON.error, 'error');
                }
            }
        });
    }
};

// ===== DOCUMENT READY =====
$(document).ready(function() {
    Patients.init();
    
    // Add animation to patient count card
    $('#totalPatientsCount').closest('.card').hover(
        function() {
            $(this).find('i').addClass('animate__animated animate__bounce');
        },
        function() {
            $(this).find('i').removeClass('animate__animated animate__bounce');
        }
    );
}); 