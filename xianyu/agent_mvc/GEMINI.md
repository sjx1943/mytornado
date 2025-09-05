## 交互习惯
1.默认用中文回复


## Gemini Added Memories
(完成)增加好友的拉黑机制，拉黑后无法评价对方的商品、无法添加对方为好友并发送消息。
剩余待办事项：
(进行中) 当一方删除好友后，另一方再发送消息时，原先一方在好友列表中应重新显示有该好友，只不过聊天内容清空。
4. 交易成功后，双方确认交易，卖家更新数据库中的商品数量和状态。商品数量为0时，商品自动下架，用户在“我的”页面可以对上传商品进行状态变更、上下架或删除。
5. 首页“编辑“按钮点击无响应，可以考虑删除或增加相应自有商品的编辑功能。
6. 增加游客访问逻辑，游客可以查看商品详情、发布商品、查看活动信息等，但不能发布评论、购买商品、添加好友等。
7. 下单后的弹出的错误贴这里。
8. 美化UI界面，页面弹性布局适配PC或移动端。
9. web端和微信小程序端正式运行后，需要共用1套数据库（mysql+mongodb），注意性能优化并进行数据一致性的检查和约束。
10. 在/home_page页面，上传的商品点击“下架”后页面没有响应。
# xianyu二手平台开发部署文档

## 项目概述
基于 Tornado 框架开发的二手闲置物品交易平台，支持商品发布、实时聊天、订单管理、商品评价等核心功能。采用 Python 3.11 + MySQL + MongoDB + Redis 技术栈，支持 Docker 容器化部署和微信小程序多端适配。

## 环境配置
1. Github的项目地址 (SSH): `git@github.com:sjx1943/mytornado.git`
2. **首次配置**: 请确保你已经 [生成了SSH密钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) 并将其 [添加到了你的GitHub账户](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)。SSH方式更安全且无需每次输入密码。

### 基础环境要求
- Python 3.11+
- MySQL 8.0+
- MongoDB 6.0+
- Redis 7.0+
- Docker & Docker Compose（推荐）
- Nginx（生产环境）

### 开发环境搭建

#### 方式一：Docker 一键部署（推荐）
```bash
# 克隆项目 (使用SSH)
git clone git@github.com:sjx1943/mytornado.git
cd mytornado/xianyu/agent_mvc

# 修改配置文件（数据库密码等）
vim docker-compose.yml

# 启动服务
docker-compose up -d
```

#### 方式二：本地手动部署
# 创建虚拟环境并激活
python3.11 -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置数据库
# 修改 config.ini 中的数据库连接信息

# 启动服务
python app.py --port=8000


## 编程规范

### 后端开发规范

# 导入约定（示例）
import tornado.web
from tornado.ioloop import IOLoop
from models.user import UserModel  # 模型导入路径
from controllers.base import BaseHandler  # 控制器基类

# 类与函数命名
class ProductHandler(BaseHandler):  # 控制器类使用PascalCase
    async def get_product_detail(self, product_id: int) -> dict:  # 函数使用camelCase，添加类型提示
        """获取商品详情
        Args:
            product_id: 商品ID
        Returns:
            商品详情字典
        """
        try:
            # 业务逻辑代码
            return await ProductModel.get_by_id(product_id)
        except Exception as e:
            self.log_error(f"获取商品失败: {str(e)}")  # 统一错误日志
            raise

### 前端开发规范
- HTML模板使用 templates/ 目录，遵循 Tornado 模板语法
- CSS/JS 存放于 mystatics/，使用模块化开发
- 微信小程序页面存放于 miniprogram/pages/，遵循小程序开发规范


## 项目结构

项目目录/
├── .venv/                # 虚拟环境（不提交git）
├── .env                  # 环境变量（不提交git）
├── config.ini            # 项目配置文件
├── requirements.txt      # Python依赖
├── Dockerfile            # Docker配置
├── docker-compose.yml    # Docker Compose配置
├── nginx.conf            # Nginx反向代理配置
├── app.py                # 应用入口
├── models/               # 数据模型
│   ├── user.py           # 用户模型
│   ├── product.py        # 商品模型
│   └── order.py          # 订单模型
├── controllers/          # 业务控制器
│   ├── product_controller.py  # 商品相关接口
│   ├── chat_controller.py     # 聊天功能接口
│   └── order_controller.py    # 订单处理接口
├── templates/            # HTML模板
├── mystatics/            # 静态资源
│   ├── css/
│   ├── js/
│   └── images/
├── miniprogram/          # 微信小程序代码
└── utils/                # 工具函数
    ├── db.py             # 数据库连接工具
    └── validator.py      # 参数验证工具



## 环境变量设置

# .env 文件
# .env 文件配置示例
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_secure_password
MYSQL_DB=xianyu_db

MONGODB_URI=mongodb://localhost:27017/chat_db
REDIS_URL=redis://localhost:6379/0


DEBUG=False
LOG_LEVEL=INFO


## 开发要点

### 团队模式
- **RoundRobinGroupChat**: 轮询组聊天
- 支持多智能体协作

### 最佳实践
- 先单独测试智能体，再组合成团队
- 使用async/await处理所有操作
- 正确关闭模型客户端连接
- 环境变量管理敏感信息
- 虚拟环境不提交到版本控制

## 文档和资源获取

### MCP服务器配置
始终使用 **context7 MCP server** 搜索指定框架最新文档和代码规范：
- 优先查询官方文档
- 获取最新的API参考和最佳实践
- 查找代码示例和模式
- 验证版本兼容性和新特性

## 注意事项
-所有用户输入必须通过 utils.validator 验证
-密码存储使用 bcrypt 加密，禁止明文存储
-生产环境必须启用 HTTPS，配置在 nginx.conf 中
-定期备份数据库：utils/backup_db.py
- 优化时要有代码审核机制，避免引入新的问题或老问题重复出现

## 性能优化
图片使用 CDN 加速，配置 mystatics/images/ 目录权限
微信小程序使用分包加载：miniprogram/app.json 中配置

## AI代码审查流程
项目已配置专属的AI代码审查命令 `cr`。
- **AI角色**: 资深Python开发者，精通Tornado、WebSocket及数据库优化。
- **审查范围**: 所有通过 `git add` 暂存的代码。
- **执行时机**: 在执行 `git commit` 前，请务必运行 `gemini cr` 命令。
- **目的**: 确保代码质量、性能和安全性，统一团队代码风格。
