from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_session
from app.schemas.user import CurrentUser
from app.services import UserService
from app.utils.redis_cache import RedisCache


# =========================
# OAuth2 标准（自动解析 Bearer Token）
# =========================
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/public/user/login"
)


# =========================
# current用户缓存 key
# =========================
def _get_current_user_cache_key(user_id: int):
    return f"user:info:{user_id}"

async def delete_current_user_cache(user_id: int):
    await RedisCache.delete(_get_current_user_cache_key(user_id))


# =========================
# 获取当前用户（含单点登录校验）
# =========================
async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> CurrentUser:
    if not token:
        raise HTTPException(401, "未登录")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "token无效或已过期")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(401, "token错误")
    try:
        user_id = int(user_id_str)
    except Exception:
        raise HTTPException(401, "token格式错误")

    cache_key = _get_current_user_cache_key(user_id)
    # 从request.state中获取user
    user: CurrentUser | None = getattr(request.state, "user", None)
    # 尝试从 Redis 缓存获取
    if not user:
        cached = await RedisCache.get(cache_key)
        if cached:
            user = CurrentUser.model_validate(cached)
    # 缓存未命中则从数据库获取
    if not user:
        user = await UserService.get_current_user(user_id, session)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        # 写缓存，生产环境可设置 TTL
        await RedisCache.set(cache_key, user.model_dump(), expire=300)
    # token_version 校验
    token_version = payload.get("ver")
    if token_version != user.token_version:
        raise HTTPException(status_code=401, detail="token已失效（已在其他地方登录）")

    # 将用户写入 request.state 避免重复查询
    request.state.user = user

    return user


# =========================
# RBAC：角色控制，调用require_role("admin")
# =========================
def require_role(role: str):
    def checker(user: CurrentUser = Depends(get_current_user)):
        if role not in user.roles:
            raise HTTPException(
                status_code=403,
                detail=f"需要角色: {role}",
            )
        return user

    return checker


# =========================
# RBAC：权限控制，调用require_permission("user:list")
# =========================
def require_permission(permission: str):
    def checker(user: CurrentUser = Depends(get_current_user)):
        if permission not in user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"需要权限: {permission}",
            )
        return user

    return checker


# =========================
# （进阶）多权限控制（AND / OR），调用require_permissions(["user:add", "user:edit"], mode="AND/OR")
# =========================
def require_permissions(permissions: list[str], mode: str = "AND"):
    """
    mode:
        AND -> 必须全部满足
        OR  -> 满足任意一个
    """
    def checker(user: CurrentUser = Depends(get_current_user)):
        user_perms = set(user.permissions)

        if mode == "AND":
            if not all(p in user_perms for p in permissions):
                raise HTTPException(
                    status_code=403,
                    detail=f"需要权限: {permissions}",
                )
        elif mode == "OR":
            if not any(p in user_perms for p in permissions):
                raise HTTPException(
                    status_code=403,
                    detail=f"需要权限之一: {permissions}",
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="权限校验模式错误",
            )

        return user

    return checker