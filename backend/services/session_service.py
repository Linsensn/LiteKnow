# backend/services/session_svc.py
import csv
from io import StringIO
from sqlalchemy.orm import Session as DBSession
from fastapi.responses import StreamingResponse
import logging

from crud import session_crud
from utils.exceptions import CustomAPIException, ErrorCode 

logger = logging.getLogger(__name__)

def audit_log(user_id: int, action: str, details: str = ""):
    """【操作日志审计】记录关键操作"""
    # 实际项目中应写入专门的 audit_logs 数据表
    logger.info(f"[Audit] User:{user_id} | Action:{action} | Detail:{details}")

async def export_sessions_csv(db: DBSession):
    """【数据导出】导出全量会话为 CSV 格式流"""
    sessions = session_crud.get_sessions(db, limit=10000) # 取出需要导出的数据
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "User ID", "Title", "Task Type", "Status", "Created At"])
    
    for s in sessions:
        writer.writerow([s.id, s.user_id, s.title, s.task_type, s.status, s.created_at]) #[cite: 26]
        
    output.seek(0)
    audit_log(user_id=0, action="EXPORT_SESSIONS", details=f"Exported {len(sessions)} records")
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=sessions_export.csv"}
    )