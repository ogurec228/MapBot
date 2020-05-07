import telebot
import requests

bot = telebot.TeleBot('*****')

type_keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
type_keyboard.row('Страна', 'Город', 'Здание', 'Улица')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, чтобы узнать о всех возможностях бота, пиши /help')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, '/GetScreen + название объекта(например, /GetScreen Москва) - '
                                      'дает изображение заданного объекта с пробками и без них \n'  
                                      '/GetCoords + объект(например, /GetCoords Москва)'
                                      ' - получить координаты данного объекта \n'
                                      '/GetAdress долгота, широта(например, /GetAdress 150.808586, 59.565151) - '
                                      'получить адрес объекта из координат \n'
                                      '/marks + объекты(например, /marks Казань улица космонавтов, Воронеж)'                                    
                                      ' - получить изображение с метками на заданных местах \n'
                                      '/GetInfo + объект(например, /GetInfo Москва) - дает немного'
                                      ' информации о заданном объекте')


object_message = ''


@bot.message_handler(commands=['GetScreen'])
def screen_type(message):
    global object_message
    bot.send_message(message.chat.id, 'Выберите тип объекта(от него будет зависеть маштаб)', reply_markup=type_keyboard)
    object_message = message.text

    @bot.message_handler(content_types=['text'])
    def image(message):
        global object_message

        object = object_message[11:]
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-" \
                           "98533de7710b&geocode=" + str(object) + "&format=json"

        response = requests.get(geocoder_request)

        if response:
            json_response = response.json()
            if json_response["response"]["GeoObjectCollection"]['metaDataProperty']['GeocoderResponseMetaData']['found'] \
                    != '0':
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_coodrinates = toponym["Point"]["pos"]

                if message.text == 'Страна':
                    coordinates = toponym_coodrinates.replace(' ', ',')
                    map_request = "http://static-maps.yandex.ru/1.x/?ll=" + str(coordinates) + "&spn=20,20&l=map"
                    map_response = requests.get(map_request)

                    trf_map_request = "http://static-maps.yandex.ru/1.x/?ll=" \
                                      + str(coordinates) + "&spn=10,10&l=sat,trf,skl"
                    trf_map_response = requests.get(trf_map_request)

                elif message.text == 'Город':
                    coordinates = toponym_coodrinates.replace(' ', ',')
                    map_request = "http://static-maps.yandex.ru/1.x/?ll=" + str(coordinates) + "&spn=0.15,0.15&l=map"
                    map_response = requests.get(map_request)

                    trf_map_request = "http://static-maps.yandex.ru/1.x/?ll=" + str(coordinates) + \
                                      "&spn=0.15,0.15&l=sat,trf,skl"
                    trf_map_response = requests.get(trf_map_request)

                elif message.text == 'Здание':
                    coordinates = toponym_coodrinates.replace(' ', ',')
                    map_request = "http://static-maps.yandex.ru/1.x/?ll=" + str(coordinates) + "&spn=0.002,0.002&l=map"
                    map_response = requests.get(map_request)

                    trf_map_request = "http://static-maps.yandex.ru/1.x/?ll=" + str(coordinates) + \
                                      "&spn=0.002,0.002&l=sat,trf,skl"
                    trf_map_response = requests.get(trf_map_request)
                elif message.text == 'Улица':
                    coordinates = toponym_coodrinates.replace(' ', ',')
                    map_request = "http://static-maps.yandex.ru/1.x/?ll=" + str(coordinates) + "&spn=0.015,0.015&l=map"
                    map_response = requests.get(map_request)

                    trf_map_request = "http://static-maps.yandex.ru/1.x/?ll=" + str(coordinates) + \
                                      "&spn=0.002,0.002&l=sat,trf,skl"
                    trf_map_response = requests.get(trf_map_request)

                    with open('spn.txt', "w") as file:
                        file.write('0.015, 0.015')

                    with open('ll.txt', "w") as file:
                        file.write(str(coordinates))

                map_file = "map.png"
                with open(map_file, "wb") as file:
                    file.write(map_response.content)

                img = open('map.png', 'rb')
                bot.send_photo(message.chat.id, img)

                trf_map_file = "trf_map.png"
                with open(trf_map_file, "wb") as file:
                    file.write(trf_map_response.content)

                img = open('trf_map.png', 'rb')
                bot.send_photo(message.chat.id, img)

            else:
                bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')

        else:
            bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')


def get_mark_coords(object):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-" \
                       "98533de7710b&geocode=" + str(object) + "&format=json"

    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]['metaDataProperty']['GeocoderResponseMetaData']['found'] \
                != '0':
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coordinates = toponym["Point"]["pos"]
            return toponym_coordinates.replace(' ', ',')

    return None


@bot.message_handler(commands=['marks'])
def marks(message):
    objects = '~'.join([get_mark_coords(i) + ',org' for i in message.text[7::].split(',')
                        if get_mark_coords(i) is not None])
    map_request = 'https://static-maps.yandex.ru/1.x/?l=map&pt=' + objects
    map_response = requests.get(map_request)

    sat_map_request = 'https://static-maps.yandex.ru/1.x/?l=sat,skl&pt=' + objects
    sat_map_response = requests.get(sat_map_request)

    if map_response:
        map_file = "mark_map.png"
        with open(map_file, "wb") as file:
            file.write(map_response.content)

        img = open('mark_map.png', 'rb')
        bot.send_photo(message.chat.id, img)

        sat_map_file = "sat_map.png"
        with open(sat_map_file, "wb") as file:
            file.write(sat_map_response.content)

        img = open('sat_map.png', 'rb')
        bot.send_photo(message.chat.id, img)

    else:
        bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')


@bot.message_handler(commands=['GetCoords'])
def get_coords(message):
    object = message.text[11:]
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-" \
                       "98533de7710b&geocode=" + str(object) + "&format=json"

    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]['metaDataProperty']['GeocoderResponseMetaData']['found'] \
                != '0':
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coordinates = toponym["Point"]["pos"]
            bot.send_message(message.chat.id, toponym_coordinates.replace(' ', ', '))

        else:
            bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')

    else:
        bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')


@bot.message_handler(commands=['GetAdress'])
def get_adress(message):
    coords = message.text[11:]
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-" \
                       "98533de7710b&geocode=" + str(coords) + "&format=json"

    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]['metaDataProperty']['GeocoderResponseMetaData']['found'] \
                != '0':
            adress_0 = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            adress = adress_0['metaDataProperty']['GeocoderMetaData']['text']
            bot.send_message(message.chat.id, adress)

        else:
            bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')

    else:
        bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')


@bot.message_handler(commands=['GetInfo'])
def get_info(message):
    object = message.text[9:]
    info = []

    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-" \
                       "98533de7710b&geocode=" + str(object) + "&format=json"

    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]['metaDataProperty']['GeocoderResponseMetaData']['found'] \
                != '0':
            json_info = json_response["response"]["GeoObjectCollection"]['featureMember'][0]['GeoObject']

            if len(json_info['metaDataProperty']['GeocoderMetaData']['Address']['Components']) > 1:
                province = json_info['metaDataProperty']['GeocoderMetaData']['Address']['Components'][1]['name']
                info.append(province)

            country = json_info['metaDataProperty']['GeocoderMetaData']['Address']['Components'][0]['name']
            info.append(country)

            country_code = json_info['metaDataProperty']['GeocoderMetaData']['Address']['country_code']
            info.append(country_code)

            if len(info) > 2:
                bot.send_message(message.chat.id, 'Область объекта: ' + info[0] + ' \n Страна объекта: ' + info[1] +
                                                  '\n Код страны объекта: ' + info[2])

            if len(info) == 2:
                bot.send_message(message.chat.id, 'Страна объекта: ' + info[0] + '\n Код страны объекта: ' + info[1])

        else:
            bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')

    else:
        bot.send_message(message.chat.id, 'Ошибка выполнения запроса, внимательно прочтите /help')


bot.polling(none_stop=True)
