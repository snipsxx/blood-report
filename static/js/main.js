// ===== GLOBAL UTILITIES =====
const LabSystem = {
    // API Base URL
    apiBase: '/api',
    
    // Show loading overlay
    showLoading: function() {
        $('#loadingOverlay').fadeIn(200);
    },
    
    // Hide loading overlay
    hideLoading: function() {
        $('#loadingOverlay').fadeOut(200);
    },
    
    // Show toast notification
    showToast: function(message, type = 'info', duration = 5000) {
        const toastId = 'toast-' + Date.now();
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="${iconMap[type]} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        $('#toastContainer').append(toastHtml);
        const toastElement = new bootstrap.Toast(document.getElementById(toastId), {
            delay: duration
        });
        toastElement.show();
        
        // Remove toast element after it's hidden
        $(`#${toastId}`).on('hidden.bs.toast', function() {
            $(this).remove();
        });
    },
    
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2
        }).format(amount);
    },
    
    // Format date
    formatDate: function(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Format datetime
    formatDateTime: function(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // AJAX helper with error handling
    ajax: function(options) {
        const defaults = {
            dataType: 'json',
            timeout: 30000,
            beforeSend: function() {
                LabSystem.showLoading();
            },
            complete: function() {
                LabSystem.hideLoading();
            },
            error: function(xhr, status, error) {
                let errorMessage = 'An error occurred';
                
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                } else if (status === 'timeout') {
                    errorMessage = 'Request timed out';
                } else if (status === 'abort') {
                    errorMessage = 'Request was cancelled';
                } else {
                    errorMessage = error || 'Unknown error occurred';
                }
                
                LabSystem.showToast(errorMessage, 'error');
            }
        };
        
        return $.ajax($.extend({}, defaults, options));
    },
    
    // Confirm dialog
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Get status badge HTML
    getStatusBadge: function(status) {
        const statusConfig = {
            pending: { class: 'bg-warning', icon: 'fas fa-clock' },
            completed: { class: 'bg-success', icon: 'fas fa-check' },
            reviewed: { class: 'bg-info', icon: 'fas fa-eye' },
            cancelled: { class: 'bg-danger', icon: 'fas fa-times' },
            unpaid: { class: 'bg-danger', icon: 'fas fa-exclamation' },
            partial: { class: 'bg-warning', icon: 'fas fa-minus' },
            paid: { class: 'bg-success', icon: 'fas fa-check' }
        };
        
        const config = statusConfig[status] || { class: 'bg-secondary', icon: 'fas fa-question' };
        return `<span class="badge ${config.class}">
                    <i class="${config.icon} me-1"></i>${status.charAt(0).toUpperCase() + status.slice(1)}
                </span>`;
    },
    
    // Initialize common UI components
    initializeUI: function() {
        // Initialize tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();
        
        // Initialize popovers
        $('[data-bs-toggle="popover"]').popover();
        
        // Auto-resize textareas
        $('textarea').on('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Form validation styling
        $('.form-control, .form-select').on('blur', function() {
            if (this.checkValidity()) {
                $(this).removeClass('is-invalid').addClass('is-valid');
            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
            }
        });
        
        // Number input formatting
        $('.currency-input').on('input', function() {
            let value = this.value.replace(/[^\d.]/g, '');
            let parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            if (parts[1] && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].substring(0, 2);
            }
            this.value = value;
        });
        
        // Phone number formatting
        $('.phone-input').on('input', function() {
            this.value = this.value.replace(/[^\d+\-\s()]/g, '');
        });
        
        // Search input with debounce
        $('.search-input').on('input', function() {
            const $input = $(this);
            const searchTerm = $input.val();
            
            clearTimeout($input.data('timeout'));
            $input.data('timeout', setTimeout(function() {
                $input.trigger('search', [searchTerm]);
            }, 300));
        });
    }
};

// ===== NAVIGATION HELPERS =====
const Navigation = {
    // Set active navigation item
    setActive: function(path) {
        $('.navbar-nav .nav-link').removeClass('active');
        $(`.navbar-nav .nav-link[href="${path}"]`).addClass('active');
    },
    
    // Get current page
    getCurrentPage: function() {
        return window.location.pathname;
    }
};

// ===== TABLE HELPERS =====
const TableHelper = {
    // Initialize DataTable
    initialize: function(tableId, options = {}) {
        const defaults = {
            responsive: true,
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search records...",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "No entries found",
                infoFiltered: "(filtered from _MAX_ total entries)",
                emptyTable: "No data available in table"
            },
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                 '<"row"<"col-sm-12"tr>>' +
                 '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
            order: [[0, 'desc']]
        };
        
        return $(`#${tableId}`).DataTable($.extend({}, defaults, options));
    },
    
    // Add action buttons to table
    getActionButtons: function(id, actions = []) {
        let buttons = '<div class="btn-group" role="group">';
        
        actions.forEach(action => {
            buttons += `<button type="button" class="btn btn-sm btn-outline-${action.color || 'primary'}" 
                                onclick="${action.onclick}" 
                                ${action.tooltip ? `data-bs-toggle="tooltip" title="${action.tooltip}"` : ''}>
                            <i class="${action.icon}"></i>
                        </button>`;
        });
        
        buttons += '</div>';
        return buttons;
    }
};

// ===== FORM HELPERS =====
const FormHelper = {
    // Serialize form to object
    serializeToObject: function(formId) {
        const formArray = $(`#${formId}`).serializeArray();
        const formObject = {};
        
        formArray.forEach(field => {
            if (formObject[field.name]) {
                if (!Array.isArray(formObject[field.name])) {
                    formObject[field.name] = [formObject[field.name]];
                }
                formObject[field.name].push(field.value);
            } else {
                formObject[field.name] = field.value;
            }
        });
        
        return formObject;
    },
    
    // Populate form from object
    populateForm: function(formId, data) {
        Object.keys(data).forEach(key => {
            const $field = $(`#${formId} [name="${key}"]`);
            if ($field.length) {
                if ($field.is(':checkbox') || $field.is(':radio')) {
                    $field.filter(`[value="${data[key]}"]`).prop('checked', true);
                } else {
                    $field.val(data[key]);
                }
            }
        });
    },
    
    // Clear form
    clearForm: function(formId) {
        $(`#${formId}`)[0].reset();
        $(`#${formId} .is-valid, #${formId} .is-invalid`).removeClass('is-valid is-invalid');
    },
    
    // Validate form
    validateForm: function(formId) {
        const form = document.getElementById(formId);
        return form.checkValidity();
    }
};

// ===== CHART HELPERS =====
const ChartHelper = {
    // Default chart options
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    },
    
    // Create line chart
    createLineChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: $.extend(true, {}, this.defaultOptions, options)
        });
    },
    
    // Create bar chart
    createBarChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: $.extend(true, {}, this.defaultOptions, options)
        });
    },
    
    // Create pie chart
    createPieChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, {
            type: 'pie',
            data: data,
            options: $.extend(true, {}, this.defaultOptions, {
                scales: undefined
            }, options)
        });
    }
};

// ===== DOCUMENT READY =====
$(document).ready(function() {
    // Initialize UI components
    LabSystem.initializeUI();
    
    // Set active navigation
    Navigation.setActive(Navigation.getCurrentPage());
    
    // Global error handler for AJAX requests
    $(document).ajaxError(function(event, xhr, settings, error) {
        console.error('AJAX Error:', error, xhr);
    });
    
    // Add CSRF token to all AJAX requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                const token = $('meta[name=csrf-token]').attr('content');
                if (token) {
                    xhr.setRequestHeader("X-CSRFToken", token);
                }
            }
        }
    });
    
    // Handle responsive navbar
    $('.navbar-toggler').on('click', function() {
        $('.navbar-collapse').toggleClass('show');
    });
    
    // Auto-hide alerts
    $('.alert').delay(5000).fadeOut(300);
    
    // Smooth scrolling for anchor links
    $('a[href*="#"]:not([href="#"])').click(function() {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            let target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html, body').animate({
                    scrollTop: target.offset().top - 80
                }, 300);
                return false;
            }
        }
    });
});

// ===== KEYBOARD SHORTCUTS =====
$(document).keydown(function(e) {
    // Ctrl+K for search
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        $('.search-input:visible:first').focus();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        $('.modal.show').modal('hide');
    }
    
    // Ctrl+S to save (prevent browser save)
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        $('.btn-primary:visible:first').click();
    }
});

// ===== EXPORT UTILITIES =====
window.LabSystem = LabSystem;
window.Navigation = Navigation;
window.TableHelper = TableHelper;
window.FormHelper = FormHelper;
window.ChartHelper = ChartHelper; 