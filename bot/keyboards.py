from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton


ACTION_REPLY_CALL = "action_reply"
ACTION_ADD_MESS_CALL = "action_add_mess"
ACTION_CANCEL_CALL = "action_cancel"

builder_cancel = InlineKeyboardBuilder()
builder_cancel.row(CallbackButton(text="❌ Отменить", payload=ACTION_CANCEL_CALL))
markup_cancel = builder_cancel.as_markup()


async def create_reply_keyboard(recip_id: int):
    builder_reply = InlineKeyboardBuilder()
    builder_reply.row(CallbackButton(text="🗣 Ответить", payload=f"{ACTION_REPLY_CALL}:{recip_id}"))
    markup_reply = builder_reply.as_markup()
    return markup_reply

async def create_add_mess_keyboard(recip_id: int):
    builder_reply = InlineKeyboardBuilder()
    builder_reply.row(CallbackButton(text="✏️ Отправить еще", payload=f"{ACTION_ADD_MESS_CALL}:{recip_id}"))
    markup_reply = builder_reply.as_markup()
    return markup_reply

async def create_share_link_keyboard(link: str):
    text = f"По%20этой%20ссылке%20можно%20задать%20мне%20анонимный%20вопрос%0A👉%20{link}"
    builder_button = InlineKeyboardBuilder()
    builder_button.row(LinkButton(text="🔗 Поделиться ссылкой", url=f"https://max.ru/:share?text={text}"))
    markup_button = builder_button.as_markup()
    return markup_button