from sqlalchemy import select
from ..models import User
from ..session import AsyncSessionLocal

async def get_hash_by_user_id(user_id: int) -> str | None:
    """
    Возвращает короткий хэш пользователя по его ID.
    
    :param session: Асинхронная сессия SQLAlchemy
    :param user_id: Оригинальный ID пользователя
    :return: short_hash (str) если найден, иначе None
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.short_hash).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()