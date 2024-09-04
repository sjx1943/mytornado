// main.js
document.addEventListener('DOMContentLoaded', function() {
    function setupWebSocket() {
        const userId = document.getElementById('logged-in-user-id').value;
        const ws = new WebSocket(`ws://${window.location.host}/chat?user_id=${userId}`);

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
            ws.send(JSON.stringify({ content: msg }));
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

    $(".want-button").click(function() {
        var productId = $(this).closest(".product-item").data("product-id");
        var uploaderId = $(this).closest(".product-item").data("uploader-id");
        window.location.href = "/chat_room?product_id=" + productId + "&uploader_id=" + uploaderId;
    });
});