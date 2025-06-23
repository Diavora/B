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
    const itemId = urlParams.get('itemId');

    if (!itemId) {
        showModal('Ошибка', 'Не удалось определить товар для покупки.');
        return;
    }

    const item = {
        id: itemId,
        name: urlParams.get('name') || 'Название товара',
        price: urlParams.get('price') || '0',
        description: urlParams.get('description') || 'Описание отсутствует.',
        image: urlParams.get('image') || 'path/to/default/image.jpg'
    };

    document.getElementById('item-image').src = item.image;
    document.getElementById('item-name').textContent = item.name;
    document.getElementById('item-price').textContent = `${item.price} ₽`;
    document.getElementById('item-description').textContent = item.description;

    const buyButton = document.getElementById('buy-button');
    buyButton.addEventListener('click', async () => {
        buyButton.disabled = true;
        buyButton.textContent = 'Обработка...';

        try {
            const response = await fetch(`${API_BASE_URL}/purchase`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    itemId: item.id,
                    initData: tg.initData
                }),
            });

            const result = await response.json();

            if (response.ok && result.status === 'ok') {
                showModal('Успешно!', result.message, true);
                tg.HapticFeedback.notificationOccurred('success');
                setTimeout(() => tg.close(), 2000);
            } else {
                throw new Error(result.message || 'Произошла неизвестная ошибка.');
            }

        } catch (error) {
            showModal('Ошибка', error.message);
            tg.HapticFeedback.notificationOccurred('error');
            buyButton.disabled = false;
            buyButton.textContent = 'Купить';
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
