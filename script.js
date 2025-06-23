document.addEventListener('DOMContentLoaded', function () {
    const tg = window.Telegram.WebApp;

    // Inform Telegram that the app is ready
    tg.ready();
    tg.expand();

    // --- THEME SETUP ---
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

    // --- DATA POPULATION ---
    const urlParams = new URLSearchParams(window.location.search);
    const params = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('itemId');
    const itemName = params.get('name') || 'Название не найдено';
    const itemDescription = params.get('description') || 'Описание не найдено.';
    const itemPrice = params.get('price') || '0';
    const itemServer = params.get('server'); // Can be null
    const sellerUsername = params.get('seller') || 'Sacred Store';

    // Simulate loading delay for better visual effect
    setTimeout(() => {
        const nameEl = document.getElementById('item-name');
        const descEl = document.getElementById('item-description');
        const descEl2 = document.getElementById('item-description-2');
        const priceEl = document.getElementById('item-price');
        const serverEl = document.getElementById('item-server');
        const sellerEl = document.getElementById('seller-username');

        nameEl.textContent = itemName;
        descEl.textContent = itemDescription;
        priceEl.textContent = `${parseFloat(itemPrice).toLocaleString('ru-RU')} ₽`;
        sellerEl.textContent = `@${sellerUsername}`;

        // Handle server display
        const serverDetails = document.getElementById('server-details');
        if (itemServer && itemServer !== 'None' && itemServer !== 'null') {
            serverEl.textContent = itemServer;
            serverDetails.style.display = 'flex';
        } else {
            serverDetails.style.display = 'none';
        }

        // Remove all skeleton classes
        document.querySelectorAll('.skeleton').forEach(el => el.classList.remove('skeleton'));
        descEl2.style.display = 'none'; // Hide the second skeleton line for description

    }, 300); // 300ms delay

    // --- MODAL & BUTTON LOGIC ---
    const buyButton = document.getElementById('buy-button');
    const confirmationModal = document.getElementById('confirmation-modal');
    const successModal = document.getElementById('success-modal');
    const confirmBuyButton = document.getElementById('confirm-buy-button');
    const cancelBuyButton = document.getElementById('cancel-buy-button');
    const successOkButton = document.getElementById('success-ok-button');

    if (!itemId) {
        buyButton.disabled = true;
        buyButton.textContent = 'Ошибка: Товар не найден';
        buyButton.style.background = 'var(--tg-theme-hint-color)';
        buyButton.style.cursor = 'not-allowed';
        return;
    }

    // Show confirmation modal
    buyButton.addEventListener('click', () => {
        confirmationModal.classList.add('visible');
        tg.HapticFeedback.impactOccurred('medium');
    });

    // Hide confirmation modal on cancel
    cancelBuyButton.addEventListener('click', () => {
        confirmationModal.classList.remove('visible');
        tg.HapticFeedback.impactOccurred('light');
    });

    // Handle final purchase on confirm
    confirmBuyButton.addEventListener('click', () => {
        confirmationModal.classList.remove('visible');
        
        buyButton.disabled = true;
        buyButton.textContent = 'Обработка...';
        tg.HapticFeedback.impactOccurred('heavy');

        const dataToSend = {
            type: 'purchase_item',
            itemId: itemId 
        };
        tg.sendData(JSON.stringify(dataToSend));

        // Assume success and show the success modal
        setTimeout(() => {
            successModal.classList.add('visible');
        }, 500);
    });

    // Close web app on success
    successOkButton.addEventListener('click', () => {
        tg.HapticFeedback.impactOccurred('light');
        tg.close();
    });
});
