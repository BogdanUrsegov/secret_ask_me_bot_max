from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    # Первичный ключ (автоинкремент)
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Оригинальный ID пользователя (BigInt, т.к. в Telegram/Max они большие)
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    
    # Короткий хэш (строка, ~5-6 символов)
    short_hash = Column(String(10), unique=True, nullable=False, index=True)
    
    # Статистика
    messages_received = Column(Integer, default=0, nullable=False)
    messages_sent = Column(Integer, default=0, nullable=False)
    link_clicks = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User(id={self.user_id}, hash='{self.short_hash}')>"