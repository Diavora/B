document.addEventListener('DOMContentLoaded', function () {
    const tg = window.Telegram.WebApp;
    const API_BASE_URL = '/api';

    try {
        tg.ready();
        tg.expand();
    } catch (e) {
        console.error("Telegram WebApp is not available.", e);
        document.body.innerHTML = '<div style="text-align: center; padding: 20px;"><h1>Ошибка</h1><p>Это приложение предназначено для работы внутри Telegram.</p></div>';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const gameName = urlParams.get('gameName');
    const server = urlParams.get('server');

    const gameInfoDiv = document.getElementById('game-info');
    if (gameName) {
        let infoText = `Игра: <b>${gameName}</b>`;
        if (server) {
            infoText += `, Сервер: <b>${server}</b>`;
        }
        gameInfoDiv.innerHTML = infoText;
    }

    const sellForm = document.getElementById('sell-form');
    const submitButton = sellForm.querySelector('button[type="submit"]');

    sellForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = 'Публикация...';

        const formData = new FormData(sellForm);
        const itemData = {
            gameId: gameId,
            server: server,
            name: formData.get('name'),
            description: formData.get('description'),
            price: formData.get('price')
        };

        try {
            const response = await fetch(`${API_BASE_URL}/sell`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    itemData: itemData,
                    initData: tg.initData
                }),
            });

            const result = await response.json();

            if (response.ok && result.status === 'ok') {
                showModal('Успешно!', result.message, true);
                tg.HapticFeedback.notificationOccurred('success');
                setTimeout(() => tg.close(), 2000);
            } else {
                throw new Error(result.message || 'Произошла ошибка при выставлении товара.');
            }

        } catch (error) {
            showModal('Ошибка', error.message);
            tg.HapticFeedback.notificationOccurred('error');
            submitButton.disabled = false;
            submitButton.textContent = 'Выставить на продажу';
        }
    });

    const modal = document.getElementById('feedback-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const closeButton = document.querySelector('.close-button');

    function showModal(title, message, isSuccess = false) {
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        modal.style.display = 'block';
        modal.className = isSuccess ? 'modal success' : 'modal error';
    }

    closeButton.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});
