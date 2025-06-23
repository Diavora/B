document.addEventListener('DOMContentLoaded', function () {
    const tg = window.Telegram.WebApp;
    const API_BASE_URL = 'https://e68b-62-60-152-117.ngrok-free.app/api'; // Используйте ваш URL

    try {
        tg.ready();
        tg.expand();
    } catch (e) {
        console.error("Telegram WebApp is not available.", e);
        document.body.innerHTML = '<div style="text-align: center; padding: 20px;"><h1>Ошибка</h1><p>Это приложение предназначено для работы внутри Telegram.</p></div>';
        return;
    }

    // Элементы
    const buyButton = document.getElementById('buy-button');
    const confirmationModal = document.getElementById('confirmation-modal');
    const successModal = document.getElementById('success-modal');
    const errorModal = document.getElementById('error-modal');
    const confirmBuyBtn = document.getElementById('confirm-buy-button');
    const cancelBuyBtn = document.getElementById('cancel-buy-button');
    const successOkBtn = document.getElementById('success-ok-button');
    const errorOkBtn = document.getElementById('error-ok-button');

    // Данные из URL
    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('itemId');

    if (!itemId) {
        showErrorModal('Не удалось определить товар для покупки.');
        return;
    }

    // --- Логика модальных окон ---
    function showConfirmationModal() { 
        if(confirmationModal) confirmationModal.style.display = 'flex'; 
    }
    function hideConfirmationModal() { 
        if(confirmationModal) confirmationModal.style.display = 'none'; 
    }
    function showSuccessModal(message) {
        if(successModal) {
            successModal.querySelector('.modal-text').textContent = message;
            successModal.style.display = 'flex';
        }
    }
    function showErrorModal(message) {
        if (errorModal) {
            errorModal.querySelector('.modal-text').textContent = message;
            errorModal.style.display = 'flex';
        }
    }
    function hideErrorModal() { 
        if (errorModal) errorModal.style.display = 'none'; 
    }

    // --- Слушатели событий ---
    if(buyButton) buyButton.addEventListener('click', () => {
        showConfirmationModal();
    });

    if(cancelBuyBtn) cancelBuyBtn.addEventListener('click', () => {
        hideConfirmationModal();
    });

    if(errorOkBtn) errorOkBtn.addEventListener('click', () => {
        hideErrorModal();
    });

    if(successOkBtn) successOkBtn.addEventListener('click', () => {
        tg.close();
    });

    if(confirmBuyBtn) confirmBuyBtn.addEventListener('click', async () => {
        hideConfirmationModal();
        buyButton.disabled = true;
        buyButton.textContent = 'Обработка...';
        tg.HapticFeedback.impactOccurred('light');

        try {
            const response = await fetch(`${API_BASE_URL}/purchase`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    itemId: itemId,
                    initData: tg.initData
                }),
            });

            const result = await response.json();

            if (response.ok && result.status === 'ok') {
                showSuccessModal(result.message || 'Покупка совершена. Продавец скоро свяжется с вами.');
                tg.HapticFeedback.notificationOccurred('success');
                setTimeout(() => tg.close(), 3000);
            } else {
                throw new Error(result.message || 'Произошла неизвестная ошибка.');
            }

        } catch (error) {
            showErrorModal(error.message);
            tg.HapticFeedback.notificationOccurred('error');
            buyButton.disabled = false;
            buyButton.textContent = 'Подтвердить и купить';
        }
    });

    // Заполнение данных о товаре
    document.getElementById('item-name').textContent = urlParams.get('name') || 'Загрузка...';
    document.getElementById('item-description').textContent = urlParams.get('description') || '';
    document.getElementById('item-price').textContent = `${urlParams.get('price') || '...'} ₽`;
    document.getElementById('seller-username').textContent = `@${urlParams.get('seller') || '...'}`;
    const server = urlParams.get('server');
    if (server && server !== 'null') {
        document.getElementById('item-server').textContent = server;
        document.getElementById('server-details').style.display = 'flex';
    }
});
