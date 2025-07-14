let currentFriendId = null;
let pollingAbortController = null;
let lastPollTimestamp = 0;
let pendingMessages = new Set();
const displayedMessageIds = new Set();

let unreadCheckInterval = null;
let ws;

// 初始化聊天界面
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const friendList = document.querySelectorAll('.friend-item');
    const noChatMessage = document.getElementById('no-chat-message');
    const messageContent = document.getElementById('message-content');
    const messageInputArea = document.getElementById('message-input-area');



// 提前定义 urlParams
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromUrlParam = urlParams.get('user_id');
    const userIdFromUrl = userIdFromUrlParam ? parseInt(userIdFromUrlParam) : null;

//    // 当前用户ID，优先从body的data属性获取，其次从URL获取
//    currentUserId = document.body.getAttribute('data-user-id') || userIdFromUrl;

    // 确保 currentUserId 是有效的数字
    if (typeof window.currentUserId === 'undefined') {
        window.currentUserId = document.body.getAttribute('data-user-id') ||
                           document.getElementById('logged-in-user-id')?.value;

        // 确保 currentUserId 是有效的数字
        if (window.currentUserId && !isNaN(parseInt(window.currentUserId))) {
            window.currentUserId = parseInt(window.currentUserId);
        } else {
            window.currentUserId = null;
        }
    }


    initChat();
    initContextMenu();
    setupLongPress();
    initWebSocket();

    if (window.currentUserId) {
        startUnreadCheck();
    }

    // 检查 URL 参数中的好友 ID 并自动选择
//    const urlParams = new URLSearchParams(window.location.search);
    const friendId = urlParams.get('friend_id');


    if (friendId) {
        const friendElement = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
        if (friendElement) {
            selectFriend(friendId, friendElement);
        }
    }

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // 为所有好友项添加点击事件
    friendList.forEach(item => {
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

    // 监听新消息事件
    document.addEventListener('newMessage', (e) => {
        const data = e.detail;
        console.log('Handling new message event, currentFriendId:', currentFriendId, 'from_user_id:', data.from_user_id);

        // 检查是否是pending消息
        if (data.temp_id && pendingMessages.has(data.temp_id)) {
            return;
        }

        if (data.from_user_id === currentFriendId || data.from_user_id === window.currentUserId) {
            const isSelf = data.from_user_id === window.currentUserId;
            const displayName = isSelf ? '我' : data.from_username;
            appendMessage(displayName, data.message, isSelf, data.timestamp, data._id);
            if (!isSelf) {
                markMessagesRead(currentFriendId);
            }
        }
    });
});

// 初始化 WebSocket 连接
function initWebSocket() {
    if (window.currentUserId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat_room?user_id=${window.currentUserId}`);

        ws.onopen = function() {
            console.log("WebSocket connection established");
        };

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Received new message:', data); // 添加日志，方便调试

            const messageEvent = new CustomEvent('newMessage', { detail: data });
            document.dispatchEvent(messageEvent);
        };

        ws.onclose = function() {
            console.log("WebSocket connection closed");
            // 尝试重新连接
            setTimeout(initWebSocket, 2000);
        };

        ws.onerror = function(error) {
            console.error("WebSocket error:", error);
        };
    } else {
        console.error("User ID not found, WebSocket connection cannot be established");
    }
}

// 初始化聊天
function initChat() {
    console.log('初始化聊天界面');
    // 默认隐藏消息输入区域
    hideMessageInputArea();
}

// 初始化右键菜单
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

    // 然后每 2 秒检查一次
    unreadCheckInterval = setInterval(checkUnreadMessages, 2000);
}

// 检查未读消息
function checkUnreadMessages() {
    if (!window.currentUserId) return;

    fetch(`/api/unread_count?user_id=${window.currentUserId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 处理不同格式的返回数据
                let counts = {};
                if (data.counts) {
                    // 如果返回的是 counts 对象
                    counts = data.counts;
                } else if (data.count !== undefined) {
                    // 如果返回的是单个 count 数字
                    // 假设所有未读消息属于当前好友
                    if (currentFriendId) {
                        counts[currentFriendId] = data.count;
                    } else {
                        // 如果没有当前好友，将所有未读分配给第一个好友
                        const firstFriend = document.querySelector('.friend-item');
                        if (firstFriend) {
                            counts[firstFriend.dataset.friendId] = data.count;
                        }
                    }
                }
                updateUnreadIndicators(counts);
            } else {
                console.warn('未收到有效的未读消息计数数据:', data);
                updateUnreadIndicators({});
            }
        })
        .catch(error => console.error('Error checking unread messages:', error));
}

// 更新未读指示器
function updateUnreadIndicators(counts = {}) {
    console.log('更新未读消息指示器，未读计数:', counts);

    // 计算总未读消息数
    let totalUnread = 0;

    // 更新好友列表中的未读计数
    document.querySelectorAll('.friend-item').forEach(item => {
        const friendId = item.getAttribute('data-friend-id');
        const redDot = item.querySelector('.red-dot');
        const friendCount = counts[friendId] || 0;

        // 累加总未读消息数
        totalUnread += friendCount;

        if (redDot) {
            if (friendCount > 0) {
                item.classList.add('unread');
                redDot.style.display = 'inline-block';
                redDot.setAttribute('title', `${friendCount}条未读消息`);
                console.log(`好友 ${friendId} 有 ${friendCount} 条未读消息，显示红点`);
            } else {
                item.classList.remove('unread');
                redDot.style.display = 'none';
                console.log(`好友 ${friendId} 没有未读消息，隐藏红点`);
            }
        }
    });

    // 更新底部菜单中的未读计数
    const bottomMenuCount = document.getElementById('unread-count');
    if (bottomMenuCount) {
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
    if (confirm('确定要删除所有消息吗？')) {
        const messageContent = document.getElementById('message-content');
        const messageIds = [];

        // 收集所有消息的ID
        document.querySelectorAll('.message-bubble').forEach(msg => {
            const messageId = msg.dataset.messageId;
            if (messageId) messageIds.push(messageId);
        });

        // 清空消息区域并显示提示
        if (messageContent) {
            messageContent.innerHTML = '';
            const noMessages = document.createElement('div');
            noMessages.className = 'no-messages';
            noMessages.textContent = '暂无消息记录';
            messageContent.appendChild(noMessages);
        }

        // 调用服务器删除
        if (messageIds.length > 0) {
            deleteMessagesFromServer(messageIds);
        } else {
            // 如果没有消息ID，也调用服务器删除，但传递空数组
            deleteMessagesFromServer([]);
        }
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
    .then(response => {
        // 打印响应状态和响应头，方便调试
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        return response.json();
    })
    .then(data => {
        // 打印后端返回的数据
        console.log('Delete response data:', data);
        if (data.status === 'success') {
            // 从 DOM 中移除已删除的消息
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
    console.log('开始选择好友，好友 ID:', friendId);
    // 更新 URL 参数
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
        console.log('好友项添加选中状态');

        // 移除红点提示(如果有)
        const redDot = element.querySelector('.red-dot');
        if (redDot) {
            redDot.style.display = 'none';
        }

        // 获取聊天消息相关 DOM 元素
        const noChat = document.getElementById('no-chat-message');
        const messageContent = document.getElementById('message-content');
        const chatMessages = document.getElementById('chat-messages');

        if (noChat && messageContent && chatMessages) {
            noChat.style.display = 'none';
            messageContent.style.display = 'block';
            messageContent.innerHTML = '<div class="loading">加载消息中...</div>';
            showMessageInputArea();
            console.log('显示消息输入区域，开始加载消息');

            // 清空已显示的消息 ID 缓存
            displayedMessageIds.clear();

            // 加载与该好友的聊天记录
            loadMessages(friendId)
              .then(() => {
                    console.log('消息加载成功');
                })
              .catch((error) => {
                    console.error('消息加载失败:', error);
                    messageContent.innerHTML = '<div class="error">加载聊天记录失败，请稍后重试</div>';
                });

            // 标记该好友的消息为已读
            markMessagesRead(friendId);

            // 启动长轮询
            startLongPolling(friendId);
        } else {
            console.error('关键 DOM 元素未找到');
        }
    } else {
        // 未选择好友时，确保消息区域显示"未选择聊天"
        const noChat = document.getElementById('no-chat-message');
        const messageContent = document.getElementById('message-content');
        if (noChat && messageContent) {
            noChat.style.display = 'block';
            messageContent.style.display = 'none';
            messageContent.innerHTML = ''; // 清空消息内容区域
            hideMessageInputArea();
        }
    }

    // 更新当前好友 ID
    currentFriendId = friendId;
    console.log('Updated currentFriendId:', currentFriendId);
}

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
            if (!window.currentUserId) {
                console.error('用户 ID 未获取');
                return;
            }

            // 获取未读消息数量
            const unreadResponse = await fetch(`/api/unread_count?user_id=${window.currentUserId}`);
            const unreadData = await unreadResponse.json();

            if (unreadData.status === 'success') {
                            // 处理未读消息计数
                            const counts = {};
                            if (unreadData.counts) {
                                Object.assign(counts, unreadData.counts);
                            } else if (unreadData.count !== undefined) {
                                counts[friendId] = unreadData.count;
                            }
                            updateUnreadIndicators(counts);
                        } else {
                            console.warn('轮询时未收到有效的未读消息计数数据:', unreadData);
                            updateUnreadIndicators({});
                        }

            const response = await fetch(`/api/messages?friend_id=${friendId}&since=${lastPollTimestamp}`);
            const messages = await response.json();

            if (messages && messages.length > 0) {
                lastPollTimestamp = new Date(messages[messages.length - 1].timestamp).getTime();

                // 如果是当前选中好友，更新消息区域
                if (friendId === currentFriendId) {
                    messages.forEach(msg => {
                        if ((msg.temp_id && !pendingMessages.has(msg.temp_id)) || !msg.temp_id) {
                            const isSelf = msg.from_user_id == window.currentUserId;
                            const displayName = isSelf ? '我' : msg.from_username;
                            appendMessage(displayName, msg.message, isSelf, msg.timestamp, msg._id || msg.temp_id);
                        }
                    });

                    // 标记为已读
                    markMessagesRead(friendId);
                } else {
                    // 更新未读消息提醒
                    const counts = {};
                    counts[friendId] = messages.length;
                    updateUnreadIndicators(counts);
//                    updateUnreadIndicator(friendId, messages.length);
                }
            }

            // 继续轮询
            setTimeout(poll, 1000);

        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('轮询错误:', err);
                // 出错后延迟重试
                setTimeout(poll, 2000);
            }
        }
    };

    poll();
}

// 加载与指定好友的聊天记录
function loadMessages(friendId) {
    return fetch(`/api/messages?friend_id=${friendId}`)
      .then(response => {
            console.log('消息请求响应状态:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
      .then(messages => {
            const messageContent = document.getElementById('message-content');
            if (!messageContent) {
                throw new Error('找不到消息内容容器');
            }
            messageContent.innerHTML = '';

            if (!messages || messages.length === 0) {
                const noMessages = document.createElement('div');
                noMessages.className = 'no-messages';
                noMessages.textContent = '暂无消息记录';
                messageContent.appendChild(noMessages);
                return;
            }

            messages.forEach(msg => {
                try {
                    const isSelf = msg.from_user_id == window.currentUserId;
                    const displayName = isSelf ? '我' : msg.from_username;
                    appendMessage(displayName, msg.message, isSelf, msg.timestamp, msg._id);
                } catch (e) {
                    console.error('处理消息时出错:', e, msg);
                }
            });
        })
      .catch(error => {
            console.error('加载聊天记录失败:', error);
            const messageContent = document.getElementById('message-content');
            if (messageContent) {
                messageContent.innerHTML = '<div class="error">加载聊天记录失败，请稍后重试</div>';
            }
            throw error;
        });
}

// 添加消息到聊天区域
function appendMessage(sender, content, isSelf, timestamp = null, messageId = null) {
    if (messageId && displayedMessageIds.has(messageId)) {
        console.log('Message already displayed, skipping:', messageId);
        return;
    }

    const messageContent = document.getElementById('message-content');
    if (!messageContent) return;

    // 隐藏"暂无消息记录"提示
    const noMessages = messageContent.querySelector('.no-messages');
    if (noMessages) {
        noMessages.style.display = 'none';
    }

    if (messageId) {
        displayedMessageIds.add(messageId); // 记录已显示的消息 ID
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
    messageContent.scrollTop = messageContent.scrollHeight;
}

// 删除好友功能
function deleteFriend(button) {
    const friendId = button.dataset.friendId;
    if (confirm('删除好友时会同步删除聊天消息，你确定吗？')) {
        const xsrfToken = getCookie('_xsrf');
        fetch('/delete_friend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-XSRFToken': xsrfToken
            },
            body: JSON.stringify({ user_id: window.currentUserId, friend_id: friendId })
        })
          .then(response => response.json())
          .then(data => {
                if (data.status === 'success') {
                    // 从 DOM 中移除对应的好友项
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

// 修改sendMessage函数
function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();

    if (!message || !currentFriendId) return;
    const tempId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    pendingMessages.add(tempId);

    // 先本地添加消息到聊天区域
    appendMessage('我', message, true, null, tempId);

    fetch('/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-XSRFToken': getCookie('_xsrf')
        },
        body: JSON.stringify({
            friend_id: currentFriendId,
            message: message,
            tempId: tempId
        })
    })
    .then(response => response.json())
    .then(data => {
        messageInput.value = '';
        if (data.status === 'success') {
            pendingMessages.delete(tempId);
            // 如果服务器返回真实消息ID，更新本地消息的ID
            if (data.messageId) {
                const messageElement = document.querySelector(`.message-bubble[data-message-id="${tempId}"]`);
                if (messageElement) {
                    messageElement.dataset.messageId = data.messageId;
                    displayedMessageIds.delete(tempId);
                    displayedMessageIds.add(data.messageId);
                }
            }
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

// 获取 Cookie
function getCookie(name) {
    const cookie = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookie ? cookie.pop() : '';
}