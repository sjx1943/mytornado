// 获取CSRF令牌
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// 删除好友功能
function deleteFriend(button) {
    const friendId = button.dataset.friendId;
    if (confirm('确定要删除这个好友吗？')) {
        // 获取XSRF令牌
        const xsrfToken = getCookie('_xsrf');

        fetch('/delete_friend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-XSRFToken': xsrfToken
            },
            body: JSON.stringify({friend_id: friendId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 从DOM中移除好友元素
                button.parentElement.remove();

                // 如果没有好友了，显示"暂无好友"提示
                const friendList = document.querySelector('.friend-list');
                if (friendList && friendList.querySelectorAll('.friend-item').length === 0) {
                    const noFriendsMsg = document.createElement('div');
                    noFriendsMsg.className = 'no-friends-message';
                    noFriendsMsg.innerText = '暂无好友';
                    friendList.appendChild(noFriendsMsg);
                }
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

// 加载好友消息
function loadFriendMessages(friendId) {
    if (friendId) {
        const userId = getUserId();
        if (!userId) {
            console.error('未找到用户ID');
            return;
        }

        fetch(`/api/messages?friend_id=${friendId}&user_id=${userId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取消息失败');
                }
                return response.json();
            })
            .then(messages => {
                const messagesContainer = document.getElementById('chat-messages');
                if (!messagesContainer) return;

                messagesContainer.innerHTML = '';
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message-item ${msg.from_user_id == userId ? 'sent' : 'received'}`;
                    messageDiv.innerHTML = `
                        <strong>${msg.from_username || '未知用户'} ${msg.timestamp || ''}:</strong>
                        <p>${msg.message}</p>
                    `;
                    messagesContainer.appendChild(messageDiv);
                });

                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                // 更新选中的好友样式
                document.querySelectorAll('.friend-item').forEach(item => {
                    item.classList.remove('active');
                });
                const activeFriend = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
                if (activeFriend) {
                    activeFriend.classList.add('active');
                }
            })
            .catch(error => console.error('加载消息失败:', error));
    } else {
        console.error('无效的好友ID');
    }
}

// 发送消息
function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput?.value.trim();
    const activeFriend = document.querySelector('.friend-item.active');

    if (message && activeFriend) {
        const friendId = activeFriend.dataset.friendId;
        const userId = getUserId();

        // 获取XSRF令牌
        const xsrfToken = getCookie('_xsrf');

        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-XSRFToken': xsrfToken
            },
            body: JSON.stringify({
                friend_id: friendId,
                message: message,
                user_id: userId
            })
        })
        .then(response => response.json())
        .then(() => {
            if (messageInput) messageInput.value = '';
            loadFriendMessages(friendId);
        })
        .catch(error => console.error('发送消息失败:', error));
    }
}

// 获取当前用户ID
function getUserId() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = parseInt(urlParams.get('user_id'));
    return userId || null;
}

// 初始化聊天功能
function initChat() {
    document.querySelectorAll('.friend-item').forEach(item => {
        item.addEventListener('click', function(e) {
            if (!e.target.classList.contains('delete-friend')) {
                const friendId = this.dataset.friendId;
                loadFriendMessages(friendId);
                const messageInput = document.getElementById('message-input');
                if (messageInput) messageInput.focus();
            }
        });
    });

    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // 为删除按钮添加事件监听
    document.querySelectorAll('.delete-friend').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            deleteFriend(this);
        });
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initChat);