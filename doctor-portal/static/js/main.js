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
    console.log('Doctor Portal initialized');
    setCurrentYear();
    
    // Hide loading containers initially
    hideElement(document.getElementById('loading-container'));
    hideElement(document.getElementById('analysis-loading-container'));
    
    // Hide containers until we have results
    hideElement(document.getElementById('results-container'));
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('analysis-error-message').style.display = 'none';
    
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
            const parts = dateString.split(' ')[0].split('-');
            if (parts.length === 3) {
                return `${parts[0]}-${parts[1]}-${parts[2]}`;
            }
            return dateString;
        } catch (e) {
            console.error('Error formatting date:', e);
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
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorElement.style.display = 'none';
            }, 5000);
        }
    };
    
    // Create a severity badge element
    window.createSeverityBadge = (severity) => {
        const badge = document.createElement('span');
        badge.className = `severity-badge severity-${severity.toLowerCase()}`;
        badge.textContent = severity;
        return badge;
    };
    
    // Format empty values
    window.formatEmptyValue = (value) => {
        return value || 'N/A';
    };
    
    // Truncate text with ellipsis
    window.truncateText = (text, maxLength = 100) => {
        if (!text) return 'N/A';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };
});

// Utility Functions

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
        element.style.display = '';
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
        const parts = dateString.split(' ')[0].split('-');
        if (parts.length === 3) {
            return `${parts[0]}-${parts[1]}-${parts[2]}`;
        }
        return dateString;
    } catch (e) {
        console.error('Error formatting date:', e);
        return dateString;
    }
}

/**
 * Create a severity badge element
 */
function createSeverityBadge(severity) {
    const badge = document.createElement('span');
    badge.className = `severity-badge severity-${severity.toLowerCase()}`;
    badge.textContent = severity;
    return badge;
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
    return text.substring(0, maxLength) + '...';
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
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }
} 