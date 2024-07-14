function setupWebSocket() {
    var ws = new WebSocket("ws://192.168.9.165:8000/chat");

    ws.onopen = function() {
        console.log("WebSocket connection established");
    };

    ws.onerror = function() {
        console.log("WebSocket connection error");
    };

    ws.onmessage = function (evt) {
        var message = JSON.parse(evt.data);
        if (message.type === 'message') {
            $('#divId').append('<p>'+message.text+'</p>');
            $('#unread-message-alert').show();
        }
    };

    document.querySelectorAll('.want-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var productId = this.getAttribute('data-product-id');
            var message = {
                type: 'want',
                productId: productId
            };
            ws.send(JSON.stringify(message));
        });
    });
}

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
});