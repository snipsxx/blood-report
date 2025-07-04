// ===== DASHBOARD MANAGEMENT =====
const Dashboard = {
    charts: {},
    
    // Initialize dashboard
    init: function() {
        this.loadOverviewData();
        this.initializeCharts();
        this.loadRecentReports();
        this.bindEvents();
    },
    
    // Load overview statistics
    loadOverviewData: function() {
        LabSystem.ajax({
            url: '/api/analytics/overview',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    Dashboard.updateStatistics(response.data);
                }
            }
        });
    },
    
    // Update statistics cards
    updateStatistics: function(data) {
        const stats = data.revenue_summary || {};
        const patientStats = data.patient_stats || {};
        const testStats = data.test_stats || {};
        
        // Update cards
        $('#totalPatients').text(patientStats.total_patients || 0);
        $('#totalReports').text(testStats.total_reports || 0);
        $('#totalRevenue').text(LabSystem.formatCurrency(stats.total_revenue || 0));
        $('#pendingReports').text(testStats.pending_reports || 0);
        
        // Add animation
        this.animateCounters();
    },
    
    // Animate counter numbers
    animateCounters: function() {
        $('.stats-value').each(function() {
            const $counter = $(this);
            const target = parseInt($counter.text().replace(/[^\d]/g, '')) || 0;
            
            if (target > 0) {
                $counter.text('0');
                $counter.animate({
                    countNum: target
                }, {
                    duration: 1000,
                    easing: 'easeOutCirc',
                    step: function() {
                        $counter.text(Math.floor(this.countNum).toLocaleString());
                    },
                    complete: function() {
                        if ($counter.attr('id') === 'totalRevenue') {
                            $counter.text(LabSystem.formatCurrency(target));
                        } else {
                            $counter.text(target.toLocaleString());
                        }
                    }
                });
            }
        });
    },
    
    // Initialize charts
    initializeCharts: function() {
        this.createRevenueChart();
        this.createTestsChart();
    },
    
    // Create revenue trend chart
    createRevenueChart: function() {
        LabSystem.ajax({
            url: '/api/analytics/revenue',
            method: 'GET',
            success: function(response) {
                if (response.success && response.data.daily_revenue) {
                    Dashboard.renderRevenueChart(response.data.daily_revenue);
                }
            }
        });
    },
    
    // Render revenue chart
    renderRevenueChart: function(data) {
        const chartData = {
            labels: data.map(item => LabSystem.formatDate(item.date)),
            datasets: [{
                label: 'Daily Revenue',
                data: data.map(item => item.revenue),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        };
        
        const options = {
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Revenue: ' + LabSystem.formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            }
        };
        
        this.charts.revenue = ChartHelper.createLineChart('revenueChart', chartData, options);
    },
    
    // Create popular tests chart
    createTestsChart: function() {
        LabSystem.ajax({
            url: '/api/analytics/tests',
            method: 'GET',
            success: function(response) {
                if (response.success && response.data.popular_tests) {
                    Dashboard.renderTestsChart(response.data.popular_tests);
                }
            }
        });
    },
    
    // Render tests chart
    renderTestsChart: function(data) {
        const chartData = {
            labels: data.map(item => item.test_name),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#f5576c',
                    '#4facfe',
                    '#00f2fe',
                    '#43e97b',
                    '#38f9d7'
                ],
                borderWidth: 0
            }]
        };
        
        const options = {
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        };
        
        this.charts.tests = ChartHelper.createPieChart('testsChart', chartData, options);
    },
    
    // Load recent reports
    loadRecentReports: function() {
        LabSystem.ajax({
            url: '/api/reports?limit=10',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    Dashboard.renderRecentReports(response.data);
                }
            }
        });
    },
    
    // Render recent reports table
    renderRecentReports: function(reports) {
        const tbody = $('#recentReportsTable tbody');
        tbody.empty();
        
        if (reports.length === 0) {
            tbody.append('<tr><td colspan="5" class="text-center text-muted">No recent reports found</td></tr>');
            return;
        }
        
        reports.forEach(report => {
            const row = `
                <tr>
                    <td>#${report.report_id}</td>
                    <td>${report.patient_name || 'N/A'}</td>
                    <td>${LabSystem.formatDate(report.test_date)}</td>
                    <td>${LabSystem.getStatusBadge(report.status)}</td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="Dashboard.viewReport(${report.report_id})" 
                                    data-bs-toggle="tooltip" title="View Report">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="Dashboard.downloadReport(${report.report_id})" 
                                    data-bs-toggle="tooltip" title="Download PDF">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
        
        // Reinitialize tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();
    },
    
    // View report details
    viewReport: function(reportId) {
        window.location.href = `/reports?view=${reportId}`;
    },
    
    // Download report PDF
    downloadReport: function(reportId) {
        LabSystem.showLoading();
        
        // Create a temporary link to trigger download
        const link = document.createElement('a');
        link.href = `/api/reports/${reportId}/pdf`;
        link.download = `blood_report_${reportId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        LabSystem.hideLoading();
        LabSystem.showToast('Report download started', 'success');
    },
    
    // Bind event handlers
    bindEvents: function() {
        // Refresh dashboard
        $('#refreshDashboard').on('click', function() {
            Dashboard.refresh();
        });
        
        // Auto refresh every 5 minutes
        setInterval(function() {
            Dashboard.refresh();
        }, 5 * 60 * 1000);
        
        // Chart resize handler
        $(window).on('resize', function() {
            Object.keys(Dashboard.charts).forEach(key => {
                if (Dashboard.charts[key]) {
                    Dashboard.charts[key].resize();
                }
            });
        });
    },
    
    // Refresh dashboard data
    refresh: function() {
        LabSystem.showToast('Refreshing dashboard...', 'info', 2000);
        this.loadOverviewData();
        this.loadRecentReports();
        
        // Refresh charts
        setTimeout(() => {
            this.createRevenueChart();
            this.createTestsChart();
        }, 500);
    }
};

// ===== DOCUMENT READY =====
$(document).ready(function() {
    Dashboard.init();
    
    // Add fade-in animation to cards
    $('.stats-card').each(function(index) {
        $(this).delay(index * 100).animate({
            opacity: 1
        }, 500);
    });
    
    // Initialize stats cards with hover effects
    $('.stats-card').hover(
        function() {
            $(this).find('.stats-icon').addClass('animate__animated animate__pulse');
        },
        function() {
            $(this).find('.stats-icon').removeClass('animate__animated animate__pulse');
        }
    );
}); 