from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from ..session import AsyncSessionLocal

import logging

from ..models import User  # Твоя модель

logger = logging.getLogger(__name__)

async def get_user(user_id: int) -> User | None:
    """
    Получает пользователя из БД по оригинальному ID.
    
    :param session: Асинхронная сессия SQLAlchemy
    :param user_id: Оригинальный ID пользователя (telegram_id / max_id)
    :return: Объект User или None, если не найден
    """
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            return result.scalar_one()
        except NoResultFound:
            logger.debug(f"Пользователь {user_id} не найден в БД")
            return None