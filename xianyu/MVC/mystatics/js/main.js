// 获取URL参数
const urlParams = new URLSearchParams(window.location.search);
const userId = parseInt(urlParams.get('user_id'));

// DOM元素
const chatBox = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const notificationBadge = document.querySelector('.notification-badge');

// 获取当前用户ID
function getUserId() {
    return userId;
}


// WebSocket连接
let ws;
if (userId && !isNaN(userId)) {
    if (window.location.protocol === 'https:') {
        ws = new WebSocket(`wss://${window.location.host}/ws/chat_room?user_id=${userId}`);
    } else {
        ws = new WebSocket(`ws://${window.location.host}/ws/chat_room?user_id=${userId}`);
    }

    ws.onopen = function() {
        console.log("WebSocket connection established");
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.error) {
            displayMessage(`Error: ${data.error}`, 'error');
        } else {
            const fromUser = data.from_username || data.from_user_id;
            const timestamp = data.timestamp || new Date().toLocaleString();

            if (data.from_user_id === userId) {
                displayMessage(`你 ${timestamp}: ${data.message}`, 'sent');
            } else {
                displayMessage(`${fromUser} ${timestamp}: ${data.message}`, 'received');
                updateNotificationBadge();
            }
        }
    };

    ws.onclose = function() {
        console.log("WebSocket connection closed");
    };

    ws.onerror = function(error) {
        console.error("WebSocket error:", error);
    };
} else {
    console.error("Invalid user ID - WebSocket connection not established");
}

// 显示消息
function displayMessage(message, type = 'normal') {
    if (!chatBox) return;

    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 更新未读消息计数
function updateNotificationBadge() {
    if (notificationBadge) {
        let count = parseInt(notificationBadge.textContent) || 0;
        notificationBadge.textContent = count + 1;
    }
}

// 加载好友消息
function loadFriendMessages(friendId) {
    if (friendId) {
        fetch(`/api/messages?friend_id=${friendId}&user_id=${getUserId()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch messages');
                }
                return response.json();
            })
            .then(messages => {
                const messagesContainer = document.getElementById('chat-messages');
                if (!messagesContainer) return;

                messagesContainer.innerHTML = '';
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${msg.from_user_id == getUserId() ? 'sent' : 'received'}`;
                    messageDiv.innerHTML = `
                        <strong>${msg.from_username} ${msg.timestamp}:</strong>
                        <p>${msg.message}</p>
                    `;
                    messagesContainer.appendChild(messageDiv);
                });

                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                document.querySelectorAll('.friend-item').forEach(item => {
                    item.classList.remove('active');
                });
                const activeFriend = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
                if (activeFriend) {
                    activeFriend.classList.add('active');
                    document.getElementById('current-friend').textContent =
                        activeFriend.querySelector('.friend-name').textContent;
                }
            })
            .catch(error => console.error('加载消息失败:', error));
    } else {
        console.error('Invalid friend ID');
    }
}

// 发送消息
function sendMessage() {
    const message = messageInput?.value.trim();
    const activeFriend = document.querySelector('.friend-item.active');

    if (message && activeFriend) {
        const friendId = activeFriend.dataset.friendId;

        fetch('/api/send_message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                friend_id: friendId,
                message: message,
                user_id: getUserId()
            })
        })
        .then(() => {
            if (messageInput) messageInput.value = '';
            loadFriendMessages(friendId);
        })
        .catch(error => console.error('发送消息失败:', error));
    }
}

// 删除好友
function deleteFriend(button) {
    const friendId = button.dataset.friendId;
    if (confirm('确定要删除这个好友吗？')) {
        fetch('/delete_friend', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({friend_id: friendId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                button.parentElement.remove();
            }
        })
        .catch(error => console.error('删除好友失败:', error));
    }
}

function loadProducts(tags) {
    // Make an AJAX request to get the product list
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/product_list' + (tags ? '?tag=' + tags.join('&tag=') : ''), true);
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
            // Parse the JSON response and update the product list
            var products = JSON.parse(xhr.responseText);
            var productListDiv = document.getElementById('product-list');
            productListDiv.innerHTML = ''; // Clear the current product list
            products.forEach(function (product) {
                // Create a new div for each product and add it to the product list
                var productDiv = document.createElement('div');
                productDiv.className = 'product-item';
                productDiv.innerHTML = `
                    
                    <div class="product-info">
                    <a href="/product/detail/${product.id}">
                        <img src="/static/images/${product.image}" alt="${product.name}">
                    </a>  
                        <h2>${product.name}</h2>
                        <p>￥${product.price}</p>
                        <p>数量：${product.quantity}</p>
                        <p>标签：${product.tag}</p>
                        <p>商品上传者ID：${product.user_id}</p>
                        <p>当前用户ID：${document.getElementById('logged-in-user-id').value}</p>
                    </div>
                    
                    
                `;
                productListDiv.appendChild(productDiv);
            });
        }
    };
    xhr.send();
}

// Load the initial product list
loadProducts();


// 初始化聊天功能
function initChat() {
    document.querySelectorAll('.friend-item').forEach(item => {
        item.addEventListener('click', function(e) {
            if (!e.target.classList.contains('delete-friend')) {
                const friendId = this.dataset.friendId;
                loadFriendMessages(friendId);
                messageInput?.focus();
            }
        });
    });

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initChat();

    document.querySelectorAll('.delete-friend').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            deleteFriend(this);
        });
    });
});