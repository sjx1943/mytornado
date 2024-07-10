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

// 处理活动相关功能
var ws = new WebSocket("ws://192.168.9.165:8000/chat");
// 在main.js中
document.querySelectorAll('.want-button').forEach(function(button) {
    button.addEventListener('click', function() {
        var productId = this.id.split('-')[1];  // 获取产品ID
        var userId = document.cookie.split('; ').find(row => row.startsWith('user_id')).split('=')[1];  // 从cookie中获取用户ID
        var message = {
            type: 'want',
            productId: productId,
            userId: userId
        };
        ws.send(JSON.stringify(message));  // 通过WebSocket发送消息
    });
});