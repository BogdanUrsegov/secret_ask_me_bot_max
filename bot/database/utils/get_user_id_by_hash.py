from sqlalchemy import select
from ..models import User
from ..session import AsyncSessionLocal

async def get_user_id_by_hash(short_hash: str) -> int | None:
    """
    Находит оригинальный user_id по короткому хэшу.
    
    :param session: Асинхронная сессия SQLAlchemy
    :param short_hash: Короткий хэш (строка, ~5-6 символов)
    :return: user_id (int) если найден, иначе None
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.user_id).where(User.short_hash == short_hash)
        )
        return result.scalar_one_or_none()