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
        
        // Show dropdown when input is focused
        inputElement.addEventListener('focus', () => {
            populateDropdown(dropdownElement, inputElement.value.trim().toLowerCase(), itemsList);
            dropdownElement.style.display = 'block';
        });
        
        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target !== inputElement && e.target !== dropdownElement) {
                dropdownElement.style.display = 'none';
            }
        });
        
        // Update dropdown as user types
        inputElement.addEventListener('input', debounce(() => {
            populateDropdown(dropdownElement, inputElement.value.trim().toLowerCase(), itemsList);
            dropdownElement.style.display = 'block';
        }, 200));
        
        // Handle keyboard navigation
        inputElement.addEventListener('keydown', (e) => {
            handleDropdownKeyboard(e, dropdownElement, inputElement);
        });
        
        // Set up click handler for dropdown items
        dropdownElement.addEventListener('click', (e) => {
            if (e.target.classList.contains('dropdown-item')) {
                inputElement.value = e.target.textContent;
                dropdownElement.style.display = 'none';
                
                // Trigger an input event to update button states
                const inputEvent = new Event('input', { bubbles: true });
                inputElement.dispatchEvent(inputEvent);
            }
        });
    }
    
    /**
     * Populate dropdown with filtered items
     */
    function populateDropdown(dropdownElement, searchTerm, itemsList) {
        // Clear current dropdown items
        dropdownElement.innerHTML = '';
        
        // Filter items based on search term
        let filteredItems = [];
        if (searchTerm) {
            filteredItems = itemsList.filter(item => 
                item.toLowerCase().includes(searchTerm)
            ).slice(0, 10); // Limit to 10 items
        } else {
            filteredItems = itemsList.slice(0, 10); // Show first 10 items
        }
        
        // Add filtered items to dropdown
        filteredItems.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'dropdown-item';
            itemElement.textContent = item;
            dropdownElement.appendChild(itemElement);
        });
        
        // Show "no results" message if no items match
        if (filteredItems.length === 0 && searchTerm) {
            const noResults = document.createElement('div');
            noResults.className = 'dropdown-item no-results';
            noResults.textContent = 'No matches found';
            dropdownElement.appendChild(noResults);
        }
    }
    
    /**
     * Handle keyboard navigation in dropdown
     */
    function handleDropdownKeyboard(event, dropdownElement, inputElement) {
        const items = dropdownElement.querySelectorAll('.dropdown-item:not(.no-results)');
        let activeItem = dropdownElement.querySelector('.dropdown-item.active');
        let activeIndex = -1;
        
        // Find current active item index
        if (activeItem) {
            for (let i = 0; i < items.length; i++) {
                if (items[i] === activeItem) {
                    activeIndex = i;
                    break;
                }
            }
        }
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                if (activeItem) activeItem.classList.remove('active');
                
                // Move to next item or first if at end
                activeIndex = (activeIndex + 1) % items.length;
                items[activeIndex].classList.add('active');
                ensureVisible(items[activeIndex], dropdownElement);
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                if (activeItem) activeItem.classList.remove('active');
                
                // Move to previous item or last if at beginning
                activeIndex = (activeIndex - 1 + items.length) % items.length;
                items[activeIndex].classList.add('active');
                ensureVisible(items[activeIndex], dropdownElement);
                break;
                
            case 'Enter':
                if (activeItem) {
                    event.preventDefault();
                    inputElement.value = activeItem.textContent;
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