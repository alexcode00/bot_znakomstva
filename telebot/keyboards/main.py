from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Заполнить анкету")],
    [KeyboardButton(text="🔍 Искать")], [KeyboardButton(text="👤 Моя анкета")], [KeyboardButton(text="💖 Мои мэтчи")]
], resize_keyboard=True)

inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❤️ Лайк", callback_data="like")], [InlineKeyboardButton(text="⏭️ Следующая анкета", callback_data="next")]
])
delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💔 Удалить анкету", callback_data="delete")]
])
def delete_match_kb(target_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Удалить", callback_data=f"delete_match:{target_id}")
    return builder.as_markup()