from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# 数据库连接配置
DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/credits_db'

# 创建数据库引擎
engine = create_engine(DATABASE_URI, pool_pre_ping=True)

# 配置会话
db_session = scoped_session(sessionmaker(bind=engine))

def get_engine():
    """
    返回数据库引擎。
    """
    return engine

def get_session():
    """
    返回数据库会话。
    """
    return db_session
