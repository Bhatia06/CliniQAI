/**
 * CliniQAI Patient Portal
 * Reports handling JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const refreshBtn = document.getElementById('refresh-btn');
    const reportsTable = document.getElementById('reports-table');
    const reportsBody = document.getElementById('reports-body');
    const loadingContainer = document.getElementById('loading-container');
    const noReportsMessage = document.getElementById('no-reports-message');
    const reportCountMessage = document.getElementById('report-count-message');
    const visibleCountElement = document.getElementById('visible-count');
    const totalCountElement = document.getElementById('total-count');
    const reportSearch = document.getElementById('report-search');
    const reportFilter = document.getElementById('report-filter');
    
    // State variables
    let allReports = [];
    let filteredReports = [];
    let visibleReports = [];
    let displayLimit = 10;
    
    // Initialize
    if (refreshBtn) {
        refreshBtn.addEventListener('click', fetchReports);
    }
    
    // Set up search and filter functionality
    if (reportSearch) {
        reportSearch.addEventListener('input', debounce(filterReports, 300));
    }
    
    if (reportFilter) {
        reportFilter.addEventListener('change', filterReports);
    }
    
    if (reportCountMessage) {
        reportCountMessage.addEventListener('click', showAllReports);
    }
    
    // Make fetchReports available globally
    window.fetchReports = fetchReports;
    
    // Fetch reports on page load
    fetchReports();
    
    /**
     * Fetch reports from API
     */
    async function fetchReports() {
        try {
            // Show loading state
            if (loadingContainer) showElement(loadingContainer);
            if (reportsTable) hideElement(reportsTable);
            if (noReportsMessage) hideElement(noReportsMessage);
            if (reportCountMessage) hideElement(reportCountMessage);
            
            // Fetch reports
            const response = await apiRequest(API_ENDPOINTS.reports);
            
            // Store reports
            allReports = response.reports || [];
            
            // Apply filters and display
            filterReports();
            
        } catch (error) {
            console.error('Error fetching reports:', error);
            showError('Failed to load reports. Please try again.');
            
            // Hide loading state
            if (loadingContainer) hideElement(loadingContainer);
            
            // Show empty state
            if (noReportsMessage) showElement(noReportsMessage);
        }
    }
    
    /**
     * Filter reports based on search and dropdown filter
     */
    function filterReports() {
        const searchTerm = reportSearch ? reportSearch.value.toLowerCase() : '';
        const filterValue = reportFilter ? reportFilter.value : 'all';
        
        // Apply filters
        filteredReports = allReports.filter(report => {
            // Apply severity filter
            const matchesSeverity = filterValue === 'all' || report.severity === filterValue;
            
            // Apply search filter (search across multiple fields)
            const matchesSearch = searchTerm === '' || 
                (report.drug_name && report.drug_name.toLowerCase().includes(searchTerm)) ||
                (report.medical_condition && report.medical_condition.toLowerCase().includes(searchTerm)) ||
                (report.adverse_reaction && report.adverse_reaction.toLowerCase().includes(searchTerm)) ||
                (report.patient_id && report.patient_id.toLowerCase().includes(searchTerm));
            
            return matchesSeverity && matchesSearch;
        });
        
        // Limit visible reports
        visibleReports = filteredReports.slice(0, displayLimit);
        
        // Update counts
        if (visibleCountElement) visibleCountElement.textContent = visibleReports.length;
        if (totalCountElement) totalCountElement.textContent = filteredReports.length;
        
        // Display reports
        displayReports();
    }
    
    /**
     * Display reports in the table
     */
    function displayReports() {
        // Hide loading
        if (loadingContainer) hideElement(loadingContainer);
        
        // Check if we have reports
        if (filteredReports.length === 0) {
            if (reportsTable) hideElement(reportsTable);
            if (noReportsMessage) showElement(noReportsMessage);
            if (reportCountMessage) hideElement(reportCountMessage);
            return;
        }
        
        // Show table
        if (reportsTable) showElement(reportsTable);
        if (noReportsMessage) hideElement(noReportsMessage);
        
        // Show/hide count message based on if we have more reports to show
        if (reportCountMessage) {
            if (filteredReports.length > visibleReports.length) {
                showElement(reportCountMessage);
            } else {
                hideElement(reportCountMessage);
            }
        }
        
        // Populate table
        if (reportsBody) {
            reportsBody.innerHTML = '';
            
            visibleReports.forEach(report => {
                const row = document.createElement('tr');
                
                // Format date
                const formattedDate = window.formatDate ? window.formatDate(report.timestamp) : report.timestamp;
                
                // Create severity badge
                const severityClass = report.severity ? `severity-badge severity-${report.severity.toLowerCase()}` : '';
                const severityHtml = report.severity ? 
                    `<span class="${severityClass}">${report.severity}</span>` : '';
                
                // Add table cells
                row.innerHTML = `
                    <td>${formattedDate}</td>
                    <td>${report.patient_id || ''}</td>
                    <td>${report.drug_name || ''}</td>
                    <td>${report.medical_condition || ''}</td>
                    <td>${report.cause_of_administration || ''}</td>
                    <td>${report.adverse_reaction || ''}</td>
                    <td>${severityHtml}</td>
                    <td>${report.gender || ''}</td>
                `;
                
                reportsBody.appendChild(row);
            });
        }
    }
    
    /**
     * Show all reports
     */
    function showAllReports() {
        displayLimit = filteredReports.length;
        visibleReports = filteredReports;
        
        // Update count
        if (visibleCountElement) visibleCountElement.textContent = visibleReports.length;
        
        // Hide count message
        if (reportCountMessage) hideElement(reportCountMessage);
        
        // Display all reports
        displayReports();
    }
    
    /**
     * Debounce function (defined here in case it's not defined in main.js)
     */
    function debounce(func, delay) {
        if (window.debounce) return window.debounce(func, delay);
        
        let debounceTimer;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(context, args), delay);
        };
    }
}); 