from bot.utils.hashed import short_hash_str
from maxapi.enums.parse_mode import ParseMode
from bot.keyboards import create_share_link_keyboard


async def send_main_mess(
    send_func,
    bot_username: str,
    user_id: int,
    attachments: list = [],
    parse_mode: ParseMode = ParseMode.HTML,
    **kwargs
):
    """Отправляет сообщение с личной ссылкой пользователя."""
    
    id_hash = short_hash_str(user_id)
    
    link = f"https://max.ru/{bot_username}?start={id_hash}"

    text = (
        "🔗 <b>Вот твоя личная ссылка:</b>\n\n"

        f"{link}\n\n"

        "📱 Опубликуй её в <b>MAX</b>, <b>Telegram</b>, <b>TikTok</b>, <b>VK</b> и получай анонимные сообщения\n\n"
    )
    
    keyboard = await create_share_link_keyboard(link=link)
    return await send_func(
        text=text,
        parse_mode=parse_mode,
        attachments=attachments + [keyboard],
        **kwargs
    )