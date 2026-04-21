/**
 * Shared Live Search with Debounce
 * Used by: professor/list, participant/list, location/list,
 *          contact/list, course/list, components/search
 */
(function () {
    'use strict';

    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const searchLoading = document.getElementById('searchLoading');
    let debounceTimer;

    if (searchInput && searchForm) {
        searchInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            if (searchLoading) searchLoading.classList.add('active');

            debounceTimer = setTimeout(function () {
                searchForm.submit();
            }, 500);
        });
    }
})();
