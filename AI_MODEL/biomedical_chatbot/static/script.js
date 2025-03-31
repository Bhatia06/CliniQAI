/**
 * CliniQAI - Adverse Drug Reaction Predictor
 * Main JavaScript functionality for the AI model component
 * 
 * This script handles:
 * 1. Dropdown implementation with search functionality
 * 2. Form validation and submission
 * 3. API integration for fetching medications and conditions
 * 4. Display of analysis results with severity categorization
 * 
 * The dropdown implementation uses a single input field that doubles
 * as both the dropdown trigger and search input, providing a clean
 * and intuitive user experience.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Main DOM elements
    const form = document.getElementById('patientForm');
    const resultPanel = document.getElementById('result');
    const loadingPanel = document.getElementById('loading');
    
    // Initialize dropdown components
    initDropdowns();
    
    // Fetch data from API
    fetchMedications();
    fetchConditions();
    
    // Handle form submission
    form.addEventListener('submit', handleFormSubmit);
    
    /**
     * Initialize custom dropdown components
     */
    function initDropdowns() {
        // Get all dropdown containers
        const dropdownContainers = document.querySelectorAll('.dropdown-container');
        
        dropdownContainers.forEach(container => {
            const field = container.querySelector('.dropdown-field');
            const menu = container.querySelector('.dropdown-menu');
            const fieldId = field.id.replace('-field', '');
            
            // Handle clicking on the field to open dropdown
            field.addEventListener('click', function(e) {
                e.stopPropagation();
                toggleDropdown(container);
            });
            
            // Handle input for filtering
            field.addEventListener('input', function(e) {
                e.stopPropagation();
                // Make sure dropdown is open when typing
                if (!container.classList.contains('active')) {
                    toggleDropdown(container);
                }
                filterDropdownItems(container, this.value);
            });
            
            // Prevent dropdown from closing when typing
            field.addEventListener('keydown', function(e) {
                e.stopPropagation();
            });
        });
        
        // Close dropdowns when clicking elsewhere
        document.addEventListener('click', function() {
            closeAllDropdowns();
        });
    }
    
    /**
     * Toggle dropdown visibility
     */
    function toggleDropdown(container) {
        const isActive = container.classList.contains('active');
        const field = container.querySelector('.dropdown-field');
        
        // Close all other dropdowns
        closeAllDropdowns();
        
        if (!isActive) {
            container.classList.add('active');
            
            // Store current value for single select fields to restore later
            if (container.classList.contains('single') && field.dataset.selectedValue) {
                field.dataset.lastValue = field.value;
            }
            
            // Focus the field
            setTimeout(() => field.focus(), 100);
        } else {
            // For single select fields, restore the selected value if one exists
            if (container.classList.contains('single') && field.dataset.selectedValue) {
                field.value = field.dataset.selectedText || '';
            }
        }
    }
    
    /**
     * Close all dropdowns
     */
    function closeAllDropdowns() {
        document.querySelectorAll('.dropdown-container').forEach(container => {
            const field = container.querySelector('.dropdown-field');
            
            if (container.classList.contains('active')) {
                // Restore selected value for single selects
                if (container.classList.contains('single') && field.dataset.selectedValue) {
                    field.value = field.dataset.selectedText || '';
                }
                
                // For dropdowns without selection, clear the input
                if (!field.dataset.selectedValue && !container.classList.contains('single')) {
                    field.value = '';
                }
                
                container.classList.remove('active');
            }
        });
    }
    
    /**
     * Filter dropdown items based on search input
     */
    function filterDropdownItems(container, searchTerm) {
        const items = container.querySelectorAll('.dropdown-item');
        const searchText = searchTerm.toLowerCase().trim();
        let hasResults = false;
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const isVisible = text.includes(searchText);
            item.style.display = isVisible ? 'block' : 'none';
            
            if (isVisible) {
                hasResults = true;
            }
        });
        
        // Show/hide no results message
        let noResults = container.querySelector('.no-results');
        
        if (!hasResults) {
            if (!noResults) {
                noResults = document.createElement('div');
                noResults.className = 'no-results';
                noResults.textContent = 'No matches found';
                noResults.style.padding = '10px';
                noResults.style.textAlign = 'center';
                noResults.style.color = 'rgba(255, 255, 255, 0.5)';
                container.querySelector('.dropdown-list').appendChild(noResults);
            }
            noResults.style.display = 'block';
        } else if (noResults) {
            noResults.style.display = 'none';
        }
    }
    
    /**
     * Add item to dropdown
     */
    function addDropdownItem(id, value, text) {
        const containerId = `${id}-menu`;
        const container = document.getElementById(containerId);
        const list = container.querySelector('.dropdown-list');
        const fieldElement = document.getElementById(`${id}-field`);
        const hiddenInput = document.getElementById(id);
        const isMultiple = container.closest('.dropdown-container').classList.contains('single') === false;
        
        // Create dropdown item
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        item.textContent = text;
        item.dataset.value = value;
        
        // Add click event
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            
            if (isMultiple) {
                // For multiple select
                if (item.classList.contains('selected')) {
                    // If already selected, remove
                    removeSelectedItem(id, value);
                    item.classList.remove('selected');
                } else {
                    // Add to selection
                    addSelectedItem(id, value, text);
                    item.classList.add('selected');
                }
                
                // Clear the input field
                fieldElement.value = '';
                fieldElement.focus();
            } else {
                // For single select
                // Update field display
                fieldElement.value = text;
                fieldElement.dataset.selectedValue = value;
                fieldElement.dataset.selectedText = text;
                
                // Update hidden input
                hiddenInput.value = value;
                
                // Update selected state
                list.querySelectorAll('.dropdown-item').forEach(i => {
                    i.classList.remove('selected');
                });
                item.classList.add('selected');
                
                // Close dropdown
                closeAllDropdowns();
            }
        });
        
        list.appendChild(item);
    }
    
    /**
     * Add a multi-select item to the selection area
     */
    function addSelectedItem(id, value, text) {
        const container = document.getElementById(`${id}-selected`);
        const hiddenInput = document.getElementById(id);
        
        // Create selected item
        const item = document.createElement('div');
        item.className = 'selected-item';
        item.dataset.value = value;
        item.innerHTML = `${text} <span class="remove-item">×</span>`;
        
        // Add remove functionality
        item.querySelector('.remove-item').addEventListener('click', function(e) {
            e.stopPropagation();
            removeSelectedItem(id, value);
            
            // Update dropdown item state
            const dropdownItem = document.querySelector(`#${id}-menu .dropdown-item[data-value="${value}"]`);
            if (dropdownItem) {
                dropdownItem.classList.remove('selected');
            }
        });
        
        container.appendChild(item);
        
        // Update hidden input value
        updateMultipleValue(id);
    }
    
    /**
     * Remove a selected item
     */
    function removeSelectedItem(id, value) {
        const container = document.getElementById(`${id}-selected`);
        const item = container.querySelector(`.selected-item[data-value="${value}"]`);
        
        if (item) {
            item.remove();
            updateMultipleValue(id);
        }
    }
    
    /**
     * Update the hidden input value for multiple selects
     */
    function updateMultipleValue(id) {
        const container = document.getElementById(`${id}-selected`);
        const hiddenInput = document.getElementById(id);
        
        // Get all selected values
        const values = Array.from(container.querySelectorAll('.selected-item')).map(item => {
            return item.dataset.value;
        });
        
        // Set as comma-separated string
        hiddenInput.value = values.join(',');
    }
    
    /**
     * Capitalize the first letter of each word in a string
     */
    function capitalizeWords(str) {
        return str.replace(/\b\w/g, char => char.toUpperCase());
    }
    
    /**
     * Fetch medications from API
     */
    async function fetchMedications() {
        try {
            const response = await fetch('/api/medications');
            const data = await response.json();
            
            if (data.success) {
                // Sort medications alphabetically
                const medications = data.medications.sort();
                
                // Add to dropdowns with capitalized names
                medications.forEach(med => {
                    const capitalizedMed = capitalizeWords(med);
                    addDropdownItem('currentMedications', med, capitalizedMed);
                    addDropdownItem('drugToUse', med, capitalizedMed);
                });
            }
        } catch (error) {
            console.error('Error fetching medications:', error);
        }
    }
    
    /**
     * Fetch conditions from API
     */
    async function fetchConditions() {
        try {
            const response = await fetch('/api/conditions');
            const data = await response.json();
            
            if (data.success) {
                // Sort conditions alphabetically
                const conditions = data.conditions.sort();
                
                // Add to dropdown with capitalized names
                conditions.forEach(condition => {
                    const capitalizedCondition = capitalizeWords(condition);
                    addDropdownItem('preexistingConditions', condition, capitalizedCondition);
                });
            }
        } catch (error) {
            console.error('Error fetching conditions:', error);
        }
    }
    
    /**
     * Extract values from form for multiple-select dropdowns
     */
    function getMultipleValues(fieldId) {
        const value = document.getElementById(fieldId).value;
        return value ? value.split(',') : [];
    }
    
    /**
     * Handle form submission
     */
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Show loading panel
        loadingPanel.style.display = 'block';
        resultPanel.style.display = 'none';

        // Get form data
        const currentMedications = getMultipleValues('currentMedications');
        const drugToUse = document.getElementById('drugToUse').value;
        const preexistingConditions = getMultipleValues('preexistingConditions');
        const age = parseInt(document.getElementById('age').value);
        const weight = parseFloat(document.getElementById('weight').value);
        
        // Validate inputs
        if (!drugToUse) {
            alert('Please select a drug to check.');
            loadingPanel.style.display = 'none';
            return;
        }
        
        if (!age || !weight) {
            alert('Please enter both age and weight.');
            loadingPanel.style.display = 'none';
            return;
        }

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    current_medications: currentMedications,
                    drug_to_use: drugToUse,
                    preexisting_conditions: preexistingConditions,
                    age: age,
                    weight: weight
                })
            });

            const data = await response.json();

            if (data.success) {
                displayResults(data.analysis);
            } else {
                throw new Error(data.error || 'An error occurred during analysis.');
            }
        } catch (error) {
            resultPanel.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            resultPanel.style.display = 'block';
        } finally {
            loadingPanel.style.display = 'none';
        }
    }
    
    /**
     * Create HTML for a reaction item
     */
    function createReactionItem(reaction) {
        const reaction_name = reaction.reaction || reaction.type;
        const trigger = reaction.trigger || reaction.triggered_by || '';
        const probability = reaction.probability ? `<span class="probability">${reaction.probability}</span>` : '';
        const source = reaction.source ? `<div class="source">${reaction.source}</div>` : '';
        const mechanism = reaction.mechanism ? `<div class="mechanism">${reaction.mechanism}</div>` : '';
        
        return `
            <li class="reaction-item">
                <div class="reaction-name">
                    ${capitalizeWords(reaction_name)}
                    ${probability}
                </div>
                <div class="trigger"><strong>Trigger:</strong> ${capitalizeWords(trigger)}</div>
                ${source}
                ${mechanism}
            </li>
        `;
    }

    /**
     * Display analysis results
     */
    function displayResults(analysis) {
        let html = `
            <div class="analysis-header">
                <h2>Adverse Drug Reaction Analysis</h2>
                <div class="patient-info">
                    <p><strong>Patient:</strong> ${analysis.patient_info.age} years, ${analysis.patient_info.weight} kg</p>
                    <p><strong>Drug to use:</strong> ${capitalizeWords(analysis.medication_info.drug_to_use)}</p>
                    <p><strong>Current medications:</strong> ${analysis.medication_info.current_medications.map(med => capitalizeWords(med)).join(', ') || 'None'}</p>
                    <p><strong>Pre-existing conditions:</strong> ${analysis.medication_info.preexisting_conditions.map(condition => capitalizeWords(condition)).join(', ') || 'None'}</p>
                </div>
            </div>
        `;

        // Group adverse reactions by severity
        const highSeverity = analysis.adverse_reactions.filter(r => r.severity === 'HIGH');
        const mediumSeverity = analysis.adverse_reactions.filter(r => r.severity === 'MEDIUM');
        const lowSeverity = analysis.adverse_reactions.filter(r => r.severity === 'LOW');

        html += `<div class="reactions-container">`;
        
        // High severity reactions
        if (highSeverity.length > 0) {
            html += `
                <div class="severity-section high">
                    <h3>High Risk Reactions</h3>
                    <ul class="reactions-list">
                        ${highSeverity.map(reaction => createReactionItem(reaction)).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Medium severity reactions
        if (mediumSeverity.length > 0) {
            html += `
                <div class="severity-section medium">
                    <h3>Medium Risk Reactions</h3>
                    <ul class="reactions-list">
                        ${mediumSeverity.map(reaction => createReactionItem(reaction)).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Low severity reactions
        if (lowSeverity.length > 0) {
            html += `
                <div class="severity-section low">
                    <h3>Low Risk Reactions</h3>
                    <ul class="reactions-list">
                        ${lowSeverity.map(reaction => createReactionItem(reaction)).join('')}
                    </ul>
                </div>
            `;
        } else if (highSeverity.length === 0 && mediumSeverity.length === 0) {
            // No reactions found
            html += `
                <div class="severity-section low">
                    <h3>No Significant Risk Detected</h3>
                    <p>Based on the provided information, no significant adverse reactions were predicted.</p>
                </div>
            `;
        }
        
        html += `</div>`;
        
        // Add disclaimer
        html += `
            <div class="disclaimer">
                <p><strong>Disclaimer:</strong> This analysis is based on a machine learning model and known medical interactions. 
                Always consult a healthcare professional before making any medication decisions.</p>
            </div>
        `;

        resultPanel.innerHTML = html;
        resultPanel.style.display = 'block';
    }
});