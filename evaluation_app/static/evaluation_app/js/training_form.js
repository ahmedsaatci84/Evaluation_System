/**
 * Training Session Form — auto-sync professor from selected course
 */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    const courseSelect = document.getElementById('course');
    const professorSelect = document.getElementById('professor');
    if (!courseSelect || !professorSelect) return;

    const form = professorSelect.closest('form');

    function updateProfessorSelection() {
        const selectedCourse = courseSelect.options[courseSelect.selectedIndex];
        const professorId = selectedCourse.getAttribute('data-professor-id');

        if (professorId) {
            professorSelect.value = professorId;
        } else {
            professorSelect.value = '';
        }
    }

    courseSelect.addEventListener('change', updateProfessorSelection);
    updateProfessorSelection();

    // Enable professor field before submission so its value is sent
    if (form) {
        form.addEventListener('submit', function () {
            professorSelect.disabled = false;
        });
    }
});
