/**
 * Evaluation Form JavaScript
 * Handles dynamic form interactions, Select2 initialization, and validation
 */

(function() {
    'use strict';
    
    const form = document.getElementById('evaluationForm');
    
    // Get translations from data attributes (set by Django template)
    const translations = window.evaluationFormTranslations || {};
    
    // Initialize Select2 on all searchable select dropdowns
    $(document).ready(function() {
        // Common Select2 configuration
        const select2Config = {
            theme: 'bootstrap-5',
            allowClear: true,
            width: '100%',
            language: {
                noResults: function() {
                    return translations.noResults || 'No results found';
                },
                searching: function() {
                    return translations.searching || 'Searching...';
                },
                inputTooShort: function() {
                    return translations.inputTooShort || 'Please enter more characters';
                }
            }
        };
        
        // Initialize each select with its own placeholder
        // Don't initialize participant select here - it will be initialized dynamically
        
        if ($('#prof').length) {
            $('#prof').select2({
                ...select2Config,
                placeholder: translations.selectProfessor || 'Select Professor'
            });
        }
        
        if ($('#course').length) {
            $('#course').select2({
                ...select2Config,
                placeholder: translations.selectCourse || 'Select Course'
            });
        }
        
        if ($('#location').length) {
            $('#location').select2({
                ...select2Config,
                placeholder: translations.selectLocation || 'Select Location'
            });
        }
        
        if ($('#train').length) {
            $('#train').select2({
                ...select2Config,
                placeholder: translations.selectTrainingSession || 'Select Training Session'
            });
        }
        
        // Handle Select2 validation with Bootstrap for all selects
        $('.searchable-select').on('select2:select select2:unselect', function() {
            if (form.classList.contains('was-validated')) {
                if (this.value) {
                    this.setCustomValidity('');
                } else {
                    this.setCustomValidity('Please select an option');
                }
            }
        });
    });
    
    // Bootstrap validation
    form.addEventListener('submit', function(event) {
        // Manually validate all Select2 fields
        const selectFields = document.querySelectorAll('.searchable-select');
        selectFields.forEach(function(select) {
            if (select.hasAttribute('required') && !select.value) {
                select.setCustomValidity('Please select an option');
            } else {
                select.setCustomValidity('');
            }
        });
        
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        form.classList.add('was-validated');
    }, false);
    
    // Training session change handler - show details and load participants
    const trainSelect = document.getElementById('train');
    const participantSelect = document.getElementById('participant');
    const trainingDetails = document.getElementById('trainingDetails');
    const detailCourse = document.getElementById('detailCourse');
    const detailProfessor = document.getElementById('detailProfessor');
    const detailLocation = document.getElementById('detailLocation');
    
    // Get evaluation ID from data attribute (for edit mode)
    const evaluationId = form.dataset.evaluationId;
    
    // Use jQuery for Select2 compatibility
    $('#train').on('change', function() {
        const trainId = $(this).val();
        const selectedOption = this.options[this.selectedIndex];
        
        if (trainId) {
            // Show training details
            if (detailCourse) detailCourse.textContent = selectedOption.getAttribute('data-course') || 'N/A';
            if (detailProfessor) detailProfessor.textContent = selectedOption.getAttribute('data-professor') || 'N/A';
            if (detailLocation) detailLocation.textContent = selectedOption.getAttribute('data-location') || 'N/A';
            if (trainingDetails) trainingDetails.style.display = 'block';
            
            // Load participants for this training session (only for non-guest users)
            if (participantSelect) {
                const currentParticipantId = $(participantSelect).val();
                
                // Destroy Select2 before clearing options
                if ($(participantSelect).data('select2')) {
                    $(participantSelect).select2('destroy');
                }
                
                // Clear existing options and show loading
                participantSelect.innerHTML = `<option value="">${translations.loadingParticipants || 'Loading participants...'}</option>`;
                
                // Build URL. In edit mode, pass evaluation_id so the server
                // excludes only OTHER evaluations from the "already submitted"
                // check and keeps the currently-assigned participant selectable.
                let fetchUrl = `/api/training/${trainId}/participants/`;
                if (evaluationId) {
                    fetchUrl += `?evaluation_id=${evaluationId}`;
                }
                
                // Fetch participants via AJAX
                fetch(fetchUrl)
                    .then(response => {
                        // Handle authentication failures - the API returns 401 JSON
                        // instead of redirecting to the HTML login page, so we can
                        // detect this case and show a meaningful message.
                        if (response.status === 401) {
                            throw new Error('Session expired. Please refresh the page and log in again.');
                        }
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        participantSelect.innerHTML = `<option value="">${translations.selectParticipant || 'Select Participant'}</option>`;
                        
                        if (data.participants && data.participants.length > 0) {
                            data.participants.forEach(participant => {
                                const option = document.createElement('option');
                                option.value = participant.id;
                                option.textContent = participant.name;
                                
                                // Preserve selection if it was previously selected
                                if (participant.id == currentParticipantId) {
                                    option.selected = true;
                                }
                                
                                participantSelect.appendChild(option);
                            });
                        } else {
                            participantSelect.innerHTML = `<option value="">${translations.noParticipants || 'No participants available for this training'}</option>`;
                        }
                        
                        // Reinitialize Select2
                        initializeParticipantSelect2();
                    })
                    .catch(error => {
                        console.error('Error loading participants:', error);
                        participantSelect.innerHTML = `<option value="">${translations.errorLoading || 'Error loading participants'}</option>`;
                        
                        // Reinitialize Select2 even on error
                        initializeParticipantSelect2();
                    });
            }
        } else {
            if (trainingDetails) trainingDetails.style.display = 'none';
            
            // Reset participants dropdown if training is deselected
            if (participantSelect) {
                if ($(participantSelect).data('select2')) {
                    $(participantSelect).select2('destroy');
                }
                participantSelect.innerHTML = `<option value="">${translations.selectTrainingFirst || 'Select Training Session first'}</option>`;
                initializeParticipantSelect2();
            }
        }
    });
    
    // Function to initialize participant Select2
    function initializeParticipantSelect2() {
        if (participantSelect) {
            $(participantSelect).select2({
                theme: 'bootstrap-5',
                allowClear: true,
                width: '100%',
                placeholder: translations.selectParticipant || 'Select Participant',
                language: {
                    noResults: function() {
                        return translations.noResults || 'No results found';
                    },
                    searching: function() {
                        return translations.searching || 'Searching...';
                    }
                }
            });
        }
    }
    
    // Initialize participant dropdown with Select2 on page load
    initializeParticipantSelect2();
    
    // Trigger on page load if a training session is already selected
    $(document).ready(function() {
        if (trainSelect && trainSelect.value) {
            $('#train').trigger('change');
        }
    });
    
    // Custom validation for number inputs (Q1-Q15)
    const questionInputs = form.querySelectorAll('input[type="number"][name^="ev_q_"]');
    questionInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const value = parseInt(this.value);
            
            if (this.value === '') {
                // Empty is not valid (required field)
                this.setCustomValidity('This field is required');
            } else if (isNaN(value) || value < 1 || value > 10) {
                this.setCustomValidity('Value must be between 1 and 10');
            } else {
                this.setCustomValidity('');
            }
        });
    });
})();
