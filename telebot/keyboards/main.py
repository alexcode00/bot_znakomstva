from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Заполнить анкету")],
    [KeyboardButton(text="🔍 Искать")], [KeyboardButton(text="👤 Моя анкета")]
], resize_keyboard=True)

inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❤️ Лайк", callback_data="like")], [InlineKeyboardButton(text="⏭️ Следующая анкета", callback_data="next")]
])
delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💔 Удалить анкету", callback_data="delete")], [InlineKeyboardButton(text="Изменить анкету", callback_data="edit_profile")],
    [InlineKeyboardButton(text="💖 Мои мэтчи", callback_data="my_match")]
])
def delete_match_kb(target_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Удалить", callback_data=f"delete_match:{target_id}")
    return builder.as_markup()
gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨 Мужчина")],
        [KeyboardButton(text="👩 Женщина")]
    ],
    resize_keyboard=True
)
looking_for_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨 Ищу парня")],
        [KeyboardButton(text="👩 Ищу девушку")]
    ],
    resize_keyboard=True
)
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="📣 Рассылка")],
        [KeyboardButton(text="👤 Найти пользователя")],
    ],
    resize_keyboard=True
)