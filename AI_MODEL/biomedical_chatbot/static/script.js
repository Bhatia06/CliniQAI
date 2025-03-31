document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patientForm');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    
    // Populate medication and condition dropdowns
    populateMedications();
    populateConditions();

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        loadingDiv.style.display = 'block';
        resultDiv.style.display = 'none';

        // Get form data
        const currentMedications = getSelectedValues('currentMedications');
        const drugToUse = document.getElementById('drugToUse').value.trim();
        const preexistingConditions = getSelectedValues('preexistingConditions');
        const age = parseInt(document.getElementById('age').value);
        const weight = parseFloat(document.getElementById('weight').value);

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
                throw new Error(data.error);
            }
        } catch (error) {
            resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            resultDiv.style.display = 'block';
        } finally {
            loadingDiv.style.display = 'none';
        }
    });

    async function populateMedications() {
        try {
            const response = await fetch('/api/medications');
            const data = await response.json();
            
            if (data.success) {
                const selectCurrent = document.getElementById('currentMedications');
                const selectDrug = document.getElementById('drugToUse');
                
                data.medications.forEach(med => {
                    const option = document.createElement('option');
                    option.value = med;
                    option.textContent = med;
                    selectCurrent.appendChild(option.cloneNode(true));
                    selectDrug.appendChild(option);
                });
                
                // Initialize select2 for better UX
                $('#currentMedications').select2({
                    placeholder: "Select current medications",
                    width: '100%'
                });
                
                $('#drugToUse').select2({
                    placeholder: "Select drug to use",
                    width: '100%'
                });
            }
        } catch (error) {
            console.error('Error loading medications:', error);
        }
    }
    
    async function populateConditions() {
        try {
            const response = await fetch('/api/conditions');
            const data = await response.json();
            
            if (data.success) {
                const select = document.getElementById('preexistingConditions');
                
                data.conditions.forEach(condition => {
                    const option = document.createElement('option');
                    option.value = condition;
                    option.textContent = condition;
                    select.appendChild(option);
                });
                
                // Initialize select2 for better UX
                $('#preexistingConditions').select2({
                    placeholder: "Select pre-existing conditions",
                    width: '100%'
                });
            }
        } catch (error) {
            console.error('Error loading conditions:', error);
        }
    }
    
    function getSelectedValues(selectId) {
        const select = document.getElementById(selectId);
        return Array.from(select.selectedOptions).map(option => option.value);
    }

    function createReactionItem(reaction) {
        // Handle both ML-predicted and rule-based reactions
        const reaction_name = reaction.reaction || reaction.type;
        const trigger = reaction.trigger || reaction.triggered_by || '';
        const probability = reaction.probability ? `<span class="probability">${reaction.probability}</span>` : '';
        const source = reaction.source ? `<div class="source">${reaction.source}</div>` : '';
        const mechanism = reaction.mechanism ? `<div class="mechanism">${reaction.mechanism}</div>` : '';
        
        return `
            <li class="reaction-item">
                <div class="reaction-name">
                    ${reaction_name}
                    ${probability}
                </div>
                <div class="trigger"><strong>Trigger:</strong> ${trigger}</div>
                ${source}
                ${mechanism}
            </li>
        `;
    }

    function displayResults(analysis) {
        let html = `
            <div class="analysis-header">
                <h2>Adverse Drug Reaction Analysis</h2>
                <div class="patient-info">
                    <p><strong>Patient:</strong> ${analysis.patient_info.age} years, ${analysis.patient_info.weight} kg</p>
                    <p><strong>Drug to use:</strong> ${analysis.medication_info.drug_to_use}</p>
                    <p><strong>Current medications:</strong> ${analysis.medication_info.current_medications.join(', ') || 'None'}</p>
                    <p><strong>Pre-existing conditions:</strong> ${analysis.medication_info.preexisting_conditions.join(', ') || 'None'}</p>
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

        resultDiv.innerHTML = html;
        resultDiv.style.display = 'block';
    }
}); 