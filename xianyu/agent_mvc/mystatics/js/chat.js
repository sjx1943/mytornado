let currentFriendId = null;
let chatPollingInterval = null;

// --- Utility Functions ---
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function scrollToBottom() {
    const container = document.getElementById('message-content-container');
    if(container) container.scrollTop = container.scrollHeight;
}

function showMessageInputArea() {
    document.getElementById('message-input-area').style.display = 'flex';
}

function hideMessageInputArea() {
    document.getElementById('message-input-area').style.display = 'none';
}

// --- Core Application Logic ---
document.addEventListener('DOMContentLoaded', function() {
    window.currentUserId = parseInt(document.body.getAttribute('data-user-id')) || null;
    initChatEventListeners();

    const urlParams = new URLSearchParams(window.location.search);
    const friendId = urlParams.get('friend_id');
    if (friendId) {
        const friendElement = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
        if (friendElement) selectFriend(friendId, friendElement);
    }
});

function initChatEventListeners() {
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    const friendList = document.querySelectorAll('.friend-item');

    if (sendButton) sendButton.addEventListener('click', sendMessage);
    if (messageInput) messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
    });

    friendList.forEach(item => {
        item.addEventListener('click', function(e) {
            const target = e.target;

            // Handle delete button click
            if (target.classList.contains('delete-friend')) {
                e.stopPropagation();
                const friendId = target.dataset.friendId;
                if (confirm('你确定要删除该好友吗？')) {
                    deleteFriend(friendId);
                }
                return;
            }

            // Handle block button click
            if (target.classList.contains('block-friend')) {
                e.stopPropagation();
                const friendId = target.dataset.friendId;
                if (confirm('你确定要拉黑该好友吗？')) {
                    blockFriend(friendId);
                }
                return;
            }

            // If not clicking buttons, select the friend for chat
            selectFriend(this.dataset.friendId, this);
        });
    });

    initContextMenu(); // Initialize context menu listeners
}


function selectFriend(friendId, element) {
    currentFriendId = friendId;
    document.querySelectorAll('.friend-item').forEach(item => item.classList.remove('active'));
    element.classList.add('active');
    document.getElementById('no-chat-message').style.display = 'none';
    document.getElementById('message-content').style.display = 'block';
    showMessageInputArea();

    loadMessages(friendId).then(() => {
        markMessagesRead(friendId);
        startChatPolling();
    });
}

function startChatPolling() {
    if (chatPollingInterval) clearInterval(chatPollingInterval);
    fetchNewData();
    chatPollingInterval = setInterval(fetchNewData, 3000);
}

function stopChatPolling() {
    clearInterval(chatPollingInterval);
    chatPollingInterval = null;
}

function fetchNewData() {
    if (!window.currentUserId) return;
    fetch(`/api/unread_count`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                updateUnreadIndicators(data.counts || {});
                if ((data.counts[currentFriendId] || 0) > 0) {
                    fetchNewMessagesForCurrentChat();
                }
            }
        });
}

function fetchNewMessagesForCurrentChat() {
    if (!currentFriendId) return;
    loadMessages(currentFriendId).then(() => {
        markMessagesRead(currentFriendId);
    });
}

function loadMessages(friendId) {
    const messageContent = document.getElementById('message-content');
    return fetch(`/api/messages?friend_id=${friendId}`)
        .then(response => response.json())
        .then(messages => {
            messageContent.innerHTML = '';
            if (!messages || messages.length === 0) {
                messageContent.innerHTML = '<div class="no-messages">暂无消息</div>';
            } else {
                messages.forEach(msg => {
                    const isSelf = msg.from_user_id == window.currentUserId;
                    appendMessage(isSelf ? '我' : msg.from_username, msg.message, isSelf, msg.timestamp, msg._id);
                });
            }
            scrollToBottom();
        });
}

function appendMessage(sender, content, isSelf, timestamp, messageId) {
    const messageContent = document.getElementById('message-content');
    if (!messageContent || document.querySelector(`.message-bubble[data-message-id="${messageId}"]`)) return;

    const noMessages = messageContent.querySelector('.no-messages');
    if (noMessages) noMessages.remove();

    const msgDiv = document.createElement('div');
    msgDiv.className = isSelf ? 'message-bubble self' : 'message-bubble';
    msgDiv.dataset.messageId = messageId;
    // THIS IS THE FIX for the "..." issue
    msgDiv.innerHTML = `
        <div class="message-info">
            <span class="sender">${sender}</span>
            <span class="time">${timestamp}</span>
        </div>
        <div class="message-text">${content}</div>
    `;
    messageContent.appendChild(msgDiv);
    scrollToBottom();
}

function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    if (!message || !currentFriendId) return;
    messageInput.value = '';

    fetch('/api/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-XSRFToken': getCookie('_xsrf') },
        body: JSON.stringify({ friend_id: currentFriendId, message: message })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            fetchNewMessagesForCurrentChat();
        }
    });
}

function markMessagesRead(friendId) {
    fetch('/api/mark_messages_read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-XSRFToken': getCookie('_xsrf') },
        body: JSON.stringify({ friend_id: friendId })
    }).then(() => updateUnreadIndicators({}));
}

function updateUnreadIndicators(counts) {
    let totalUnread = 0;
    document.querySelectorAll('.friend-item').forEach(item => {
        const friendId = item.dataset.friendId;
        const count = counts[friendId] || 0;
        totalUnread += count;
        const redDot = item.querySelector('.red-dot');
        if (redDot) redDot.style.display = count > 0 ? 'inline-block' : 'none';
    });

    const unreadCountElement = document.getElementById('unread-count');
    if (unreadCountElement) {
        unreadCountElement.style.display = totalUnread > 0 ? 'inline-block' : 'none';
        unreadCountElement.textContent = totalUnread > 0 ? totalUnread : '';
    }
}

// --- Context Menu and Deletion Logic ---
function initContextMenu() {
    const contextMenu = document.getElementById('context-menu');
    const messageContent = document.getElementById('message-content');

    document.addEventListener('click', () => contextMenu.style.display = 'none');

    messageContent.addEventListener('contextmenu', function(e) {
        const targetMessage = e.target.closest('.message-bubble');
        if (targetMessage) {
            e.preventDefault();
            targetMessage.classList.toggle('selected');

            contextMenu.style.display = 'block';
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.top = `${e.pageY}px`;
        }
    });

    document.getElementById('delete-selected').addEventListener('click', deleteSelectedMessages);
    document.getElementById('delete-all').addEventListener('click', deleteAllMessages);
}

function deleteSelectedMessages() {
    const selected = document.querySelectorAll('.message-bubble.selected');
    if (selected.length === 0) return;
    if (confirm(`确定删除选中的 ${selected.length} 条消息吗？`)) {
        const messageIds = Array.from(selected).map(msg => msg.dataset.messageId);
        deleteMessagesFromServer(messageIds);
    }
}

function deleteAllMessages() {
    if (confirm(`确定删除与该好友的所有聊天记录吗？`)) {
        const allMessages = document.querySelectorAll('.message-bubble');
        const messageIds = Array.from(allMessages).map(msg => msg.dataset.messageId);
        deleteMessagesFromServer(messageIds);
    }
}

function deleteMessagesFromServer(messageIds) {
    if (messageIds.length === 0) return;
    fetch('/api/delete_messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-XSRFToken': getCookie('_xsrf') },
        body: JSON.stringify({ message_ids: messageIds, friend_id: currentFriendId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            messageIds.forEach(id => {
                const el = document.querySelector(`.message-bubble[data-message-id="${id}"]`);
                if (el) el.remove();
            });
            if (document.querySelectorAll('.message-bubble').length === 0) {
                document.getElementById('message-content').innerHTML = '<div class="no-messages">暂无消息</div>';
            }
        }
    });
}

// --- Friend Management Functions ---

function deleteFriend(friendId) {
    fetch('/api/delete_friend', {
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
            alert('好友删除成功');
            const friendElement = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
            if (friendElement) {
                friendElement.remove();
            }
            if (currentFriendId === friendId) {
                document.getElementById('message-content').innerHTML = '<div class="no-chat-selected" id="no-chat-message">未选择聊天</div>';
                hideMessageInputArea();
                stopChatPolling();
                currentFriendId = null;
            }
        } else {
            alert('删除失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error deleting friend:', error);
        alert('删除好友时发生错误');
    });
}

function blockFriend(friendId) {
    fetch('/api/block_friend', {
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
            alert('好友拉黑成功');
            const friendElement = document.querySelector(`.friend-item[data-friend-id="${friendId}"]`);
            if (friendElement) {
                friendElement.classList.add('blocked');
                const blockButton = friendElement.querySelector('.block-friend');
                if (blockButton) {
                    blockButton.textContent = '已拉黑';
                    blockButton.disabled = true;
                }
            }
        } else {
            alert('拉黑失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error blocking friend:', error);
        alert('拉黑好友时发生错误');
    });
}
