/**
 * Train Participant Form JavaScript
 * Handles Select2 initialization and dynamic participant loading
 */

(function() {
    'use strict';

    // Get translations
    const translations = window.trainParticipantFormTranslations || {};

    // Initialize Select2 for all searchable selects
    function initializeSelect2() {
        $('.searchable-select').select2({
            theme: 'bootstrap-5',
            width: '100%',
            placeholder: function() {
                const selectId = $(this).attr('id');
                if (selectId === 'train') {
                    return translations.selectTrainingSession || 'Select Training Session';
                } else if (selectId === 'participant') {
                    return translations.selectParticipant || 'Select Participant';
                }
                return '';
            },
            allowClear: true,
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

    // Load available participants for selected training session
    function loadParticipants(trainId) {
        const participantSelect = $('#participant');
        const form = $('#trainParticipantForm');
        const trainParticipantId = form.data('train-participant-id') || '';

        console.log('Loading participants for training:', trainId);

        // Show loading state
        participantSelect.html(`<option value="">${translations.loadingParticipants || 'Loading participants...'}</option>`);
        participantSelect.prop('disabled', true);

        // Build URL with optional train_participant_id parameter
        let url = `/api/training/${trainId}/available-participants/`;
        if (trainParticipantId) {
            url += `?train_participant_id=${trainParticipantId}`;
        }

        console.log('Fetching from URL:', url);

        // Fetch available participants
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin'
        })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json().then(data => {
                    if (!response.ok) {
                        console.error('Server error:', data);
                        throw new Error(data.error || `HTTP error! status: ${response.status}`);
                    }
                    return data;
                });
            })
            .then(data => {
                console.log('Received participants:', data);
                
                // Clear and populate dropdown
                participantSelect.html(`<option value="">${translations.selectParticipant || 'Select Participant'}</option>`);
                
                if (data.participants && data.participants.length > 0) {
                    data.participants.forEach(participant => {
                        const option = new Option(participant.name, participant.id, false, false);
                        participantSelect.append(option);
                    });
                    participantSelect.prop('disabled', false);
                    console.log('Added', data.participants.length, 'participants to dropdown');
                } else {
                    participantSelect.html(`<option value="">${translations.noParticipants || 'No available participants for this training'}</option>`);
                    participantSelect.prop('disabled', false);
                    console.log('No participants available');
                }

                // Re-initialize Select2 for participant dropdown
                participantSelect.select2('destroy');
                participantSelect.select2({
                    theme: 'bootstrap-5',
                    width: '100%',
                    placeholder: translations.selectParticipant || 'Select Participant',
                    allowClear: true,
                    language: {
                        noResults: function() {
                            return translations.noResults || 'No results found';
                        },
                        searching: function() {
                            return translations.searching || 'Searching...';
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error loading participants:', error);
                const errorMsg = error.message || (translations.errorLoading || 'Error loading participants');
                participantSelect.html(`<option value="">${errorMsg}</option>`);
                participantSelect.prop('disabled', false);
            });
    }

    // Handle training session change
    function handleTrainingChange() {
        const trainSelect = $('#train');
        const trainId = trainSelect.val();

        console.log('Training session changed to:', trainId);

        if (trainId) {
            loadParticipants(trainId);
        } else {
            // Reset participant dropdown
            const participantSelect = $('#participant');
            participantSelect.html(`<option value="">${translations.selectTrainingFirst || 'Select Training Session first'}</option>`);
            participantSelect.prop('disabled', false);
            
            // Re-initialize Select2
            participantSelect.select2('destroy');
            participantSelect.select2({
                theme: 'bootstrap-5',
                width: '100%',
                placeholder: translations.selectParticipant || 'Select Participant',
                allowClear: true,
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

    // Form validation
    function validateForm() {
        const forms = document.querySelectorAll('.needs-validation');
        
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    // Initialize when DOM is ready
    $(document).ready(function() {
        console.log('Train Participant Form initialized');
        
        // Initialize Select2
        initializeSelect2();

        // Setup event listeners - use select2:select for Select2 compatibility
        $('#train').on('select2:select', handleTrainingChange);
        $('#train').on('change', handleTrainingChange);

        // Form validation
        validateForm();

        // If editing OR if training is preselected, load participants
        const form = $('#trainParticipantForm');
        const trainSelect = $('#train');
        const trainId = trainSelect.val();
        
        console.log('Initial training ID:', trainId);
        
        if (trainId) {
            // Load participants if a training session is already selected
            loadParticipants(trainId);
        }
    });

})();
