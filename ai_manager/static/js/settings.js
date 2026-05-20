document.addEventListener('DOMContentLoaded', () => {
    const tempSlider = document.getElementById('ai-temperature');
    const tempValue = document.getElementById('temp-value');

    // Обновление цифры температуры при движении ползунка
    if (tempSlider && tempValue) {
        tempSlider.addEventListener('input', (e) => {
            tempValue.textContent = e.target.value;
        });
    }

    // Создаем кнопку сохранения
    const saveBtn = document.createElement('button');
    saveBtn.type = 'button';
    saveBtn.className = 'btn-primary';
    saveBtn.style.marginTop = '2rem';
    saveBtn.style.width = '100%';
    saveBtn.textContent = 'SAVE SYSTEM CONFIGURATION';
    
    const container = document.querySelector('.settings-container');
    if (container) container.appendChild(saveBtn);

    saveBtn.addEventListener('click', async () => {
        saveBtn.textContent = 'SAVING CORES...';
        
        const config = {
            display_name: document.getElementById('display-name')?.value || 'Alex Chen',
            email: document.getElementById('email-address')?.value || 'alex.chen@example.com',
            theme: document.getElementById('theme-select')?.value || 'cyberpunk',
            ai_model: document.getElementById('ai-model')?.value || 'llama3',
            temperature: tempSlider?.value || 0.7
        };

        try {
            const response = await fetch('/api/save-settings/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            if (data.status === 'ok') {
                saveBtn.textContent = 'CONFIGURATION SAVED SUCCESSFULLY';
                saveBtn.style.borderColor = 'var(--neon-green)';
                saveBtn.style.color = 'var(--neon-green)';
                
                setTimeout(() => {
                    saveBtn.textContent = 'SAVE SYSTEM CONFIGURATION';
                    saveBtn.style.borderColor = 'var(--neon-cyan)';
                    saveBtn.style.color = 'var(--neon-cyan)';
                }, 3000);
            }
        } catch (error) {
            saveBtn.textContent = 'ERROR SAVING CONFIGURATION';
            console.error(error);
        }
    });
});