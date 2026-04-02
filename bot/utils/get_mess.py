import html
from maxapi.types import MessageCreated


async def get_mess(event: MessageCreated):
    source_msg = getattr(event.message.link, 'message', None) if event.message.link else None
    body = source_msg if source_msg else event.message.body

    # Извлекаем текст и экранируем его
    raw_text = body.html_text or ""

    text = html.escape(raw_text) if raw_text else ""

    # Извлекаем вложения
    attachments = body.attachments or []

    return text, attachments