// 初始化聊天界面
document.addEventListener('DOMContentLoaded', function() {
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

    // 为所有好友项添加点击事件
    const friendItems = document.querySelectorAll('.friend-item');
    friendItems.forEach(item => {
        item.addEventListener('click', function() {
            const friendId = this.dataset.friendId;
            selectFriend(friendId, this);
        });
    });

    // 为所有删除好友按钮添加点击事件
    const deleteButtons = document.querySelectorAll('.delete-friend');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡，避免触发好友选择
            deleteFriend(this);
        });
    });
});

// 初始化聊天
function initChat() {
    console.log('初始化聊天界面');
    // 默认隐藏消息输入区域
    hideMessageInputArea();
}

// 隐藏消息输入区域
function hideMessageInputArea() {
    const messageInputArea = document.getElementById('message-input-area');
    if (messageInputArea) {
        messageInputArea.style.display = 'none';
    }
}

// 显示消息输入区域
function showMessageInputArea() {
    const messageInputArea = document.getElementById('message-input-area');
    if (messageInputArea) {
        messageInputArea.style.display = 'flex';
    }
}

// 选择好友聊天
function selectFriend(friendId, element) {
    // 移除其他好友项的选中状态
    document.querySelectorAll('.friend-item').forEach(item => {
        item.classList.remove('active');
    });

    // 添加选中状态到当前点击的好友项
    if (element) {
        element.classList.add('active');

        // 移除红点提示(如果有)
        const redDot = element.querySelector('.red-dot');
        if (redDot) {
            redDot.classList.remove('show');
        }
    }

    // 获取聊天消息
    const chatMessages = document.getElementById('chat-messages');
    const noChat = document.getElementById('no-chat-message');
    const messageContent = document.getElementById('message-content');

    if (chatMessages && noChat && messageContent) {
        noChat.style.display = 'none';
        messageContent.style.display = 'block';
        messageContent.innerHTML = '<div class="loading">加载消息中...</div>';
        showMessageInputArea();

        // 加载与该好友的聊天记录
        loadMessages(friendId);

        // 标记该好友的消息为已读
        markMessagesRead(friendId);
    }
}

// 加载与指定好友的聊天记录
function loadMessages(friendId) {
    fetch(`/api/messages?friend_id=${friendId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(messages => {
            const messageContent = document.getElementById('message-content');
            if (!messageContent) {
                console.error('找不到消息内容容器');
                return;
            }
            messageContent.innerHTML = '';

            if (!messages || messages.length === 0) {
                messageContent.innerHTML = '<div class="no-messages">暂无消息记录</div>';
                return;
            }

            messages.forEach(msg => {
                try {
                    const isSelf = msg.from_user_id == getUserId();
                    const displayName = isSelf ? '我' : msg.from_username;
                    appendMessage(displayName, msg.message, isSelf, msg.timestamp);
                } catch (e) {
                    console.error('处理消息时出错:', e, msg);
                }
            });
        })
        .catch(error => {
            console.error('获取消息失败:', error);
            const messageContent = document.getElementById('message-content');
            if (messageContent) {
                messageContent.innerHTML = `
                    <div class="error">
                        获取消息失败: ${error.message}<br>
                        请刷新页面重试
                    </div>
                `;
            }
        });
}

// 获取当前激活的好友ID
function getActiveFriendId() {
    const activeFriend = document.querySelector('.friend-item.active');
    return activeFriend ? activeFriend.dataset.friendId : null;
}

// 添加消息到聊天区域
function appendMessage(sender, content, isSelf, timestamp = null) {
    const messageContent = document.getElementById('message-content');
    const chatMessages = messageContent || document.getElementById('chat-messages');

    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = isSelf ? 'message-bubble self' : 'message-bubble';

    // 格式化时间
    const time = timestamp || new Date().toLocaleString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });

    messageDiv.innerHTML = `
        <div class="message-info">
            <span class="sender">${sender}</span>
            <span class="time">${time}</span>
        </div>
        <div class="message-text">${content}</div>
    `;

    if (messageContent) {
        messageContent.appendChild(messageDiv);
    } else {
        chatMessages.appendChild(messageDiv);
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
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
                chatMessages.innerHTML = '<div class="no-chat-selected" id="no-chat-message">未选择聊天</div>';
                // 隐藏消息输入区域
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

    if (!message || !friendId) return;

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

// 标记消息为已读
function markMessagesRead(friendId) {
    fetch('/api/mark_messages_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-XSRFToken': getCookie('_xsrf')
        },
        body: JSON.stringify({ friend_id: friendId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(`标记来自用户${friendId}的消息为已读`);
        }
    })
    .catch(error => console.error("标记消息为已读失败:", error));
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

// 获取Cookie
function getCookie(name) {
    const cookie = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookie ? cookie.pop() : '';
}