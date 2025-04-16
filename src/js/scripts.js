function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);

    const icon = document.querySelector('#themeIcon');
    const promise = window._svgCache[theme === 'dark' ? 'moon' : 'sun']
    promise.then((value) => {
        icon.innerHTML = value;
    })
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

setTheme(document.documentElement.getAttribute('data-bs-theme'));

document.querySelectorAll('.external-icon').forEach(el => {
    fetch(el.dataset.src)
        .then(res => res.text())
        .then(svg => {
            el.innerHTML = svg;
            el.querySelector('svg')
        });
});