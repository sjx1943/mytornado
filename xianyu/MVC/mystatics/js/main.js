// main.js
document.addEventListener('DOMContentLoaded', function() {
    function setupWebSocket() {
        const ws = new WebSocket(`ws://${window.location.host}/chat`);

        ws.onopen = function() {
            console.log("WebSocket connection established");
            displayMessage("欢迎来到聊天室");
        };

        ws.onerror = function() {
            console.log("WebSocket connection error");
        };

        ws.onmessage = function(evt) {
            const message = evt.data;
            displayMessage(message);
        };

        document.getElementById('send-button').addEventListener('click', function() {
            const msg = document.getElementById('message-input').value;
            ws.send(msg);
            document.getElementById('message-input').value = '';
            displayMessage(msg);
        });
    }

    function displayMessage(message) {
        const messageList = document.getElementById('chat-messages');
        const messageItem = document.createElement('p');
        messageItem.textContent = message;
        messageList.appendChild(messageItem);
    }

    if (document.getElementById('chat-messages')) {
        setupWebSocket();
    }

    document.getElementById('my-messages-link').addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = "/chat_room";
    });

    document.querySelectorAll('.want-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var productId = this.closest(".product-item").dataset.productId;
            var uploaderId = this.closest(".product-item").dataset.uploaderId;
            window.location.href = "/chat_room?product_id=" + productId + "&uploader_id=" + uploaderId;
        });
    });

    function openChatDialog(userId, productId) {
        const url = `/chat_room?user_id=${userId}&product_id=${productId}`;
        window.open(url, 'Chat', 'width=600,height=400');
    }

    document.querySelectorAll('.recent-message').forEach(item => {
        item.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const productId = this.dataset.productId;
            openChatDialog(userId, productId);
        });
    });
});