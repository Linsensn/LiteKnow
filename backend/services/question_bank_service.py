import csv
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from crud import question_banks_crud
from crud.favorites_crud import favorite_crud
from utils.exceptions import CustomAPIException, ErrorCode

class QuestionBankService:
    async def create_bank(self, db: AsyncSession, current_user, bank_in: dict):
        try:
            new_bank = await question_banks_crud.create_question_bank(db=db, obj_in=bank_in, user_id=current_user.id)
            db.commit()
            return new_bank
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.QUESTION_BANK_CREATE_FAILED, data={"error_detail": str(e)})

    async def get_bank_detail(self, db: AsyncSession, current_user, bank_id: int):
        bank = await question_banks_crud.get_question_bank(db=db, id=bank_id)
        if not bank:
            raise CustomAPIException(code=ErrorCode.DATA_NOT_FOUND, data={"detail": "题库不存在"})
            
        # 鉴权：如果是管理员直接放行，否则必须是自己的题库
        user_role = getattr(current_user, 'role', None) 
        is_admin = user_role == "admin"
        if not is_admin and bank.user_id != current_user.id:
            raise CustomAPIException(code=ErrorCode.RESOURCE_ACCESS_DENIED, data={"detail": "无权访问此题库"})
            
        # 如果是管理员查看全局题库，不计算答题统计
        if is_admin:
            setattr(bank, "completion_rate", 0.0)
            setattr(bank, "accuracy_rate", 0.0)
        else:
            # 动态计算该学生在此题库的练习数据
            completed_count, total_attempts, correct_attempts = await question_banks_crud.get_user_bank_stats(db, current_user.id, bank_id)
            total_questions = bank.total_questions or 0
            setattr(bank, "completion_rate", round((completed_count / total_questions) * 100, 2) if total_questions > 0 else 0.0)
            setattr(bank, "accuracy_rate", round((correct_attempts / total_attempts) * 100, 2) if total_attempts > 0 else 0.0)
            
        return bank

    # 👇 修复重点：引入 is_admin_mode，默认开启数据隔离保护
    async def get_banks(self, db: AsyncSession, current_user, keyword: str, page: int, page_size: int, sort_by: str = "desc", is_admin_mode: bool = False):
        query_user_id = None if is_admin_mode else current_user.id
        skip = (page - 1) * page_size
        
        items, total = await question_banks_crud.get_multi_question_banks(
            db=db, user_id=query_user_id, keyword=keyword, skip=skip, limit=page_size, sort_by=sort_by
        )
        
        # 给列表渲染进度条。如果是管理员视角则直接设为0
        for bank in items:
            if is_admin_mode:
                setattr(bank, "completion_rate", 0.0)
                setattr(bank, "accuracy_rate", 0.0)
            else:
                completed_count, total_attempts, correct_attempts = await question_banks_crud.get_user_bank_stats(db, current_user.id, bank.id)
                total_questions = bank.total_questions or 0
                setattr(bank, "completion_rate", round((completed_count / total_questions) * 100, 2) if total_questions > 0 else 0.0)
                setattr(bank, "accuracy_rate", round((correct_attempts / total_attempts) * 100, 2) if total_attempts > 0 else 0.0)

        return {"total": total, "items": items}

    async def update_bank(self, db: AsyncSession, current_user, bank_id: int, update_data: dict) -> int:
        await self.get_bank_detail(db=db, current_user=current_user, bank_id=bank_id)
        update_dict = {k: v for k, v in update_data.items() if v is not None}
        if not update_dict:
            return 0
        try:
            rowcount = await question_banks_crud.update_question_bank(db=db, bank_id=bank_id, update_data=update_dict)
            db.commit()
            return rowcount
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.DATABASE_ERROR, data={"detail": str(e)})

    # 👇 同理修复：彻底阻断潜在的越权删除风险
    async def bulk_delete(self, db: AsyncSession, current_user, bank_ids: list[int], is_admin_mode: bool = False) -> int:
        query_user_id = None if is_admin_mode else current_user.id
        try:
            # 先级联清理收藏夹中对应的题库ID
            await favorite_crud.remove_content_ids_by_type(
                db, content_type="bank", content_ids=bank_ids
            )
            # 再删除题库
            rowcount = await question_banks_crud.delete_banks_by_ids(db=db, ids=bank_ids, user_id=query_user_id)
            db.commit()
            return rowcount
        except Exception as e:
            db.rollback()
            raise CustomAPIException(code=ErrorCode.QUESTION_BANK_DELETE_FAILED, data={"error_detail": str(e)})

    async def export_banks_to_csv(self, db: AsyncSession, current_user, is_admin_mode: bool = False) -> str:
        query_user_id = None if is_admin_mode else current_user.id
        banks, _ = await question_banks_crud.get_multi_question_banks(db=db, user_id=query_user_id, limit=2000)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["题库ID", "题库名称", "描述", "题目数量", "创建时间"])
        for b in banks:
            writer.writerow([
                b.id, b.bank_name, b.description or "", b.total_questions, 
                b.created_at.strftime("%Y-%m-%d %H:%M:%S") if b.created_at else ""
            ])
        return output.getvalue()
        
    async def import_banks_from_csv(self, db: AsyncSession, current_user, file: UploadFile):
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(StringIO(decoded))
        objs_in = []
        for row in reader:
            objs_in.append({
                "bank_name": row.get("题库名称", "导入的题库"),
                "description": row.get("描述", "")
            })
        if objs_in:
            await question_banks_crud.create_multi_question_banks(db=db, objs_in=objs_in, user_id=current_user.id)
            db.commit()

qb_service = QuestionBankService()