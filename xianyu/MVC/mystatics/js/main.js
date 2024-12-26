// main.js 文件

// 获取页面中的 DOM 元素
const userId = new URLSearchParams(window.location.search).get('user_id') || 'default_user_id';
const productId = new URLSearchParams(window.location.search).get('product_id') || 'default_product_id';
const chatBox = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

// 建立 WebSocket 连接
const ws = new WebSocket(`ws://${window.location.host}/ws/chat_room?user_id=${userId}&product_id=${productId}`);

ws.onopen = function() {
    console.log("WebSocket connection opened");
};

// 处理接收到的消息
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.error) {
        alert(data.error);
    } else {
        displayMessage(`From ${data.from_user_id}: ${data.message}`);
    }
};

function displayMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 滚动到底部
}

// 发送消息
sendButton.addEventListener('click', function() {
    const message = messageInput.value;
    const targetUserId = prompt("请输入对方的用户 ID:"); // 测试用，实际可以换成 UI 控件
    const productName = document.getElementById('product-name').value; // Assuming you have a hidden input field for product name

    if (message && targetUserId && productId && productName) {
        ws.send(JSON.stringify({
            target_user_id: targetUserId,
            message: message,
            product_id: productId,
            product_name: productName
        }));
        messageInput.value = ''; // 清空输入框
        displayMessage(`To ${targetUserId}: ${message}`);
    }
});

// 处理 WebSocket 关闭
ws.onclose = function() {
    alert("WebSocket 连接已关闭！");
};