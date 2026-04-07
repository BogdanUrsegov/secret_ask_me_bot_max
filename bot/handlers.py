import logging
import os
from maxapi.types import BotStarted, Command, MessageCreated
from maxapi import F, Router
from maxapi.types import BotCommand, MessageCallback
from maxapi.enums.parse_mode import ParseMode
from bot.database.utils.get_global_stats import get_global_stats
from bot.states import Sending, Responding
from bot.utils.forward_message import forward_message
from bot.utils.get_mess import get_mess
from bot.utils.hashed import short_hash_str
from bot.utils.send_main_mess import send_main_mess
from bot.database.utils.add_user import add_user
from bot.database.utils.get_user import get_user
from bot.database.utils.increment_user_stat import increment_user_stats
from bot.database.utils.get_user_id_by_hash import get_user_id_by_hash
from maxapi.context import MemoryContext
from bot.utils.log_ch import send_to_channel
from bot.utils.has_sticker import has_sticker
from .keyboards import ACTION_ADD_MESS_CALL, ACTION_CANCEL_CALL, ACTION_REPLY_CALL, create_add_mess_keyboard, create_reply_keyboard, markup_cancel


ADMIN_ID = int(os.getenv("ADMIN_ID"))

logger = logging.getLogger(__name__)

router = Router()


@router.message_created(Command('stats'))
async def show_stats(event: MessageCreated):
    # Проверка на админа (замени на свою логику проверки ID)
    if event.from_user.user_id != ADMIN_ID:
        return

    stats = await get_global_stats()
    
    text = (
        "📊 <b>Глобальная статистика бота:</b>\n\n"
        f"👥 Всего пользователей: <b>{stats['users_count']}</b>\n"
        f"✉️ Всего отправлено сообщений: <b>{stats['total_sent']}</b>"
    )
    
    await event.message.answer(text, parse_mode=ParseMode.HTML)

# Ответ бота при нажатии на кнопку "Начать"
@router.bot_started()
async def bot_started(event: BotStarted, context: MemoryContext):
    commands = [
        BotCommand(name="start", description="🚀 Получить ссылку / Начать"),
        BotCommand(name="profile", description="📊 Статистика")
    ]
    
    # Отправляем список команд в API мессенджера
    await event.bot.set_my_commands(*commands)

    user_id = event.from_user.user_id
    id_hash = short_hash_str(user_id)
    res = await add_user(user_id, id_hash)
    if res:
        logger.info(f"✅ Новый пользователь добавлен: {user_id} (hash: {id_hash})")
        await send_to_channel(
            event.bot,
            f"✅ Новый пользователь: {user_id} (hash: {id_hash})"
        )

    start_param = event.payload

    if start_param:
        recip_id = await get_user_id_by_hash(start_param)
        if recip_id != user_id:
            await increment_user_stats({recip_id: "link_clicks"})
            mess = await event.bot.send_message(
                user_id=user_id,
                text="<i>🤫 Отлично! Теперь можешь отправить свое анонимное послание\n\n"

                    "📝 Поддерживаются:\n"
                    "• Текст\n"
                    "• Фото\n"
                    "• Видео\n"
                    "• Кружки\n"
                    "• Голосовые\n\n"

                    "🚀 Всё полетит анонимно!</i>",
                parse_mode=ParseMode.HTML,
                disable_link_preview=True,
                attachments=[markup_cancel]
            )

            await context.set_state(Sending.wait)
            await context.update_data(
                recip_id=recip_id,
                mess_id=mess.message.body.mid
            )
        else:
            await event.bot.send_message(
                user_id=user_id,
                text="🤔 <i>Нельзя отправлять сообщения самому себе! Попробуйте отправить кому-то другому.</i>",
                parse_mode=ParseMode.HTML,
                disable_link_preview=True
            )

            await context.clear()
    else:
        await send_main_mess(
            send_func=event.bot.send_message,
            bot_username=event.bot.me.username,
            user_id=user_id,
            disable_link_preview=True
        )

@router.message_created(Command('start'))
async def cmd_start(event: MessageCreated):
    user_id = event.from_user.user_id
    await send_main_mess(
        event.message.answer,
        bot_username=event.bot.me.username,
        user_id=user_id,
        disable_link_preview=True
    )
    
@router.message_created(Command('profile'))
async def cmd_profile(event: MessageCreated):
    try:
        user = await get_user(event.from_user.user_id)
        await event.message.answer(
                "👤 <b>Ваш профиль</b>\n\n"

                f"📬 Получено сообщений: {user.messages_received}\n"
                f"✉️ Отправлено сообщений: {user.messages_sent}\n"
                f"🔗 Переходов по вашей ссылке: {user.link_clicks}\n\n"


                "🔗 <b>Ваша текущая ссылка:</b>\n\n"
                f"https://max.ru/{event.bot.me.username}?start={user.short_hash}",
                disable_link_preview=True,
                parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Ошибка при получении профиля пользователя {event.from_user.user_id}: {e}")
        await event.message.answer(
            "⚠️ <i>Произошла ошибка при загрузке вашего профиля. Пожалуйста, попробуйте позже</i>",
            parse_mode=ParseMode.HTML,
            disable_link_preview=True
        )

        await send_to_channel(
            event.bot,
            f"❌ Ошибка при загрузке профиля пользователя {event.from_user.user_id}: {e}"
        )

@router.message_created(Responding.wait)
async def handle_responding_message(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()
    user_id = event.from_user.user_id
    recip_id = data.get("recip_id")
    mess_id = data.get("mess_id")
    try:
        if recip_id:
            await forward_message(event, recip_id, comment="<b>💬 Ответ на ваше сообщение:</b>")

        await event.bot.edit_message(
                message_id=mess_id,
                attachments=[]
            )

        await event.message.answer(
                "<b>Ваш ответ отправлен!</b>",
                parse_mode=ParseMode.HTML,
                disable_link_preview=True
            )

        await increment_user_stats(
                                    {
                                recip_id: "messages_received", 
                                user_id: "messages_sent"
                                }
                            )
        
        await send_main_mess(
                send_func=event.message.answer,
                bot_username=event.bot.me.username,
                user_id=user_id,
                disable_link_preview=True
            )
        
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа: {e}")
        await event.message.answer(
            "⚠️ <i>Произошла ошибка при отправке ответа. Пожалуйста, попробуйте позже</i>",
            parse_mode=ParseMode.HTML,
            disable_link_preview=True
        )
        await send_to_channel(
            event.bot,
            f"❌ Ошибка при отправке ответа от {user_id} к {recip_id}: {e}"
        )
    await context.clear()

@router.message_created(Sending.wait)
async def handle_anonymous_message(event: MessageCreated, context: MemoryContext):
    user_id = event.from_user.user_id
    data = await context.get_data()
    recip_id = data.get("recip_id")
    mess_id = data.get("mess_id")
    logger.info(event.message)
    try:
        if recip_id:
            await forward_message(event, recip_id, comment="<b>💬 У тебя новое сообщение!</b>")

            await event.message.answer(
                "<b>Ваше сообщение отправлено!</b>",
                parse_mode=ParseMode.HTML,
                disable_link_preview=True
            )

            await increment_user_stats(
                                    {
                                recip_id: "messages_received", 
                                user_id: "messages_sent"
                                }
                            )

            await event.bot.edit_message(
                message_id=mess_id,
                attachments=[]
            )

            await send_main_mess(
                send_func=event.message.answer,
                bot_username=event.bot.me.username,
                user_id=user_id,
                disable_link_preview=True
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке анонимного сообщения: {e}")
        await event.message.answer(
            "⚠️ <i>Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже</i>",
            parse_mode=ParseMode.HTML,
            disable_link_preview=True
        )
        await send_to_channel(
            event.bot,
            f"❌ Ошибка при отправке сообщения от {user_id} к {recip_id}: {e}"
        )
    await context.clear()

@router.message_callback(F.callback.payload.startswith(ACTION_ADD_MESS_CALL))
async def handle_action_add_mess(event: MessageCallback, context: MemoryContext):
    await event.answer("Новое сообщение...")
    mess = await event.message.answer(
                text="<i>🤫 Отлично! Теперь можешь отправить свое анонимное послание\n\n"

                    "📝 Поддерживаются:\n"
                    "• Текст\n"
                    "• Фото\n"
                    "• Видео\n"
                    "• Кружки\n"
                    "• Голосовые\n\n"

                    "🚀 Всё полетит анонимно!</i>",
                parse_mode=ParseMode.HTML,
                disable_link_preview=True,
                attachments=[markup_cancel]
            )

    recip_id = int(event.callback.payload.split(":")[1])
    await context.set_state(Sending.wait)
    await context.update_data(
                        recip_id=recip_id,
                        mess_id=mess.message.body.mid
                            )

@router.message_callback(F.callback.payload.startswith(ACTION_REPLY_CALL))
async def handle_action_reply(event: MessageCallback, context: MemoryContext):
    await event.answer("Ответ на сообщение...")
    mess = await event.message.answer(
        "<b>✏️ Введите ваш ответ</b>\n\n"

        "Отправьте сообщение, и я анонимно перешлю его пользователю",
        parse_mode=ParseMode.HTML,
        disable_link_preview=True,
        attachments=[markup_cancel]
    )

    recip_id = int(event.callback.payload.split(":")[1])
    await context.set_state(Responding.wait)
    await context.update_data(
                            recip_id=recip_id,
                            mess_id=mess.message.body.mid
                        )

@router.message_callback(F.callback.payload.startswith(ACTION_CANCEL_CALL))
async def handle_action_reply(event: MessageCallback, context: MemoryContext):
    await event.answer("Отмена действия...")
    user_id = event.from_user.user_id
    await send_main_mess(
        send_func=event.message.edit,
        bot_username=event.bot.me.username,
        user_id=user_id
    )
    await context.clear()

@router.message_created()
async def handle_ignore(event: MessageCreated):
    user_id = event.from_user.user_id
    await send_main_mess(
        event.message.answer,
        bot_username=event.bot.me.username,
        user_id=user_id,
        disable_link_preview=True
    )