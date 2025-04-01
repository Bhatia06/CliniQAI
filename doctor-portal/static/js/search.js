/**
 * CliniQAI Doctor Portal
 * Search functionality JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Form elements
    const searchForm = document.getElementById('search-form');
    const clearBtn = document.getElementById('clear-btn');
    const searchBtn = document.getElementById('search-btn');
    
    // Dropdown input fields
    const drugNameInput = document.getElementById('drug-name');
    const adverseReactionInput = document.getElementById('adverse-reaction');
    const medicalConditionInput = document.getElementById('medical-condition');
    
    // Dropdown lists
    const drugNameDropdown = document.getElementById('drug-name-dropdown');
    const adverseReactionDropdown = document.getElementById('adverse-reaction-dropdown');
    const medicalConditionDropdown = document.getElementById('medical-condition-dropdown');
    
    // Lists of items for each dropdown
    let drugsList = [];
    let reactionsList = [];
    let conditionsList = [];
    
    // Initialize
    setupSearch();
    
    /**
     * Set up search functionality
     */
    async function setupSearch() {
        // Load dropdown data
        await Promise.all([
            loadDrugs(),
            loadReactions(),
            loadConditions()
        ]);
        
        // Set up event listeners
        if (searchForm) {
            searchForm.addEventListener('submit', handleSearchSubmit);
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', clearSearchForm);
        }
        
        // Set up dropdown functionality
        setupDropdown(drugNameInput, drugNameDropdown, drugsList);
        setupDropdown(adverseReactionInput, adverseReactionDropdown, reactionsList);
        setupDropdown(medicalConditionInput, medicalConditionDropdown, conditionsList);
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            const dropdowns = [drugNameDropdown, adverseReactionDropdown, medicalConditionDropdown];
            
            // Close all dropdowns if click is outside any input or dropdown
            if (!isInsideAnyDropdownOrInput(e.target)) {
                dropdowns.forEach(dropdown => {
                    if (dropdown) dropdown.style.display = 'none';
                });
            }
        });
    }
    
    /**
     * Check if element is inside any dropdown or input
     */
    function isInsideAnyDropdownOrInput(element) {
        const inputs = [drugNameInput, adverseReactionInput, medicalConditionInput];
        const dropdowns = [drugNameDropdown, adverseReactionDropdown, medicalConditionDropdown];
        
        // Check if element is inside any input or dropdown
        return inputs.some(input => input && input.contains(element)) || 
               dropdowns.some(dropdown => dropdown && dropdown.contains(element));
    }
    
    /**
     * Load drugs list from API
     */
    async function loadDrugs() {
        try {
            const response = await fetch('/api/drugs');
            const data = await response.json();
            
            if (data.success && Array.isArray(data.drugs)) {
                drugsList = data.drugs;
                console.log(`Loaded ${drugsList.length} drugs`);
            }
        } catch (error) {
            console.error('Error loading drugs:', error);
        }
    }
    
    /**
     * Load adverse reactions list from API
     */
    async function loadReactions() {
        try {
            const response = await fetch('/api/reactions');
            const data = await response.json();
            
            if (data.success && Array.isArray(data.reactions)) {
                reactionsList = data.reactions;
                console.log(`Loaded ${reactionsList.length} reactions`);
            }
        } catch (error) {
            console.error('Error loading reactions:', error);
        }
    }
    
    /**
     * Load medical conditions list from API
     */
    async function loadConditions() {
        try {
            const response = await fetch('/api/conditions');
            const data = await response.json();
            
            if (data.success && Array.isArray(data.conditions)) {
                conditionsList = data.conditions;
                console.log(`Loaded ${conditionsList.length} conditions`);
            }
        } catch (error) {
            console.error('Error loading conditions:', error);
        }
    }
    
    /**
     * Set up dropdown functionality for an input field
     */
    function setupDropdown(inputElement, dropdownElement, itemsList) {
        if (!inputElement || !dropdownElement) return;
        
        // Show dropdown on input focus
        inputElement.addEventListener('focus', () => {
            populateDropdown(dropdownElement, itemsList, inputElement.value);
        });
        
        // Update dropdown on input
        inputElement.addEventListener('input', () => {
            populateDropdown(dropdownElement, itemsList, inputElement.value);
        });
        
        // Handle keyboard navigation
        inputElement.addEventListener('keydown', (e) => {
            if (dropdownElement.style.display === 'block') {
                handleDropdownKeyNav(e, dropdownElement, inputElement);
            }
            
            // Show dropdown on arrow down if it's closed
            if (e.key === 'ArrowDown' && dropdownElement.style.display !== 'block') {
                populateDropdown(dropdownElement, itemsList, inputElement.value);
                dropdownElement.style.display = 'block';
                e.preventDefault();
            }
            
            // Hide dropdown on escape
            if (e.key === 'Escape') {
                dropdownElement.style.display = 'none';
                e.preventDefault();
            }
        });
        
        // Show dropdown when clicking on input
        inputElement.addEventListener('click', (e) => {
            e.stopPropagation();
            populateDropdown(dropdownElement, itemsList, inputElement.value);
        });
        
        // Handle clicks on dropdown items
        dropdownElement.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item && !item.classList.contains('no-results')) {
                inputElement.value = item.textContent.trim();
                dropdownElement.style.display = 'none';
                
                // Trigger an input event to update button states
                const inputEvent = new Event('input', { bubbles: true });
                inputElement.dispatchEvent(inputEvent);
                
                // Move focus to next input if available
                const inputs = Array.from(document.querySelectorAll('.dropdown-input'));
                const currentIndex = inputs.indexOf(inputElement);
                if (currentIndex < inputs.length - 1) {
                    inputs[currentIndex + 1].focus();
                }
            }
        });
    }
    
    /**
     * Populate dropdown with filtered items
     */
    function populateDropdown(dropdownElement, itemsList, filter = '') {
        dropdownElement.innerHTML = '';
        
        if (!itemsList || itemsList.length === 0) {
            const noItems = document.createElement('div');
            noItems.className = 'dropdown-item no-results';
            noItems.textContent = 'No options available';
            dropdownElement.appendChild(noItems);
            return;
        }
        
        // Filter items based on input
        const filteredItems = filter ? 
            itemsList.filter(item => item.toLowerCase().includes(filter.toLowerCase())) : 
            itemsList;
        
        // Sort exact matches to the top
        filteredItems.sort((a, b) => {
            if (a.toLowerCase() === filter.toLowerCase()) return -1;
            if (b.toLowerCase() === filter.toLowerCase()) return 1;
            return 0;
        });
        
        // Limit to 10 items
        const displayItems = filteredItems.slice(0, 10);
        
        // Add filtered items to dropdown
        if (displayItems.length > 0) {
            displayItems.forEach((item, index) => {
                const option = document.createElement('div');
                option.className = 'dropdown-item';
                option.textContent = item;
                
                // Highlight first item by default
                if (index === 0) {
                    option.classList.add('active');
                }
                
                dropdownElement.appendChild(option);
            });
        } else {
            // Show "no results" message if no items match
            const noResults = document.createElement('div');
            noResults.className = 'dropdown-item no-results';
            noResults.textContent = 'No matches found';
            dropdownElement.appendChild(noResults);
        }
        
        // Show dropdown if it has content
        if (dropdownElement.children.length > 0) {
            dropdownElement.style.display = 'block';
        } else {
            dropdownElement.style.display = 'none';
        }
    }
    
    /**
     * Handle keyboard navigation in dropdowns
     */
    function handleDropdownKeyNav(e, dropdownElement, inputElement) {
        const active = dropdownElement.querySelector('.dropdown-item.active');
        const items = dropdownElement.querySelectorAll('.dropdown-item:not(.no-results)');
        
        if (items.length === 0) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (active) {
                    active.classList.remove('active');
                    const next = active.nextElementSibling || items[0];
                    next.classList.add('active');
                    ensureVisible(next, dropdownElement);
                } else {
                    items[0].classList.add('active');
                }
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                if (active) {
                    active.classList.remove('active');
                    const prev = active.previousElementSibling || items[items.length - 1];
                    prev.classList.add('active');
                    ensureVisible(prev, dropdownElement);
                } else {
                    items[items.length - 1].classList.add('active');
                }
                break;
                
            case 'Enter':
                if (active) {
                    e.preventDefault();
                    inputElement.value = active.textContent;
                    dropdownElement.style.display = 'none';
                    
                    // Trigger an input event to update button states
                    const inputEvent = new Event('input', { bubbles: true });
                    inputElement.dispatchEvent(inputEvent);
                }
                break;
                
            case 'Escape':
                dropdownElement.style.display = 'none';
                break;
        }
    }
    
    /**
     * Ensure an element is visible in scrollable container
     */
    function ensureVisible(element, container) {
        const containerTop = container.scrollTop;
        const containerBottom = containerTop + container.clientHeight;
        const elementTop = element.offsetTop;
        const elementBottom = elementTop + element.clientHeight;
        
        if (elementTop < containerTop) {
            container.scrollTop = elementTop;
        } else if (elementBottom > containerBottom) {
            container.scrollTop = elementBottom - container.clientHeight;
        }
    }
    
    /**
     * Handle search form submission
     */
    async function handleSearchSubmit(event) {
        event.preventDefault();
        
        // Check if the button is disabled
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn && searchBtn.disabled) {
            console.log('Search button is disabled, not proceeding with search');
            return;
        }
        
        // Get search criteria
        const drugName = drugNameInput.value.trim();
        const adverseReaction = adverseReactionInput.value.trim();
        const medicalCondition = medicalConditionInput.value.trim();
        const dateRange = document.getElementById('date-range').value;
        
        // Validate search criteria
        if (!drugName && !adverseReaction && !medicalCondition) {
            // Display error message
            const errorMessage = document.getElementById('error-message');
            if (errorMessage) {
                errorMessage.textContent = 'Please enter at least one search criteria.';
                errorMessage.style.display = 'block';
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    errorMessage.style.display = 'none';
                }, 5000);
            }
            return;
        }
        
        // Show loading, hide results and errors
        const loadingContainer = document.getElementById('loading-container');
        const resultsContainer = document.getElementById('results-container');
        const errorMessage = document.getElementById('error-message');
        
        showElement(loadingContainer);
        hideElement(resultsContainer);
        hideElement(errorMessage);
        
        // Call the search results handler (in results.js)
        try {
            await handleSearchResults({
                drug_name: drugName,
                adverse_reaction: adverseReaction,
                medical_condition: medicalCondition,
                date_range: dateRange
            });
        } catch (error) {
            console.error('Search error:', error);
            displayError('Failed to perform search. Please try again.');
            hideElement(loadingContainer);
        }
    }
    
    /**
     * Clear the search form
     */
    function clearSearchForm() {
        drugNameInput.value = '';
        adverseReactionInput.value = '';
        medicalConditionInput.value = '';
        document.getElementById('date-range').value = 'all';
        
        // Hide results and error message
        hideElement(document.getElementById('results-container'));
        hideElement(document.getElementById('error-message'));
    }
}); 