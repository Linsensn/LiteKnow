r"""
@Project : LiteKnow (教育助手)
@File    : backend\utils\exceptions.py
@Desc    : 全局异常处理与状态码字典模块。集中定义业务状态码枚举、自定义业务异常类，并提供 FastAPI 全局异常拦截器。
"""

import traceback
from enum import Enum
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from config.settings import settings

class HttpErrMsg:
    """HTTP 错误提示语字典常量"""
    LOGIN_FAILED = "鉴权失败或 Code 无效"
    ACCOUNT_DISABLED = "账号已被禁用"
    UNAUTHORIZED = "凭证无效或已过期，请重新登录"
    PERMISSION_DENIED = "权限不足，拒绝访问"
    NOT_FOUND = "请求的资源或路由不存在"

class ErrorCode(int, Enum):
    """LiteKnow 业务与系统异常状态码字典"""
    # 鉴权与用户
    WECHAT_AUTH_FAILED = 10001
    USER_NOT_FOUND = 10002
    USER_ALREADY_EXISTS = 10003
    ROLE_PERMISSION_DENIED = 10004
    RESOURCE_ACCESS_DENIED = 10005  # 新增：数据资源级越权访问拦截 (例如：访问不属于自己的题库)
    
    # 业务通用
    BUSINESS_PARAM_ERROR = 20001
    METHOD_NOT_ALLOW = 20003
    DATA_NOT_FOUND = 20004
    DB_OPERATION_FAILED = 20005
    DATABASE_ERROR = 20006
    
    # 题库与练习业务特定错误 (201xx)
    PRACTICE_RECORD_SUBMIT_FAILED = 20101
    PRACTICE_SESSION_CREATE_FAILED = 20102
    QUESTION_BANK_CREATE_FAILED = 20103
    QUESTION_BANK_DELETE_FAILED = 20104
    WRONG_QUESTION_UPDATE_FAILED = 20105
    WRONG_QUESTION_DELETE_FAILED = 20106
    WRONG_QUESTION_CREATE_FAILED = 20107
    
    # AI 与任务
    AI_SERVICE_BUSY = 30001
    AI_VALIDATION_FAILED = 30002
    SYS_RES_EXHAUSTED = 30006

ERROR_MESSAGES = {
    ErrorCode.WECHAT_AUTH_FAILED: "微信授权失败，请重试",
    ErrorCode.USER_NOT_FOUND: "找不到该用户档案",
    ErrorCode.USER_ALREADY_EXISTS: "用户信息已存在，请勿重复注册",
    ErrorCode.ROLE_PERMISSION_DENIED: "越权操作，需要管理员权限",
    ErrorCode.RESOURCE_ACCESS_DENIED: "越权访问：您无权操作或查看此数据资源", # 新增对应的错误描述
    
    ErrorCode.BUSINESS_PARAM_ERROR: "业务级参数格式错误",
    ErrorCode.METHOD_NOT_ALLOW: "请求方法不支持",
    ErrorCode.DATA_NOT_FOUND: "请求的数据不存在或无权限访问",
    ErrorCode.DB_OPERATION_FAILED: "数据库操作失败，请稍后重试",
    ErrorCode.DATABASE_ERROR: "系统底层数据库交互异常，请联系管理员",
    
    ErrorCode.PRACTICE_RECORD_SUBMIT_FAILED: "提交答题记录失败，请检查网络后重试",
    ErrorCode.PRACTICE_SESSION_CREATE_FAILED: "创建练习会话失败，请稍后重试",
    ErrorCode.QUESTION_BANK_CREATE_FAILED: "创建题库失败，请稍后重试",
    ErrorCode.QUESTION_BANK_DELETE_FAILED: "批量删除题库失败",
    ErrorCode.WRONG_QUESTION_UPDATE_FAILED: "更新错题解析失败",
    ErrorCode.WRONG_QUESTION_DELETE_FAILED: "移除错题失败",
    ErrorCode.WRONG_QUESTION_CREATE_FAILED: "新增或导入错题失败",
    
    ErrorCode.AI_SERVICE_BUSY: "大模型推荐服务暂不可用",
    ErrorCode.AI_VALIDATION_FAILED: "大模型语义解析失败",
    ErrorCode.SYS_RES_EXHAUSTED: "服务器正忙，请稍后重试"
}

class CustomAPIException(Exception):
    """业务逻辑中主动触发的异常容器"""
    def __init__(self, code: ErrorCode, message: str = None, data: any = None):
        self.code = code.value if isinstance(code, Enum) else code 
        self.message = message or ERROR_MESSAGES.get(code, "未知业务错误") 
        self.data = data if data is not None else {} 

async def custom_api_exception_handler(request: Request, exc: CustomAPIException):
    content = {"code": exc.code, "success": False, "message": exc.message, "data": exc.data} 
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(content)) 

async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    detail = "数据库开小差了，请稍后再试" 
    if isinstance(exc, IntegrityError): 
        detail = "数据约束冲突（可能是重复操作）" 
        
    error_data = {"error_type": type(exc).__name__, "error_detail": str(exc), "traceback": traceback.format_exc()} if settings.DEBUG else {} 
    content = {"code": 50001, "success": False, "message": detail, "data": error_data} 
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(content)) 

async def global_exception_handler(request: Request, exc: Exception):
    error_data = {"error_type": type(exc).__name__, "error_detail": str(exc), "traceback": traceback.format_exc()} if settings.DEBUG else {} 
    content = {"code": 50000, "success": False, "message": "服务器内部开小差了，工程师正在火速抢修", "data": error_data} 
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=jsonable_encoder(content)) 

async def http_exception_handler(request: Request, exc: HTTPException):
    content = {"code": exc.status_code, "success": False, "message": str(exc.detail), "data": {}} 
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(content)) 

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors() 
    error_details = [f"参数 {'.'.join([str(loc) for loc in error['loc']])}: {error['msg']}" for error in errors] 
    return JSONResponse(
        status_code=422, 
        content={"code": 422, "success": False, "message": "请求参数格式校验失败", "data": {"details": error_details}} 
    )