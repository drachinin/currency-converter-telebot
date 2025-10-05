import telebot
import requests
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# токен бота (получите у @BotFather)
BOT_TOKEN = ""
bot = telebot.TeleBot(BOT_TOKEN)

# API от exchangerate-api.com (бесплатный)
API_KEY = ""
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"

# популярные валюты для кнопок
POPULAR_CURRENCIES = {
    'USD': {'name': '🇺🇸 Доллар', 'emoji': '🇺🇸'},
    'EUR': {'name': '🇪🇺 Евро', 'emoji': '🇪🇺'},
    'RUB': {'name': '🇷🇺 Рубль', 'emoji': '🇷🇺'},
    'CNY': {'name': '🇨🇳 Юань', 'emoji': '🇨🇳'},
    'AED': {'name': '🇦🇪 Дирхам ОАЭ', 'emoji': '🇦🇪'},
    'THB': {'name': '🇹🇭 Бат Таиланд', 'emoji': '🇹🇭'},
    'TRY': {'name': '🇹🇷 Лира', 'emoji': '🇹🇷'},
    'BYN': {'name': '🇧🇾 Белорусский рубль', 'emoji': '🇧🇾'}
}

# все доступные валюты
ALL_CURRENCIES = {
    'USD': '🇺🇸 Доллар США',
    'EUR': '🇪🇺 Евро',
    'RUB': '🇷🇺 Российский рубль',
    'GBP': '🇬🇧 Фунт стерлингов',
    'JPY': '🇯🇵 Японская иена',
    'AED': '🇦🇪 Дирхам ОАЭ',
    'THB': '🇹🇭 Бат Таиланд',
    'CNY': '🇨🇳 Китайский юань',
    'CAD': '🇨🇦 Канадский доллар',
    'AUD': '🇦🇺 Австралийский доллар',
    'CHF': '🇨🇭 Швейцарский франк',
    'SGD': '🇸🇬 Сингапурский доллар',
    'TRY': '🇹🇷 Турецкая лира',
    'BYN': '🇧🇾 Белорусский рубль',
    'KZT': '🇰🇿 Казахстанский тенге'
}

user_states = {}

# меню
def create_main_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    menu.add(
        KeyboardButton("💱 Обычная конвертация"),
        KeyboardButton("🔄 Обратная конвертация"),
        KeyboardButton("📊 Курс валют"),
        KeyboardButton("📋 Доступные валюты")
    )
    return menu

# функция для форматирования числа
def format_number(number):
    try:
        if isinstance(number, float):
            integer_part = int(number)
            fractional_part = number - integer_part
        else:
            integer_part = number
            fractional_part = 0

        formatted_integer = "{:,}".format(integer_part).replace(",", " ")

        if fractional_part > 0:
            fractional_str = f"{fractional_part:.2f}".split('.')[1]
            return f"{formatted_integer}.{fractional_str}"
        else:
            return formatted_integer
    except:
        return str(number)

# получение курса валюты
def get_exchange_rate(base_currency, target_currency):
    try:
        response = requests.get(f"{BASE_URL}{base_currency}")
        data = response.json()

        if data['result'] == 'success':
            return data['conversion_rates'].get(target_currency)
        else:
            return None
    except:
        return None

# курсы валют относительно рубля
def get_rub_exchange_rates():
    try:
        response = requests.get(f"{BASE_URL}USD")
        data = response.json()

        if data['result'] != 'success':
            return None

        usd_rates = data['conversion_rates']
        rub_per_usd = usd_rates.get('RUB')

        if not rub_per_usd:
            return None

        rates = {}
        for currency in ['USD', 'EUR', 'AED', 'THB', 'CNY', 'BYN', 'GBP', 'JPY', 'TRY', 'KZT', 'CAD', 'AUD', 'CHF',
                         'SGD']:
            if currency == 'RUB':
                continue

            if currency == 'USD':
                rates[currency] = rub_per_usd
            else:
                currency_to_usd = usd_rates.get(currency)
                if currency_to_usd and currency_to_usd > 0:
                    rates[currency] = rub_per_usd / currency_to_usd

        return rates
    except:
        return None

# создание инлайн клавиатуры
def create_currency_keyboard(selected_currency=None, step=1, conversion_type='normal'):
    keyboard = InlineKeyboardMarkup(row_width=3)

    buttons = []
    for currency, info in POPULAR_CURRENCIES.items():
        if step == 1:
            buttons.append(InlineKeyboardButton(
                text=f"{info['emoji']} {currency}",
                callback_data=f"{conversion_type}_from_{currency}"
            ))
        else:
            if currency != selected_currency:
                buttons.append(InlineKeyboardButton(
                    text=f"{info['emoji']} {currency}",
                    callback_data=f"{conversion_type}_to_{currency}"
                ))

    for i in range(0, len(buttons), 3):
        keyboard.add(*buttons[i:i + 3])

    if step == 1:
        keyboard.add(InlineKeyboardButton("📋 Все валюты", callback_data=f"{conversion_type}_all_currencies"))
    else:
        keyboard.add(InlineKeyboardButton("📋 Все валюты",
                                          callback_data=f"{conversion_type}_all_currencies_to_{selected_currency}"))

    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))

    return keyboard

# клавиатура со всеми валютами
def create_all_currencies_keyboard(selected_currency=None, step=1, conversion_type='normal'):
    keyboard = InlineKeyboardMarkup(row_width=3)

    buttons = []
    for currency, name in ALL_CURRENCIES.items():
        if step == 1:
            buttons.append(InlineKeyboardButton(
                text=f"{currency}",
                callback_data=f"{conversion_type}_from_{currency}"
            ))
        else:
            if currency != selected_currency:
                buttons.append(InlineKeyboardButton(
                    text=f"{currency}",
                    callback_data=f"{conversion_type}_to_{currency}"
                ))

    for i in range(0, len(buttons), 3):
        keyboard.add(*buttons[i:i + 3])

    if step == 1:
        keyboard.add(InlineKeyboardButton("◀️ Назад к популярным", callback_data=f"{conversion_type}_back_to_popular"))
    else:
        keyboard.add(InlineKeyboardButton("◀️ Назад к популярным",
                                          callback_data=f"{conversion_type}_back_to_popular_to_{selected_currency}"))

    return keyboard

# старт
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
Доступные функции:
*Обычная конвертация* - перевести сумму из одной валюты в другую
*Обратная конвертация* - узнать сколько нужно валюты для получения нужной суммы
*Курс валют* - актуальные курсы к рублю
*Доступные валюты* - список всех поддерживаемых валют

Используйте кнопки меню ниже для удобства!
    """

    bot.send_message(message.chat.id, welcome_text,
                     parse_mode='Markdown',
                     reply_markup=create_main_menu())

# обычная конвертация
@bot.message_handler(commands=['convert'])
def start_conversion_command(message):
    start_conversion_process(message.chat.id, 'normal')

# обратная конвертация
@bot.message_handler(commands=['reverse'])
def start_reverse_conversion_command(message):
    start_conversion_process(message.chat.id, 'reverse')

# показать курсы валют
@bot.message_handler(commands=['rates'])
def show_rates_command(message):
    show_rates(message.chat.id)

# показать список валют
@bot.message_handler(commands=['currencies'])
def show_currencies_command(message):
    """Показать список валют через команду"""
    show_currencies(message.chat.id)

# нажатие на кнопку
@bot.message_handler(
    func=lambda message: message.text in ["💱 Обычная конвертация", "🔄 Обратная конвертация", "📊 Курс валют",
                                          "📋 Доступные валюты"])
def handle_menu_buttons(message):
    if message.text == "💱 Обычная конвертация":
        start_conversion_process(message.chat.id, 'normal')
    elif message.text == "🔄 Обратная конвертация":
        start_conversion_process(message.chat.id, 'reverse')
    elif message.text == "📊 Курс валют":
        show_rates(message.chat.id)
    elif message.text == "📋 Доступные валюты":
        show_currencies(message.chat.id)

# показать курсы валют к рублю
def show_rates(chat_id):
    try:
        rates_text = "📈 *Курсы валют к российскому рублю:*\n\n"
        rates_text += "*Сколько рублей дают за 1 единицу валюты:*\n\n"

        rub_rates = get_rub_exchange_rates()

        if not rub_rates:
            bot.send_message(chat_id, "❌ *Не удалось получить актуальные курсы*", parse_mode='Markdown',
                             reply_markup=create_main_menu())
            return

        main_currencies = ['USD', 'EUR', 'AED', 'THB', 'CNY', 'BYN']
        for currency in main_currencies:
            rate = rub_rates.get(currency)
            if rate:
                currency_name = POPULAR_CURRENCIES.get(currency, {}).get('name', ALL_CURRENCIES.get(currency, currency))
                formatted_rate = format_number(round(rate, 2))
                rates_text += f"• 1 {currency} ({currency_name}) = *{formatted_rate} RUB*\n"

        rates_text += "\n*Другие валюты:*\n"

        other_currencies = ['GBP', 'JPY', 'TRY', 'KZT', 'CAD', 'AUD']
        for currency in other_currencies:
            rate = rub_rates.get(currency)
            if rate:
                currency_name = ALL_CURRENCIES.get(currency, currency)
                formatted_rate = format_number(round(rate, 2))
                rates_text += f"• 1 {currency} = *{formatted_rate} RUB*\n"

        rates_text += f"\n🔀 *Популярные кросс-курсы:*\n"
        cross_pairs = [('EUR', 'USD'), ('USD', 'AED'), ('USD', 'THB')]

        for from_curr, to_curr in cross_pairs:
            rate = get_exchange_rate(from_curr, to_curr)
            if rate:
                rates_text += f"• 1 {from_curr} = *{rate:.4f}* {to_curr}\n"

        rates_text += f"\n📅 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"

        bot.send_message(chat_id, rates_text, parse_mode='Markdown', reply_markup=create_main_menu())

    except Exception as e:
        bot.send_message(chat_id, f"❌ *Ошибка при получении курсов:* {str(e)}", parse_mode='Markdown',
                         reply_markup=create_main_menu())

# показать список доступных валют
def show_currencies(chat_id):
    try:
        currencies_text = "📋 *Доступные валюты:*\n\n"

        for code, name in ALL_CURRENCIES.items():
            currencies_text += f"• *{code}* - {name}\n"

        currencies_text += f"\n*Всего валют:* {len(ALL_CURRENCIES)}"

        bot.send_message(chat_id, currencies_text, parse_mode='Markdown', reply_markup=create_main_menu())

    except Exception as e:
        bot.send_message(chat_id, f"❌ *Ошибка при получении списка валют:* {str(e)}", parse_mode='Markdown',
                         reply_markup=create_main_menu())


@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "cancel":
        bot.delete_message(chat_id, message_id)
        if chat_id in user_states:
            del user_states[chat_id]
        bot.send_message(chat_id, "Операция отменена.", reply_markup=create_main_menu())

    elif call.data == "normal_back_to_popular":
        bot.edit_message_text(
            "💱 *Обычная конвертация*\n\nВыберите исходную валюту:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(step=1, conversion_type='normal')
        )

    elif call.data.startswith("normal_back_to_popular_to_"):
        from_currency = call.data.split('_')[-1]
        bot.edit_message_text(
            f"💱 *Обычная конвертация из {from_currency}*\n\nВыберите целевую валюту:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(selected_currency=from_currency, step=2, conversion_type='normal')
        )

    elif call.data == "normal_all_currencies":
        bot.edit_message_text(
            "💱 *Обычная конвертация*\n\nВыберите исходную валюту из полного списка:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_all_currencies_keyboard(step=1, conversion_type='normal')
        )

    elif call.data.startswith("normal_all_currencies_to_"):
        from_currency = call.data.split('_')[-1]
        bot.edit_message_text(
            f"💱 *Обычная конвертация из {from_currency}*\n\nВыберите целевую валюту из полного списка:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_all_currencies_keyboard(selected_currency=from_currency, step=2,
                                                        conversion_type='normal')
        )

    elif call.data.startswith("normal_from_"):
        from_currency = call.data.split('_')[-1]
        user_states[chat_id] = {
            'conversion_type': 'normal',
            'from_currency': from_currency,
            'step': 2,
            'last_message_id': message_id
        }

        bot.edit_message_text(
            f"💱 *Обычная конвертация из {from_currency}*\n\nВыберите целевую валюту:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(selected_currency=from_currency, step=2, conversion_type='normal')
        )

    elif call.data.startswith("normal_to_"):
        to_currency = call.data.split('_')[-1]

        if chat_id in user_states and user_states[chat_id]['step'] == 2 and user_states[chat_id][
            'conversion_type'] == 'normal':
            from_currency = user_states[chat_id]['from_currency']
            user_states[chat_id] = {
                'conversion_type': 'normal',
                'from_currency': from_currency,
                'to_currency': to_currency,
                'step': 3,
                'last_message_id': message_id
            }

            bot.edit_message_text(
                f"💱 *Обычная конвертация: {from_currency} → {to_currency}*\n\n*Введите сумму для конвертации:*",
                chat_id, message_id,
                parse_mode='Markdown'
            )

    elif call.data == "reverse_back_to_popular":
        bot.edit_message_text(
            "🔄 *Обратная конвертация*\n\nВыберите исходную валюту:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(step=1, conversion_type='reverse')
        )

    elif call.data.startswith("reverse_back_to_popular_to_"):
        from_currency = call.data.split('_')[-1]
        bot.edit_message_text(
            f"🔄 *Обратная конвертация из {from_currency}*\n\nВыберите целевую валюту:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(selected_currency=from_currency, step=2, conversion_type='reverse')
        )

    elif call.data == "reverse_all_currencies":
        bot.edit_message_text(
            "🔄 *Обратная конвертация*\n\nВыберите исходную валюту из полного списка:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_all_currencies_keyboard(step=1, conversion_type='reverse')
        )

    elif call.data.startswith("reverse_all_currencies_to_"):
        from_currency = call.data.split('_')[-1]
        bot.edit_message_text(
            f"🔄 *Обратная конвертация из {from_currency}*\n\nВыберите целевую валюту из полного списка:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_all_currencies_keyboard(selected_currency=from_currency, step=2,
                                                        conversion_type='reverse')
        )

    elif call.data.startswith("reverse_from_"):
        from_currency = call.data.split('_')[-1]
        user_states[chat_id] = {
            'conversion_type': 'reverse',
            'from_currency': from_currency,
            'step': 2,
            'last_message_id': message_id
        }

        bot.edit_message_text(
            f"🔄 *Обратная конвертация из {from_currency}*\n\nВыберите целевую валюту:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(selected_currency=from_currency, step=2, conversion_type='reverse')
        )

    elif call.data.startswith("reverse_to_"):
        to_currency = call.data.split('_')[-1]

        if chat_id in user_states and user_states[chat_id]['step'] == 2 and user_states[chat_id][
            'conversion_type'] == 'reverse':
            from_currency = user_states[chat_id]['from_currency']
            user_states[chat_id] = {
                'conversion_type': 'reverse',
                'from_currency': from_currency,
                'to_currency': to_currency,
                'step': 3,
                'last_message_id': message_id
            }

            bot.edit_message_text(
                f"🔄 *Обратная конвертация: {from_currency} → {to_currency}*\n\n*Введите желаемую сумму в {to_currency}:*",
                chat_id, message_id,
                parse_mode='Markdown'
            )

# запуск процесса конвертации
def start_conversion_process(chat_id, conversion_type='normal', message_id=None):
    user_states[chat_id] = {'step': 1, 'conversion_type': conversion_type}

    type_text = "💱 Обычная конвертация" if conversion_type == 'normal' else "🔄 Обратная конвертация"

    if message_id:
        bot.edit_message_text(
            f"{type_text}\n\nВыберите исходную валюту:",
            chat_id, message_id,
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(step=1, conversion_type=conversion_type)
        )
    else:
        msg = bot.send_message(
            chat_id,
            f"{type_text}\n\nВыберите исходную валюту:",
            parse_mode='Markdown',
            reply_markup=create_currency_keyboard(step=1, conversion_type=conversion_type)
        )
        user_states[chat_id]['last_message_id'] = msg.message_id

# обработка текста
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    chat_id = message.chat.id

    if chat_id in user_states and user_states[chat_id]['step'] == 3:
        process_amount(message)
    else:
        bot.send_message(chat_id,
                         "*Выберите действие с помощью кнопок меню ниже:*",
                         parse_mode='Markdown',
                         reply_markup=create_main_menu())

# обработка введенной суммы
def process_amount(message):
    chat_id = message.chat.id

    if chat_id not in user_states or user_states[chat_id]['step'] != 3:
        bot.send_message(chat_id, "❌ Сессия устарела. Начните заново.", reply_markup=create_main_menu())
        return

    try:
        amount = float(message.text.replace(',', '.'))

        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        conversion_type = user_states[chat_id]['conversion_type']
        from_currency = user_states[chat_id]['from_currency']
        to_currency = user_states[chat_id]['to_currency']
        last_message_id = user_states[chat_id].get('last_message_id')

        rate = get_exchange_rate(from_currency, to_currency)

        if rate is None:
            raise Exception("Не удалось получить курс валют")

        if conversion_type == 'normal':
            converted_amount = amount * rate
            result_text = create_normal_conversion_text(amount, from_currency, converted_amount, to_currency, rate)
        else:
            required_amount = amount / rate
            result_text = create_reverse_conversion_text(amount, to_currency, required_amount, from_currency, rate)

        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass

        if last_message_id:
            try:
                completion_text = "*Конвертация завершена✅  Результат ниже:*" if conversion_type == 'normal' else "✅ *Расчет завершен. Результат ниже:*"
                bot.edit_message_text(
                    completion_text,
                    chat_id, last_message_id,
                    parse_mode='Markdown'
                )
            except:
                pass

        bot.send_message(chat_id, result_text,
                         parse_mode='Markdown',
                         reply_markup=create_main_menu())

        del user_states[chat_id]

    except ValueError:
        conversion_type = user_states[chat_id]['conversion_type']
        error_msg = "*Введите корректную сумму (например: 100 или 150.50):*" if conversion_type == 'normal' else "❌ *Введите корректную желаемую сумму (например: 5000 или 7500.50):*"
        msg = bot.send_message(chat_id, error_msg, parse_mode='Markdown')

        user_states[chat_id]['step'] = 3
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Ошибка:* {str(e)}\n\nПопробуйте снова.",
                         parse_mode='Markdown',
                         reply_markup=create_main_menu())
        if chat_id in user_states:
            del user_states[chat_id]

# создание текста сообщения для обычной конвертации
def create_normal_conversion_text(amount, from_currency, converted_amount, to_currency, rate):
    formatted_amount = format_number(amount)
    formatted_converted = format_number(converted_amount)
    formatted_rate = format_number(rate)

    return f"""
💱 *Результат конвертации:*

*{formatted_amount} {from_currency}* = *{formatted_converted} {to_currency}*

📊 *Курс:* 1 {from_currency} = {formatted_rate} {to_currency}
📅 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}

{POPULAR_CURRENCIES.get(from_currency, {}).get('name', from_currency)} → {POPULAR_CURRENCIES.get(to_currency, {}).get('name', to_currency)}
    """

# создание текста сообщения для обратной конвертации
def create_reverse_conversion_text(desired_amount, to_currency, required_amount, from_currency, rate):
    formatted_desired = format_number(desired_amount)
    formatted_required = format_number(required_amount)
    formatted_rate = format_number(rate)

    return f"""
🔄 *Результат обратной конвертации:*

Чтобы получить *{formatted_desired} {to_currency}*
нужно *{formatted_required} {from_currency}*

📊 *Курс:* 1 {from_currency} = {formatted_rate} {to_currency}
📅 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}

{POPULAR_CURRENCIES.get(from_currency, {}).get('name', from_currency)} → {POPULAR_CURRENCIES.get(to_currency, {}).get('name', to_currency)}
    """


if __name__ == "__main__":
    print("Точно в Курсе запущен и готов к работе!")
    print("Бот ожидает сообщений")
    bot.infinity_polling()