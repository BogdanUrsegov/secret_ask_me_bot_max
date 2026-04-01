import logging
from sqlalchemy.exc import IntegrityError
from ..models import User
from ..session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def add_user(user_id: int, short_hash: str) -> bool:
    """Добавляет пользователя. Возвращает True при успехе, False если ID занят."""
    async with AsyncSessionLocal() as session:
        try:
            new_user = User(user_id=user_id,
                            short_hash=short_hash
                            )
            session.add(new_user)
            await session.commit()
            logger.info(f"Пользователь {user_id} успешно добавлен")
            return True
        except IntegrityError:
            # Ошибка уникальности (ID уже существует)
            await session.rollback()
            logger.warning(f"Пользователь {user_id} уже существует")
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Критическая ошибка add_user: {e}")
            raise  # Перевыбрасываем только критические ошибки