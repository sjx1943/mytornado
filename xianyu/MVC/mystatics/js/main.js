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
        checkUnreadMessages();
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
                 // 更新未读消息计数
                updateNotificationBadge();
                // 如果是新消息且不是自己发送的，触发未读检查
                checkUnreadMessages();
            }
        }
    };
     // 添加未读消息检查函数
    function checkUnreadMessages() {
        fetch('/api/unread_count?user_id=' + userId)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateUnreadIndicators(data.counts);
                }
            })
            .catch(error => console.error('Error checking unread messages:', error));
    }

    // 更新未读指示器
    function updateUnreadIndicators(counts) {
        // 这里可以根据实际DOM结构更新未读提示
        if (notificationBadge) {
            const totalUnread = Object.values(counts).reduce((sum, count) => sum + count, 0);
            notificationBadge.textContent = totalUnread > 0 ? totalUnread : '';
            notificationBadge.style.display = totalUnread > 0 ? 'inline-block' : 'none';
        }
    }

    ws.onclose = function() {
        console.log("WebSocket connection closed");
        // 尝试重新连接
        setTimeout(() => {
            if (userId && !isNaN(userId)) {
                ws = new WebSocket(ws.url);
            }
        }, 5000);
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



// 发送消息





function loadProducts(tag = 'all') {
    // 使用fetch API替代XMLHttpRequest
    fetch(`/product_list${tag && tag !== 'all' ? `?tag=${tag}` : ''}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(products => {
            const productListDiv = document.getElementById('product-list');
            productListDiv.innerHTML = '';

            // 添加无商品提示
            if (products.length === 0) {
                productListDiv.innerHTML = '<p class="no-products">暂无相关商品</p>';
                return;
            }

            products.forEach(product => {
                const productDiv = document.createElement('div');
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
                        ${product.user_id === parseInt(document.getElementById('logged-in-user-id').value) ? 
                          '<button class="edit-product" data-id="${product.id}">编辑</button>' : ''}
                    </div>
                `;
                productListDiv.appendChild(productDiv);
            });

            // 更新活跃标签样式
            updateActiveTag(tag);
        })
        .catch(error => {
            console.error('加载商品失败:', error);
            document.getElementById('product-list').innerHTML =
                '<p class="error-msg">加载商品失败，请稍后重试</p>';
        });
}

// 更新活跃标签样式
function updateActiveTag(tag) {
    document.querySelectorAll('.category-nav a').forEach(link => {
        link.classList.toggle('active', link.dataset.tag === tag);
    });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    // 绑定标签点击事件
    document.querySelectorAll('.category-nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            loadProducts(link.dataset.tag);
        });
    });

    // 初始加载所有商品
    loadProducts();
    
    // 检查未读消息并设置轮询
    checkUnreadMessages();
    setInterval(checkUnreadMessages, 30000);
});