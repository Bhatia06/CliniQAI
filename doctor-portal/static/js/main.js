/**
 * CliniQAI Doctor Portal
 * Main JavaScript file for core functionality
 */

// Global variables and constants
const API_ENDPOINTS = {
    search: '/api/search',
    analyze: '/api/analyze'
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('CliniQAI Doctor Portal initialized');
    setCurrentYear();
    
    // Hide loading containers initially
    hideElement(document.getElementById('loading-container'));
    hideElement(document.getElementById('analysis-loading-container'));
    
    // Hide containers until we have results
    hideElement(document.getElementById('results-container'));
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('analysis-error-message').style.display = 'none';
    
    // Set up button disabling logic
    setupButtonDisabling();
    
    // Manually check button states after a short delay to ensure proper initialization
    setTimeout(() => {
        const drugNameInput = document.getElementById('drug-name');
        const adverseReactionInput = document.getElementById('adverse-reaction');
        const medicalConditionInput = document.getElementById('medical-condition');
        const searchBtn = document.getElementById('search-btn');
        const analyzeBtn = document.getElementById('analyze-btn');
        
        if (drugNameInput && adverseReactionInput && medicalConditionInput && searchBtn && analyzeBtn) {
            const hasInput = 
                drugNameInput.value.trim() !== '' || 
                adverseReactionInput.value.trim() !== '' || 
                medicalConditionInput.value.trim() !== '';
            
            searchBtn.disabled = !hasInput;
            analyzeBtn.disabled = !hasInput;
            
            if (hasInput) {
                searchBtn.classList.remove('btn-disabled');
                analyzeBtn.classList.remove('btn-disabled');
            } else {
                searchBtn.classList.add('btn-disabled');
                analyzeBtn.classList.add('btn-disabled');
            }
            
            console.log('Initial button state check - Has input:', hasInput);
        }
    }, 500);
    
    // Show/hide elements utility functions
    window.showElement = (element) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.style.display = 'block';
        }
    };
    
    window.hideElement = (element) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.style.display = 'none';
        }
    };
    
    // Utility function to safely get DOM elements
    window.getElement = (id) => {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`Element with ID "${id}" not found.`);
        }
        return element;
    };
    
    // Format date for display
    window.formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    };
    
    // Add throttle function to limit function calls
    window.throttle = (func, delay) => {
        let lastCall = 0;
        return function(...args) {
            const now = new Date().getTime();
            if (now - lastCall < delay) {
                return;
            }
            lastCall = now;
            return func(...args);
        };
    };
    
    // Debounce function for inputs
    window.debounce = (func, delay) => {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func(...args), delay);
        };
    };
    
    // Handle API requests
    window.apiRequest = async (endpoint, method = 'GET', data = null) => {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            if (data && (method === 'POST' || method === 'PUT')) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(endpoint, options);
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    };
    
    // Display error message
    window.showError = (message, elementId = 'error-message') => {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = specialCapitalize(message);
            errorElement.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorElement.style.display = 'none';
            }, 5000);
        }
    };
    
    // Create a severity badge element
    window.createSeverityBadge = (severity) => {
        const badgeEl = document.createElement('span');
        badgeEl.className = 'severity-badge';
        
        const severityLower = (severity || '').toLowerCase();
        
        switch (severityLower) {
            case 'mild':
                badgeEl.classList.add('severity-mild');
                badgeEl.textContent = 'Mild';
                break;
            case 'moderate':
                badgeEl.classList.add('severity-moderate');
                badgeEl.textContent = 'Moderate';
                break;
            case 'severe':
                badgeEl.classList.add('severity-severe');
                badgeEl.textContent = 'Severe';
                break;
            case 'critical':
                badgeEl.classList.add('severity-critical');
                badgeEl.textContent = 'Critical';
                break;
            default:
                badgeEl.classList.add('severity-unknown');
                badgeEl.textContent = 'Unknown';
        }
        
        return badgeEl;
    };
    
    // Format empty values
    window.formatEmptyValue = (value) => {
        return value || 'N/A';
    };
    
    // Truncate text with ellipsis
    window.truncateText = (text, maxLength = 100) => {
        if (!text) return 'N/A';
        if (text.length <= maxLength) return text;
        return text.slice(0, maxLength) + '...';
    };
});

// Utility Functions

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
 * Set current year in the footer copyright text
 */
function setCurrentYear() {
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
}

/**
 * Show an element
 */
function showElement(element) {
    if (element) {
        element.style.display = 'block';
    }
}

/**
 * Hide an element
 */
function hideElement(element) {
    if (element) {
        element.style.display = 'none';
    }
}

/**
 * Get a DOM element safely
 */
function getElement(id) {
    return document.getElementById(id);
}

/**
 * Format a date string for display
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return dateString;
    }
}

/**
 * Create a severity badge element
 */
function createSeverityBadge(severity) {
    const badgeEl = document.createElement('span');
    badgeEl.className = 'severity-badge';
    
    const severityLower = (severity || '').toLowerCase();
    
    switch (severityLower) {
        case 'mild':
            badgeEl.classList.add('severity-mild');
            badgeEl.textContent = 'Mild';
            break;
        case 'moderate':
            badgeEl.classList.add('severity-moderate');
            badgeEl.textContent = 'Moderate';
            break;
        case 'severe':
            badgeEl.classList.add('severity-severe');
            badgeEl.textContent = 'Severe';
            break;
        case 'critical':
            badgeEl.classList.add('severity-critical');
            badgeEl.textContent = 'Critical';
            break;
        default:
            badgeEl.classList.add('severity-unknown');
            badgeEl.textContent = 'Unknown';
    }
    
    return badgeEl;
}

/**
 * Format empty values
 */
function formatEmptyValue(value) {
    return value || 'N/A';
}

/**
 * Truncate text if it's too long
 */
function truncateText(text, maxLength = 100) {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
}

/**
 * Handle API requests
 */
async function apiRequest(url, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Throttle function calls
 */
function throttle(func, delay) {
    let lastCall = 0;
    return function(...args) {
        const now = new Date().getTime();
        if (now - lastCall < delay) {
            return;
        }
        lastCall = now;
        return func(...args);
    };
}

/**
 * Debounce function calls
 */
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), delay);
    };
}

/**
 * Display error message
 */
function displayError(message, elementId = 'error-message') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = specialCapitalize(message);
        errorElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
}

/**
 * Setup functionality to disable search and analyze buttons when no input is provided
 */
function setupButtonDisabling() {
    const drugNameInput = document.getElementById('drug-name');
    const adverseReactionInput = document.getElementById('adverse-reaction');
    const medicalConditionInput = document.getElementById('medical-condition');
    const searchBtn = document.getElementById('search-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    if (!drugNameInput || !adverseReactionInput || !medicalConditionInput || !searchBtn || !analyzeBtn) {
        console.warn('Not all required elements found for button disabling');
        return;
    }
    
    // Initially disable buttons if inputs are empty
    updateButtonState();
    
    // Add event listeners to inputs
    drugNameInput.addEventListener('input', updateButtonState);
    adverseReactionInput.addEventListener('input', updateButtonState);
    medicalConditionInput.addEventListener('input', updateButtonState);
    
    // Also add event listeners for change events
    drugNameInput.addEventListener('change', updateButtonState);
    adverseReactionInput.addEventListener('change', updateButtonState);
    medicalConditionInput.addEventListener('change', updateButtonState);
    
    // Add focus and blur events to ensure state is updated
    drugNameInput.addEventListener('focus', () => setTimeout(updateButtonState, 100));
    adverseReactionInput.addEventListener('focus', () => setTimeout(updateButtonState, 100));
    medicalConditionInput.addEventListener('focus', () => setTimeout(updateButtonState, 100));
    
    drugNameInput.addEventListener('blur', () => setTimeout(updateButtonState, 100));
    adverseReactionInput.addEventListener('blur', () => setTimeout(updateButtonState, 100));
    medicalConditionInput.addEventListener('blur', () => setTimeout(updateButtonState, 100));
    
    // Function to update button state
    function updateButtonState() {
        const drugValue = drugNameInput.value.trim();
        const reactionValue = adverseReactionInput.value.trim();
        const conditionValue = medicalConditionInput.value.trim();
        
        const hasInput = drugValue !== '' || reactionValue !== '' || conditionValue !== '';
        
        console.log('Button state update - Has input:', hasInput);
        console.log('Drug:', drugValue, 'Reaction:', reactionValue, 'Condition:', conditionValue);
        
        searchBtn.disabled = !hasInput;
        analyzeBtn.disabled = !hasInput;
        
        // Update button styles
        if (hasInput) {
            searchBtn.classList.remove('btn-disabled');
            analyzeBtn.classList.remove('btn-disabled');
        } else {
            searchBtn.classList.add('btn-disabled');
            analyzeBtn.classList.add('btn-disabled');
        }
    }
} 