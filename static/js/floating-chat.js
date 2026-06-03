/**
 * DiagnoPet Floating Assistant
 * Reuses existing /chatbot/process, /chatbot/reset endpoints via fetch API.
 */
(function () {
    'use strict';

    // ── DOM refs ──
    const fab        = document.getElementById('dpFab');
    const popup      = document.getElementById('dpChatPopup');
    const closeBtn   = document.getElementById('dpChatClose');
    const resetBtn   = document.getElementById('dpChatReset');
    const messagesEl = document.getElementById('dpChatMessages');
    const inputEl    = document.getElementById('dpChatInput');
    const sendBtn    = document.getElementById('dpChatSend');
    const qrBox      = document.getElementById('dpQuickReplies');
    const badge      = document.getElementById('dpFabBadge');

    if (!fab || !popup) return; // guard

    let isOpen    = false;
    let isSending = false;
    let unread    = 0;

    // ── Helpers ──
    function getTime() {
        return new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
    }

    function scrollToBottom() {
        requestAnimationFrame(() => {
            messagesEl.scrollTop = messagesEl.scrollHeight;
        });
    }

    /** Lightweight markdown-ish → HTML for bot bubbles */
    function formatBotText(text) {
        // Escape HTML
        let s = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        // Bold **text**
        s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Italic *text* (but not inside **)
        s = s.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
        // Bullets: lines starting with • or -
        s = s.replace(/^([•\-])\s+(.*)$/gm, '<span class="fc-bullet">$1 $2</span>');
        // Emoji headers 🏥 📋 etc already look fine
        // Newlines → <br>
        s = s.replace(/\n/g, '<br>');
        return s;
    }

    // ── Bubble builders ──
    function addBotMessage(text) {
        const group = document.createElement('div');
        group.className = 'fc-msg fc-msg-bot fc-animate';
        group.innerHTML = `
            <div class="fc-avatar fc-avatar-bot"><i class="bi bi-robot"></i></div>
            <div class="fc-bubble fc-bubble-bot">${formatBotText(text)}<div class="fc-time">${getTime()}</div></div>`;
        messagesEl.appendChild(group);
        scrollToBottom();
    }

    function addUserMessage(text) {
        const group = document.createElement('div');
        group.className = 'fc-msg fc-msg-user fc-animate';
        const escaped = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
        group.innerHTML = `
            <div class="fc-bubble fc-bubble-user">${escaped}<div class="fc-time fc-time-user">${getTime()}</div></div>
            <div class="fc-avatar fc-avatar-user"><i class="bi bi-person-fill"></i></div>`;
        messagesEl.appendChild(group);
        scrollToBottom();
    }

    function showTyping() {
        const el = document.createElement('div');
        el.className = 'fc-msg fc-msg-bot fc-animate';
        el.id = 'dpTyping';
        el.innerHTML = `
            <div class="fc-avatar fc-avatar-bot"><i class="bi bi-robot"></i></div>
            <div class="fc-bubble fc-bubble-bot fc-typing-bubble">
                <div class="fc-typing"><span></span><span></span><span></span></div>
            </div>`;
        messagesEl.appendChild(el);
        scrollToBottom();
    }

    function hideTyping() {
        const el = document.getElementById('dpTyping');
        if (el) el.remove();
    }

    // ── Quick replies ──
    function renderQuickReplies(list) {
        qrBox.innerHTML = '';
        if (!list || list.length === 0) {
            qrBox.style.display = 'none';
            return;
        }
        list.forEach(text => {
            const btn = document.createElement('button');
            btn.className = 'fc-qr-btn';
            btn.textContent = text;
            btn.addEventListener('click', () => sendMessage(text));
            qrBox.appendChild(btn);
        });
        qrBox.style.display = 'flex';
    }

    // ── Badge ──
    function updateBadge() {
        if (unread > 0 && !isOpen) {
            badge.textContent = unread > 9 ? '9+' : unread;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }

    // ── Send message via fetch ──
    async function sendMessage(text) {
        if (isSending || !text.trim()) return;

        const msg = text.trim();
        addUserMessage(msg);
        renderQuickReplies([]);
        inputEl.value = '';
        inputEl.focus();
        isSending = true;

        showTyping();

        try {
            const fd = new FormData();
            fd.append('message', msg);

            const res = await fetch('/chatbot/process', { method: 'POST', body: fd });
            const data = await res.json();

            hideTyping();

            if (data.response) {
                addBotMessage(data.response);
                if (!isOpen) { unread++; updateBadge(); }
            }
            if (data.quick_replies) {
                renderQuickReplies(data.quick_replies);
            }
        } catch (err) {
            hideTyping();
            addBotMessage('⚠️ Terjadi kesalahan koneksi. Silakan coba lagi.');
        }
        isSending = false;
    }

    // ── Reset session ──
    async function resetChat() {
        messagesEl.innerHTML = '';
        renderQuickReplies([]);

        try {
            await fetch('/chatbot/reset', { method: 'POST' });
        } catch (_) { /* silent */ }

        addWelcomeMessage();
    }

    // ── Welcome ──
    function addWelcomeMessage() {
        addBotMessage(
            "Halo! 👋\n\n" +
            "Ceritakan gejala yang dialami hewan Anda.\n\n" +
            "**Contoh:**\n" +
            "• Anjing saya batuk dan pilek\n" +
            "• Kucing saya lesu dan tidak mau makan\n" +
            "• Hewan saya muntah dan diare\n\n" +
            "Saya akan membantu menganalisis kemungkinan penyakit menggunakan sistem pakar **Naive Bayes**."
        );
    }

    // ── Toggle open / close ──
    function openChat() {
        isOpen = true;
        popup.classList.add('fc-open');
        fab.classList.add('fc-fab-hidden');
        unread = 0;
        updateBadge();
        inputEl.focus();

        // First open → show welcome
        if (messagesEl.children.length === 0) {
            addWelcomeMessage();
        }
        scrollToBottom();
    }

    function closeChat() {
        isOpen = false;
        popup.classList.remove('fc-open');
        fab.classList.remove('fc-fab-hidden');
    }

    // ── Event listeners ──
    fab.addEventListener('click', openChat);
    closeBtn.addEventListener('click', closeChat);
    resetBtn.addEventListener('click', resetChat);

    sendBtn.addEventListener('click', () => sendMessage(inputEl.value));

    inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputEl.value);
        }
    });

    // Close on ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isOpen) closeChat();
    });

})();
