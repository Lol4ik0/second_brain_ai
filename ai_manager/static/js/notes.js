document.addEventListener('DOMContentLoaded', () => {
    // Select all note items in the sidebar directory tree
    const noteItems = document.querySelectorAll('.directory-tree li.cursor-pointer');
    
    // Select the main article container where the content is rendered
    const contentArea = document.querySelector('article'); 

    if (!noteItems || !contentArea) return;

    noteItems.forEach(item => {
        item.addEventListener('click', async (e) => {
            // 1. Extract the actual filename (removing emojis/icons if any)
            // Using textContent and trimming whitespace
            const noteName = item.textContent.replace('📄', '').trim();

            if (!noteName) return;

            // 2. Visual Update: Remove active styling from all items
            noteItems.forEach(node => {
                node.classList.remove(
                    'text-[var(--active-accent)]', 
                    'bg-[var(--active-accent)]', 
                    'bg-opacity-10', 
                    'shadow-[var(--glow-active)]', 
                    'border', 
                    'border-[var(--active-accent)]', 
                    'border-opacity-20'
                );
            });

            // 3. Visual Update: Add active styling to the clicked item
            item.classList.add(
                'text-[var(--active-accent)]', 
                'bg-[var(--active-accent)]', 
                'bg-opacity-10', 
                'shadow-[var(--glow-active)]', 
                'border', 
                'border-[var(--active-accent)]', 
                'border-opacity-20'
            );

            // 4. Show a loading state in the main content area
            contentArea.innerHTML = `
                <div class="flex items-center justify-center h-full">
                    <p class="text-[var(--active-accent)] animate-pulse font-bold tracking-widest uppercase">
                        Fetching Core Data...
                    </p>
                </div>
            `;

            // 5. Fetch the parsed HTML content from the Django API
            try {
                const response = await fetch(`/api/get-note/?name=${encodeURIComponent(noteName)}`);
                const data = await response.json();
                
                if (data.status === 'ok') {
                    // Render the injected HTML payload securely
                    contentArea.innerHTML = `
                        <header class="mb-8 border-b border-[var(--border-glass)] pb-6">
                            <h1 class="text-3xl lg:text-4xl font-bold text-[var(--text-primary)] mb-2 tracking-tight">${noteName}</h1>
                            <p class="text-xs text-[var(--active-accent)] opacity-80 uppercase tracking-widest font-semibold">
                                Synchronized from Matrix
                            </p>
                        </header>
                        
                        <div class="text-[var(--text-secondary)] leading-relaxed space-y-6 markdown-body">
                            ${data.html_content}
                        </div>
                    `;
                } else {
                    // Handle logical backend errors
                    contentArea.innerHTML = `
                        <div class="p-6 bg-red-500 bg-opacity-10 border border-red-500 border-opacity-30 rounded-xl">
                            <h3 class="text-red-400 font-bold mb-2">System Error</h3>
                            <p class="text-sm opacity-80">${data.msg}</p>
                        </div>
                    `;
                }
            } catch (error) {
                // Handle network or execution errors
                console.error('Core API transmission failure:', error);
                contentArea.innerHTML = `
                    <div class="p-6 bg-red-500 bg-opacity-10 border border-red-500 border-opacity-30 rounded-xl">
                        <h3 class="text-red-400 font-bold mb-2">Connection Lost</h3>
                        <p class="text-sm opacity-80">Failed to establish connection with the central database.</p>
                    </div>
                `;
            }
        });
    });
});