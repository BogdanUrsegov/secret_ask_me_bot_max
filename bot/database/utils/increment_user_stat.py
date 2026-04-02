from sqlalchemy import update
from ..models import User
from ..session import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)

async def increment_user_stats(updates: dict[int, str]):
    """
    :param updates: Словарь, где:
                    Ключ = user_id (int)
                    Значение = имя поля (str)
                    
    Пример:
    await increment_user_stats({
        sender_id: 'messages_sent', 
        recipient_id: 'messages_received'
    })
    """
    allowed_fields = {'messages_received', 'messages_sent', 'link_clicks'}
    
    if not updates:
        return # Нечего обновлять

    async with AsyncSessionLocal() as session:
        try:
            for user_id, field_name in updates.items():
                if field_name not in allowed_fields:
                    raise ValueError(f"Недопустимое поле '{field_name}' для пользователя {user_id}.")

                column = getattr(User, field_name)
                
                await session.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(**{field_name: column + 1})
                )
            
            await session.commit()
            logger.info(f"✅ Статистика обновлена для {len(updates)} пользователей.")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Ошибка при обновлении статистики (откат): {e}")
            raise e