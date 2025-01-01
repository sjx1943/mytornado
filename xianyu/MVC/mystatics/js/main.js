// main.js

const userId = new URLSearchParams(window.location.search).get('user_id') || 'default_user_id';
const productId = new URLSearchParams(window.location.search).get('product_id') || 'default_product_id';
const chatBox = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const notificationBadge = document.querySelector('.notification-badge');

// Establish WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws/chat_room?user_id=${userId}&product_id=${productId}`);

ws.onopen = function() {
    console.log("WebSocket connection opened");
};

// Handle incoming messages
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.error) {
        alert(data.error);
    } else {
        displayMessage(`From ${data.from_username || data.from_user_id}: ${data.message}`, data.timestamp);
        updateNotificationBadge();
    }
};

function displayMessage(message, timestamp) {
    const messageElement = document.createElement('div');
    messageElement.textContent = `${message} [${new Date(timestamp).toLocaleTimeString()}]`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
}

function updateNotificationBadge() {
    if (notificationBadge) {
        let count = parseInt(notificationBadge.textContent) || 0;
        notificationBadge.textContent = count + 1;
        notificationBadge.style.display = 'inline';
    }
}

// Send message
sendButton.addEventListener('click', function() {
    const message = messageInput.value;
    const targetUserId = prompt("请输入对方的用户 ID:"); // For testing, replace with UI control
    const productName = document.getElementById('product-name').value; // Assuming you have a hidden input field for product name

    if (message && targetUserId && productId && productName) {
        ws.send(JSON.stringify({
            target_user_id: targetUserId,
            message: message,
            product_id: productId,
            product_name: productName
        }));
        messageInput.value = ''; // Clear input field
        displayMessage(`To ${targetUserId}: ${message}`, new Date().toISOString());
    }
});

// Handle WebSocket close
ws.onclose = function() {
    alert("WebSocket connection closed!");
};

// Disable send button if input is empty
messageInput.addEventListener('input', function() {
    sendButton.disabled = !messageInput.value.trim();
});