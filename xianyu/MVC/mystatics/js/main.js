document.addEventListener('DOMContentLoaded', function() {
    const productList = document.querySelector('.product-list');
    const productItems = document.querySelectorAll('.product-item');
    const itemWidth = 200; // 假设每个商品项目的宽度为 200px
    const itemMargin = 20; // 假设每个商品项目的左右边距为 10px

    // 计算并设置商品项目的宽度
    function adjustLayout() {
        const containerWidth = productList.offsetWidth;
        const maxItemsPerRow = Math.floor((containerWidth + itemMargin) / (itemWidth + itemMargin * 2));

        const calculatedItemWidth = (containerWidth - itemMargin * (maxItemsPerRow + 1)) / maxItemsPerRow;
        productItems.forEach(item => {
            item.style.width = `${calculatedItemWidth}px`;
            item.style.margin = `${itemMargin / 2}px`;
        });
    }

    // 监听窗口调整事件
    window.addEventListener('resize', adjustLayout);

    // 初始化布局
    adjustLayout();

    // 设置 WebSocket 连接
    setupWebSocket();

    // 添加“想要”按钮的点击事件监听器
    productItems.forEach(item => {
        const wantButton = item.querySelector('.want-button');
    wantButton.addEventListener('click', function() {
        const productId = item.getAttribute('data-product-id');
        console.log(`Product ID: ${productId}`);
        const uploaderId = item.getAttribute('data-uploader-id');
        const loggedInUserId = document.getElementById('logged-in-user-id').value;
        const message = {
                type: 'want',
                content: '对这个商品感兴趣',
                receiver_id: uploaderId
            };
        console.log(productId);
            setupPrivateWebSocket(loggedInUserId, productId, function() {
                privateWs.send(JSON.stringify(message));
                alert("想要点击成功");
            });
        });
    });

    let privateWs;

    function setupPrivateWebSocket(buyerId, productId, callback) {

          const wsUrl = `ws://192.168.9.166:8000/schat?user_id=${buyerId}&product_id=${productId}`;
          console.log(`WebSocket URL: ${wsUrl}`);  // Add this line
          privateWs = new WebSocket(wsUrl);

        privateWs.onerror = function() {
            console.log("Private WebSocket connection error");
        };

        privateWs.onmessage = function(evt) {
            const message = evt.data;
            $('#divId').append(`<p>${message}</p>`);
            $('#unread-message-alert').show();
        };

        window.sendPrivate = function() {
            const msg = $('#msg').val();
            const message = JSON.stringify({ content: msg });
            privateWs.send(message);
            $('#msg').val('');
        };
    }

    function setupWebSocket() {
        const userId = "1"; // Replace with actual current user ID
        const ws = new WebSocket(`ws://192.168.9.166:8000/gchat?user_id=${userId}`);

        ws.onopen = function() {
            console.log("WebSocket connection established");
        };

        ws.onerror = function() {
            console.log("WebSocket connection error");
        };

        ws.onmessage = function(evt) {
            const message = evt.data;
            $('#divId').append(`<p>${message}</p>`);
            $('#unread-message-alert').show();
        };

        window.send = function() {
            const msg = $('#msg').val();
            ws.send(msg);
            $('#msg').val('');
        };
    }
});