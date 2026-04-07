from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import delete_current_user_cache
from app.db.session import get_session
from app.schemas.response import ResponseModel, Response
from app.schemas.user import UserLogin, Token
from app.services import UserService


router = APIRouter(prefix="/public/user")


@router.post("/login", response_model=ResponseModel[Token])
async def login(
    params: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    user_id, token = await UserService.login(params, session)
    # 删除旧缓存
    await delete_current_user_cache(user_id)
    return Response.success(data=Token(token=token), message="Login success")
