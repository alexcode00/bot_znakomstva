import asyncio
import os
from aiogram.types import ReplyKeyboardRemove
from telebot.valid import validate_age, validate_name, is_admin
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from telebot.database import db
from telebot.states import Reg, Broadcast, Search
import telebot.keyboards as kb

load_dotenv()
router = Router()
MALE = "male"
FEMALE = "female"



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
async def get_name(message: Message, state: FSMContext):
    name = message.text
    error = validate_name(name)
    if error:
        await message.answer(error)
        return
    await state.update_data(name=name)
    await state.set_state(Reg.age)
    await message.answer("😁 Введите возраст:")

@router.message(Reg.age)
async def name(message: Message, state: FSMContext):
    age = message.text
    error = validate_age(age)
    if error:
        await message.answer(error)
        return
    await state.update_data(age=age)
    await state.set_state(Reg.gender)
    await message.answer(
        "Укажите пол:",
        reply_markup=kb.gender_kb
    )
@router.message(Reg.gender)
async def get_gender(message: Message, state: FSMContext):

    if message.text not in ["👨 Мужчина", "👩 Женщина"]:
        await message.answer("Выберите вариант кнопкой")
        return

    gender = MALE if "Мужчина" in message.text else FEMALE

    await state.update_data(gender=gender)
    await state.set_state(Reg.looking_for)

    await message.answer(
        "Кого хотите найти?",
        reply_markup=kb.looking_for_kb
    )
@router.message(Reg.looking_for)
async def get_looking_for(message: Message, state: FSMContext):

    if message.text == "👨 Ищу парня":
        looking_for = MALE

    elif message.text == "👩 Ищу девушку":
        looking_for = FEMALE

    else:
        await message.answer("Выберите вариант кнопкой")
        return

    await state.update_data(looking_for=looking_for)
    await state.set_state(Reg.city)
    await message.answer("🎰 Введите город:", reply_markup=ReplyKeyboardRemove())



@router.message(Reg.city)
async def get_city(message: Message, state: FSMContext):
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
    if not photo_user:
        await message.answer("Отправьте фото")
        return
    await state.update_data(photo=photo_user)
    data = await state.get_data()
    photo_from_user = data.get("photo")
    if data["mode"] == "create":
        await db.add_user(
            message.from_user.id,
            data["name"],
            data["age"],
            data["gender"],
            data["looking_for"],
            data["city"],
            data["about"],
            data["photo"]
        )
        await message.answer("🎉 Анкета успешно создана!", reply_markup=kb.main)

    elif data["mode"] == "edit":
        await db.update_user(
            message.from_user.id,
            data["name"],
            data["age"],
            data["gender"],
            data["looking_for"],
            data["city"],
            data["about"],
            data["photo"]
        )
        await message.answer("🎉 Анкета успешно обновлена!", reply_markup=kb.main)

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

@router.message(F.text == "👤 Моя анкета")
async def my_profile(message: Message):
    profile = await db.get_user(message.from_user.id)
    if not profile:
        await message.answer("💢У вас нет анкеты")
        return
    await message.answer_photo(photo=profile[4], caption=f'Ваша анкета\n\n👤Имя: {profile[0]}\n🎂Возраст: {profile[1]}\n🏙Город: {profile[2]}\n💬О себе: {profile[3]}', reply_markup=kb.delete)


@router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user = await db.get_user(callback.from_user.id)

    if not user:
        await callback.message.answer("Сначала создайте анкету.")
        return

    await state.update_data(mode="edit")
    await state.set_state(Reg.name)

    await callback.message.answer("✏️ Введите новое имя:")
@router.message(F.text == "🔍 Искать")
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
async def next_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("🔍 Ищу анкету...")
    user = await db.get_random_user(callback.from_user.id)
    if not user:
        await callback.message.answer("😔 Новых анкет пока нет, загляни позже!")
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


        my_profile = await db.get_user(callback.from_user.id)
        contact = f"@{callback.from_user.username}" if callback.from_user.username else f"tg://user?id={callback.from_user.id}"
        await callback.message.answer(f"🎉 У вас взаимный лайк!\nНапишите ему: tg://user?id={target_id}")
        await callback.bot.send_message(
            target_id,
            f"🎉 Взаимный лайк!\n"
            f"👤 {my_profile[0]}, напишите: {contact}"
        )
    else:
        await callback.answer("💖 Лайк поставлен!")
@router.callback_query(F.data == "my_match")
async def my_match(callback: CallbackQuery):
    await callback.answer()
    my_matches = await db.my_match(callback.from_user.id)
    if not my_matches:
        await callback.message.answer("У вас нет мэтчэй!")
        return
    await callback.message.answer(f"У вас {len(my_matches)} мэтчей")
    for row in my_matches:
        await callback.message.answer_photo(photo=row[5], caption=f"💖 Ваш мэтч!\n\n👤 Имя: {row[1]}\n🎂 Возраст: {row[2]}\n🏙 Город: {row[3]}\n💬 Обо мне:{row[4]}", reply_markup=kb.delete_match_kb(row[0]))
@router.callback_query(F.data.startswith("delete_match:"))
async def del_match(callback: CallbackQuery):
    try:
        target_id = int(callback.data.split(":")[1])
    except Exception as err:
        await callback.answer(f"Ошибка {err}", show_alert=True)
        return
    await db.delete_match(callback.from_user.id, target_id)
    await callback.message.delete()
    await callback.answer("💔 Матч удалён")
@router.message(Command("admin_panel"))
async def adm_pan(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа")
        return
    await message.answer("Ваша админ панель", reply_markup=kb.admin_menu)
@router.message(F.text == "📊 Статистика")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    users = await db.count_users()
    likes = await db.count_likes()

    await message.answer(
        f"📊 Статистика:\n\n"
        f"👥 Пользователей: {users}\n"
        f"💖 Лайков: {likes}\n"
    )
@router.message(F.text == "📣 Рассылка")
async def start_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(Broadcast.message)
    await message.answer("Введите текст рассылки:")
@router.message(Broadcast.message)
async def send_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    text = message.text
    await message.answer("Начало рассылки")
    users = await db.get_all_users(message.from_user.id)

    for user in users:
        try:
            await message.bot.send_message(user[1], text)
            await asyncio.sleep(0.05)
        except Exception as error:
            print(f"Произошла ошибка {error}")
            continue
    await state.clear()
    await message.answer("Рассылка завершена", reply_markup=kb.admin_menu)
@router.message(F.text == "👤 Найти пользователя")
async def search_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Введите id пользователя чью анкету надо найти")
    await state.set_state(Search.user_id)
@router.message(Search.user_id)
async def send_anketa(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    if not message.text.isdigit():
        await message.answer("Введите числовой ID")
        return

    user = await db.get_user(int(message.text))

    if not user:
        await message.answer("Пользователь не найден")
        return

    await message.answer_photo(
        photo=user[4],
        caption=
        f'Анкета пользователя\n\n'
        f'👤Имя: {user[0]}\n'
        f'🎂Возраст: {user[1]}\n'
        f'🏙Город: {user[2]}\n'
        f'💬О себе: {user[3]}',
        reply_markup=kb.admin_menu
    )

    await state.clear()
