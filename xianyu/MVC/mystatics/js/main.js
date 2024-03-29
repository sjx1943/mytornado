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
// ...
