/*
 * Shared responsive navigation controller loaded by the base template.
 * It connects the mobile menu buttons to the sidebar's translate utility classes;
 * desktop visibility is controlled by responsive classes in the template.
 */
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('main-sidebar');
    const openBtn = document.getElementById('mobile-menu-open');
    const closeBtn = document.getElementById('mobile-menu-close');

    // Guard each interaction so pages without a rendered sidebar remain safe.
    if (openBtn && sidebar) {
        openBtn.addEventListener('click', () => {
            sidebar.classList.remove('-translate-x-full');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
        });
    }
});