/**
 * CliniQAI Patient Portal
 * Form handling JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Form elements
    const adrForm = document.getElementById('adr-form');
    const submitBtn = document.getElementById('submit-btn');
    
    // Dropdown input fields
    const drugInput = document.getElementById('drug-name');
    const drugDropdown = document.getElementById('drug-dropdown');
    const causeInput = document.getElementById('cause');
    const causeDropdown = document.getElementById('cause-dropdown');
    const conditionInput = document.getElementById('medical-condition');
    const conditionDropdown = document.getElementById('condition-dropdown');
    const medicationInput = document.getElementById('current-medication');
    const medicationDropdown = document.getElementById('medication-dropdown');
    
    // Predefined lists for autocomplete
    const drugList = [
        'Aspirin', 'Ibuprofen', 'Paracetamol', 'Amoxicillin', 'Lisinopril', 
        'Metformin', 'Cetirizine', 'Warfarin', 'Calpol', 'Levothyroxine', 
        'Atorvastatin', 'Simvastatin', 'Omeprazole', 'Diazepam', 'Morphine',
        'Losartan', 'Amlodipine', 'Fluoxetine', 'Sertraline', 'Ramipril'
    ];
    
    const causeList = [
        'Pain relief', 'Fever', 'Infection', 'Blood pressure', 'Inflammation',
        'Headache', 'Allergies', 'Blood clot prevention', 'Diabetes management',
        'Thyroid regulation', 'Cholesterol control', 'Anxiety', 'Depression',
        'Acid reflux', 'Heart condition', 'Sleep aid', 'Joint pain', 'Asthma'
    ];
    
    const conditionList = [
        'Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Migraine', 
        'Blood Clots', 'Cold', 'Fever', 'Hypothyroidism', 'High Cholesterol',
        'Depression', 'Anxiety', 'GERD', 'Insomnia', 'Rheumatoid Arthritis',
        'COPD', 'Atrial Fibrillation', 'Osteoporosis', 'Cancer', 'Epilepsy'
    ];
    
    const medicationList = [
        'None', 'Vitamins', 'Insulin', 'Metformin', 'Atorvastatin', 
        'Aspirin', 'Paracetamol', 'Ibuprofen', 'Cetirizine', 'Levothyroxine',
        'Amlodipine', 'Lisinopril', 'Ramipril', 'Losartan', 'Omeprazole',
        'Sertraline', 'Fluoxetine', 'Warfarin', 'Albuterol', 'Montelukast'
    ];
    
    // Set up autocomplete dropdowns
    setupDropdowns();
    
    // Set up form submission
    setupFormSubmission();
    
    /**
     * Set up all dropdown functionality
     */
    function setupDropdowns() {
        // Set up each dropdown
        setupDropdown(drugInput, drugDropdown, drugList);
        setupDropdown(causeInput, causeDropdown, causeList);
        setupDropdown(conditionInput, conditionDropdown, conditionList);
        setupDropdown(medicationInput, medicationDropdown, medicationList);
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            const dropdowns = [drugDropdown, causeDropdown, conditionDropdown, medicationDropdown];
            
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
        const inputs = [drugInput, causeInput, conditionInput, medicationInput];
        const dropdowns = [drugDropdown, causeDropdown, conditionDropdown, medicationDropdown];
        
        // Check if element is inside any input or dropdown
        return inputs.some(input => input && input.contains(element)) || 
               dropdowns.some(dropdown => dropdown && dropdown.contains(element));
    }
    
    /**
     * Set up individual dropdown
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
        });
        
        // Show dropdown when clicking on input
        inputElement.addEventListener('click', (e) => {
            e.stopPropagation();
            populateDropdown(dropdownElement, itemsList, inputElement.value);
        });
        
        // Handle clicks on dropdown items
        dropdownElement.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item) {
                inputElement.value = item.textContent;
                dropdownElement.style.display = 'none';
            }
        });
    }
    
    /**
     * Populate dropdown with filtered items
     */
    function populateDropdown(dropdownElement, itemsList, filter = '') {
        dropdownElement.innerHTML = '';
        
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
        
        // Show "Add new" option if we have input but no exact match
        if (filter.trim() !== '' && !filteredItems.some(item => item.toLowerCase() === filter.toLowerCase())) {
            const option = document.createElement('div');
            option.className = 'dropdown-item add-new';
            option.textContent = `Use "${filter}"`;
            dropdownElement.appendChild(option);
        }
        
        // Add items to dropdown
        filteredItems.forEach((item, index) => {
            const option = document.createElement('div');
            option.className = 'dropdown-item';
            option.textContent = item;
            
            // Highlight first item by default
            if (index === 0) {
                option.classList.add('active');
            }
            
            dropdownElement.appendChild(option);
        });
        
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
        const items = dropdownElement.querySelectorAll('.dropdown-item');
        
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
                }
                break;
                
            case 'Escape':
                dropdownElement.style.display = 'none';
                break;
        }
    }
    
    /**
     * Ensure dropdown item is visible in scrollable dropdown
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
     * Set up form submission
     */
    function setupFormSubmission() {
        if (!adrForm) return;
        
        adrForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                // Disable submit button to prevent double-submission
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Submitting...';
                }
                
                // Hide any previous messages
                hideElement('success-message');
                hideElement('error-message');
                
                // Get form data
                const formData = {
                    drug_name: drugInput.value.trim(),
                    cause_of_administration: causeInput.value.trim(),
                    medical_condition: conditionInput.value.trim(),
                    adverse_reaction: document.getElementById('adverse-reaction').value.trim(),
                    severity: document.getElementById('severity').value,
                    gender: document.getElementById('gender').value,
                    current_medication: medicationInput.value.trim() || 'None'
                };
                
                // Validate required fields
                if (!formData.drug_name || !formData.cause_of_administration || 
                    !formData.medical_condition || !formData.adverse_reaction || 
                    !formData.severity || !formData.gender) {
                    throw new Error('Please fill out all required fields.');
                }
                
                // Submit form data
                const result = await apiRequest(API_ENDPOINTS.reports, 'POST', formData);
                
                if (result.success) {
                    // Show success message
                    showSuccess(`Report submitted successfully. Your patient ID is: ${result.patient_id}`);
                    
                    // Reset form
                    adrForm.reset();
                    
                    // Refresh reports table
                    if (window.fetchReports) {
                        window.fetchReports();
                    }
                } else {
                    throw new Error(result.error || 'An error occurred while submitting the report.');
                }
            } catch (error) {
                showError(error.message);
                console.error('Form submission error:', error);
            } finally {
                // Re-enable submit button
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit Report';
                }
            }
        });
    }
}); 