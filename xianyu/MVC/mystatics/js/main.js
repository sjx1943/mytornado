// 获取URL参数
const urlParams = new URLSearchParams(window.location.search);
const userIdFromUrl = parseInt(urlParams.get('user_id'));

// DOM元素
const productListDiv = document.getElementById('product-list');

// 当前用户ID，优先从body的data属性获取，其次从URL获取
window.currentUserId = document.body.getAttribute('data-user-id') || userIdFromUrl;

// 加载商品信息
function loadProducts(tag = 'all') {
    const productListDiv = document.getElementById('product-list');
    if (!productListDiv) {
        console.error('Product list div not found');
        return;
    }
    // 使用fetch API替代XMLHttpRequest
    fetch(`/product_list${tag && tag !== 'all' ? `?tag=${tag}` : ''}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(products => {
            productListDiv.innerHTML = '';

            // 添加无商品提示
            if (products.length === 0) {
                productListDiv.innerHTML = '<p class="no-products">暂无相关商品</p>';
                return;
            }

            products.forEach(product => {
                const productDiv = document.createElement('div');
                productDiv.className = 'product-item';
                productDiv.innerHTML = `
                    <div class="product-info">
                        <a href="/product/detail/${product.id}">
                            <img src="/static/images/${product.image}" alt="${product.name}">
                        </a>
                        <h2>${product.name}</h2>
                        <p>￥${product.price}</p>
                        <p>数量：${product.quantity}</p>
                        <p>标签：${product.tag}</p>
                        <p>商品上传者ID：${product.user_id}</p>
                        <p>当前用户ID：${window.currentUserId}</p>
                        ${product.user_id === parseInt(window.currentUserId) ?
                          `<button class="edit-product" data-id="${product.id}">编辑</button>` : ''}
                    </div>
                `;
                productListDiv.appendChild(productDiv);
            });

            // 更新活跃标签样式
            updateActiveTag(tag);
        })
        .catch(error => {
            console.error('加载商品失败:', error);
            productListDiv.innerHTML =
                '<p class="error-msg">加载商品失败，请稍后重试</p>';
        });
}

// 更新活跃标签样式
function updateActiveTag(tag) {
    document.querySelectorAll('.category-nav a').forEach(link => {
        link.classList.toggle('active', link.dataset.tag === tag);
    });
}

// 获取未读消息数量
async function getUnreadMessageCount() {
    try {
        const response = await fetch('/api/unread_count');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        const unreadCount = data.count;
        const unreadCountElement = document.getElementById('unread-count');

        if (unreadCount > 0) {
            unreadCountElement.textContent = unreadCount;
            unreadCountElement.style.display = 'inline-block';
        } else {
            unreadCountElement.style.display = 'none';
        }
    } catch (error) {
        console.error('获取未读消息数量失败:', error);
    }
}

// 处理新消息事件
function handleNewMessage() {
    getUnreadMessageCount();
}

// 监听新消息自定义事件
document.addEventListener('newMessage', handleNewMessage);

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    // 绑定标签点击事件
    document.querySelectorAll('.category-nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            loadProducts(link.dataset.tag);
        });
    });
    if (window.location.pathname.includes('chat_room')) {
            return;
        }

    // 初始加载所有商品
    loadProducts();
    // 初始获取未读消息数量
    getUnreadMessageCount();

});

