import os
import logging
from maxapi.types import MessageCreated
from maxapi.enums.parse_mode import ParseMode
from bot.keyboards import create_reply_keyboard
from bot.utils.get_mess import get_mess
from bot.utils.log_ch import send_to_channel
from bot.utils.has_sticker import has_sticker


logger = logging.getLogger(__name__)

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

    
async def forward_message(event: MessageCreated, recip_id: int, comment: str = ""):
    user_id = event.from_user.user_id

    text, attachments = await get_mess(event)
            
    keyboard = await create_reply_keyboard(user_id)
    
    if has_sticker(attachments):
        mess = await event.bot.send_message(
            user_id=recip_id, 
            attachments=attachments
        )
        await mess.message.reply(
            text=f"{comment}\n\n{text}", 
            attachments=[keyboard],
            parse_mode=ParseMode.HTML
        )
        attachments = []
    else:
        await event.bot.send_message(
            user_id=recip_id, 
            text=f"{comment}</b>\n\n{text}", 
            attachments=attachments + [keyboard],
            parse_mode=ParseMode.HTML
        )
    mess = await send_to_channel(event.bot, text=f"Новое сообщение от {user_id} для {recip_id}:\n\n{comment}\n\n{text}", attachments=attachments)