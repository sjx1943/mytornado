document.addEventListener('DOMContentLoaded', function() {
    // 实现弹性伸缩布局
    window.addEventListener('resize', function() {
        const productItems = document.querySelectorAll('.product-item');
        const containerWidth = document.querySelector('.product-list').offsetWidth;
        const itemWidth = 200; // 假设每个商品项目的宽度为 200px
        const itemMargin = 20; // 假设每个商品项目的左右边距为 10px
        const maxItemsPerRow = Math.floor((containerWidth + itemMargin) / (itemWidth + itemMargin * 2));

        productItems.forEach((item, index) => {
            item.style.width = `${(containerWidth - itemMargin * (maxItemsPerRow + 1)) / maxItemsPerRow}px`;
            item.style.margin = `${itemMargin / 2}px`;
        });
    });

    // 触发窗口调整大小事件以初始化布局
    window.dispatchEvent(new Event('resize'));

    // 在页面加载完成后设置 WebSocket 连接
    setupWebSocket();

    // 添加“想要”按钮的点击事件监听器
    document.querySelectorAll('.want-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var productId = this.getAttribute('data-product-id');
            var uploaderId = this.getAttribute('data-uploader-id'); // Assuming uploader ID is stored in a data attribute
            var loggedInUserId = document.getElementById('logged-in-user-id').value;
            var message = {
                type: 'want',
                content: '对这个商品感兴趣',
                receiver_id: uploaderId
            };
            setupPrivateWebSocket(loggedInUserId, productId, function() {
                privateWs.send(JSON.stringify(message));
                alert("想要点击成功");
            });
        });
    });
});

var privateWs;

function setupPrivateWebSocket(BuyerId, ProductId, callback) {
    privateWs = new WebSocket(`ws://192.168.199.27:8000/schat?user_id=${BuyerId}&product_id=${ProductId}`);

    privateWs.onopen = function() {
        console.log("Private WebSocket connection established");
        if (callback) callback();
    };

    privateWs.onerror = function() {
        console.log("Private WebSocket connection error");
    };

    privateWs.onmessage = function (evt) {
        var message = evt.data; // 直接使用 evt.data 获取消息
        $('#divId').append('<p>' + message + '</p>'); // 将消息添加到 divId 元素中
        $('#unread-message-alert').show();
    };

    window.sendPrivate = function() {
        var msg = $('#msg').val();
        var message = JSON.stringify({ content: msg });
        privateWs.send(message);
        $('#msg').val('');
    };
}

function setupWebSocket() {
    var userId = "1"; // Replace with actual current user ID
    var ws = new WebSocket(`ws://192.168.199.27:8000/gchat?user_id=${userId}`);

    ws.onopen = function() {
        console.log("WebSocket connection established");
    };

    ws.onerror = function() {
        console.log("WebSocket connection error");
    };

    ws.onmessage = function (evt) {
        var message = evt.data; // 直接使用 evt.data 获取消息
        $('#divId').append('<p>' + message + '</p>'); // 将消息添加到 divId 元素中
        $('#unread-message-alert').show();
    };

    window.send = function() {
        var msg = $('#msg').val();
        ws.send(msg);
        $('#msg').val('');
    };
}