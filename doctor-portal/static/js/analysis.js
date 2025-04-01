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
     * Handle analysis action
     */
    async function handleAnalysis() {
        try {
            // Show loading, hide results and error
            if (analysisLoadingContainer) {
                showElement(analysisLoadingContainer);
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
            
            // Get the current search results to analyze
            if (!window.currentResults || window.currentResults.length === 0) {
                throw new Error('No search results to analyze');
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
                throw new Error(data.message || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Error performing analysis:', error);
            if (analysisErrorMessage) {
                analysisErrorMessage.textContent = error.message || 'Failed to perform analysis. Please try again.';
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
                analysisErrorMessage.textContent = 'No patterns were found in the current results.';
                showElement(analysisErrorMessage);
            }
            if (emptyAnalysis) {
                showElement(emptyAnalysis);
            }
            return;
        }
        
        // Process each analysis item
        analysisData.forEach(item => {
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
        description.innerHTML = analysis.description.replace(/\[([^\]]+)\]/g, '<span class="highlight">$1</span>');
        
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