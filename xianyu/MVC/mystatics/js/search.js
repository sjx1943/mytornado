// 搜索功能实现
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');

    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('search-input').value.trim();
            if (query) {
                loadSearchResults(query);
            }
        });
    }
});

// 加载搜索结果
function loadSearchResults(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) throw new Error('搜索失败');
            return response.json();
        })
        .then(products => {
            renderSearchResults(products);
        })
        .catch(error => {
            console.error('搜索错误:', error);
            document.getElementById('product-list').innerHTML =
                '<p class="error-msg">搜索失败，请稍后重试</p>';
        });
}

// 渲染搜索结果
function renderSearchResults(products) {
    const productListDiv = document.getElementById('product-list');
    productListDiv.innerHTML = '';

    if (products.length === 0) {
        productListDiv.innerHTML = '<p class="no-products">没有找到匹配的商品</p>';
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
                <p>标签：${product.tags.join(', ')}</p>
            </div>
        `;
        productListDiv.appendChild(productDiv);
    });
}
