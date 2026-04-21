/**
 * Evaluation List — client-side instant search with Arabic normalisation
 * Requires window.evaluationSearchConfig to be defined inline before this script:
 * {
 *   forText, noResultsTitle, noResultsMessage,
 *   tipKeywords, tipSpelling, tipFewer, tipArabic
 * }
 */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    const cfg = window.evaluationSearchConfig || {};

    const searchInput = document.getElementById('instantSearch');
    const clearBtn    = document.getElementById('clearSearch');
    const searchStats = document.getElementById('searchStats');
    const matchCount  = document.getElementById('matchCount');
    const searchTerm  = document.getElementById('searchTerm');
    const tableBody   = document.querySelector('table tbody');
    const allRows     = tableBody ? Array.from(tableBody.querySelectorAll('tr')) : [];
    const totalRows   = allRows.length;

    // Normalise Arabic text for better matching
    function normalizeArabic(text) {
        if (!text) return '';
        text = text.toLowerCase().trim();
        text = text.replace(/[\u064B-\u065F\u0670]/g, '');
        text = text.replace(/[أإآ]/g, 'ا');
        text = text.replace(/ى/g, 'ي');
        text = text.replace(/ة/g, 'ه');
        text = text.replace(/ؤ/g, 'و');
        text = text.replace(/ئ/g, 'ي');
        text = text.replace(/\s+/g, '');
        return text;
    }

    const rowData = allRows.map(function (row) {
        const cells        = row.querySelectorAll('td');
        const originalText = Array.from(cells).map(function (c) { return c.textContent.trim(); }).join(' ');
        return {
            element:      row,
            text:         normalizeArabic(originalText),
            originalText: originalText
        };
    });

    function performSearch() {
        const query = searchInput.value.trim();

        if (!query) {
            rowData.forEach(function (item) {
                item.element.style.display = '';
                item.element.style.backgroundColor = '';
            });
            if (searchStats) searchStats.style.display = 'none';
            if (clearBtn)    clearBtn.style.display = 'none';
            return;
        }

        if (clearBtn) clearBtn.style.display = 'block';

        const normalizedQuery = normalizeArabic(query);
        const searchWords     = normalizedQuery.split(/\s+/).filter(function (w) { return w.length > 0; });
        let visibleCount = 0;

        rowData.forEach(function (item) {
            const matches = searchWords.every(function (word) { return item.text.includes(word); });
            if (matches) {
                item.element.style.display = '';
                item.element.style.backgroundColor = '#fffbea';
                visibleCount++;
            } else {
                item.element.style.display = 'none';
                item.element.style.backgroundColor = '';
            }
        });

        if (matchCount)  matchCount.textContent  = visibleCount;
        if (searchTerm)  searchTerm.textContent   = (cfg.forText || 'for') + ' "' + query + '"';
        if (searchStats) searchStats.style.display = 'block';

        updateNoResultsMessage(visibleCount, query);
    }

    function updateNoResultsMessage(count, query) {
        let noResultsDiv = document.getElementById('noResultsMessage');

        if (count === 0 && query) {
            if (!noResultsDiv) {
                noResultsDiv = document.createElement('div');
                noResultsDiv.id        = 'noResultsMessage';
                noResultsDiv.className = 'alert alert-info mt-3';
                noResultsDiv.innerHTML =
                    '<h5><i class="bi bi-info-circle"></i> ' + (cfg.noResultsTitle   || 'No Results Found') + '</h5>' +
                    '<p>' + (cfg.noResultsMessage || 'No evaluations match your search. Try:') + '</p>' +
                    '<ul>' +
                    '<li>' + (cfg.tipKeywords || 'Using different keywords')                      + '</li>' +
                    '<li>' + (cfg.tipSpelling || 'Checking your spelling')                        + '</li>' +
                    '<li>' + (cfg.tipFewer    || 'Using fewer search terms')                      + '</li>' +
                    '<li>' + (cfg.tipArabic   || 'Typing without diacritics for Arabic text')     + '</li>' +
                    '</ul>';

                if (tableBody && tableBody.parentElement && tableBody.parentElement.parentElement) {
                    tableBody.parentElement.parentElement.appendChild(noResultsDiv);
                } else {
                    const tableDiv = document.querySelector('.table-responsive');
                    if (tableDiv && tableDiv.parentElement) {
                        tableDiv.parentElement.appendChild(noResultsDiv);
                    }
                }
            }
            if (noResultsDiv) noResultsDiv.style.display = 'block';
        } else if (noResultsDiv) {
            noResultsDiv.style.display = 'none';
        }
    }

    function clearSearch() {
        searchInput.value = '';
        performSearch();
        searchInput.focus();
    }

    if (searchInput) {
        searchInput.addEventListener('input', performSearch);
        if (clearBtn) clearBtn.addEventListener('click', clearSearch);
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') clearSearch();
        });
    }

    if (totalRows > 0) {
        console.log('Evaluation search initialised with ' + totalRows + ' rows.');
    }
});
