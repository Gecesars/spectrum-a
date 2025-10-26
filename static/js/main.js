document.addEventListener('DOMContentLoaded', () => {
    const timestampElement = document.querySelector('[data-current-year]');
    if (timestampElement) {
        timestampElement.textContent = new Date().getFullYear();
    }
});
