import datetime
from utils import get_furnitures, get_text_order, get_text_to_manager
from config import MANAGER, TOKEN
from template import translations
from db import check_user, create_order, get_chat_id_by_order, get_order, get_order_by_pk, get_phone, get_user, login_user, update_order, register_user, get_orders_by_user
from keyboards import choose_day_keyboard, choose_language_keyboard, choose_month_keyboard, choose_time_keyboard, confirmation_keyboard, confirmation_order_keyboard, phone_button_keyboard, main_menu_keyboard, \
    catalog_categories_keyboard, back_to_main_menu_keyboard, \
    catalog_subcategories_keyboard, catalog_styles_keyboard, \
    catalog_furnitures_keyboard

from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, MediaGroup, InputFile, ReplyKeyboardRemove

storage = MemoryStorage()

class Create_order(StatesGroup):
    furniture = State()
    description = State()
    month = State()
    day = State()
    time = State()

bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

def default_message(message: Message):
    """
    Default variables
    """
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    first_name = message.from_user.first_name
    username = message.from_user.username,
    message_id = message.message_id
    return chat_id, full_name, first_name, username, message_id

def default_call(call: CallbackQuery):
    """
    Default variables
    """
    chat_id = call.message.chat.id
    full_name = call.from_user.full_name
    first_name = call.from_user.first_name
    username = call.from_user.username,
    message_id = call.message.message_id
    return chat_id, full_name, first_name, username, message_id

def get_translate_text(data, value):
    """
    Get translate text 
    """
    try:
        language = data.get('language')
        return translations[language][value]
    except KeyError:
        pass

@dp.message_handler(commands=['start', 'help', 'about']) 
async def commands(message: Message):
    """
    Reaction on commands
    """
    text = message.text
    match text:
        case '/start':
            await choose_language(message)
        case '/about':
            await message.answer(
                'Этот Бот Создан для заказа мебели...',
                parse_mode='Markdown'
            )
        case '/help':
            await message.answer(
                'У вас вопросы пишите к <Manager>...',
                parse_mode='Markdown'
            )

async def choose_language(message: Message):
    """
    Choose language bot
    """     
    await message.answer(
        text='Выберите ваш язык.',
        parse_mode='Markdown',
        reply_markup=choose_language_keyboard()
    )   

@dp.message_handler(lambda message: 'Русский'  in message.text or "O'zbekcha" in message.text)
async def set_language(message: Message, state: FSMContext):
    """
    Set language
    """
    chat_id, _, _, _, message_id = default_message(message)
    languages = {'🇷🇺 Русский': 'ru', "🇺🇿 O'zbekcha": 'uz'}
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id-1
    )
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )
    await state.update_data(
        language=languages[message.text]
    )
    await register_and_login(message, state)

async def register_and_login(message: CallbackQuery, state: FSMContext):
    """
    Login and Registration
    """
    chat_id, _, _, _, _ = default_message(message)
    data = await state.get_data()
    user = check_user(chat_id=chat_id)

    if user:
        login_user(chat_id)
        await message.answer(
            text=get_translate_text(data, 'succes_auth'),
        )
        await main_menu(message, state)
    else:
        await message.answer(
            text=get_translate_text(data, 'registration_text'),
            reply_markup=phone_button_keyboard(get_translate_text(data, 'phone_btn_keyboard'))
        )

@dp.message_handler(content_types=['contact']) 
async def finish_register(message: Message, state: FSMContext):
    """
    Registration User
    """
    chat_id, _, _, username, message_id = default_message(message)
    data = await state.get_data()
    phone = message.contact.phone_number
    register_user(username, phone, chat_id)

    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id-1
    )

    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )

    await message.answer(
        text=get_translate_text(data, 'finished_register'),
    )
    await main_menu(message, state)

async def main_menu(message: Message, state: FSMContext):
    """
    Main Menu
    """
    chat_id, _, _, _, _ = default_message(message)
    data = await state.get_data()
    catalog = get_translate_text(data, 'catalog_btn_keyboard')
    orders = get_translate_text(data, 'orders_btn_keyboard')
    settings = get_translate_text(data, 'settings_btn_keyboard')

    await bot.send_message(
        chat_id=chat_id,
        text=get_translate_text(data, 'main_menu'),
        reply_markup=main_menu_keyboard(catalog, orders, settings)
    )

async def main_menu_call(call: CallbackQuery, state: FSMContext):
    """
    Main Menu
    """
    chat_id, _, _, _, _ = default_call(call)
    data = await state.get_data()
    catalog = get_translate_text(data, 'catalog_btn_keyboard')
    orders = get_translate_text(data, 'orders_btn_keyboard')
    settings = get_translate_text(data, 'settings_btn_keyboard')
    await bot.send_message(
        chat_id=chat_id,
        text=get_translate_text(data, 'main_menu'),
        reply_markup=main_menu_keyboard(catalog, orders, settings)
    )

@dp.message_handler(lambda message: 'Каталог'  in message.text or 'Katalog' in message.text)
async def catalog_categories_list(message: Message, state: FSMContext):
    """
    Reaction on button
    """
    chat_id, _, _, _, _ = default_message(message)
    data = await state.get_data()

    await bot.send_message(
        chat_id, 
        text=get_translate_text(data, 'lets_go'),
        reply_markup=back_to_main_menu_keyboard(get_translate_text(data, 'back_to_main_menu_btn_keyboard'))
    )
    await bot.send_message(
        chat_id, 
        text=get_translate_text(data, 'choose_category'),
        reply_markup=catalog_categories_keyboard(data.get('language'))
    )

@dp.callback_query_handler(lambda call: 'categories_' in call.data)
async def catalog_subcategories_list(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data()
    category_id = int(call.data.split('_')[-1])

    await state.update_data(category_id=category_id) 
    await bot.edit_message_text(
        chat_id=chat_id,
        text=get_translate_text(data, 'choose_subcategory'),
        message_id=message_id,
        reply_markup=catalog_subcategories_keyboard(data.get('language'), get_translate_text(data, 'back'), category_id)
    )

@dp.callback_query_handler(lambda call: 'subcategory_' in call.data)
async def catalog_styles_list(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data()
    subcategory_id = int(call.data.split('_')[-1])
    
    await state.update_data(subcategory_id=subcategory_id) 
    await bot.edit_message_text(
        chat_id=chat_id,
        text=get_translate_text(data, 'choose_style'),
        message_id=message_id,
        reply_markup=catalog_styles_keyboard(data.get('language'), get_translate_text(data, 'back'))
    )

@dp.callback_query_handler(lambda call: 'style_' in call.data)
async def catalog_furnitures(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data() 
    category_id = data.get('subcategory_id')
    style_id = int(call.data.split('_')[-1])
    
    await state.update_data(style_id=style_id) 

    images_path, pk, text, quantity_furnitures, get_pk = get_furnitures(
        language=data.get('language'),
        category_id=category_id,
        style_id=style_id,
        pk=0
    )
    
    await state.update_data(pk=0) 
    
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )

    count = 0
    media = MediaGroup()

    for path in images_path:
        media.attach_photo(
            photo=InputFile(f'api{path}'), 
            caption='Фото'
        )
        count += 1

    await state.update_data(count=count) 

    await bot.send_media_group(
        chat_id=chat_id,
        media=media
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=catalog_furnitures_keyboard(get_translate_text(data, 'create_order'), pk, quantity_furnitures, get_pk),
        parse_mode='Markdown'
    )

@dp.callback_query_handler(lambda call: 'action_+' in call.data)
async def catalog_action_plus(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data() 
    category_id = data.get('subcategory_id')
    style_id = data.get('style_id')
    pk = data.get('pk') + 1
    await state.update_data(pk=pk) 

    images_path, _, text, quantity_furnitures, get_pk = get_furnitures(
        language=data.get('language'),
        category_id=category_id,
        style_id=style_id,
        pk=pk
    )
    get_count = data.get('count')

    for _ in range(get_count+1):
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id-_
        )

    count = 0
    media = MediaGroup()

    for path in images_path:
        media.attach_photo(
            photo=InputFile(f'api{path}'), 
            caption='Фото'
        )
        count += 1

    await state.update_data(count=count) 

    await bot.send_media_group(
        chat_id=chat_id,
        media=media
    )

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=catalog_furnitures_keyboard(get_translate_text(data, 'create_order'), pk, quantity_furnitures, get_pk),
        parse_mode='Markdown'
    )

@dp.callback_query_handler(lambda call: 'action_-' in call.data)
async def catalog_action_minus(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data() 
    category_id = data.get('subcategory_id')
    style_id = data.get('style_id')
    pk = data.get('pk') - 1
    await state.update_data(pk=pk) 

    images_path, _, text, quantity_furnitures, get_pk = get_furnitures(
        language=data.get('language'),
        category_id=category_id,
        style_id=style_id,
        pk=pk
    )
    get_count = data.get('count')

    for _ in range(get_count+1):
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id-_
        )

    count = 0
    media = MediaGroup()

    for path in images_path:
        media.attach_photo(
            photo=InputFile(f'api{path}'), 
            caption='Фото'
        )
        count += 1

    await state.update_data(count=count) 

    await bot.send_media_group(
        chat_id=chat_id,
        media=media
    )

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=catalog_furnitures_keyboard(get_translate_text(data, 'create_order'), pk, quantity_furnitures, get_pk),
        parse_mode='Markdown'
    )

@dp.callback_query_handler(lambda call: 'back_to_categories' in call.data)
async def back_to_categories(call: CallbackQuery, state: FSMContext):
    """
    Back to categories list
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data() 

    await bot.edit_message_text(
        text=get_translate_text(data, 'choose_category'),
        chat_id=chat_id, 
        message_id=message_id,
        reply_markup=catalog_categories_keyboard(data.get('language'))
    )

@dp.callback_query_handler(lambda call: 'back_to_subcategories' in call.data)
async def back_to_subcategories(call: CallbackQuery, state: FSMContext):
    """
    Back to subcategories list
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data() 
    category_id = data.get('category_id')

    await bot.edit_message_text(
        text=get_translate_text(data, 'choose_subcategory'),
        chat_id=chat_id, 
        message_id=message_id,
        reply_markup=catalog_subcategories_keyboard(data.get('language'), get_translate_text(data, 'back'), category_id)
    )

@dp.message_handler(lambda message: 'Главное меню'  in message.text or 'Asosiy menyu' in message.text)
async def back_to_main(message: Message, state: FSMContext):
    """
    Reaction on back button 
    """
    chat_id, _, _, _, message_id = default_message(message)
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id - 1
    )
    await main_menu(message, state)
    
@dp.callback_query_handler(lambda call: 'create_order_' in call.data)
async def confirmation(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    chat_id, _, _, _, message_id = default_call(call)
    furniture = int(call.data.split('_')[-1])
    data = await state.get_data() 
    num = data.get('count')

    for _ in range(num+1):
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id - _
        )

    await bot.send_message(
        chat_id=chat_id,
        text=get_translate_text(data, 'confirmation_order'),
        reply_markup=confirmation_keyboard(furniture)
    )
    await Create_order.furniture.set()

@dp.callback_query_handler(lambda call: 'confirmation_rejected_' in call.data, state=Create_order.furniture)
async def confirmation_rejected(call: CallbackQuery, state: FSMContext):
    """
    Back to main menu
    """
    chat_id, _, _, _, message_id = default_call(call)
    
    await state.set_state(None)
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )
    await main_menu_call(call)

@dp.callback_query_handler(lambda call: 'confirmation_confirmed_' in call.data, state=Create_order.furniture)
async def get_furniture_for_order(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    chat_id, _, _, _, message_id = default_call(call)
    data = await state.get_data() 

    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )
    await bot.send_message(
        chat_id=chat_id,
        text=get_translate_text(data, 'description_for_order'),
        reply_markup=ReplyKeyboardRemove()
    )
    async with state.proxy() as data:
        data['furniture_pk'] = int(call.data.split('_')[-1])

    await Create_order.next()

@dp.message_handler(content_types=['text'], state=Create_order.description)
async def get_description_for_order(message: Message, state: FSMContext):
    """
    Reaction on description
    """
    chat_id, _, _, _, _ = default_message(message)
    data = await state.get_data() 
    description = message.text

    await bot.send_message(
        chat_id=chat_id,
        text='Выберите месяц:',
        reply_markup=choose_month_keyboard()
    )

    async with state.proxy() as data:
        data['description'] = description

    await Create_order.next()

@dp.callback_query_handler(lambda call: 'select_month_' in call.data, state=Create_order.month)
async def get_month_for_order(call: CallbackQuery, state: FSMContext):
    chat_id, _, _, _, message_id = default_call(call)
    month = int(call.data.split('_')[-1])
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text='Выберите день: Примечание в воскресение мы не работаем.',
        reply_markup=choose_day_keyboard(month)
    )
    async with state.proxy() as data:
        data['month'] = month
    await Create_order.next()

@dp.callback_query_handler(lambda call: 'select_day_' in call.data, state=Create_order.day)
async def get_day_for_order(call: CallbackQuery, state: FSMContext):
    chat_id, _, _, _, message_id = default_call(call)
    day = int(call.data.split('_')[-1])
    name_day = call.data.split('_')[-2]
    if name_day == 'Сб':
        markup = choose_time_keyboard(
            ['10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00']
        )
    else:
        markup = choose_time_keyboard(
            ['8:00-10:00', '17:00-19:00']
        ) 
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text='Выберите время:',
        reply_markup=markup
    )
    async with state.proxy() as data:
        data['day'] = day
    await Create_order.next()

@dp.callback_query_handler(lambda call: 'select_time_' in call.data, state=Create_order.time)
async def get_time_for_order(call: CallbackQuery, state: FSMContext):
    chat_id, _, _, username, _ = default_call(call)
    data = await state.get_data() 
    status = 'Ожидание принятия заказа'
    completed = False
    user = get_user(chat_id)
    language = data.get('language')
    time = call.data.split('_')[-1]

    await bot.send_message(
        chat_id=chat_id,
        text=get_translate_text(data, 'success_create_order')
    )
    async with state.proxy() as data:
        month = int(data['month'])
        day = int(data['day'])
        description = data['description']
        furniture_pk = data(['furniture_pk'])

    datetime_order = f'{datetime.datetime.now().year}-{month}-{day}, {time}'

    create_order(
        user=user,
        furniture=furniture_pk,
        description=description,
        status=status,
        completed=completed,
        datetime_booking=datetime_order
    )

    text = send_message_to_manager(
        chat_id=chat_id, 
        username=username, 
        furniture_pk=furniture_pk, 
        description=description, 
        status=status,
        datetime_order=datetime_order
    )

    order = get_order(
        user=user, 
        furniture_pk=furniture_pk, 
        description=description, 
        status=status, 
        completed=completed,
        datetime_order=datetime_order
    )
    await bot.send_message(
        chat_id=MANAGER,
        text=text,
        reply_markup=confirmation_order_keyboard(order[0]['pk']),
        parse_mode='Markdown'
    )
    await main_menu_call(call, state)
    await state.finish()
    await state.update_data(
        language=language
    )


def send_message_to_manager(chat_id, username, furniture_pk, description, status, datetime_order):
    """
    Send message to manager group
    """
    phone = get_phone(chat_id)
    text = get_text_to_manager(
        phone=phone,
        username=username, 
        furniture_pk=furniture_pk, 
        description=description,
        status=status,
        datetime_order=datetime_order
    )
    return text
    
@dp.callback_query_handler(lambda call: 'confirmation_accepted_order_' in call.data)
async def confirmed_order(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    order = int(call.data.split('_')[-1])

    await state.update_data(
        order_pk=order
    )
    await state.update_data(
        status='принят'
    )
    await state.update_data(
        note='Через некоторое время к вам позвонит или напишет наш представитель.'
    )
    await bot.send_message(
        chat_id=MANAGER,
        text='Отправьте сообщение пользователю.'
    )
   
@dp.message_handler(content_types=['text'], chat_id=MANAGER)
async def send_message_order_accepted_to_user(message: Message, state: FSMContext):
    data = await state.get_data()
    order_pk = data.get('order_pk')
    status = data.get('status')
    note = data.get('note')

    if order_pk:
        await bot.send_message(
            chat_id=MANAGER,
            text='Сообщение отправлено пользователю.'
        )
        chat_id = get_chat_id_by_order(order_pk)
        await bot.send_message(
            chat_id=chat_id,
            text=f'''
Ваш заказ был {status}!
        
Сообщение:
{message.text}

{note}
            '''
        )
        order = get_order_by_pk(order_pk)[0]
        update_order(order_pk, order['user'], status.capitalize(), order['completed'])
        await state.update_data(
            confirmed_order_pk=None 
        )

@dp.message_handler(lambda message: 'Заказы'  in message.text or 'Buyurtmalar' in message.text)
async def user_orders(message: Message, state: FSMContext):
    """
    Reaction on button
    """
    chat_id, _, _, _, _ = default_message(message)
    data = await state.get_data() 

    await bot.send_message(
        chat_id=chat_id,
        text=get_translate_text(data, 'last_orders'), 
        reply_markup=back_to_main_menu_keyboard(get_translate_text(data, 'back_to_main_menu_btn_keyboard'))
    )

    orders = get_orders_by_user(
        user=get_user(chat_id)
    )[::-1]
    for order in orders[:5]:
        await bot.send_message(
            chat_id=chat_id,
            text=get_text_order(data.get('language'), order),
            parse_mode='Markdown'
        )
    
@dp.message_handler(lambda message: 'Настройки'  in message.text or 'Sozlamalar' in message.text)
async def settings(message: Message, state: FSMContext):
    """
    Reaction on button
    """
    chat_id, _, _, _, _ = default_message(message)
    data = await state.get_data() 

    await bot.send_message(
        chat_id=chat_id,
        text=get_translate_text(data, 'change_language'),
        reply_markup=choose_language_keyboard()
    )

@dp.callback_query_handler(lambda call: 'confirmation_rejected_order_' in call.data)
async def confirmed_rejected_order(call: CallbackQuery, state: FSMContext):
    """
    Reaction on call button
    """
    order = int(call.data.split('_')[-1])
    await state.update_data(
        order_pk=order
    )
    await state.update_data(
        order_pk=order
    )
    await state.update_data(
        status='отказан'
    )
    await state.update_data(
        note='Статус вашего заказа изменен на отказ.'
    )

    await bot.send_message(
        chat_id=MANAGER,
        text='Отправьте причину отказа пользователю.'
    )
   
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)