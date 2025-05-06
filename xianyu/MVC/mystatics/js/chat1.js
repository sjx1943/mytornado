// 获取CSRF令牌
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// 存储未读消息状态
const unreadMessages = new Map();

// 初始化聊天功能
function initChat() {
    // 建立WebSocket连接
    setupWebSocket();

    // 绑定好友点击事件
    document.querySelectorAll('.friend-item').forEach(item => {
        item.addEventListener('click', function() {
            const friendId = this.dataset.friendId;
            // 移除所有好友项的活跃状态
            document.querySelectorAll('.friend-item').forEach(el => {
                el.classList.remove('active');
            });
            // 添加当前好友的活跃状态
            this.classList.add('active');
            // 移除未读状态
            this.classList.remove('unread');
            // 加载该好友的消息
            loadFriendMessages(friendId);
            // 标记该好友的消息为已读
            markMessagesAsRead(friendId);
        });
    });

    // 绑定删除好友按钮事件
    document.querySelectorAll('.delete-friend').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡到好友项
            deleteFriend(this);
        });
    });
}

// 设置WebSocket连接
function setupWebSocket() {
    const userId = getUserId();
    if (!userId) return;

    let wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/chat_room?user_id=${userId}`);

    ws.onopen = () => {
        console.log("WebSocket连接已建立");
    };

    ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const activeFriendId = getActiveFriendId();

    if (data.error) {
        displayMessage(`Error: ${data.error}`, 'error');
    } else if (data.from_user_id && data.message) { // 确保存在 from_user_id 和 message 字段
        if (data.from_user_id != getUserId()) {
            if (data.from_user_id == activeFriendId) {
                appendMessage(data.from_username, data.message, false);
                markMessagesAsRead(activeFriendId);
            } else {
                markFriendUnread(data.from_user_id);
            }
        }
    } else {
        console.log("Received:", data); // 记录收到的其他类型消息
    }
};

    ws.onclose = () => {
        console.log("WebSocket连接已关闭");
        setTimeout(setupWebSocket, 3000);
    };

    ws.onerror = (error) => {
        console.error("WebSocket错误:", error);
    };

    // 保存WebSocket连接以供后续使用
    window.chatWs = ws;
}

// 获取当前活跃的好友ID
function getActiveFriendId() {
    const active = document.querySelector('.friend-item.active');
    return active ? active.dataset.friendId : null;
}

// 未读好友标记
function markFriendUnread(friendId) {
    const friendElements = document.querySelectorAll(`.friend-item[data-friend-id="${friendId}"]`);
    friendElements.forEach(item => {
        item.classList.add('unread');
        // 添加红点
        let redDot = item.querySelector('.red-dot');
        if (!redDot) {
            redDot = document.createElement('span');
            redDot.className = 'red-dot';
            item.appendChild(redDot);
        }
    });
}

// 隐藏消息输入区域
function hideMessageInputArea() {
    const messageInputArea = document.querySelector('.message-input-area');
    if (messageInputArea) {
        messageInputArea.style.display = 'none';
    }
}

// 显示消息输入区域
function showMessageInputArea() {
    const messageInputArea = document.querySelector('.message-input-area');
    if (messageInputArea) {
        messageInputArea.style.display = 'block';
    }
}

// 加载指定好友的聊天消息
function loadFriendMessages(friendId) {
    fetch(`/api/messages?friend_id=${friendId}`)
        .then(response => response.json())
        .then(messages => {
            clearChatArea(); // 清空聊天区域
            messages.forEach(msg => {
                const isMe = msg.from_user_id == getUserId();
                appendMessage(isMe ? '我' : msg.from_username, msg.message, isMe);
            });
            scrollToBottom(); // 滚动到底部
            markMessagesAsRead(friendId); // 标记为已读
            showMessageInputArea();  // 显示消息输入区域
        })
        .catch(error => console.error("加载消息失败:", error));
}

// 清空聊天区域
function clearChatArea() {
    const chatArea = document.getElementById('chat-messages');
    if (chatArea) {
        chatArea.innerHTML = '';
    }
}

// 滚动聊天区域到底部
function scrollToBottom() {
    const chatArea = document.getElementById('chat-messages');
    if (chatArea) {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
}

// 追加消息到聊天区域
function appendMessage(sender, content, isMe) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-item ${isMe ? 'my-message' : 'friend-message'}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-sender">${sender}:</span>
            <span class="message-text">${content}</span>
        </div>
    `;
    const inputArea = chatMessages.querySelector('.message-input-area');
    if (inputArea) {
        chatMessages.insertBefore(messageDiv, inputArea);
    } else {
        chatMessages.appendChild(messageDiv);
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 将消息标记为已读
function markMessagesAsRead(friendId) {
    fetch('/api/mark_messages_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-XSRFToken': getCookie('_xsrf')
        },
        body: JSON.stringify({ friend_id: friendId })
    })
    .then(() => {
        const friendItem = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
        if (friendItem) {
            friendItem.classList.remove('unread');
        }
    })
    .catch(error => console.error("标记消息为已读失败:", error));
}

// 删除好友功能
function deleteFriend(button) {
    const friendId = button.dataset.friendId;
    const userId = getUserId();
    console.log('Delete button clicked');
    if (confirm('删除好友时会同步删除聊天消息，确定吗？')) {
        const xsrfToken = getCookie('_xsrf');
        fetch('/delete_friend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-XSRFToken': xsrfToken
            },
            body: JSON.stringify({ user_id: userId, friend_id: friendId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 从DOM中移除对应的好友项
                const friendItem = button.closest('.friend-item');
                if (friendItem) {
                    friendItem.remove();
                }
                // 若好友列表为空则显示提示
                const friendList = document.querySelector('.friend-list');
                if (friendList && friendList.querySelectorAll('.friend-item').length === 0) {
                    const noFriendsMsg = document.createElement('div');
                    noFriendsMsg.className = 'no-friends-message';
                    noFriendsMsg.innerText = '暂无好友';
                    friendList.appendChild(noFriendsMsg);
                }
                // 删除当前选中好友时清空聊天区域
                const chatMessages = document.getElementById('chat-messages');
                chatMessages.innerHTML = '<div class="no-chat-selected">未选择聊天</div>';
                // 保留消息输入区域
                hideMessageInputArea();
            } else {
                alert('删除好友失败：' + (data.error || '未知错误'));
            }
        })
        .catch(error => {
            console.error('删除好友失败:', error);
            alert('删除好友请求失败，请稍后再试');
        });
    }
}

// 发送消息
function sendMessage() {
    const message = document.getElementById('message-input').value.trim();
    const friendId = getActiveFriendId();
    fetch('/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-XSRFToken': getCookie('_xsrf')
        },
        body: JSON.stringify({ friend_id: friendId, message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            appendMessage('我', message, true);
            document.getElementById('message-input').value = '';
        }
    })
    .catch(error => console.error("发送消息失败:", error));
}

// 获取当前用户ID
function getUserId() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');
    if (userId) return userId;
    const cookieUser = document.cookie.split('; ').find(row => row.startsWith('user_id='));
    if (cookieUser) {
        return cookieUser.split('=')[1];
    }
    return null;
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    initChat();

    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});