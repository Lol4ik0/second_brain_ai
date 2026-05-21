document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.chat-input-form');
    const input = document.getElementById('chat-input');
    const chatFeed = document.getElementById('chat-feed');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = input.value.trim();
        if (!message) return;

        // Draw User message
        appendMessage('user', message);
        input.value = '';

        // Draw AI loading placeholder
        const loadingId = appendMessage('ai', 'Processing logical cores...');

        try {
            const response = await fetch('/api/send-message/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            updateMessage(loadingId, data.reply || data.message);
            
        } catch (error) {
            updateMessage(loadingId, '❌ Connection to local AI core failed.');
            console.error(error);
        }
    });

    function appendMessage(sender, text) {
        const id = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const isAI = sender === 'ai';
        const avatar = isAI ? '✨' : '👤';
        
        // Use Tailwind / Glassmorphism logic based on sender
        const alignmentClass = isAI ? 'self-start' : 'self-end flex-row-reverse';
        const bubbleStyle = isAI 
            ? 'rounded-tl-none border-[var(--active-accent)] shadow-[var(--glow-active)]' 
            : 'rounded-tr-none bg-[var(--active-accent)] bg-opacity-10 border border-[var(--active-accent)]';

        const html = `
            <article class="flex gap-4 w-full ${alignmentClass}" id="${id}">
                <div class="text-2xl mt-1">${avatar}</div>
                <div class="glass-card rounded-2xl p-4 max-w-[85%] ${bubbleStyle}">
                    <p class="text-[var(--text-primary)] leading-relaxed">${text.replace(/\n/g, '<br>')}</p>
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
            msgEl.querySelector('p').innerHTML = text.replace(/\n/g, '<br>');
        }
    }
    
    // Auto-resize textarea and submit on Enter
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.requestSubmit();
            }
        });

        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            if(this.value === '') this.style.height = '60px'; // Reset to min-height
        });
    }
});