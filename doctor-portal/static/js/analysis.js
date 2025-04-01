/**
 * CliniQAI Doctor Portal
 * Analysis functionality JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const analyzeBtn = document.getElementById('analyze-btn');
    const analysisLoadingContainer = document.getElementById('analysis-loading-container');
    const analysisResultsContainer = document.getElementById('analysis-results-container');
    const analysisErrorMessage = document.getElementById('analysis-error-message');
    const emptyAnalysis = document.getElementById('empty-analysis');
    
    // Initialize
    init();
    
    /**
     * Initialize analysis functionality
     */
    function init() {
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', handleAnalysis);
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
     * Handle analysis action
     */
    async function handleAnalysis() {
        try {
            // Check if button is disabled
            if (analyzeBtn && analyzeBtn.disabled) {
                console.log('Analyze button is disabled, not proceeding with analysis');
                return;
            }
            
            // Validate that at least one search field has been filled
            const drugNameInput = document.getElementById('drug-name');
            const adverseReactionInput = document.getElementById('adverse-reaction');
            const medicalConditionInput = document.getElementById('medical-condition');
            
            if (!drugNameInput || !adverseReactionInput || !medicalConditionInput) {
                console.warn('Search form inputs not found');
                throw new Error('Search form not available');
            }
            
            // Validate search criteria
            const drugName = drugNameInput.value.trim();
            const adverseReaction = adverseReactionInput.value.trim();
            const medicalCondition = medicalConditionInput.value.trim();
            
            if (!drugName && !adverseReaction && !medicalCondition) {
                throw new Error('Please enter at least one search criteria');
            }
            
            // Only show the analysis section
            const analysisSection = document.getElementById('analysis-section');
            if (analysisSection) {
                analysisSection.style.display = 'block';
            }
            
            // Show loading, hide results and error
            if (analysisLoadingContainer) {
                showElement(analysisLoadingContainer);
                
                // Update the loading message with special capitalization
                if (analysisLoadingContainer.querySelector('p')) {
                    analysisLoadingContainer.querySelector('p').textContent = 'AI is Analyzing Patterns in the Data...';
                }
            }
            
            if (analysisResultsContainer) {
                analysisResultsContainer.innerHTML = '';
                hideElement(analysisResultsContainer);
            }
            
            if (analysisErrorMessage) {
                hideElement(analysisErrorMessage);
            }
            
            if (emptyAnalysis) {
                hideElement(emptyAnalysis);
            }
            
            // Disable analyze button
            if (analyzeBtn) {
                analyzeBtn.disabled = true;
                const originalText = analyzeBtn.innerHTML;
                analyzeBtn.innerHTML = '<span class="ai-btn-icon">🔄</span>Analyzing...';
            }
            
            // Check if we have search results, if not, perform a default search first
            if (!window.currentResults || window.currentResults.length === 0) {
                // Show a message that we're running a search first
                if (analysisLoadingContainer && analysisLoadingContainer.querySelector('p')) {
                    analysisLoadingContainer.querySelector('p').textContent = 'Running Search and Analyzing Results...';
                }
                
                // Trigger a search with default parameters
                const defaultSearchParams = {
                    drug_name: '',
                    adverse_reaction: '',
                    medical_condition: '',
                    date_range: 'all'
                };
                
                // Check if the search function is available
                if (typeof window.handleSearchResults === 'function') {
                    // Wait for search to complete but don't show the results section
                    const prevResults = await fetch('/api/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(defaultSearchParams)
                    });
                    
                    const data = await prevResults.json();
                    
                    if (!data.success) {
                        throw new Error(data.message || 'Failed to Retrieve Search Results');
                    }
                    
                    // Store results in the global variable
                    window.currentResults = data.results || [];
                } else {
                    // Fallback: make the API call directly
                    const response = await fetch('/api/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(defaultSearchParams)
                    });
                    
                    const data = await response.json();
                    
                    if (!data.success) {
                        throw new Error(data.message || 'Failed to Retrieve Search Results');
                    }
                    
                    // Store results in the global variable
                    window.currentResults = data.results || [];
                }
                
                // Reset loading message
                if (analysisLoadingContainer && analysisLoadingContainer.querySelector('p')) {
                    analysisLoadingContainer.querySelector('p').textContent = 'AI is Analyzing Patterns in the Data...';
                }
            }
            
            // If still no results after search attempt, throw an error
            if (!window.currentResults || window.currentResults.length === 0) {
                throw new Error('No Search Results to Analyze');
            }
            
            // Call the AI analysis API endpoint
            const response = await fetch('/api/ai-analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    results: window.currentResults
                })
            });
            
            const data = await response.json();
            
            // Process the results
            if (data.success && data.analysis) {
                displayAnalysisResults(data.analysis);
            } else {
                throw new Error(data.message || 'Analysis Failed');
            }
            
        } catch (error) {
            console.error('Error performing analysis:', error);
            if (analysisErrorMessage) {
                analysisErrorMessage.textContent = specialCapitalize(error.message) || 'Failed to Perform Analysis. Please Try again.';
                showElement(analysisErrorMessage);
            }
            if (emptyAnalysis) {
                showElement(emptyAnalysis);
            }
        } finally {
            // Hide loading
            if (analysisLoadingContainer) {
                hideElement(analysisLoadingContainer);
            }
            
            // Re-enable analyze button
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<span class="ai-btn-icon">🧠</span>Analyze Patterns';
            }
        }
    }
    
    /**
     * Display analysis results
     */
    function displayAnalysisResults(analysisData) {
        if (!analysisResultsContainer) return;
        
        // Clear previous results
        analysisResultsContainer.innerHTML = '';
        
        // Hide empty state
        if (emptyAnalysis) {
            hideElement(emptyAnalysis);
        }
        
        // Check if there are results to display
        if (!analysisData || analysisData.length === 0) {
            if (analysisErrorMessage) {
                analysisErrorMessage.textContent = 'No Patterns Were Found in the Current Results.';
                showElement(analysisErrorMessage);
            }
            if (emptyAnalysis) {
                showElement(emptyAnalysis);
            }
            return;
        }
        
        // Process each analysis item
        analysisData.forEach(item => {
            // Keep original cases for titles and descriptions - don't capitalize
            const analysisElement = createAnalysisElement(item);
            analysisResultsContainer.appendChild(analysisElement);
        });
        
        // Show results container
        showElement(analysisResultsContainer);
    }
    
    /**
     * Create an analysis result element
     */
    function createAnalysisElement(analysis) {
        const element = document.createElement('div');
        element.className = 'analysis-result';
        
        // Create title
        const title = document.createElement('div');
        title.className = 'analysis-title';
        title.textContent = analysis.title;
        
        // Create description
        const description = document.createElement('div');
        description.className = 'analysis-description';
        
        // Replace text within brackets, but maintain special capitalization
        let processedDescription = analysis.description.replace(/\[([^\]]+)\]/g, (match, content) => {
            return `<span class="highlight">${content}</span>`;
        });
        
        description.innerHTML = processedDescription;
        
        // Add match rate if available
        let matchRate = null;
        if (analysis.confidence) {
            matchRate = document.createElement('div');
            matchRate.className = 'match-rate';
            
            const matchRateLabel = document.createElement('div');
            matchRateLabel.className = 'match-rate-label';
            
            const matchRateName = document.createElement('span');
            matchRateName.textContent = 'Confidence Level';
            
            const matchRateValue = document.createElement('span');
            matchRateValue.className = 'match-rate-value';
            matchRateValue.textContent = `${Math.round(analysis.confidence * 100)}%`;
            
            matchRateLabel.appendChild(matchRateName);
            matchRateLabel.appendChild(matchRateValue);
            
            const matchRateBar = document.createElement('div');
            matchRateBar.className = 'match-rate-bar';
            
            const matchRateFill = document.createElement('div');
            matchRateFill.className = 'match-rate-fill';
            matchRateFill.style.width = `${analysis.confidence * 100}%`;
            
            matchRateBar.appendChild(matchRateFill);
            
            matchRate.appendChild(matchRateLabel);
            matchRate.appendChild(matchRateBar);
        }
        
        // Add elements to container
        element.appendChild(title);
        element.appendChild(description);
        if (matchRate) {
            element.appendChild(matchRate);
        }
        
        return element;
    }
}); 