# backend/crud/session_crud.py
from sqlalchemy.orm import Session as DBSession, joinedload
from sqlalchemy import func, update
from models.sessions import Session  

# --- 1. 新增相关 ---
def create_session(db: DBSession, user_id: int, obj_in: dict) -> Session:
    """【单条新增】"""
    db_obj = Session(user_id=user_id, **obj_in)  
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def batch_create_sessions(db: DBSession, user_id: int, objs_in: list[dict]) -> int:
    """【批量新增】"""
    db_objs = [Session(user_id=user_id, **obj) for obj in objs_in]  
    db.add_all(db_objs)
    db.commit()
    return len(db_objs)

# --- 2. 查询相关 ---
def get_session_by_id(db: DBSession, session_id: int) -> Session | None:
    """【单条查询】与【关联查询】(joinedload 级联拉取 user)"""
    return db.query(Session).options(joinedload(Session.user)).filter(Session.id == session_id, Session.is_deleted == False).first()

def get_sessions_paginated(
    db: DBSession, skip: int = 0, limit: int = 20, 
    user_id: int = None, keyword: str = None, task_type: str = None
):
    """返回 (总条数, 当前页数据列表)"""
    # 关联查询：使用 joinedload 提前加载 user 信息以避免 N+1 问题
    query = db.query(Session).options(joinedload(Session.user)).filter(Session.is_deleted == False)
    
    if user_id:
        query = query.filter(Session.user_id == user_id)
    if task_type:
        query = query.filter(Session.task_type == task_type)
    if keyword:
        query = query.filter(Session.title.like(f"%{keyword}%"))
        
    total = query.count()
    sessions = query.order_by(Session.created_at.desc()).offset(skip).limit(limit).all()
    return total, sessions

def get_sessions_tree(db: DBSession, user_id: int) -> list[Session]:
    """树形查询：基于 parent_id 提取"""
    # 这里仅演示提取顶层（parent_id == None）。实际项目中可通过 SQLAlchemy 的 CTE 递归查询或在内存中组装 children
    return db.query(Session).filter(
        Session.user_id == user_id, 
        Session.parent_id == None, 
        Session.is_deleted == False
    ).all()

# --- 3. 更新与状态切换 ---
def update_session(db: DBSession, db_obj: Session, update_data: dict) -> Session:
    """【单条更改】"""
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_sessions(db: DBSession, limit: int = 10000):
    """【全量查询】用于导出等场景（返回未删除的会话列表）"""
    return db.query(Session).filter(Session.is_deleted == False).limit(limit).all()

def batch_update_status(db: DBSession, session_ids: list[int], new_status: str) -> int:
    """【批量更改】与【状态切换】"""
    stmt = update(Session).where(Session.id.in_(session_ids)).values(status=new_status)
    result = db.execute(stmt)
    db.commit()
    return result.rowcount

# --- 4. 删除相关 ---
def soft_delete_session(db: DBSession, db_obj: Session):
    """【逻辑删除】"""
    db_obj.is_deleted = True
    db.commit()

def batch_delete_sessions(db: DBSession, session_ids: list[int], physical: bool = False):
    """【批量删除】支持物理删除与逻辑删除"""
    if physical:
        db.query(Session).filter(Session.id.in_(session_ids)).delete(synchronize_session=False)
    else:
        db.execute(update(Session).where(Session.id.in_(session_ids)).values(is_deleted=True))
    db.commit()

# --- 5. 数据分析 ---
def get_task_type_statistics(db: DBSession):
    """【聚合计算】按 task_type 统计会话数量"""
    return db.query(Session.task_type, func.count(Session.id).label('count'))\
             .filter(Session.is_deleted == False)\
             .group_by(Session.task_type).all()  