from datetime import datetime, timedelta, UTC
from typing import Any, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

# =========================
# 密码加密
# =========================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# =========================
# JWT 工具
# =========================
def _validate_and_normalize_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生产级 payload 校验：
    - sub 必须存在
    - sub 不允许为 None
    - sub 必须是字符串
    """
    to_encode = data.copy()

    sub = to_encode.get("sub")

    # 强约束（推荐）
    if sub is None:
        raise ValueError("JWT payload must contain 'sub' and cannot be None")

    # 统一转字符串（JWT规范推荐）
    if not isinstance(sub, str):
        to_encode["sub"] = str(sub)

    return to_encode


# =========================
# 生成 access_token
# =========================
def create_access_token(
    data: Dict[str, Any],
    token_version: int,
) -> str:
    settings = get_settings().secret

    to_encode = _validate_and_normalize_payload(data)

    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expires)

    # 标准字段
    to_encode.update({
        "iat": int(now.timestamp()),       # 签发时间
        "exp": int(expire.timestamp()),   # 过期时间
        "type": "access",                 # token类型（预留扩展）
        "ver": token_version,             # 单点登录核心
    })

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )


# =========================
# 解析 token
# =========================
def decode_token(token: str) -> Dict[str, Any] | None:
    settings = get_settings().secret

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        # 基础字段校验（防御性编程）
        if "sub" not in payload or payload["sub"] is None:
            return None

        return payload

    except JWTError:
        return None