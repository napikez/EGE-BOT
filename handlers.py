from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

from database import update_progress, check_progress, set_setting, get_setting
from ai_teacher import get_teacher_answer

router = Router()

class AdminState(StatesGroup):
    waiting_for_photo = State()

async def clear_chat(message: Message, state: FSMContext, new_msg_id: int = None):
    """Удаляет старые сообщения, чтобы интерфейс был чистым."""
    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    
    if last_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, last_msg_id)
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass
    
    if new_msg_id:
        await state.update_data(last_msg_id=new_msg_id)

def get_main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пройти тест (Тема 1)", callback_data="test_topic_1")],
        [InlineKeyboardButton(text="Задать вопрос учителю", callback_data="ask_teacher")]
    ])

@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    kb = get_main_menu_kb()
    photo_id = get_setting("main_menu_photo")
    text = "Добро пожаловать в ЕГЭ Бот. Выберите нужное действие:"
    
    if photo_id:
        msg = await message.answer_photo(photo=photo_id, caption=text, reply_markup=kb)
    else:
        msg = await message.answer(text, reply_markup=kb)
        
    await clear_chat(message, state, msg.message_id)

@router.message(Command("setphoto"))
async def set_photo_cmd(message: Message, state: FSMContext):
    # Проверка на админа
    if str(message.from_user.id) != str(os.getenv("ADMIN_ID")):
        return
    
    msg = await message.answer("Отправьте фотографию для главного меню бота.")
    await state.set_state(AdminState.waiting_for_photo)
    await clear_chat(message, state, msg.message_id)

@router.message(AdminState.waiting_for_photo, F.photo)
async def save_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    set_setting("main_menu_photo", photo_id)
    msg = await message.answer("Фотография успешно обновлена. Нажмите /start для проверки.")
    await state.clear()
    await clear_chat(message, state, msg.message_id)

@router.callback_query(F.data.startswith("test_topic_"))
async def start_test(callback: CallbackQuery):
    topic = callback.data
    status = check_progress(callback.from_user.id, topic)
    
    status_text = "✅ Пройдено" if status else "❌ Не пройдено"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить полностью", callback_data=f"finish_{topic}")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_menu")]
    ])
    
    await callback.message.edit_text(
        f"Тестовый блок.\nСтатус: {status_text}\n\nЗдесь находится теория и задание...",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("finish_"))
async def finish_test(callback: CallbackQuery):
    topic = callback.data.replace("finish_", "")
    update_progress(callback.from_user.id, topic, 1) # Сохраняем, что прошел
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пройти заново", callback_data=topic)],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_menu")]
    ])
    
    await callback.message.edit_text(
        "Блок успешно пройден! Статус обновлен в вашей личной статистике.",
        reply_markup=kb
    )

@router.callback_query(F.data == "back_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    kb = get_main_menu_kb()
    photo_id = get_setting("main_menu_photo")
    text = "Главное меню:"
    
    if photo_id:
        await callback.message.delete()
        msg = await callback.message.answer_photo(photo=photo_id, caption=text, reply_markup=kb)
        await state.update_data(last_msg_id=msg.message_id)
    else:
        await callback.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "ask_teacher")
async def ask_teacher_btn(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.edit_text("Напишите ваш вопрос для учителя прямо в чат:")
    await state.update_data(last_msg_id=msg.message_id)

@router.message(F.text)
async def handle_teacher_question(message: Message, state: FSMContext):
    # Показываем заглушку, пока нейросеть думает
    wait_msg = await message.answer("Учитель проверяет информацию и печатает ответ...")
    await clear_chat(message, state, wait_msg.message_id)
    
    answer = await get_teacher_answer(message.text)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_menu")]
    ])
    
    await wait_msg.edit_text(answer, reply_markup=kb)
