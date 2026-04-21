/**
 * Dashboard Page — system status toggle confirmation
 * The toggle form must carry a data-confirm-message attribute
 * with the already-translated confirmation string.
 */
function confirmToggle(form) {
    'use strict';
    const message = (form && form.dataset.confirmMessage) || 'Are you sure?';
    return confirm(message);
}
