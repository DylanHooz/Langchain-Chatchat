from functools import wraps
from contextlib import contextmanager
from server.db.base import SessionLocal
from sqlalchemy.orm import Session

# NOTE：数据库线程连接上下文
# 创建完引擎后，SQLAlchemy会默认为我们生成一个连接池（Connection Pool），但是一般都不推介直接使用连接来进行数据库操作，而是通过建立在某一个连接之上的会话（Session）来进行数据库的增删查改。
#  而创建会话时，通常先创建一个Session工厂（sessionmaker本质上实现了一个工厂模式），再通过这个工厂方法来创建一个Session实例。

# SQLAlchemy默认所有数据库操作都是基于事务的。如果没有手动.commit()，默认也会直接回滚事务。
# https://juejin.cn/post/6844904164141580302
@contextmanager
def session_scope() -> Session:
    """上下文管理器用于自动获取 Session, 避免错误"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def with_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 数据库事务提交回滚策略，提交失败时回滚整个事务
        with session_scope() as session:
            try:
                result = f(session, *args, **kwargs)
                session.commit()
                return result
            except:
                session.rollback()
                raise

    return wrapper


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db0() -> SessionLocal:
    db = SessionLocal()
    return db
