(function () {
    function block(e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
    }

    function showOverlayWarning(message) {
        if (document.getElementById('security-warning')) return;

        const warning = document.createElement('div');
        warning.id = 'security-warning';
        warning.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.96);
            color: #fff;
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            text-align: center;
            backdrop-filter: blur(2px);
        `;

        const innerHTML = `
            <div id="warning-close" style="
                position: fixed;
                top: 12px;
                right: 30px;
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                z-index: 1000000;
                background: none;
                border: none;
                padding: 0;
                margin: 0;
                line-height: 1;
            ">✕</div>
            <div>
                <div style="font-size: 3rem; color: #ff4444;">&#9888;</div>
                <div>${message || 'This action is not allowed!'}</div>
            </div>
        `;

        warning.innerHTML = innerHTML;
        document.body.appendChild(warning);

        document.getElementById('warning-close').addEventListener('click', () => {
            warning.remove();
        });
    }

    function detectDevTools() {
        const threshold = 160;
        if (
            window.outerHeight - window.innerHeight > threshold ||
            window.outerWidth - window.innerWidth > threshold
        ) {
            showOverlayWarning('DevTools is not allowed!');
        }
    }

    setInterval(() => {
        const start = performance.now();
        debugger;
        const time = performance.now() - start;
        if (time > 10) {
            showOverlayWarning('DevTools has been detected!');
        }
        detectDevTools();
    }, 500);

    document.addEventListener('contextmenu', block);
    document.addEventListener('selectstart', block);
    document.addEventListener('copy', block);
    document.addEventListener('cut', block);
    document.addEventListener('paste', block);
    document.addEventListener('dragstart', block);
    document.addEventListener('drop', block);

    document.addEventListener('keydown', function (e) {
        const k = e.key.toLowerCase();
        const combo = e.ctrlKey || e.metaKey;
        if (
            (combo && ['u', 's', 'p'].includes(k)) ||
            (combo && e.shiftKey && ['i', 'j', 'c'].includes(k)) ||
            k === 'f12'
        ) {
            block(e);
            showOverlayWarning('This action is not allowed!');
        }
    });

    window.addEventListener('resize', detectDevTools);
    detectDevTools();

    const disabledMethods = [
        'log', 'warn', 'error', 'debug', 'info',
        'trace', 'dir', 'dirxml', 'group', 'groupCollapsed',
        'groupEnd', 'time', 'timeEnd', 'timeLog', 'profile',
        'profileEnd', 'count', 'countReset', 'assert', 'clear'
    ];

    disabledMethods.forEach(method => {
        console[method] = function () {};
    });

    Object.defineProperty(window, 'console', {
        get: () => ({
            log: () => {},
            warn: () => {},
            error: () => {},
            info: () => {},
            debug: () => {}
        }),
        set: () => {}
    });
})();
