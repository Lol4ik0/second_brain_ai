document.addEventListener('DOMContentLoaded', () => {
    
    // Core Document Object Model Reference Points
    const fileItems = document.querySelectorAll('.file-item');
    const contentArea = document.getElementById('workspace-content-area');
    const mentionsFeed = document.getElementById('linked-mentions-feed');
    const backlinksLabel = document.getElementById('backlinks-counter-label');

    if (!contentArea || !mentionsFeed) return;

    /**
     * Unified Centralized Matrix Loader for Obsidian Vault Notes.
     * Can be invoked by File Explorer, internal WikiLinks, or Backlink Cards.
     */
    async function loadNoteArchitecture(noteName) {
        if (!noteName) return;

        // 1. Visual Navigation State Sync (Update Left Sidebar Highlight)
        fileItems.forEach(item => {
            if (item.getAttribute('data-filename') === noteName) {
                item.classList.add('text-[var(--active-accent)]', 'bg-[var(--active-accent)]', 'bg-opacity-10', 'shadow-[var(--glow-active)]', 'border', 'border-[var(--active-accent)]', 'border-opacity-20');
            } else {
                item.classList.remove('text-[var(--active-accent)]', 'bg-[var(--active-accent)]', 'bg-opacity-10', 'shadow-[var(--glow-active)]', 'border', 'border-[var(--active-accent)]', 'border-opacity-20');
            }
        });

        // 2. Initializing Core Loading Screen Matrix
        contentArea.innerHTML = `
            <div class="flex items-center justify-center h-full">
                <p class="text-[var(--active-accent)] animate-pulse font-mono text-sm uppercase tracking-widest">
                    Defragmenting Vault Node Content: ${noteName}...
                </p>
            </div>
        `;

        try {
            // 3. Dispatching Request Pipeline to Django Backend API Router
            const response = await fetch(`/api/get-note/?name=${encodeURIComponent(noteName)}`);
            const data = await response.json();

            if (data.status === 'ok') {
                // 4. Inject parsed Markdown HTML Content inside main viewport
                contentArea.innerHTML = `
                    <header class="mb-8 border-b border-[var(--border-glass)] pb-6">
                        <h1 class="text-3xl lg:text-4xl font-bold text-[var(--text-primary)] mb-2 tracking-tight">${noteName}</h1>
                        <p class="text-xs text-[var(--active-accent)] opacity-80 uppercase tracking-widest font-mono font-semibold">
                            Secure Sandbox Node Sync Matrix
                        </p>
                    </header>
                    <div class="text-[var(--text-secondary)] leading-relaxed space-y-6 markdown-body">
                        ${data.html_content}
                    </div>
                `;

                // 5. Build and Inject Dynamic Backlinks Entities Layout
                mentionsFeed.innerHTML = '';
                const totalBacklinks = data.backlinks.length;
                backlinksLabel.textContent = `${totalBacklinks} note${totalBacklinks === 1 ? '' : 's'} link here`;

                if (totalBacklinks > 0) {
                    data.backlinks.forEach(mention => {
                        const cardHtml = `
                            <article class="backlink-card p-4 rounded-xl border border-[var(--border-glass)] hover:border-[var(--active-accent)] hover:shadow-[var(--glow-active)] transition-all cursor-pointer bg-[var(--bg-base)] bg-opacity-40 hover:-translate-y-0.5" data-target="${mention.title}">
                                <h4 class="font-medium text-[var(--text-primary)] text-sm mb-1 truncate">${mention.title}</h4>
                                <p class="text-[11px] opacity-60 leading-relaxed font-serif italic">${mention.snippet}</p>
                            </article>
                        `;
                        mentionsFeed.insertAdjacentHTML('beforeend', cardHtml);
                    });
                } else {
                    mentionsFeed.innerHTML = `
                        <div class="p-4 rounded-xl border border-dashed border-[var(--border-glass)] text-center text-xs opacity-50 italic">
                            No active backlinks mapped for this node.
                        </div>
                    `;
                }

            } else {
                // Handle Backend Runtime Errors gracefully
                contentArea.innerHTML = `
                    <div class="p-5 bg-red-500 bg-opacity-10 border border-red-500 border-opacity-20 rounded-xl text-red-400">
                        <h4 class="font-bold mb-1">Core Link Interrupted</h4>
                        <p class="text-xs opacity-80">${data.msg}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('API Transmission failure:', error);
            contentArea.innerHTML = `
                <div class="p-5 bg-red-500 bg-opacity-10 border border-red-500 border-opacity-20 rounded-xl text-red-400">
                    <h4 class="font-bold mb-1">Network Synchronization Loss</h4>
                    <p class="text-xs opacity-80">Failed to establish handshake pipeline with server cluster.</p>
                </div>
            `;
        }
    }

    // --- INTERACTION PATTERN 1: LEFT SIDEBAR DIRECTORY CLICKS ---
    fileItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetNoteName = item.getAttribute('data-filename');
            loadNoteArchitecture(targetNoteName);
        });
    });

    // --- INTERACTION PATTERN 2: CENTRAL VIEWPORT ADVANCED DELEGATION ---
    // Listens to WikiLinks dynamically injected into the note body at runtime
    contentArea.addEventListener('click', (e) => {
        const wikiLinkAnchor = e.target.closest('.wiki-link');
        if (wikiLinkAnchor) {
            e.preventDefault();
            const linkedNoteTarget = wikiLinkAnchor.getAttribute('data-note');
            loadNoteArchitecture(linkedNoteTarget);
        }
    });

    // --- INTERACTION PATTERN 3: RIGHT SIDEBAR BACKLINK CARD CLICKS ---
    // Listens to dynamic clicks on generated Mentions items cards
    mentionsFeed.addEventListener('click', (e) => {
        const backlinkCard = e.target.closest('.backlink-card');
        if (backlinkCard) {
            const historyNodeTarget = backlinkCard.getAttribute('data-target');
            loadNoteArchitecture(historyNodeTarget);
        }
    });

});