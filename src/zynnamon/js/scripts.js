const tracker = document.getElementById('tracker-count');

function updateDisplay(count) {
    tracker.textContent = count;
    tracker.style.textShadow = count > 0 ? '0 0 15px #ff5a36' : 'none';
}

function getZynCount() {
    return parseInt(localStorage.getItem('zynCount')) || 0;
}

function addZyn() {
    let count = getZynCount() + 1;
    localStorage.setItem('zynCount', count);
    updateDisplay(count);
}

function resetZyn() {
    localStorage.removeItem('zynCount');
    updateDisplay(0);
}

// On page load
updateDisplay(getZynCount());