document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Handle Task Checkbox Toggling
    const checkboxes = document.querySelectorAll('.task-checkbox');
    checkboxes.forEach(box => {
        box.addEventListener('change', async (e) => {
            const taskId = e.target.getAttribute('data-id');
            const newStatus = e.target.checked ? 'done' : 'todo';
            
            try {
                const response = await fetch('/api/update-task/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_id: taskId, status: newStatus })
                });
                
                if (response.ok) {
                    // Reload the page to move the task between lists visually
                    window.location.reload(); 
                }
            } catch (error) {
                console.error('Error updating task:', error);
                e.target.checked = !e.target.checked; // Revert visually on error
            }
        });
    });

    // 2. Handle Adding a New Task via the Modal
    const addTaskForm = document.getElementById('add-task-form');
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const payload = {
                title: document.getElementById('task-title').value,
                priority: document.getElementById('task-priority').value,
                due_date: document.getElementById('task-date').value,
                tags: document.getElementById('task-tags').value
            };

            try {
                const response = await fetch('/api/add-task/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (response.ok) {
                    // Close modal and refresh to show new task
                    document.getElementById('task-modal').classList.add('hidden');
                    window.location.reload();
                }
            } catch (error) {
                console.error('Error creating task:', error);
                alert("Failed to create task.");
            }
        });
    }
});