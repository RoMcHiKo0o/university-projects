import telebot
from telebot import types
import main

token = '5893721862:AAFLY9DvhPOjoJSOKGWerHeKijkS3s4731E'
bot = telebot.TeleBot(token, parse_mode='html')
user = lambda \
        message: f"{message.from_user.first_name}" \
                 f"{' ' + message.from_user.last_name if message.from_user.last_name is not None else ''}"

info = {}


@bot.message_handler(commands=["start"])
def first_start(message):
    print(user(message) + ": start")
    help_message = f"Привет, {user(message)}.\n" \
                   + 'Я бот для получения расписания общественного транспорта по Беларуси.\n' \
                     'Просто следуй инструкциям, чтобы узнать расписание.\n' \
                     'Если хочешь вернуться назад, нажми "На главную"\n' \
                     'Если вводишь город, пиши с большой буквы (Минск, Гродно...)\n' \
                     'При вводе номера транспорта пиши число\n' \
                     'Для вызова этого сообщения пиши команду /start\n' \
                     'Приятного использования'
    bot.send_message(message.chat.id, help_message)
    start(message)


@bot.message_handler(func=lambda message: message.text == 'На главную')
def start(message):
    global info
    print(user(message) + ": start")
    for ms in ['dir_ms', 'tr_type_ms', 'stops_ms']:
        if ms in info.keys():
            bot.delete_message(chat_id=message.chat.id, message_id=info[ms].message_id)
    if 'inline_buttons' in info.keys():
        if len(info['inline_buttons']) > 0:
            bot.edit_message_reply_markup(info['time_message'].chat.id, info['time_message'].id, reply_markup=None)
    search(message)


def search(message):
    global info
    info = {}
    keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboards.add("На главную")
    print(user(message) + ": before city")
    inner_message = bot.send_message(message.chat.id, "Введи город", reply_markup=keyboards)
    bot.register_next_step_handler(inner_message, city_home_fork)


def city_home_fork(message):
    if message.content_type == 'text':
        if message.text == "На главную":
            print(user(message) + ": go home")
            start(message)
        else:
            print(user(message) + ": city")
            flag = main.is_valid_city(message.text.strip())
            handle_city(message, flag)
    else:
        bot.send_message(message.chat.id, 'Некорректный ввод\nВведи город')
        bot.register_next_step_handler(message, city_home_fork)


def handle_city(message, flag=None):
    city_name = message.text.strip()
    if flag is True or flag is None:
        if flag is not None:
            info['city'] = city_name
        print(user(message) + ": before type")
        info['all_types'] = main.get_tr_types(info['city'])
        kb = types.InlineKeyboardMarkup()
        for i in range(len(info['all_types'])):
            kb.add(types.InlineKeyboardButton(text=info['all_types'][i][0], callback_data=f'1{i}'))
        inner_message = bot.send_message(message.chat.id, "Введи тип траспорта", reply_markup=kb)
        info['tr_type_ms'] = inner_message
    else:
        print(user(message) + ": error")
        inner_message = bot.send_message(message.chat.id, f"Города {city_name} нет. Попробуй ещё раз")
        search(inner_message)


@bot.callback_query_handler(func=lambda call: call.data[0] == '1')
def tr_type_handle(call):
    tr_name, href = info['all_types'][int(call.data[1:])]
    info['type_name'] = tr_name
    info['href1'] = href
    bot.delete_message(chat_id=call.message.chat.id, message_id=info['tr_type_ms'].message_id)
    info.pop('tr_type_ms')
    handle_type2(call.message)


def handle_type2(message):
    print(user(message) + ": before number")
    convert_types = {
        "Автобус": "автобуса",
        "Троллейбус": "троллейбуса",
        "Трамвай": "трамвая"
    }
    inner_message = bot.send_message(message.chat.id, f"Введи номер {convert_types[info['type_name']]}")
    bot.register_next_step_handler(inner_message, number_home_fork)


def number_home_fork(message):
    if message.content_type == 'text':
        if message.text == "На главную":
            print(user(message) + ": go home")
            start(message)
        else:
            print(user(message) + ": number")

            if message.text.strip() not in ['Инфо', 'i', '!']:
                ans = main.is_valid_number(info['href1'], message.text)
                if flag := ans['status']:
                    info['href2'] = ans['message']
            else:
                flag = False
            handle_number(message, flag)
    else:
        bot.send_message(message.chat.id, 'Некорректный ввод\nВведи номер')
        bot.register_next_step_handler(message, number_home_fork)


def handle_number(message, flag=None):
    number = message.text.strip()
    if flag is True or flag is None:
        if flag is not None:
            info['number'] = number
            info['directions'] = main.get_directions(info['href2'])
        directions = info['directions']
        print(user(message) + ": before direction")

        kb = types.InlineKeyboardMarkup()
        for i in range(len(directions)):
            kb.row(types.InlineKeyboardButton(text=directions[i], callback_data=f'2{i}'))
        inner_message = bot.send_message(message.chat.id, "Выбери направление", reply_markup=kb)
        info['dir_ms'] = inner_message
    else:
        print(user(message) + ": error")
        convert_types = {
            "Автобус": "Автобуса",
            "Троллейбус": "Троллейбуса",
            "Трамвай": "Трамвая"
        }
        bot.send_message(message.chat.id,
                         f"{convert_types[info['type_name']]} с номером {number} нет. Попробуй ещё раз")
        handle_type2(message)


@bot.callback_query_handler(func=lambda call: call.data[0] == '2')
def tr_dir_handle(call):
    dir_name = info['directions'][int(call.data[1:])]
    info['direction'] = dir_name
    bot.delete_message(chat_id=call.message.chat.id, message_id=info['dir_ms'].message_id)
    info.pop('dir_ms')
    handle_direction2(call.message)


def handle_direction2(message):
    stops = main.get_stops(info['href2'], info['direction'])
    info['stops'] = stops
    print(user(message) + ": before stop")
    kb = types.InlineKeyboardMarkup()
    for i in range(len(stops)):
        kb.row(types.InlineKeyboardButton(text=stops[i], callback_data=f'3{i}'))
    inner_message = bot.send_message(message.chat.id, text="Выбери остановку", reply_markup=kb)
    info['stops_ms'] = inner_message


@bot.callback_query_handler(func=lambda call: call.data[0] == '3')
def stop_handle(call):
    stop = info['stops'][int(call.data[1:])]
    info['stop'] = stop
    info['stop_number'] = int(call.data[1:])
    bot.delete_message(chat_id=call.message.chat.id, message_id=info['stops_ms'].message_id)
    info.pop('stops_ms')
    handle_stop2(call.message)


def handle_stop2(message):
    print(user(message) + ": before time")
    info['href3'] = main.get_stop_href(info['href2'], info['direction'], info['stop'])
    next_ride, href = main.get_next_ride(info['href3'])
    info['href4'] = href
    reply_markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("Показать всё расписание", callback_data="4show_all_time_table")
    btn2 = types.InlineKeyboardButton("Выбрать конечную остановку", callback_data="4ending_station")
    lst = [btn1]
    reply_markup.add(btn1)
    if href is not None and info['stop_number'] + 1 < len(info['stops']):
        reply_markup.add(btn2)
        lst.append(btn2)
    info['inline_buttons'] = lst
    inner_message = bot.send_message(message.chat.id, next_ride, reply_markup=reply_markup)
    info['time_message'] = inner_message


@bot.callback_query_handler(func=lambda call: call.data[0] == '4')
def check_call(call):
    if call.data == "4show_all_time_table":
        print(user(call.message) + ': show_all_time_table')
        time_table = main.get_all_rides(info['href3'])
        tmp = info['inline_buttons']
        info['inline_buttons'] = list(filter(lambda el: el.callback_data != '4show_all_time_table', tmp))
        new_kb = types.InlineKeyboardMarkup(
            [
                info['inline_buttons']
            ]
        )
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              text=call.message.text + '\nПолное расписание:\n' + time_table,
                              reply_markup=new_kb)

    elif call.data == '4ending_station':
        print(user(call.message) + ': ending_station')
        tmp = info['inline_buttons']
        info['inline_buttons'] = list(filter(lambda el: el.callback_data != '4ending_station', tmp))
        new_kb = types.InlineKeyboardMarkup(
            [
                info['inline_buttons']
            ]
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id, reply_markup=new_kb
        )
        get_last_stop2(call.message)


def get_last_stop2(message):
    kb = types.InlineKeyboardMarkup()
    tmp = list(zip(*main.get_all_route_times(info['href4'])))[0]
    info['last_stops'] = tmp[info['stop_number'] + 1:]
    for i in range(len(info['last_stops'])):
        kb.row(types.InlineKeyboardButton(text=info['last_stops'][i], callback_data=f'5{i}'))
    inner_message = bot.send_message(message.chat.id, 'Выбери конечную остановку', reply_markup=kb)
    info['stops_ms'] = inner_message


@bot.callback_query_handler(func=lambda call: call.data[0] == '5')
def last_stop_handle(call):
    info['final_stop'] = info['last_stops'][int(call.data[1:])]
    bot.delete_message(call.message.chat.id, info['stops_ms'].message_id)
    info.pop('stops_ms')
    handle_last_stop2(call.message, int(call.data[1:]))


def handle_last_stop2(message, last_number):
    print(user(message) + ": before last stop")
    from_to_time = main.get_time_from_to(
        href=info['href4'],
        from_stop=int(info['stop_number']),
        to_stop=int(info['stop_number']) + last_number + 1)
    bot.send_message(message.chat.id, from_to_time)


if __name__ == "__main__":
    bot.infinity_polling()
