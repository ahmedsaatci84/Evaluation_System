/**
 * Logout Confirmation Page
 * Requires data attributes on #logout-form:
 *   data-cancel-url  — URL to redirect when user presses Escape
 *   data-logout-text — Translated "Logging out…" string
 */
(function () {
    'use strict';

    // Live clock
    function updateTime() {
        const now = new Date();
        const el = document.getElementById('current-time');
        if (el) {
            el.textContent = now.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
    }

    updateTime();
    setInterval(updateTime, 1000);

    // Form submit loading state
    const logoutForm = document.getElementById('logout-form');
    if (!logoutForm) return;

    const cancelUrl  = logoutForm.dataset.cancelUrl  || '/';
    const logoutText = logoutForm.dataset.logoutText || 'Logging out…';

    logoutForm.addEventListener('submit', function () {
        const btn = document.getElementById('confirm-logout-btn');
        if (btn) {
            btn.classList.add('loading');
            const span = btn.querySelector('span');
            if (span) span.textContent = logoutText;
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            window.location.href = cancelUrl;
        }
        if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
            e.preventDefault();
            logoutForm.submit();
        }
    });
})();
