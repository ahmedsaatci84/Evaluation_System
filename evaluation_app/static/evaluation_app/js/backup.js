/**
 * Database Backup Page
 * Requires window.backupConfig to be defined inline before this script:
 * {
 *   createUrl: string,
 *   messages: {
 *     backupSuccess, size, backupFailed, anError,
 *     restoreWarning, filename, dataWillBeReplaced, cannotUndo,
 *     restoring, restoreSuccess, refreshPage, restoreFailed,
 *     deleteConfirm, cannotUndoShort
 *   }
 * }
 */
(function () {
    'use strict';

    const cfg  = window.backupConfig  || {};
    const msg  = cfg.messages         || {};

    // CSRF helpers
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) return metaTag.getAttribute('content');

        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;

        return getCookie('csrftoken');
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(function (cookie) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    }

    // Create backup
    window.createBackup = function () {
        const btn               = document.getElementById('createBackupBtn');
        const progressContainer = document.getElementById('progressContainer');

        btn.disabled = true;
        btn.classList.add('creating');
        progressContainer.classList.add('active');

        fetch(cfg.createUrl || '', {
            method: 'POST',
            credentials: 'same-origin'
        })
        .then(function (response) {
            if (!response.ok) {
                return response.text().then(function (text) {
                    throw new Error('HTTP error! status: ' + response.status + ', message: ' + text);
                });
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                alert((msg.backupSuccess || 'Backup created successfully!') + '\n' + data.message + '\n' + (msg.size || 'Size:') + ' ' + data.size_formatted);
                window.location.reload();
            } else {
                alert((msg.backupFailed || 'Backup failed:') + ' ' + data.error);
                btn.disabled = false;
                btn.classList.remove('creating');
                progressContainer.classList.remove('active');
            }
        })
        .catch(function (error) {
            console.error('Backup error:', error);
            alert((msg.anError || 'An error occurred:') + ' ' + error.message);
            btn.disabled = false;
            btn.classList.remove('creating');
            progressContainer.classList.remove('active');
        });
    };

    // Confirm and restore backup
    window.confirmRestore = function (filename) {
        var confirmMsg =
            (msg.restoreWarning      || 'WARNING: This will restore the database from the selected backup!') + '\n\n' +
            (msg.filename            || 'Filename:') + ' ' + filename + '\n\n' +
            (msg.dataWillBeReplaced  || 'All current data will be replaced with data from this backup!') + '\n\n' +
            (msg.cannotUndo          || 'This action cannot be undone! Are you sure you want to continue?');

        if (!confirm(confirmMsg)) return;

        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'alert alert-warning position-fixed top-50 start-50 translate-middle';
        loadingMsg.style.zIndex = '9999';
        loadingMsg.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + (msg.restoring || 'Restoring database... Please wait...');
        document.body.appendChild(loadingMsg);

        fetch('/database-backup/restore/' + filename + '/', {
            method: 'POST',
            credentials: 'same-origin'
        })
        .then(function (response) {
            if (!response.ok) {
                return response.text().then(function (text) {
                    throw new Error('HTTP error! status: ' + response.status + ', message: ' + text);
                });
            }
            return response.json();
        })
        .then(function (data) {
            document.body.removeChild(loadingMsg);
            if (data.success) {
                alert((msg.restoreSuccess || 'Database restored successfully!') + '\n' + data.message + '\n\n' + (msg.refreshPage || 'Please refresh the page.'));
                window.location.reload();
            } else {
                alert((msg.restoreFailed || 'Restore failed:') + ' ' + data.error);
            }
        })
        .catch(function (error) {
            if (document.body.contains(loadingMsg)) document.body.removeChild(loadingMsg);
            console.error('Restore error:', error);
            alert((msg.anError || 'An error occurred:') + ' ' + error.message);
        });
    };

    // Confirm and delete backup
    window.confirmDelete = function (filename) {
        var confirmMsg =
            (msg.deleteConfirm   || 'Are you sure you want to delete this backup?') + '\n\n' +
            filename + '\n\n' +
            (msg.cannotUndoShort || 'This action cannot be undone!');

        if (!confirm(confirmMsg)) return;

        const form = document.getElementById('deleteBackupForm');
        form.action = '/database-backup/delete/' + filename + '/';
        form.submit();
    };

    // Auto-hide Bootstrap alerts after 5 s
    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
})();
