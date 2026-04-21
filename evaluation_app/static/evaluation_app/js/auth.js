/**
 * Authentication Pages — password visibility toggle
 * Used by: login.html, register.html
 */
function togglePassword(fieldId) {
    'use strict';

    const field = document.getElementById(fieldId);
    const icon = document.getElementById(fieldId + '-icon');
    if (!field || !icon) return;

    if (field.type === 'password') {
        field.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        field.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}
