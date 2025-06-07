let currentFriendId = null; // 当前选中好友ID
let pollingAbortController = null; // 用于取消轮询请求
let lastPollTimestamp = 0; // 最后轮询时间戳
let pendingMessages = new Set(); // 用于跟踪已发送但尚未通过轮询确认的消息
// 添加全局变量记录已显示的消息ID
const displayedMessageIds = new Set();
let currentUserId = null;
let unreadCheckInterval = null;


// 初始化聊天界面
document.addEventListener('DOMContentLoaded', function() {
    initChat();
    // 初始化右键菜单
    initContextMenu();
    // 添加长按事件监听
    setupLongPress();
    // 检查URL参数中的好友ID并自动选择
    const urlParams = new URLSearchParams(window.location.search);
    const friendId = urlParams.get('friend_id');
    currentUserId = document.body.getAttribute('data-user-id') ||
                   new URLSearchParams(window.location.search).get('user_id');
    if (currentUserId) {
        startUnreadCheck();
    }

    if (friendId) {
        const friendElement = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
        if (friendElement) {
            selectFriend(friendId, friendElement);
        }
    }

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
        item.addEventListener('click', function(e) {
            // 如果点击的是删除按钮则不处理
            if (e.target.classList.contains('delete-friend')) {
                return;
            }
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
// 初始��右键菜单
function initContextMenu() {
    const contextMenu = document.getElementById('context-menu');

    // 隐藏右键菜单
    document.addEventListener('click', () => {
        contextMenu.style.display = 'none';
    });

    // 阻止默认右键菜单
    document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    });

    // 消息区域右键菜单
    const messageContent = document.getElementById('message-content');
    if (messageContent) {
        messageContent.addEventListener('contextmenu', (e) => {
            if (e.target.closest('.message-bubble')) {
                const messageBubble = e.target.closest('.message-bubble');
                messageBubble.classList.toggle('selected');

                contextMenu.style.display = 'block';
                contextMenu.style.left = `${e.pageX}px`;
                contextMenu.style.top = `${e.pageY}px`;
                e.preventDefault();
            }
        });
    }

    // 右键菜单项点击事件
    document.getElementById('delete-selected').addEventListener('click', deleteSelectedMessages);
    document.getElementById('delete-all').addEventListener('click', deleteAllMessages);
}

// 设置长按事件
function setupLongPress() {
    const messageContent = document.getElementById('message-content');
    if (!messageContent) return;

    let pressTimer;
    const longPressDuration = 800; // 长按时间(毫秒)

    messageContent.addEventListener('touchstart', (e) => {
        if (e.target.closest('.message-bubble')) {
            const messageBubble = e.target.closest('.message-bubble');
            pressTimer = setTimeout(() => {
                messageBubble.classList.add('selected');
                showMobileActionSheet();
            }, longPressDuration);
        }
    });

    messageContent.addEventListener('touchend', () => {
        clearTimeout(pressTimer);
    });

    messageContent.addEventListener('touchmove', () => {
        clearTimeout(pressTimer);
    });
}

// 显示移动端操作菜单
function showMobileActionSheet() {
    const actionSheet = document.createElement('div');
    actionSheet.className = 'mobile-action-sheet';
    actionSheet.innerHTML = `
        <div class="action-sheet-content">
            <button class="action-sheet-button" id="delete-selected-mobile">删除选中消息</button>
            <button class="action-sheet-button" id="delete-all-mobile">删除所有消息</button>
            <button class="action-sheet-button cancel">取消</button>
        </div>
    `;

    document.body.appendChild(actionSheet);

    // 添加事件监听
    document.getElementById('delete-selected-mobile').addEventListener('click', deleteSelectedMessages);
    document.getElementById('delete-all-mobile').addEventListener('click', deleteAllMessages);
    document.querySelector('.mobile-action-sheet .cancel').addEventListener('click', () => {
        document.body.removeChild(actionSheet);
        clearMessageSelection();
    });
}

// 启动未读消息检查
function startUnreadCheck() {
    // 先立即检查一次
    checkUnreadMessages();

    // 然后每10秒检查一次
    unreadCheckInterval = setInterval(checkUnreadMessages, 10000);
}

// 检查未读消息
function checkUnreadMessages() {
    if (!currentUserId) return;

    fetch(`/api/unread_count?user_id=${currentUserId}`)
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
    // 更新好友列表中的未读计数
    document.querySelectorAll('.friend-item').forEach(item => {
        const friendId = item.getAttribute('data-friend-id');
        const redDot = item.querySelector('.red-dot');

        if (counts[friendId] > 0) {
            item.classList.add('unread');
            redDot.style.display = 'inline-block';
            redDot.setAttribute('title', `${counts[friendId]}条未读消息`);
        } else {
            item.classList.remove('unread');
            redDot.style.display = 'none';
        }
    });
    
    // 更新底部菜单中的未读计数
    const bottomMenuCount = document.getElementById('bottom-menu-unread-count');
    if (bottomMenuCount) {
        const totalUnread = Object.values(counts).reduce((sum, count) => sum + count, 0);
        bottomMenuCount.textContent = totalUnread > 0 ? totalUnread : '';
        bottomMenuCount.style.display = totalUnread > 0 ? 'inline-block' : 'none';
    }
}

// 删除选中消息
function deleteSelectedMessages() {
    const selectedMessages = document.querySelectorAll('.message-bubble.selected');
    if (selectedMessages.length === 0) {
        alert('请先选择要删除的消息');
        return;
    }

    if (confirm(`确定要删除选中的 ${selectedMessages.length} 条消息吗？`)) {
        const messageIds = [];
        selectedMessages.forEach(msg => {
            const messageId = msg.dataset.messageId;
            if (messageId) messageIds.push(messageId);
        });

        deleteMessagesFromServer(messageIds);
        clearMessageSelection();
    }
}

// 删除所有消息
function deleteAllMessages() {
    const messages = document.querySelectorAll('.message-bubble');
    if (messages.length === 0) {
        alert('没有消息可删除');
        return;
    }

    if (confirm('确定要删除所有消息吗？')) {
        const messageIds = [];
        messages.forEach(msg => {
            const messageId = msg.dataset.messageId;
            if (messageId) messageIds.push(messageId);
        });

        deleteMessagesFromServer(messageIds);
    }
}

// 从服务器删除消息
function deleteMessagesFromServer(messageIds) {
    if (messageIds.length === 0) return;

    fetch('/api/delete_messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-XSRFToken': getCookie('_xsrf')
        },
        body: JSON.stringify({
            message_ids: messageIds,
            friend_id: currentFriendId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 从DOM中移除已删除的消息
            messageIds.forEach(id => {
                const msgElement = document.querySelector(`.message-bubble[data-message-id="${id}"]`);
                if (msgElement) msgElement.remove();
            });

            // 如果没有消息了，显示提示
            const messageContent = document.getElementById('message-content');
            if (messageContent && messageContent.children.length === 0) {
                messageContent.innerHTML = '<div class="no-messages">暂无消息记录</div>';
            }
        } else {
            alert('删除消息失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('删除消息失败:', error);
        alert('删除消息请求失败，请稍后再试');
    });
}

// 清除消息选择状态
function clearMessageSelection() {
    document.querySelectorAll('.message-bubble.selected').forEach(msg => {
        msg.classList.remove('selected');
    });
    const contextMenu = document.getElementById('context-menu');
    if (contextMenu) contextMenu.style.display = 'none';

    const actionSheet = document.querySelector('.mobile-action-sheet');
    if (actionSheet) document.body.removeChild(actionSheet);
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

// 选择好友聊天，轮询时这里要慎重修改
function selectFriend(friendId, element) {
    // 更新URL参数
    const url = new URL(window.location.href);
    url.searchParams.set('friend_id', friendId);
    window.history.replaceState(null, '', url.toString());
    
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

        // 获取聊天消息
        const chatMessages = document.getElementById('chat-messages');
        const noChat = document.getElementById('no-chat-message');
        const messageContent = document.getElementById('message-content');

        if (chatMessages && noChat && messageContent) {
            noChat.style.display = 'none';
            messageContent.style.display = 'block';
            messageContent.innerHTML = '<div class="loading">加载消息中...</div>';
            showMessageInputArea();

            // 清空已显示的消息ID缓存
            displayedMessageIds.clear();
            
            // 加载与该好友的聊天记录
            loadMessages(friendId);

            // 标记该好友的消息���已读
            markMessagesRead(friendId);

            // 启动长轮询
            startLongPolling(friendId);
        }
    } else {
        // 未选择好友时，确保消息区域显示"未选择聊天"
        const noChat = document.getElementById('no-chat-message');
        const messageContent = document.getElementById('message-content');
        if (noChat && messageContent) {
            noChat.style.display = 'block';
            messageContent.style.display = 'none';
            hideMessageInputArea();
        }
    }
    
    // 更新当前好友ID
    currentFriendId = friendId;
}

// 全局变量记录未读消息数量
let unreadMessageCounts = {};
// 底部菜单栏未读消息计数元素
const bottomMenuUnreadCount = document.getElementById('bottom-menu-unread-count');

// 启动长轮询
function startLongPolling(friendId) {
    // 取消现有轮询
    if (pollingAbortController) {
        pollingAbortController.abort();
    }

    pollingAbortController = new AbortController();
    const signal = pollingAbortController.signal;

    const poll = async () => {
        try {
            const user_id = getUserId();
            if (!user_id) {
                console.error('用户ID未获取');
                return;
            }
            
            // 获取未读消息数量
            const unreadResponse = await fetch(`/api/unread_count?user_id=${user_id}`);
            const unreadData = await unreadResponse.json();
            
            if (unreadData.status === 'success') {
                unreadMessageCounts = unreadData.counts;
                updateBottomMenuUnreadCount();
            }

            const response = await fetch(`/api/messages?friend_id=${friendId}&since=${lastPollTimestamp}`);
            const messages = await response.json();

            if (messages && messages.length > 0) {
                lastPollTimestamp = new Date(messages[messages.length-1].timestamp).getTime();

                // 如果是当前选中好友，更新消息区域
                if (friendId === currentFriendId) {
                    messages.forEach(msg => {
                        // 检查是否是pending消息或新消息
                        if ((msg.temp_id && !pendingMessages.has(msg.temp_id)) || !msg.temp_id) {
                            const isSelf = msg.from_user_id == getUserId();
                            const displayName = isSelf ? '我' : msg.from_username;
                            appendMessage(displayName, msg.message, isSelf, msg.timestamp, msg._id || msg.temp_id);
                        }
                    });

                    // 标记为已读
                    markMessagesRead(friendId);
                    // 更新未读消息计数
                    unreadMessageCounts[friendId] = 0;
                    updateBottomMenuUnreadCount();
                } else {
                    // 更新未读消息提醒
                    updateUnreadIndicator(friendId, messages.length);
                }
            }

            // 继续轮询
            setTimeout(poll, 3000);

        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('轮询错误:', err);
                // 出错后延迟重试
                setTimeout(poll, 5000);
            }
        }
    };

    poll();
}


// 加载与指定好友的聊天记录
function loadMessages(friendId) {
    fetch(`/api/messages?friend_id=${friendId}`)
        .then(response => response.json())

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
                    appendMessage(displayName, msg.message, isSelf, msg.timestamp,msg._id);
                } catch (e) {
                    console.error('处理消息时出错:', e, msg);
                }
            });
        });


}

// 获取当前激活的好友ID
function getActiveFriendId() {
    const activeFriend = document.querySelector('.friend-item.active');
    return activeFriend ? activeFriend.dataset.friendId : null;
}

// 添加消息到聊天区域
function appendMessage(sender, content, isSelf, timestamp = null,messageId = null) {
    if (messageId && displayedMessageIds.has(messageId)) {
        return; // 如果消息已显示则跳过
    }

    if (messageId) {
        displayedMessageIds.add(messageId); // 记录已显示的消息ID
    }

    const messageContent = document.getElementById('message-content');
    const chatMessages = messageContent || document.getElementById('chat-messages');

    if (!chatMessages) return;
    // 确保消息区域可见
    messageContent.style.display = 'block';

    // 如果当前显示的是"未选择聊天"或"加载中"，清除它们
    if (chatMessages.querySelector('.no-chat-selected') || chatMessages.querySelector('.loading')) {
        chatMessages.innerHTML = '';
    }


    const messageDiv = document.createElement('div');
    messageDiv.className = isSelf ? 'message-bubble self' : 'message-bubble';
    if (messageId) {
        messageDiv.dataset.messageId = messageId;
    }

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

    messageContent.appendChild(messageDiv);
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 删除好友功能
function deleteFriend(button) {
    const friendId = button.dataset.friendId;
    const userId = getUserId();
    console.log('Delete button clicked');
    if (confirm('删除好友时会同步删除聊天消息，ni确定吗？')) {
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
    const tempId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    pendingMessages.add(tempId);

    fetch('/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-XSRFToken': getCookie('_xsrf')
        },
        body: JSON.stringify({ friend_id: friendId, message: message,tempId: tempId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {

            document.getElementById('message-input').value = '';
            pendingMessages.delete(tempId);
        }
    })
    .catch(error => console.error("发送消息失败:", error));
    pendingMessages.delete(tempId);
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