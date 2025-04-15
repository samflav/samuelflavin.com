(function () {
    const currentPath = window.location.pathname.replace(/\/$/, '');

    document.addEventListener('DOMContentLoaded', () => {
        const parent = document.querySelector('#navbarContent');
        if (!parent) return;

        const links = parent.querySelectorAll('a');

        links.forEach(link => {
            const linkPath = new URL(link.href).pathname.replace(/\/$/, '');
            if (linkPath === currentPath) {
                link.classList.add('active');
            }
        });
    });
})();