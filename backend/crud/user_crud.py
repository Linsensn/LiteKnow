# backend/crud/crud_user.py
from sqlalchemy.orm import Session
from sqlalchemy import func, update, or_
from models.users import User

def get_user_by_openid(db: Session, openid: str) -> User | None:
    return db.query(User).filter(User.wechat_openid == openid).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

# 复杂查询与分页
def get_users_advanced(
    db: Session, skip: int = 0, limit: int = 20, 
    role: str = None, keyword: str = None, is_active: bool = None
):
    """【多条件组合查询】+【模糊查询】"""
    query = db.query(User).filter(User.is_deleted == False)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if keyword:
        # 支持同时匹配昵称或签名
        query = query.filter(
            or_(User.nickname.like(f"%{keyword}%"), User.signature.like(f"%{keyword}%"))
        )
        
    return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

def get_users_paginated(
    db: Session, 
    skip: int = 0, 
    limit: int = 20, 
    role: str = None, 
    keyword: str = None, 
    is_active: bool = None
):
    """
    【分页 + 多条件组合查询】返回 (总条数, 当前页列表)
    """
    query = db.query(User).filter(User.is_deleted == False)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if keyword:
        query = query.filter(
            or_(User.nickname.like(f"%{keyword}%"), User.signature.like(f"%{keyword}%"))
        )
    
    total = query.count() 
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return total, users

def batch_create_users(db: Session, objs_in: list[dict]) -> int:
    """【批量新增】"""
    db_objs = [User(**obj) for obj in objs_in]
    db.add_all(db_objs)
    db.commit()
    return len(db_objs)

def create_user(db: Session, openid: str, role: str = "student") -> User:
    db_user = User(wechat_openid=openid, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 20):
    return db.query(User).offset(skip).limit(limit).all()

def batch_update_status(db: Session, user_ids: list[int], is_active: bool) -> int:
    """【批量更改】与【状态切换】(如批量封禁/解封)"""
    stmt = update(User).where(User.id.in_(user_ids)).values(is_active=is_active)
    result = db.execute(stmt)
    db.commit()
    return result.rowcount

def update_user(db: Session, db_user: User, update_data: dict) -> User:
    db.add(db_user)

    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def soft_delete_user(db: Session, db_user: User):
    """【逻辑删除】单条"""
    db_user.is_deleted = True
    db.commit()

def batch_delete_users(db: Session, user_ids: list[int], physical: bool = False):
    """【批量删除】支持物理抹除与逻辑标记"""
    if physical:
        db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    else:
        db.execute(update(User).where(User.id.in_(user_ids)).values(is_deleted=True))
    db.commit()

def get_role_statistics(db: Session):
    """【聚合计算】按角色统计用户数量"""
    return db.query(User.role, func.count(User.id).label('count'))\
             .filter(User.is_deleted == False)\
             .group_by(User.role).all()