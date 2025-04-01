/**
 * CliniQAI Doctor Portal
 * Results functionality JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const resultsContainer = document.getElementById('results-container');
    const loadingContainer = document.getElementById('loading-container');
    const resultsList = document.getElementById('results-list');
    const resultsCount = document.getElementById('results-count');
    const sortSelect = document.getElementById('sort-by');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const paginationInfo = document.getElementById('pagination-info');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');
    
    // State variables
    let filteredResults = [];
    let currentPage = 1;
    let totalPages = 1;
    const resultsPerPage = 5;
    
    // Initialize
    init();
    
    /**
     * Initialize results functionality
     */
    function init() {
        // Set up sorting functionality
        if (sortSelect) {
            sortSelect.addEventListener('change', handleSortChange);
        }
        
        // Set up pagination
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => navigateToPage(currentPage - 1));
        }
        
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => navigateToPage(currentPage + 1));
        }
    }
    
    /**
     * Capitalize first letter of words that aren't vowels, conjunctions, or articles
     */
    function specialCapitalize(text) {
        if (!text) return '';
        
        // List of words to keep lowercase
        const keepLowercase = ['a', 'an', 'the', 'and', 'or', 'but', 'nor', 'for', 'so', 'yet', 'in', 'on', 'at', 'to', 'by', 'as', 'of'];
        
        return text.split(' ').map((word, index) => {
            // Skip empty words
            if (!word) return word;
            
            // First word always gets capitalized
            if (index === 0) {
                return word.charAt(0).toUpperCase() + word.slice(1);
            }
            
            // Check if this is a word we want to keep lowercase
            const lowercaseWord = word.toLowerCase();
            if (keepLowercase.includes(lowercaseWord)) {
                return lowercaseWord;
            }
            
            // Check if the word starts with a vowel
            const firstChar = lowercaseWord.charAt(0);
            if (['a', 'e', 'i', 'o', 'u'].includes(firstChar)) {
                return lowercaseWord;
            }
            
            // Otherwise capitalize the first letter
            return word.charAt(0).toUpperCase() + word.slice(1);
        }).join(' ');
    }
    
    /**
     * Handle search results
     */
    window.handleSearchResults = async function(searchParams) {
        try {
            // Show the results section
            const resultsSection = document.getElementById('results-section');
            if (resultsSection) {
                resultsSection.style.display = 'block';
            }
            
            // Call the API to get search results
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchParams)
            });
            
            const data = await response.json();
            
            // Hide loading indicator
            hideElement(loadingContainer);
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to Retrieve Search Results');
            }
            
            // Update results count
            if (resultsCount) {
                resultsCount.textContent = `${data.count} Results Found`;
            }
            
            // Store results in state
            window.currentResults = data.results || [];
            
            // Apply current sorting
            const sortOption = sortSelect ? sortSelect.value : 'date-desc';
            filteredResults = sortResults(window.currentResults, sortOption);
            
            // Calculate pagination
            totalPages = Math.max(1, Math.ceil(filteredResults.length / resultsPerPage));
            currentPage = 1;
            
            // Display results
            displayResults();
            
            // Scroll to the results section
            if (resultsSection) {
                setTimeout(() => {
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300); // Small delay to ensure the section is visible first
            }
            
            // Return the results for possible use by the caller
            return window.currentResults;
            
        } catch (error) {
            console.error('Error handling search results:', error);
            hideElement(loadingContainer);
            displayError(error.message || 'An error occurred while Processing Search Results');
            return [];
        }
    }
    
    /**
     * Display results with pagination
     */
    function displayResults() {
        if (!resultsList || !resultsContainer) return;
        
        // Clear previous results
        resultsList.innerHTML = '';
        
        // Show results container
        showElement(resultsContainer);
        
        // Check if there are results to display
        if (filteredResults.length === 0) {
            resultsList.innerHTML = '<div class="no-results">No Matching Results Found.</div>';
            hideElement(document.querySelector('.pagination'));
            return;
        }
        
        // Show pagination
        const paginationElement = document.querySelector('.pagination');
        if (paginationElement) {
            showElement(paginationElement);
        }
        
        // Get current page results
        const startIndex = (currentPage - 1) * resultsPerPage;
        const endIndex = Math.min(startIndex + resultsPerPage, filteredResults.length);
        const pageResults = filteredResults.slice(startIndex, endIndex);
        
        // Create result cards
        pageResults.forEach(result => {
            const resultCard = createResultCard(result);
            resultsList.appendChild(resultCard);
        });
        
        // Update pagination info
        if (currentPageSpan) currentPageSpan.textContent = currentPage;
        if (totalPagesSpan) totalPagesSpan.textContent = totalPages;
        
        // Update pagination buttons
        if (prevPageBtn) {
            prevPageBtn.disabled = currentPage <= 1;
            prevPageBtn.classList.toggle('disabled', currentPage <= 1);
        }
        
        if (nextPageBtn) {
            nextPageBtn.disabled = currentPage >= totalPages;
            nextPageBtn.classList.toggle('disabled', currentPage >= totalPages);
        }
    }
    
    /**
     * Create a result card element
     */
    function createResultCard(result) {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Result header with title and date
        const header = document.createElement('div');
        header.className = 'result-header';
        
        const title = document.createElement('div');
        title.className = 'result-title';
        title.textContent = result.drug_name || 'Unknown Drug';
        
        const meta = document.createElement('div');
        meta.className = 'result-meta';
        meta.textContent = `Report Date: ${formatDate(result.date)}`;
        
        header.appendChild(title);
        header.appendChild(meta);
        
        // Result details
        const details = document.createElement('div');
        details.className = 'result-details';
        
        // Adverse Reaction
        const reactionDetail = createDetailItem('Adverse Reaction', result.adverse_reaction);
        details.appendChild(reactionDetail);
        
        // Medical Condition
        const conditionDetail = createDetailItem('Medical Condition', result.medical_condition);
        details.appendChild(conditionDetail);
        
        // Severity - only show the badge, not the text
        const severityDetail = createDetailItem('Severity', '');
        severityDetail.querySelector('.detail-value').appendChild(createSeverityBadge(result.severity || 'Unknown'));
        details.appendChild(severityDetail);
        
        // Patient Details
        const patientDetail = createDetailItem('Patient', `ID: ${result.id || 'N/A'} | Gender: ${result.gender || 'N/A'}`);
        details.appendChild(patientDetail);
        
        // Current Medication
        if (result.current_medication) {
            const medicationDetail = createDetailItem('Current Medication', result.current_medication);
            details.appendChild(medicationDetail);
        }
        
        // Assemble the card
        card.appendChild(header);
        card.appendChild(details);
        
        return card;
    }
    
    /**
     * Create a detail item for the result card
     */
    function createDetailItem(label, value) {
        const item = document.createElement('div');
        item.className = 'detail-item';
        
        const labelElement = document.createElement('div');
        labelElement.className = 'detail-label';
        labelElement.textContent = label;
        
        const valueElement = document.createElement('div');
        valueElement.className = 'detail-value';
        
        // Special case for severity badge - don't add any text
        if (value === '' && label === 'Severity') {
            // Don't set textContent, badge will be appended later
        } else if (typeof value === 'string') {
            valueElement.textContent = formatEmptyValue(value);
        } else {
            valueElement.appendChild(value);
        }
        
        item.appendChild(labelElement);
        item.appendChild(valueElement);
        
        return item;
    }
    
    /**
     * Sort results based on selected criteria
     */
    function sortResults(results, sortBy) {
        const sortedResults = [...results];
        
        switch (sortBy) {
            case 'date-desc':
                sortedResults.sort((a, b) => new Date(b.date) - new Date(a.date));
                break;
            case 'date-asc':
                sortedResults.sort((a, b) => new Date(a.date) - new Date(b.date));
                break;
            case 'severity-desc':
                sortedResults.sort((a, b) => {
                    const severityOrder = { 'Severe': 3, 'Moderate': 2, 'Mild': 1, 'Unknown': 0 };
                    return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
                });
                break;
            case 'severity-asc':
                sortedResults.sort((a, b) => {
                    const severityOrder = { 'Severe': 3, 'Moderate': 2, 'Mild': 1, 'Unknown': 0 };
                    return (severityOrder[a.severity] || 0) - (severityOrder[b.severity] || 0);
                });
                break;
        }
        
        return sortedResults;
    }
    
    /**
     * Handle sort change event
     */
    function handleSortChange(event) {
        const sortOption = event.target.value;
        filteredResults = sortResults(window.currentResults, sortOption);
        currentPage = 1; // Reset to first page
        displayResults();
    }
    
    /**
     * Navigate to a specific page
     */
    function navigateToPage(pageNumber) {
        if (pageNumber < 1 || pageNumber > totalPages) return;
        
        currentPage = pageNumber;
        displayResults();
        
        // Scroll to top of results
        if (resultsContainer) {
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }
}); 