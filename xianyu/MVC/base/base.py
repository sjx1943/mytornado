from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

# 异步MySQL连接配置
conn_url = 'mysql+asyncmy://sgg:Zpepc001@ser74785.ddns.net:13306/xianyu_db?charset=utf8mb4'

# 创建异步引擎（禁用连接池避免greenlet问题）
engine = create_async_engine(
    conn_url,
    echo=True,
    poolclass=NullPool,  # 禁用连接池
    connect_args={
        'connect_timeout': 10
    }
)

# 异步会话工厂（关键修改）
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 声明基类
Base = declarative_base()

async def get_async_db():
    """获取异步数据库会话的依赖项"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
