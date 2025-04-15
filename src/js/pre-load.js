(function () {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-bs-theme', theme);
})();

const sunIconURL = 'https://cdn.samuelflavin.com/sun.svg';
const moonIconURL = 'https://cdn.samuelflavin.com/moon.svg';

// Start early fetch
const sunIconPromise = fetch(sunIconURL).then(r => r.text());
const moonIconPromise = fetch(moonIconURL).then(r => r.text());

// Store them for later use (e.g., in DOMContentLoaded or toggle)
window._svgCache = {
    sun: sunIconPromise,
    moon: moonIconPromise
};