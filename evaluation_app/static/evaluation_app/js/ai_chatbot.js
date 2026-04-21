/**
 * AI Chatbot Widget
 * Reads API URLs from data attributes on #ai-chatbot-widget:
 *   data-status-url  — URL for GET /ai/status/
 *   data-chat-url    — URL for POST /ai/chat/
 */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    const widget     = document.getElementById('ai-chatbot-widget');
    if (!widget) return;

    const aiStatusUrl = widget.dataset.statusUrl || '';
    const aiChatUrl   = widget.dataset.chatUrl   || '';

    const chatToggle   = document.getElementById('ai-chat-toggle');
    const chatWindow   = document.getElementById('ai-chat-window');
    const chatClose    = document.getElementById('ai-chat-close');
    const chatMinimize = document.getElementById('ai-chat-minimize');
    const chatInput    = document.getElementById('ai-chat-input');
    const chatSend     = document.getElementById('ai-chat-send');
    const chatBody     = document.getElementById('ai-chat-body');
    const statusBadge  = document.getElementById('ai-status-badge');

    // Check AI availability
    if (aiStatusUrl) {
        fetch(aiStatusUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.available && statusBadge) statusBadge.classList.add('offline');
            })
            .catch(function () {
                if (statusBadge) statusBadge.classList.add('offline');
            });
    }

    // Toggle chat window
    chatToggle.addEventListener('click', function () {
        chatWindow.classList.toggle('active');
    });

    chatClose.addEventListener('click', function () {
        chatWindow.classList.remove('active');
    });

    chatMinimize.addEventListener('click', function () {
        chatWindow.classList.remove('active');
    });

    // Send message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addUserMessage(message);
        chatInput.value = '';
        showTypingIndicator();

        fetch(aiChatUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ question: message })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            removeTypingIndicator();
            if (data.response) {
                addAIMessage(data.response);
            } else if (data.error) {
                addAIMessage('Sorry, I encountered an error: ' + data.error);
            }
        })
        .catch(function () {
            removeTypingIndicator();
            addAIMessage("Sorry, I couldn't process your request. Please try again.");
        });
    }

    chatSend.addEventListener('click', sendMessage);

    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Quick action buttons
    document.querySelectorAll('.ai-quick-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            chatInput.value = this.dataset.question;
            sendMessage();
        });
    });

    // Helpers
    function addUserMessage(text) {
        const div = document.createElement('div');
        div.className = 'user-message';
        div.innerHTML = '<div class="ai-message"><p>' + escapeHtml(text) + '</p></div>';
        chatBody.appendChild(div);
        scrollToBottom();
    }

    function addAIMessage(text) {
        const div = document.createElement('div');
        div.className = 'ai-response';
        div.innerHTML =
            '<div class="ai-avatar"><i class="fas fa-robot"></i></div>' +
            '<div class="ai-message"><p>' + escapeHtml(text) + '</p></div>';
        chatBody.appendChild(div);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'ai-typing';
        div.id = 'ai-typing-indicator';
        div.innerHTML =
            '<div class="ai-avatar"><i class="fas fa-robot"></i></div>' +
            '<div class="ai-typing-indicator">' +
            '<span class="ai-typing-dot"></span>' +
            '<span class="ai-typing-dot"></span>' +
            '<span class="ai-typing-dot"></span>' +
            '</div>';
        chatBody.appendChild(div);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const el = document.getElementById('ai-typing-indicator');
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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
});
