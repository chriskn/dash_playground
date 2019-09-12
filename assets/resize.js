document.body.addEventListener('click', function (evt) {
    if (evt.target.className === 'summary') {
        window.dispatchEvent(new Event('resize'));
    }
}, false);