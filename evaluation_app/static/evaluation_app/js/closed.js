/**
 * System Closed / Maintenance Page
 * Handles theme toggle and language switcher dropdown.
 */
(function () {
    'use strict';

    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);

        themeToggle.addEventListener('click', function () {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Language Switcher
    const languageToggle   = document.getElementById('language-toggle');
    const languageDropdown = document.getElementById('language-dropdown');
    if (languageToggle && languageDropdown) {
        languageToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            languageDropdown.classList.toggle('active');
        });

        document.addEventListener('click', function () {
            languageDropdown.classList.remove('active');
        });

        languageDropdown.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }
})();
