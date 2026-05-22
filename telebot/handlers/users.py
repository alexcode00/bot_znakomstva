from aiogram.types import FSInputFile
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from typing_inspection.typing_objects import target

from telebot.database import db
from telebot.states import Reg
import telebot.keyboards as kb
from aiogram.filters.logic import or_f

router = Router()




@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer("💘 <b>Добро пожаловать в бот знакомств!</b>\n\n"
"Здесь вы можете:\n"
"📝 Создать анкету\n"
"🔍 Найти интересных людей\n"
"💖 Получать взаимные лайки", reply_markup=kb.main, parse_mode="HTML")


@router.message(F.text == "📝 Заполнить анкету")
async def create_profile(message: Message, state: FSMContext):
    if await db.get_user(message.from_user.id):
        await message.answer("Вы уже есть в базе.")
        return

    await state.update_data(mode="create")
    await state.set_state(Reg.name)
    await message.answer("📝 Введите имя:")
@router.message(Reg.name)
async def name(message: Message, state: FSMContext):
    text = message.text.strip()


    if not text.isalpha():
        await message.answer("Имя должно содержать только буквы.🫸")
        return


    if len(text) < 2 or len(text) > 30:
        await message.answer("Имя должно быть от 2 до 30 символов.🫸")
        return


    name = text.capitalize()
    await state.update_data(name=name)
    await state.set_state(Reg.age)
    await message.answer("😁 Введите возраст:")

@router.message(Reg.age)
async def name(message: Message, state: FSMContext):
    age = message.text
    if not age.isdigit():
        await message.answer("Введите число🫸")
        return
    if int(age) < 16 or int(age) > 50:
        await message.answer("Ваш возраст указан неккоректно либо вам меньше 16🫸")
        return
    await state.update_data(age=message.text)
    await state.set_state(Reg.city)
    await message.answer("🎰 Введите город:")




@router.message(Reg.city)
async def city(message: Message, state: FSMContext):
    city = message.text
    if not city.isalpha():
        await message.answer("Введите корректный город🫸")
        return
    await state.update_data(city=message.text)
    await state.set_state(Reg.about)
    await message.answer("🆔 Введите информацию о себе:")

@router.message(Reg.about)
async def about(message: Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(Reg.photo)
    await message.answer("📷Отправьте вашу фотографию")
@router.message(Reg.photo)
async def photo(message: Message, state: FSMContext):
    photo_user = message.photo[-1].file_id
    await state.update_data(photo=photo_user)
    data = await state.get_data()
    photo_from_user = data.get("photo")
    if data["mode"] == "create":
        await db.add_user(
            message.from_user.id,
            data["name"],
            data["age"],
            data["city"],
            data["about"],
            data["photo"]
        )
        await message.answer("🎉 Анкета успешно создана!")

    elif data["mode"] == "edit":
        await db.update_user(
            message.from_user.id,
            data["name"],
            data["age"],
            data["city"],
            data["about"],
            data["photo"]
        )
        await message.answer("🎉 Анкета успешно обновлена!")

    await message.answer_photo(photo=photo_from_user,
        caption=
        f"👤Имя: {data['name']}\n"
        f"🎂Возраст: {data['age']}\n"
        f"🏙Город: {data['city']}\n"
        f"💬О себе: {data['about']}"
    )
    await state.clear()


@router.callback_query(F.data == "delete")
async def del_profile(callback: CallbackQuery):
    await callback.answer()
    if await db.delete_profile(callback.from_user.id):
        await callback.message.answer("💢Ваша анкета была удалена")
    else:
        await callback.message.answer("💢У вас нет анкеты")

@router.message(or_f(Command("my_profile"), F.text == "👤 Моя анкета"))
async def my_profile(message: Message):
    profile = await db.get_user(message.from_user.id)
    if not profile:
        await message.answer("💢У вас нет анкеты")
        return
    await message.answer_photo(photo=profile[4], caption=f'Ваша анкета\n\n👤Имя: {profile[0]}\n🎂Возраст: {profile[1]}\n🏙Город: {profile[2]}\n💬О себе: {profile[3]}', reply_markup=kb.delete)


@router.message(Command("edit_profile"))
async def edit_profile(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)

    if not user:
        await message.answer(
            "Сначала создайте анкету.",
            reply_markup=kb.main
        )
        return

    await state.update_data(mode="edit")
    await state.set_state(Reg.name)
    await message.answer("Введите новое имя")

@router.message(or_f(Command("search"), F.text == "🔍 Искать"))
async def search_user(message: Message, state: FSMContext):
    if not await db.get_user(message.from_user.id):
        await message.answer("💢Сначала создайте анкету!")
        return
    await message.answer("🔍 Ищу анкету...")
    user = await db.get_random_user(message.from_user.id)
    if not user:
        await message.answer("😔 Новых анкет пока нет, загляни позже!")
        return
    await state.update_data(target_id=user[0])
    await message.answer_photo(photo=user[5], caption=f'🎉Найденный пользователь:\n\n👤Имя: {user[1]}\n🎂Возраст: {user[2]}\n🏙Город: {user[3]}\n💬О себе: {user[4]}', reply_markup=kb.inline)
@router.callback_query(F.data == "next")
async def next(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("🔍 Ищу анкету...")
    user = await db.get_random_user(callback.from_user.id)
    if not user:
        await callback.answer("😔 Новых анкет пока нет, загляни позже!")
        return
    await state.update_data(target_id=user[0])
    await callback.message.answer_photo(photo=user[5],
        caption=f'🎉Найденный пользователь:\n\n👤Имя: {user[1]}\n🎂Возраст: {user[2]}\n🏙Город: {user[3]}\n💬О себе: {user[4]}',
        reply_markup=kb.inline)


@router.callback_query(F.data == "like")
async def like(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")

    if not target_id:
        await callback.answer("Сначала найдите анкету!", show_alert=True)
        return

    await db.add_like(callback.from_user.id, target_id)

    if await db.is_match(callback.from_user.id, target_id):
        await callback.answer("🎉 У вас взаимный лайк!", show_alert=True)

        # Получаем данные обоих пользователей чтобы передать контакт
        my_profile = await db.get_user(callback.from_user.id)

        await callback.message.answer(f"🎉 У вас взаимный лайк!\nНапишите ему: tg://user?id={target_id}")
        await callback.bot.send_message(
            target_id,
            f"🎉 Взаимный лайк!\n"
            f"👤 {my_profile[0]}, напишите: @{callback.from_user.username}"
        )
    else:
        await callback.answer("💖 Лайк поставлен!")
@router.message(F.text == "💖 Мои мэтчи")
async def my_match(message: Message):
    my_matches = await db.my_match(message.from_user.id)
    if not my_matches:
        await message.answer("У вас нет мэтчэй!")
        return
    await message.answer(f"У вас {len(my_matches)} мэтчей")
    for row in my_matches:
        await message.answer_photo(photo=row[5], caption=f"💖 Ваш мэтч!\n\n👤 Имя: {row[1]}\n🎂 Возраст: {row[2]}\n🏙 Город: {row[3]}\n💬 Обо мне:{row[4]}", reply_markup=kb.delete_match_kb(row[0]))
@router.callback_query(F.data.startswith("delete_match:"))
async def del_match(callback: CallbackQuery):
    target_id = int(callback.data.split(":")[1])
    await db.delete_match(callback.from_user.id, target_id)
    await callback.message.delete()
    await callback.answer("💔 Матч удалён")

