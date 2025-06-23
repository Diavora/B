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
    const sellForm = document.getElementById('sell-form');
    const sellButton = document.getElementById('sell-button');
    const successModal = document.getElementById('success-modal');
    const errorModal = document.getElementById('error-modal');
    const successOkBtn = document.getElementById('success-ok-button');
    const errorOkBtn = document.getElementById('error-ok-button');
    const descriptionCounter = document.getElementById('description-counter');
    const descriptionTextarea = document.getElementById('description');

    // Данные из URL
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const gameName = urlParams.get('gameName');
    const server = urlParams.get('server');

    // --- Логика модальных окон ---
    function showSuccessModal(message) {
        if(successModal) {
            successModal.querySelector('.modal-text').textContent = message;
            successModal.style.display = 'flex';
        }
    }
    function showErrorModal(message) {
        if(errorModal) {
            errorModal.querySelector('.modal-text').textContent = message;
            errorModal.style.display = 'flex';
        }
    }
    function hideErrorModal() { 
        if(errorModal) errorModal.style.display = 'none'; 
    }

    // --- Слушатели событий ---
    if(sellButton) sellButton.addEventListener('click', () => {
        if(sellForm) sellForm.requestSubmit(); // Вызывает событие 'submit'
    });

    if(sellForm) sellForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        sellButton.disabled = true;
        sellButton.textContent = 'Публикация...';
        tg.HapticFeedback.impactOccurred('light');

        const itemData = {
            gameId: gameId,
            server: server,
            name: document.getElementById('name').value,
            description: document.getElementById('description').value,
            price: document.getElementById('price').value
        };

        try {
            const response = await fetch(`${API_BASE_URL}/sell`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    itemData: itemData,
                    initData: tg.initData
                }),
            });

            const result = await response.json();

            if (response.ok && result.status === 'ok') {
                showSuccessModal(result.message || 'Ваше объявление успешно создано.');
                tg.HapticFeedback.notificationOccurred('success');
                setTimeout(() => tg.close(), 3000);
            } else {
                throw new Error(result.message || 'Произошла ошибка при выставлении товара.');
            }

        } catch (error) {
            showErrorModal(error.message);
            tg.HapticFeedback.notificationOccurred('error');
            sellButton.disabled = false;
            sellButton.textContent = 'Выставить на продажу';
        }
    });

    if(errorOkBtn) errorOkBtn.addEventListener('click', () => {
        hideErrorModal();
    });

    if(successOkBtn) successOkBtn.addEventListener('click', () => {
        tg.close();
    });
    
    // Счетчик символов для описания
    if(descriptionTextarea) descriptionTextarea.addEventListener('input', () => {
        const maxLength = descriptionTextarea.maxLength;
        const currentLength = descriptionTextarea.value.length;
        if(descriptionCounter) descriptionCounter.textContent = `${currentLength}/${maxLength}`;
    });

    // Заполнение контекстной информации
    const contextInfo = document.getElementById('context-info');
    if (contextInfo && gameName) {
        let infoText = `Игра: <b>${gameName}</b>`;
        if (server && server !== 'null') {
            infoText += `, Сервер: <b>${server}</b>`;
        }
        contextInfo.innerHTML = infoText;
    }
});
