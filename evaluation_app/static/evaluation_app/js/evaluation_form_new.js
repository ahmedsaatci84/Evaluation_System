/**
 * Evaluation Form (new style) — rating buttons, progress bar, validation
 * Requires window.evaluationFormNewConfig to be defined inline:
 * { completeText }
 */
(function () {
    'use strict';

    const cfg  = window.evaluationFormNewConfig || {};
    const form = document.getElementById('evaluationForm');
    if (!form) return;

    const progressBar  = document.getElementById('formProgress');
    const progressText = document.getElementById('progressText');

    // Rating buttons
    const ratingButtons = document.querySelectorAll('.rating-buttons');
    ratingButtons.forEach(function (container) {
        const inputId = container.getAttribute('data-input');
        const input   = document.getElementById(inputId);
        const buttons = container.querySelectorAll('.rating-btn');

        if (input && input.value) updateButtonState(buttons, input.value);

        buttons.forEach(function (button) {
            button.addEventListener('click', function () {
                const value = this.getAttribute('data-value');
                input.value = value;
                updateButtonState(buttons, value);
                updateProgress();
            });
        });

        if (input) {
            input.addEventListener('input', function () {
                updateButtonState(buttons, this.value);
                updateProgress();
            });
        }
    });

    function updateButtonState(buttons, value) {
        buttons.forEach(function (btn) {
            const btnValue      = parseInt(btn.getAttribute('data-value'));
            const selectedValue = parseInt(value);
            if (btnValue <= selectedValue) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Progress indicator
    function updateProgress() {
        const requiredFields = form.querySelectorAll('[required]');
        let filledFields = 0;
        requiredFields.forEach(function (field) {
            if (field.value && field.value.trim() !== '') filledFields++;
        });
        const percentage = Math.round((filledFields / requiredFields.length) * 100);
        if (progressBar)  progressBar.style.width  = percentage + '%';
        if (progressText) progressText.textContent = percentage + '% ' + (cfg.completeText || 'Complete');
    }

    // Character counter for notes
    const notesTextarea = document.getElementById('ev_q_notes');
    const charCount     = document.getElementById('charCount');

    function updateCharCount() {
        if (!notesTextarea || !charCount) return;
        const count = notesTextarea.value.length;
        charCount.textContent = count;
        charCount.style.color = count > 450 ? '#ef4444' : count > 400 ? '#f59e0b' : '#6c757d';
    }

    if (notesTextarea) {
        notesTextarea.addEventListener('input', updateCharCount);
        updateCharCount();
    }

    // Watch all inputs for progress
    form.querySelectorAll('input, select, textarea').forEach(function (input) {
        input.addEventListener('change', updateProgress);
        input.addEventListener('input', updateProgress);
    });

    // Bootstrap validation
    form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
        }
        form.classList.add('was-validated');
    }, false);

    // Scroll-in animation for form cards
    const formCards = document.querySelectorAll('.form-card');
    const observer  = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity   = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    formCards.forEach(function (card) {
        card.style.opacity    = '0';
        card.style.transform  = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // Initial progress calculation
    updateProgress();

    // Page header animation
    setTimeout(function () {
        const header = document.querySelector('.page-header');
        if (header) {
            header.style.opacity   = '1';
            header.style.transform = 'translateY(0)';
        }
    }, 100);
})();
