import logging
from maxapi import Bot
from maxapi.enums.parse_mode import ParseMode
import os


CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


logger = logging.getLogger(__name__)

async def send_to_channel(bot: Bot, text: str, attachments: list = []):
    """
    Отправляет текстовое сообщение в канал.
    
    :param bot: Экземпляр бота
    :param text: Текст сообщения
    """
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            attachments=attachments,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"✅ Сообщение отправлено в канал {CHANNEL_ID}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в канал {CHANNEL_ID}: {e}", exc_info=True)
        raise e