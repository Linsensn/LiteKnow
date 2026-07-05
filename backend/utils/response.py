r"""
@Project : LiteKnow (教育助手)
@File    : backend\utils\response.py
@Desc    : 全局响应工具模块，快速生成符合 ResponseModel 规范的成功/失败响应字典。
"""

from typing import Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from utils.exceptions import ErrorCode 

def success(data: Any = None, message: str = "请求成功", code: int = 200) -> JSONResponse:
    """快捷生成成功响应字典的工具函数"""
    content = {
        "code": code, 
        "success": True, 
        "message": message, 
        "data": data if data is not None else {} 
    }
    return JSONResponse(content=jsonable_encoder(content)) 

def fail(code: ErrorCode, message: str = None, data: Any = None, status_code: int = 200) -> JSONResponse:
    """快捷返回失败响应，强制要求传入 ErrorCode 枚举"""
    from utils.exceptions import ERROR_MESSAGES
    
    content = {
        "code": code.value, 
        "success": False, 
        "message": message or ERROR_MESSAGES.get(code, "未知错误"),
        "data": data if data is not None else {} 
    }
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content)) 