from sqlalchemy import func, select
from ..models import User
from ..session import AsyncSessionLocal

async def get_global_stats() -> dict:
    """
    Возвращает общее количество пользователей и сумму всех отправленных сообщений.
    
    :return: Словарь {'users_count': int, 'total_sent': int}
    """
    async with AsyncSessionLocal() as session:
        # Запрашиваем: COUNT(id) и SUM(messages_sent)
        result = await session.execute(
            select(
                func.count(User.id).label('users_count'),
                func.coalesce(func.sum(User.messages_sent), 0).label('total_sent')
            )
        )
        
        row = result.first()
        
        return {
            'users_count': row.users_count or 0,
            'total_sent': row.total_sent or 0
        }