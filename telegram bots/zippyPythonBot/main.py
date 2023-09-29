from prettytable import PrettyTable
import requests
from bs4 import BeautifulSoup
from datetime import datetime

base_url = 'https://zippybus.com/'


def has_class(tag, class_name):
    return class_name in tag['class'] if tag.has_attr('class') else False


def is_valid_city(city_name):
    req = requests.get(base_url)
    soup = BeautifulSoup(req.text, "html.parser")
    for i in soup.findAll('h3'):
        if i.findChild('a').get_text().strip() == city_name:
            return True
    return False


def get_tr_types(city_name):
    convert_types = {
        "автобусов": "Автобус",
        "троллейбусов": "Троллейбус",
        "трамваев": "Трамвай"
    }
    req = requests.get(base_url)
    soup = BeautifulSoup(req.text, "html.parser")

    tmp = soup.find(lambda tag: tag.text == city_name).parent.find_next_siblings()
    data = [(el.text.strip(), el.get('href')) for el in tmp]
    ans = []
    for i in data:
        tmp = i[0].split(' ')[1]
        if tmp in convert_types.keys():
            ans.append([convert_types[tmp], i[1]])
    return ans


def is_valid_number(href, number):
    req = requests.get(href)
    soup = BeautifulSoup(req.text, "html.parser")
    routes = soup.find('ul', {'id': 'routes'})
    cur_route = routes.find(lambda tag: tag.text == number)
    if cur_route is not None:
        return {"status": True, "message": cur_route.get('href')}
    return {"status": False, "message": "Нет транспорта с номером " + number}


def get_directions(href):
    req = requests.get(href)
    soup = BeautifulSoup(req.text, "html.parser")
    return [el.text.strip() for el in soup.findAll('h4')]


def get_stops(href, direction):
    req = requests.get(href)
    soup = BeautifulSoup(req.text, "html.parser")
    stops = soup.find(lambda tag: tag.name == 'h4' and direction in tag.text).parent
    stops = [el.text.strip() for el in stops.findAll('a')]
    return stops


def get_stop_href(href, direction, stop_name):
    req = requests.get(href)
    soup = BeautifulSoup(req.text, "html.parser")
    stops = soup.find(lambda tag: tag.name == 'h4' and direction in tag.text).parent
    return stops.find(lambda tag: tag.name == 'a' and stop_name in tag.text).get('href')


def get_next_ride(href):
    req = requests.get(href)
    soup = BeautifulSoup(req.text, "html.parser")
    table = [[el.text, el.get('href')] for el in soup.find('table', {'class': 'scheduleTable'}).findAll('a')]
    cur_time = datetime.now().hour * 60 + datetime.now().minute

    message = 'Сегодня рейсов больше нет'
    href = None

    for i in table:
        if len(i[0]) > 5:
            i[0] = i[0][:-1]
        if cur_time < convert_to_min(i[0]):
            href = i[1]
            message = f'{i[0]}. Ближайший рейс через {convert_to_time(convert_to_min(i[0]) - cur_time)}'
            break

    return [message, href]


def convert_to_min(string_time):
    return 60 * int(str(string_time[:2])) + int(str(string_time[3:]))


def convert_to_time(mins):
    ans = ''
    if mins // 60 != 0:
        ans = f'{mins // 60} ч. '
    return f'{ans}{mins % 60} мин'


def get_all_rides(href):
    x = PrettyTable(header=False, align='l')
    req = requests.get(href)
    soup = BeautifulSoup(req.text, "html.parser")
    content = soup.find('table', {'class': 'scheduleTable'}).findAll('tr')
    for i in content:
        x.add_row(
            [i.find('td').text.strip(),
             ','.join([el.text.strip()[3:5] for el in i.findAll('a')])])

    return f'<pre>{x}</pre>'


def get_all_route_times(href):
    req = requests.get(href)
    soup = BeautifulSoup(req.text, "html.parser")
    content = soup.find('table', {'class': 'table-striped'}).find('tbody').findAll('tr')
    ans = []
    for i in content:
        ans.append([el.text.strip() for el in i.findAll('td')])
    return ans


def get_time_from_to(href, from_stop, to_stop):
    stop_times = get_all_route_times(href)
    start = stop_times[from_stop]
    end = stop_times[to_stop]
    time_diff = convert_to_time(convert_to_min(end[1]) - convert_to_min(start[1]))
    return f'Ехать {time_diff}'


if __name__ == '__main__':
    print(get_time_from_to('https://zippybus.com/minsk/route/bus/1/kirova-ds-vesnyanka/67/stop-9625/23/1', 'Крупцы',
                           'Нарочанская'))
