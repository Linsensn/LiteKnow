
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

# 定义一个泛型变量 T
T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    """
    全局通用的 API 响应数据结构契约 (泛型类)。
    
    作为前后端交互的顶层标准数据外壳，强制规范了所有业务接口的返回格式。
    通过泛型 T 动态约束内层 data 的具体结构，以便 Swagger UI 能够正确推导并生成嵌套的接口文档。
    
    Attributes:
        code (int): HTTP 状态码。
        success (bool): 快速判断位。提供给前端 Axios 拦截器用于第一时间的成功/失败分发。
        message (str): 业务提示信息。经过脱敏处理，前端可直接将其用于 Toast 弹窗或 UI 引导。
        data (Optional[T]): 业务数据载体。成功时为具体业务数据结构，异常时通常为 null。
    """
    
    code: int = Field(default=200, description="HTTP 状态码")
    success: bool = Field(default=True, description="快速判断位：true为成功，false为失败")
    message: str = Field(default="请求成功", description="提示信息：可直接用于前端弹窗或 UI 引导")
    data: Optional[T] = Field(default=None, description="业务数据载体：异常时通常为 null")

class PageResult(BaseModel, Generic[T]):
    """
    通用分页数据响应体结构，用于嵌套在 ResponseModel 的 data 节点中，即 ResponseModel[PageResult[T]]。

    attributes:
        list: 当前页的数据列表，类型为泛型 T 的列表
        total: 数据总条数
        page: 当前页码
        page_size: 每页数据条数
    """
    list: List[T] = Field(..., description="当前页数据列表")
    total: int = Field(..., description="数据总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")