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
    console.log("WebSocket connection established");
};

// Handle incoming messages
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.error) {
        displayMessage(`Error: \`${data.error}\``, 'error');
    } else {
        const fromUser = data.from_username || data.from_user_id;
        const toUser = data.to_username || data.to_user_id;
        const timestamp = new Date(data.timestamp).toLocaleString();

        // Detect if this is our own message coming back from the server
        if (data.from_user_id === userId) {
            displayMessage(`Message sent successfully at \`${timestamp}\`: \`${data.message}\``, 'success');
        } else if (data.to_user_id === userId) {
            displayMessage(`From \`${fromUser}\` \`${timestamp}\`: \`${data.message}\``);
            updateNotificationBadge();
        }
    }
};

// Display message utility
function displayMessage(message, type = 'normal') {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type);
    messageElement.innerHTML = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Update notification badge when a new message arrives
function updateNotificationBadge() {
    if (notificationBadge) {
        let count = parseInt(notificationBadge.textContent) || 0;
        notificationBadge.textContent = count + 1;
    }
}

// Send message on button click
sendButton.addEventListener('click', function() {
    const message = messageInput.value;
    const targetUserId = parseInt(prompt("请输入对方的用户 ID:").trim());
    const productName = document.getElementById('product-name')
        ? document.getElementById('product-name').value
        : 'Unknown Product';

    if (message && !isNaN(targetUserId) && productId && productName) {
        ws.send(JSON.stringify({
            target_user_id: targetUserId,
            message: message,
            product_id: productId,
            product_name: productName
        }));
        messageInput.value = '';
        console.log(`Sent message: \`${message}\``);
    }
});

// Handle WebSocket close
ws.onclose = function() {
    console.log("WebSocket connection closed");
};

// Disable send button if input is empty
messageInput.addEventListener('input', function() {
    sendButton.disabled = !messageInput.value.trim();
});

// Optional function for chat initiation
function initiateChat(button) {
    const userIdAttr = button.getAttribute('data-user-id');
    const productIdAttr = button.getAttribute('data-product-id');
    window.location.href = `/initiate_chat?user_id=${userIdAttr}&product_id=${productIdAttr}`;
}

// DOM ready event
document.addEventListener("DOMContentLoaded", function() {
    // No need for fallback WebSocket code here
});
