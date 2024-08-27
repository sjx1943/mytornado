document.addEventListener('DOMContentLoaded', function() {
    function setupWebSocket() {
        const userId = "1"; // Replace with actual current user ID
        const ws = new WebSocket(`ws://192.168.221.27:8000/gchat?user_id=${userId}`);

        ws.onopen = function() {
            console.log("WebSocket connection established");
            displayPublicMessage("欢迎来到公共聊天室");
        };

        ws.onerror = function() {
            console.log("WebSocket connection error");
        };

        ws.onmessage = function(evt) {
            const message = evt.data;
            displayPublicMessage(message);
        };

        window.send = function() {
            const msg = document.getElementById('msg').value;
            ws.send(msg);
            document.getElementById('msg').value = '';
            displayPublicMessage(msg); // Display the message on the page
        };
    }

    function setupPrivateWebSocket(buyerId, productId, callback) {
        const wsUrl = `ws://192.168.221.27:8000/schat?user_id=${buyerId}&product_id=${productId}`;
        const privateWs = new WebSocket(wsUrl);

        privateWs.onerror = function() {
            console.log("Private WebSocket connection error");
        };

        privateWs.onopen = function() {
            console.log("Private WebSocket connection established");
            displayPrivateMessage("欢迎来到私人聊天室");
            if (callback) callback();
        };

        privateWs.onmessage = function(evt) {
            const message = evt.data;
            displayPrivateMessage(message);
        };

        window.sendPrivate = function() {
            const msg = document.getElementById('msg').value;
            const message = JSON.stringify({ content: msg });
            privateWs.send(message);
            document.getElementById('msg').value = '';
            displayPrivateMessage(msg); // Display the message on the page
        };
    }

    function displayPublicMessage(message) {
        const messageList = document.getElementById('divId');
        const messageItem = document.createElement('p');
        messageItem.textContent = message;
        messageList.appendChild(messageItem);
    }

    function displayPrivateMessage(message) {
        const messageList = document.getElementById('private-message-list');
        const messageItem = document.createElement('li');
        messageItem.textContent = message;
        messageItem.style.border = "1px solid black"; // Add border
        messageItem.style.padding = "10px"; // Add padding
        messageItem.style.margin = "5px 0"; // Add margin
        messageList.appendChild(messageItem);
    }

    // Initialize private WebSocket for private chat page
    if (document.getElementById('private-message-list')) {
        const loggedInUserId = document.getElementById('logged-in-user-id').value;
        const productId = "1"; // Replace with actual product ID
        setupPrivateWebSocket(loggedInUserId, productId);
    }

    // Initialize public WebSocket for public chat page
    if (document.getElementById('divId')) {
        setupWebSocket();
    }
});

        // const productId = item.getAttribute('data-product-id');
