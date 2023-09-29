import json
import re
import uuid
import pyperclip
import requests
import telebot
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from telebot import types


bot = telebot.TeleBot(token='6251838992:AAGIwjW1T3JzqslHxQGVCaALMboN8SBBO_E', parse_mode='html')

cur_page = 1

info = {}


def get_news(page=1):
    url = 'https://mmf.bsu.by/ru/category/news/'
    url = url + (f'page/{page}' if page > 1 else '')
    req = requests.get(url)
    data = req.text
    soup = BeautifulSoup(data, "html.parser")
    res = soup.findAll('div', {'class': 'archive-post'})
    all_info = []
    for i in res:
        info = {}
        el = i.findAll('a')
        info['day'] = el[0].find('div', {'class': 'archive-post-date-day'}).text.strip()
        info['month'] = el[0].find('div', {'class': 'archive-post-date-month'}).text.strip()
        info['year'] = el[0].find('div', {'class': 'archive-post-date-year'}).text.strip()
        info['title'] = el[1].find('h3').text.strip()
        info['href'] = el[1].get('href').strip()
        all_info.append(info)
    return all_info


def create_note(id, data):
    all_user_notes = get_notes(id)
    data['id'] = str(uuid.uuid4())
    with open("notes.json", "r", encoding='utf-8') as jsonFile:
        notes_data = json.load(jsonFile)
        if all_user_notes is not None:
            all_user_notes.append(data)
            for i in range(len(notes_data)):
                if notes_data[i]["id"] == id:
                    notes_data[i]["user_notes"] = all_user_notes
                    break
        else:
            notes_data.append({"id": id, "user_notes": [data], "time_tables": []})
    with open("notes.json", "w", encoding='utf-8') as jsonFile:
        json.dump(notes_data, jsonFile, indent=4, ensure_ascii=False)


def get_notes(id, note_id=None):
    try:
        with open('notes.json', encoding='utf-8') as f:
            data = json.loads(f.read())
            for el in data:
                if el['id'] == id:
                    if note_id is None:
                        return el['user_notes']
                    else:
                        for note in el['user_notes']:
                            if note['id'] == note_id:
                                return note
    except:
        print('error get notes')


def delete_note(id, note_id):
    with open("notes.json", "r", encoding='utf-8') as jsonFile:
        notes_data = json.load(jsonFile)
        for i in range(len(notes_data)):
            if notes_data[i]["id"] == id:
                for note_number in range(len(notes_data[i]['user_notes'])):
                    if notes_data[i]['user_notes'][note_number]['id'] == note_id:
                        notes_data[i]['user_notes'].pop(note_number)
                        break
    with open("notes.json", "w", encoding='utf-8') as jsonFile:
        json.dump(notes_data, jsonFile, indent=4, ensure_ascii=False)


def edit_note(id, edit_note):
    with open("notes.json", "r", encoding='utf-8') as jsonFile:
        notes_data = json.load(jsonFile)
        for i in range(len(notes_data)):
            if notes_data[i]["id"] == id:
                for note_number in range(len(notes_data[i]['user_notes'])):
                    if notes_data[i]['user_notes'][note_number]['id'] == edit_note['id']:
                        notes_data[i]['user_notes'][note_number] = edit_note
                        break
    with open("notes.json", "w", encoding='utf-8') as jsonFile:
        json.dump(notes_data, jsonFile, indent=4, ensure_ascii=False)


def news_to_msg(news):
    msg = ''
    for n in news:
        msg = msg + f"""{n['day']} {n['month']} {n['year']}\n"""
        msg = msg + f"<a href='{n['href']}'>{n['title']}</a>\n\n"
    return msg


@bot.message_handler(commands=['start'])
def first_start(message):
    kb = types.ReplyKeyboardMarkup()
    kb.add(types.KeyboardButton('Новости'))
    kb.add(types.KeyboardButton('Мои заметки'))
    kb.add(types.KeyboardButton('Расписание'))
    bot.send_message(message.chat.id, 'Hi', reply_markup=kb)


@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text == 'Новости')
def start(message):
    global cur_page
    news = get_news(cur_page)
    if cur_page == 1:
        btns = [types.InlineKeyboardButton('➡️', callback_data='f')]
    else:
        btns = [types.InlineKeyboardButton('⬅️', callback_data='b'),
                types.InlineKeyboardButton('➡️', callback_data='f')]
    kb = types.InlineKeyboardMarkup([
        btns
    ])

    bot.send_message(message.chat.id, news_to_msg(news), reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data in ['f', 'b'])
def paginate(call):
    global cur_page
    cur_page += (1 if call.data == 'f' else -1)
    new_news = get_news(cur_page)
    if cur_page == 1:
        btns = [types.InlineKeyboardButton('➡️', callback_data='f')]
    else:
        btns = [types.InlineKeyboardButton('⬅️', callback_data='b'),
                types.InlineKeyboardButton('➡️', callback_data='f')]
    kb = types.InlineKeyboardMarkup([
        btns
    ])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=news_to_msg(new_news), reply_markup=kb)


@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text == 'Мои заметки')
def notes(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    global info
    info = {}
    notes = get_notes(message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton('Создать заметку', callback_data='create'))
    if notes is not None:
        for note in notes:
            kb.row(types.InlineKeyboardButton(text=note['title'], callback_data='show_note' + note['id']))

    info['notes_ms'] = bot.send_message(message.chat.id, text='Заметки', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'create')
def create_note_callback(call):
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton(text='Назад', callback_data='go_home1'))
    inner_message = bot.send_message(call.message.chat.id, 'Введи название и описание', reply_markup=kb)
    bot.register_next_step_handler(inner_message, handle_create_note, call)


def handle_create_note(message, call):
    data = message.text
    note = {
        'title': data.split('\n')[0],
        'text': data.split('\n')[1]
    }
    create_note(message.chat.id, note)
    bot.answer_callback_query(call.id, 'Заметка создана')

    notes(message)


def send_mes(message):
    bot.send_message(message.chat.id, '123')


@bot.callback_query_handler(func=lambda call: call.data[:9] == 'show_note')
def show_note_callback(call):
    global info
    note_id = call.data[9:]
    note = get_notes(call.message.chat.id, note_id)
    note_msg = f"""{note['title']}\n{note['text']}"""
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton(text='Edit', callback_data='edit' + note_id))
    kb.row(types.InlineKeyboardButton(text='Delete', callback_data='delete' + note_id))
    kb.row(types.InlineKeyboardButton(text='Назад', callback_data='go_home1'))
    bot.edit_message_text(text=note_msg, chat_id=call.message.chat.id, message_id=info['notes_ms'].id, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data[:7] == 'go_home')
def edit_note_callback(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    if call.data[-1] == '1':
        notes(call.message)
    elif call.data[-1] == '2':
        timetable_handle(call.message)


@bot.callback_query_handler(func=lambda call: call.data[:4] == 'edit')
def edit_note_callback(call):
    pyperclip.copy(call.message.text)
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton(text='Назад', callback_data='go_home'))
    inner_message = bot.send_message(call.message.chat.id,
                                     'Отправь сообщение с измененной заметкой', reply_markup=kb)
    bot.register_next_step_handler(inner_message, edit_note_handle, call, call.data[4:])


def edit_note_handle(message, call, note_id):
    data = message.text
    note = {
        'id': note_id,
        'title': data.split('\n')[0],
        'text': data.split('\n')[1]
    }
    edit_note(message.chat.id, note)
    bot.answer_callback_query(call.id, 'Заметка изменена')

    notes(message)


@bot.callback_query_handler(func=lambda call: call.data[:6] == 'delete')
def delete_note_callback(call):
    delete_note(call.message.chat.id, call.data[6:])
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    notes(call.message)


def get_time_table_data_by_day(data, day):
    days = data.findAll('td', {'class': 'weekday'})
    data = list(filter(lambda x: x.text.strip() == day, days))
    day_data = [i.parent for i in data]
    x = PrettyTable()
    x.align = 'l'
    x.header = False
    for i in day_data:
        res = i.text.split('\n')[2:]
        tmp = re.split(r'<td class="subject-teachers">|<br/>|</td>',
                       str(i.find('td', {'class': 'subject-teachers'})))[1:3]
        res[2] = '\n'.join(tmp)
        x.add_row(res[:-1], divider=True)
    return f"<pre>{x}</pre>"


def get_time_table_data(chatid=None, course=None, group=None, title=None, day=None):
    if chatid is None:
        if group == 'ВФ':
            group = 'vf/'
        else:
            group = str(group) + '-gruppa/'
        url = 'https://mmf.bsu.by/ru/raspisanie-zanyatij/dnevnoe-otdelenie/' + str(course) + '-kurs/' + group
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        res = soup.find('table')
        ans = get_time_table_data_by_day(res, day)
        return {'title': title, 'data': ans}
    else:
        with open("notes.json", "r", encoding='utf-8') as jsonFile:
            all_data = json.load(jsonFile)
            for data in all_data:
                if data['id'] == chatid:
                    return data['time_tables']


@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text == 'Расписание')
def timetable_handle(message):
    global info
    info = {}
    kb = types.InlineKeyboardMarkup()
    info['time_tables'] = time_table = get_time_table_data(message.chat.id)
    kb.row(types.InlineKeyboardButton('Найти расписание', callback_data='add_time_table'))
    if time_table is not None:
        for i in range(len(time_table)):
            kb.row(types.InlineKeyboardButton(time_table[i]['title'], callback_data=f'showTimeTable_{i}'))

    info['time_table_ms'] = bot.send_message(message.chat.id, text='Выбери', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'add_time_table')
def add_time_table(call):
    kb = types.InlineKeyboardMarkup()
    courses = info['courses'] = [str(i) for i in range(1, 5)]
    info['title'] = ''
    for i in range(len(courses)):
        kb.row(types.InlineKeyboardButton(courses[i] + ' курс', callback_data='course_' + str(i)))
    kb.row(types.InlineKeyboardButton('Назад', callback_data='go_home2'))

    bot.send_message(call.message.chat.id, text='Выбери курс', reply_markup=kb)


def get_groups(course):
    res = [str(i) for i in range(1, 10)]
    if course in ['2', '3', '4']:
        res.append('10')
        if course == '4':
            res.append('11')
    res.append("ВФ")
    return res


@bot.callback_query_handler(func=lambda call: call.data[:6] == 'course')
def course_handle(call):
    kb = types.InlineKeyboardMarkup()
    course = info['courses'][int(call.data.split('_')[1])]
    info['course'] = course
    info['title'] = info['title'] + course + ' курс, '
    groups = get_groups(course)
    info['groups'] = groups
    for i in range(len(groups)):
        tmp = groups[i]
        if tmp != 'ВФ':
            tmp = tmp + ' группа'
        kb.row(types.InlineKeyboardButton(tmp, callback_data='group_' + str(i)))
    kb.row(types.InlineKeyboardButton('Назад', callback_data='go_home2'))

    bot.send_message(call.message.chat.id, text='Выбери группу', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data[:5] == 'group')
def group_handle(call):
    group = info['groups'][int(call.data.split('_')[1])]
    info['group'] = group
    info['title'] = info['title'] + group
    if group != 'ВФ':
        info['title'] = info['title'] + ' группа'
    get_day(call.message)


def get_day(message):
    kb = types.InlineKeyboardMarkup()
    for i in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']:
        kb.row(types.InlineKeyboardButton(text=i, callback_data='day' + i))
    kb.row(types.InlineKeyboardButton(text="Назад", callback_data='go_home2'))
    bot.send_message(message.chat.id, reply_markup=kb, text='Выбери день')


def has_time_tableQ(user_id, course, group):
    with open("notes.json", "r", encoding='utf-8') as jsonFile:
        all_data = json.load(jsonFile)
        for data in all_data:
            if data['id'] == user_id:
                for table in data['time_tables']:
                    if table['course'] == course and table['group'] == group:
                        return True
    return False


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'day')
def day_handle(call):
    info['day'] = call.data[3:]
    get_full_time_table(call.message)


def get_full_time_table(message):
    kb = types.InlineKeyboardMarkup()
    time_table = get_time_table_data(course=info['course'], group=str(info['group']), title=info['title'],
                                     day=info['day'])
    if has_time_tableQ(user_id=message.chat.id, course=info['course'], group=info['group']):
        kb.row(types.InlineKeyboardButton('Удалить из избранного', callback_data='del_fav_time_table'))
    else:
        kb.row(types.InlineKeyboardButton('Добавить в избранное', callback_data='add_fav_time_table'))
    kb.row(types.InlineKeyboardButton('Назад', callback_data='go_home2'))

    bot.send_message(message.chat.id, text=time_table['data'], reply_markup=kb, parse_mode='html')


def add_to_fav(user_id, course, group, title):
    data = {'title': title, 'course': course, 'group': group}
    with open("notes.json", "r", encoding='utf-8') as jsonFile:
        all_data = json.load(jsonFile)
        no_user = True
        for i in range(len(all_data)):
            if all_data[i]['id'] == user_id:
                no_user = False
                tmp = all_data[i]['time_tables']
                tmp.append(data)
                all_data[i]['time_tables'] = tmp
        if no_user:
            all_data.append({"id": user_id, "user_notes": [], "time_tables": [data]})

    with open("notes.json", "w", encoding='utf-8') as jsonFile:
        json.dump(all_data, jsonFile, indent=4, ensure_ascii=False)


@bot.callback_query_handler(func=lambda call: call.data == 'add_fav_time_table')
def add_fav_handle(call):
    add_to_fav(call.message.chat.id, course=info['course'], group=info['group'], title=info['title'])
    bot.answer_callback_query(call.id, 'Добавлено в избранное')
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    timetable_handle(call.message)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'showTimeTable')
def show_time_table_handle(call):
    user_time_tables = get_time_table_data(chatid=call.message.chat.id)
    time_table_info = user_time_tables[int(call.data.split('_')[1])]
    info['course'] = time_table_info['course']
    info['group'] = time_table_info['group']
    info['title'] = time_table_info['title']
    get_day(call.message)


def delete_fav_time_table(chatid, course, group):
    with open("notes.json", "r", encoding='utf-8') as jsonFile:
        all_data = json.load(jsonFile)
        for i in range(len(all_data)):
            if all_data[i]['id'] == chatid:
                for j in range(len(all_data[i]['time_tables'])):
                    tmp = all_data[i]['time_tables'][j]
                    if tmp['course'] == course and tmp['group'] == group:
                        all_data[i]['time_tables'].pop(j)
    with open("notes.json", "w", encoding='utf-8') as jsonFile:
        json.dump(all_data, jsonFile, indent=4, ensure_ascii=False)


@bot.callback_query_handler(func=lambda call: call.data == 'del_fav_time_table')
def del_fav_handle(call):
    delete_fav_time_table(chatid=call.message.chat.id, course=info['course'], group=info['group'])
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    timetable_handle(call.message)


if __name__ == '__main__':
    bot.infinity_polling()
    # print(get_time_table_data(course=3, group=5, day='Понедельник'))
