document.addEventListener('DOMContentLoaded', function () {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    // Apply theme
    function applyTheme() {
        const root = document.documentElement;
        const theme = tg.themeParams;
        root.style.setProperty('--tg-theme-bg-color', theme.bg_color || '#f0f2f5');
        root.style.setProperty('--tg-theme-text-color', theme.text_color || '#000000');
        root.style.setProperty('--tg-theme-button-color', theme.button_color || '#007aff');
        root.style.setProperty('--tg-theme-button-text-color', theme.button_text_color || '#ffffff');
        root.style.setProperty('--tg-theme-hint-color', theme.hint_color || '#999999');
        root.style.setProperty('--tg-theme-secondary-bg-color', theme.secondary_bg_color || '#ffffff');
    }
    tg.onEvent('themeChanged', applyTheme);
    applyTheme();

    // Get context from URL
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const gameName = urlParams.get('gameName');
    const server = urlParams.get('server');

    const contextInfo = document.getElementById('context-info');
    if (gameName) {
        let contextText = `Игра: ${gameName}`;
        if (server) {
            contextText += ` | Сервер: ${server}`;
        }
        contextInfo.textContent = contextText;
    }

    const sellButton = document.getElementById('sell-button');
    const form = document.getElementById('sell-form');
    const nameInput = document.getElementById('name');
    const descInput = document.getElementById('description');
    const charCounter = document.getElementById('description-counter');
    const maxChars = descInput.getAttribute('maxlength');

    function updateCounter() {
        const currentLength = descInput.value.length;
        charCounter.textContent = `${currentLength} / ${maxChars}`;
        if (currentLength > maxChars) {
            charCounter.style.color = 'var(--tg-theme-destructive-text-color, #ff4d4d)';
        } else {
            charCounter.style.color = 'var(--tg-theme-hint-color)';
        }
    }

    descInput.addEventListener('input', updateCounter);
    updateCounter(); // Initial call
    const priceInput = document.getElementById('price');

    sellButton.addEventListener('click', function() {
        if (!nameInput.value || !descInput.value || !priceInput.value) {
            tg.HapticFeedback.notificationOccurred('error');
            tg.showAlert('Пожалуйста, заполните все поля.');
            return;
        }

        const price = parseFloat(priceInput.value);
        if (isNaN(price) || price <= 0) {
            tg.HapticFeedback.notificationOccurred('error');
            tg.showAlert('Пожалуйста, введите корректную цену.');
            return;
        }
        
        tg.HapticFeedback.impactOccurred('medium');

        const dataToSend = {
            type: 'create_item', // To distinguish from purchase
            gameId: gameId,
            server: server,
            name: nameInput.value,
            description: descInput.value,
            price: price
        };

        tg.sendData(JSON.stringify(dataToSend));

        // Show success modal
        const successModal = document.getElementById('success-modal');
        setTimeout(() => {
            successModal.classList.add('visible');
        }, 300);

        const successOkButton = document.getElementById('success-ok-button');
        successOkButton.addEventListener('click', () => {
            tg.HapticFeedback.impactOccurred('light');
            tg.close();
        });
    });
});
