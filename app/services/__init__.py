from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.user import UserCreate
from app.services.user_service import UserService

router = APIRouter()


@router.post("/users")
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    return await UserService.create_user(
        session, data.username, data.email
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await UserService.get_user(session, user_id)