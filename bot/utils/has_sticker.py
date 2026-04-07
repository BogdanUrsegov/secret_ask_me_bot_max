import logging
from maxapi.types.attachments import Sticker


logger = logging.getLogger(__name__)


def has_sticker(attachments: list) -> bool:
    res = any(isinstance(att, Sticker) for att in attachments)
    logger.info(f"Проверка наличия стикера в вложениях: {res}")
    return res
