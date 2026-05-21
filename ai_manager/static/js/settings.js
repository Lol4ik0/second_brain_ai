document.addEventListener('DOMContentLoaded', () => {
    const tempSlider = document.getElementById('ai-temperature');
    const tempValue = document.getElementById('temp-value');
    const themeSelect = document.getElementById('theme-select');
    const accentRadios = document.querySelectorAll('input[name="accent-color"]');

    // Update temperature label dynamically
    if (tempSlider && tempValue) {
        tempSlider.addEventListener('input', (e) => {
            tempValue.textContent = e.target.value;
        });
    }

    // Live preview for Theme change
    if (themeSelect) {
        themeSelect.addEventListener('change', (e) => {
            document.documentElement.setAttribute('data-theme', e.target.value);
        });
    }

    // Live preview for Accent Color change
    accentRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.documentElement.setAttribute('data-accent', e.target.value);
        });
    });

    // Create and append the Save Button
    const saveBtn = document.createElement('button');
    saveBtn.type = 'button';
    saveBtn.className = 'btn-primary w-full py-3 mt-8 rounded-lg font-bold uppercase tracking-wider text-sm';
    saveBtn.textContent = 'Save System Configuration';
    
    const container = document.querySelector('.settings-container');
    if (container) container.appendChild(saveBtn);

    saveBtn.addEventListener('click', async () => {
        saveBtn.textContent = 'Saving Cores...';
        
        // Find selected accent color
        let selectedAccent = 'cyan';
        accentRadios.forEach(radio => {
            if (radio.checked) selectedAccent = radio.value;
        });

        // Build Payload
        const config = {
            display_name: document.getElementById('display-name')?.value || 'Alex Chen',
            email: document.getElementById('email-address')?.value || 'alex@example.com',
            theme: document.getElementById('theme-select')?.value || 'cyberpunk',
            accent_color: selectedAccent,
            ai_model: document.getElementById('ai-model')?.value || 'llama3',
            temperature: tempSlider?.value || 0.7,
            github_repo_url: document.getElementById('github-repo')?.value || '',
            github_token: document.getElementById('github-token')?.value || ''
        };

        try {
            const response = await fetch('/api/save-settings/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            if (data.status === 'ok') {
                saveBtn.textContent = 'Configuration Saved Successfully';
                
                // Temporarily override styles for visual feedback
                saveBtn.style.backgroundColor = 'var(--neon-green)';
                saveBtn.style.color = '#000';
                saveBtn.style.borderColor = 'var(--neon-green)';
                
                setTimeout(() => {
                    saveBtn.textContent = 'Save System Configuration';
                    saveBtn.style.backgroundColor = 'transparent';
                    saveBtn.style.color = 'var(--active-accent)';
                    saveBtn.style.borderColor = 'var(--active-accent)';
                }, 3000);
            }
        } catch (error) {
            saveBtn.textContent = 'Error Saving Configuration';
            console.error(error);
        }
    });
});