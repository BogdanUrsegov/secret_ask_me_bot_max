import ssl
import aiohttp


# Отключаем проверку SSL для всех запросов aiohttp в этом процессе
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Перехватываем создание коннектора, чтобы подменить SSL контекст
original_tcp_connector = aiohttp.TCPConnector.__init__

def patched_tcp_connector(self, *args, **kwargs):
    if 'ssl' not in kwargs or kwargs['ssl'] is None:
        kwargs['ssl'] = ssl_context
    return original_tcp_connector(self, *args, **kwargs)

aiohttp.TCPConnector.__init__ = patched_tcp_connector

import asyncio
import logging
from maxapi import Bot, Dispatcher
from bot.database.session import init_db
from bot.handlers import router
import os

logging.basicConfig(level=logging.INFO)


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_routers(router)

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())