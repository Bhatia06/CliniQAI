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
            
            // Disable analyze button
            if (analyzeBtn) {
                analyzeBtn.disabled = true;
                const originalText = analyzeBtn.innerHTML;
                analyzeBtn.innerHTML = '<span class="ai-btn-icon">🔄</span>Analyzing...';
            }
            
            // Simulate API call with timeout
            // In a real app, this would be an actual API call to analyze the data
            const mockAnalysisCall = new Promise((resolve) => {
                setTimeout(() => {
                    // This is dummy data - in a real app, this would come from the API
                    resolve({
                        success: true,
                        analysis: mockAnalysisData
                    });
                }, 3000); // Simulate longer analysis time
            });
            
            const response = await mockAnalysisCall;
            
            // Process the results
            if (response.success && response.analysis) {
                displayAnalysisResults(response.analysis);
            } else {
                throw new Error('Analysis failed');
            }
            
        } catch (error) {
            console.error('Error performing analysis:', error);
            if (analysisErrorMessage) {
                analysisErrorMessage.textContent = 'Failed to perform analysis. Please try again.';
                showElement(analysisErrorMessage);
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
    
    // Mock analysis data for demonstration
    const mockAnalysisData = [
        {
            title: "Strong Correlation: Amoxicillin and Severe Reactions",
            description: "Analysis shows that [Amoxicillin] has a significantly higher rate of [severe adverse reactions] compared to other antibiotics in the database. In particular, respiratory symptoms and rashes occur more frequently, suggesting a potential allergic component.",
            confidence: 0.87
        },
        {
            title: "Gender-Specific Pattern: Gastrointestinal Effects",
            description: "Female patients report [gastrointestinal side effects] from NSAIDs like [Ibuprofen] at approximately 1.8 times the rate of male patients. This pattern is consistent across age groups and dosage levels.",
            confidence: 0.79
        },
        {
            title: "Drug Interaction Pattern Detected",
            description: "Patients taking [Warfarin] concurrently with [NSAIDs] show a 3.2x increased risk of bleeding complications. Consider alternative pain management for patients on anticoagulant therapy.",
            confidence: 0.92
        },
        {
            title: "Dosage Correlation with Side Effects",
            description: "For [Metformin], adverse gastrointestinal effects show a strong correlation with starting dosage. Patients started on lower doses with gradual increases reported [fewer side effects] while maintaining efficacy.",
            confidence: 0.83
        }
    ];
}); 