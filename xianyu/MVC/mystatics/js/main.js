// main.js

const userId = parseInt(new URLSearchParams(window.location.search).get('user_id'));
const productId = parseInt(new URLSearchParams(window.location.search).get('product_id')) || 'default_product_id';
const chatBox = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const notificationBadge = document.querySelector('.notification-badge');

// Ensure userId is a valid integer
if (!userId || isNaN(userId)) {
    throw new Error("Invalid user ID");
}

// Establish WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws/chat_room?user_id=${userId}&product_id=${productId}`);

ws.onopen = function() {
    // WebSocket connection opened
};

// Handle incoming messages

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.error) {
        displayMessage(`Error: ${data.error}`, 'error'); // Add 'error' class for styling
    } else {
        const fromUser = data.from_username || data.from_user_id || 'Unknown';  // Ensure from_username is used
        displayMessage(`From ${fromUser}: ${data.message}`);
        updateNotificationBadge();
    }
};

function displayMessage(message, type = 'normal') {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type);
    messageElement.innerHTML = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
}

function updateNotificationBadge() {
    // Function to update notification badge
    if (notificationBadge) {
        let count = parseInt(notificationBadge.textContent) || 0;
        notificationBadge.textContent = count + 1;
    }
}

// Send message
sendButton.addEventListener('click', function() {
    const message = messageInput.value;
    const targetUserId = parseInt(prompt("请输入对方的用户 ID:").trim()); // Ensure input is trimmed and parsed as an integer
    const productName = document.getElementById('product-name').value; // Assuming you have a hidden input field for product name

    if (message && !isNaN(targetUserId) && productId && productName) {
        ws.send(JSON.stringify({
            target_user_id: targetUserId,
            message: message,
            product_id: productId,
            product_name: productName
        }));
        messageInput.value = ''; // Clear input field
        displayMessage(`To ${targetUserId}: ${message}`);
    }
});

// Handle WebSocket close
ws.onclose = function() {
    // WebSocket connection closed
};

// Disable send button if input is empty
messageInput.addEventListener('input', function() {
    sendButton.disabled = !messageInput.value.trim();
});