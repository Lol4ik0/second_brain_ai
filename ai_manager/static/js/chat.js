document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.chat-input-form');
    const input = document.getElementById('chat-input');
    const chatFeed = document.querySelector('.chat-feed');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = input.value.trim();
        if (!message) return;

        // Рисуем сообщение пользователя
        appendMessage('user', message);
        input.value = '';

        // Рисуем заглушку ИИ с УНИКАЛЬНЫМ ID
        const loadingId = appendMessage('ai', 'Thinking... (это может занять время)');

        try {
            const response = await fetch('/api/send-message/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            updateMessage(loadingId, data.reply || data.message);
            
        } catch (error) {
            updateMessage(loadingId, '❌ Ошибка соединения с локальной моделью.');
            console.error(error);
        }
    });

    function appendMessage(sender, text) {
        // Гарантированно уникальный ID
        const id = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const isAI = sender === 'ai';
        const avatar = isAI ? '✨' : '👤';
        const msgClass = isAI ? 'ai-message' : 'user-message';
        
        const html = `
            <article class="message ${msgClass}" id="${id}">
                <div class="message-avatar">${avatar}</div>
                <div class="message-bubble">
                    <p>${text.replace(/\n/g, '<br>')}</p>
                </div>
            </article>
        `;
        chatFeed.insertAdjacentHTML('beforeend', html);
        chatFeed.scrollTop = chatFeed.scrollHeight;
        return id;
    }

    function updateMessage(id, text) {
        const msgEl = document.getElementById(id);
        if (msgEl) {
            msgEl.querySelector('.message-bubble p').innerHTML = text.replace(/\n/g, '<br>');
        }
    }
    
    // Отправка по Enter
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });
    }
});