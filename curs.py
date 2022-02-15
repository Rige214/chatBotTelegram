# -*- coding: utf-8 -*-
import configur
import telebot
from telebot import types
import datetime
import xmltodict
import requests
from pyowm import OWM
from pyowm.utils import config
import emoji
import geopy
from geopy.geocoders import Nominatim


bot = telebot.TeleBot(configur.token)
config_dict = config.DEFAULT_CONFIG
config_dict['language'] = 'ru'

owm = OWM(configur.id_two)
mgr = owm.weather_manager()


@bot.message_handler(commands=['start'])
def message_start(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard="True")
    item1 = types.KeyboardButton('/currency')
    item2 = types.KeyboardButton('Богородск')
    item3 = types.KeyboardButton('Нижний Новгород')
    item4 = types.KeyboardButton(emoji.emojize(':round_pushpin: Текущее местоположение'), request_location= True)
    #item5 = types.KeyboardButton(emoji.emojize(':apple: /weather'))
    markup.add(item1, item2, item3, item4)

    bot.send_message(message.chat.id,
                     emoji.emojize('<strong>Приветствую, ' + message.from_user.first_name +
                                   ' !</strong>:wave:\nБот создан <a href="https://t.me/rige214">безукоризненным лентяем</a>, поэтому убедительная просьба!'
                                   ' <em> Не ожидайте идеальной и стабильной работы.Спасибо!</em>'
                                   '\nДля того, чтобы узнать погоду,напиши название необходимого тебе населенного пункта'
                                   '\n\nНапример: <code>Богородск</code>\n\n<code>Если у Вас возникли вопросы, обращайтесь по ссылке ниже</code>', use_aliases=True),
                     parse_mode="HTML", reply_markup=markup)


@bot.message_handler(commands=['currency'])
def get_rates(message):
    try:
        get_curl = 'https://cbr.ru/scripts/xml_daily.asp'
        date_format = '%d/%m/%Y'
        today = datetime.date.today()
        params = {
            "date_req": today.strftime(date_format),
        }
        r = requests.get(get_curl, params=params)

        data = xmltodict.parse(r.text)

        section_id1 = 'R01235'  # dollar
        section_id2 = 'R01239'  # euro
        section_id3 = 'R01720'  # grivna
        section_id4 = 'R01820'  # yen

        for item in data['ValCurs']['Valute']:
            if item['@ID'] == section_id1:
                currency_rate1 = item['Value']
                bot.send_message(message.chat.id, 'На текущий момент (' + str(today) + ') курсы валют таковы: ')
                bot.send_message(message.chat.id, '1 Доллар 🇺🇸: ' + currency_rate1 + ' рублей')
                break

        for item in data['ValCurs']['Valute']:
            if item['@ID'] == section_id2:
                currency_rate2 = item['Value']
                bot.send_message(message.chat.id, '1 Евро 🇪🇺: ' + currency_rate2 + ' рублей')
                break

        for item in data['ValCurs']['Valute']:
            if item['@ID'] == section_id3:
                currency_rate3 = item['Value']
                bot.send_message(message.chat.id, '10 Гривен 🇺🇦: ' + currency_rate3 + ' рублей')
                break

        for item in data['ValCurs']['Valute']:
            if item['@ID'] == section_id4:
                currency_rate4 = item['Value']
                bot.send_message(message.chat.id, '1 Йена 🇯🇵: ' + currency_rate4 + ' рублей')
                break
    except:
        bot.send_message(message.chat.id, 'Команда введена некорректно' + ' " ' + message.text + ' " ')


@bot.message_handler(content_types=['text'])
def send_weather(message):
    try:
        observation = mgr.weather_at_place(message.text)
        weather = observation.weather
        wind_speed = weather.wind()['speed']
        temp = weather.temperature('celsius')['temp']
        temp_feels = weather.temperature('celsius')['feels_like']
        answer = "В городе <code>" + message.text + "</code>\nСейчас <code>" + weather.detailed_status + "</code>"
        answer += "\nТемпература :  <code>" + str(temp) + "</code>  ℃"
        answer += "\nОщущается как :  <code>" + str(temp_feels) + "</code>  ℃"
        answer += "\nСкорость ветра :  <code>" + str(wind_speed) + "</code>  М/с"
        bot.send_message(message.chat.id, answer, parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, 'Введено некорректное значение ' + ' " ' + message.text + ' " ')


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        observation = mgr.one_call(lat=message.location.latitude, lon=message.location.longitude)
        geolocation = Nominatim(user_agent="Rge")
        pos = str(message.location.latitude) + ',' + str(message.location.longitude)
        loc = geolocation.reverse(pos, exactly_one=True, timeout=1,  addressdetails=True)
        place = loc.address
        temp = observation.current.temperature('celsius').get('temp', None)
        temp_feels_like = observation.current.temperature('celsius').get('feels_like', None)
        wind = observation.current.wind().get('speed', 0)
        status = observation.current.detailed_status
        message_loc = "Вы находитесь по следующему адресу <code>" + str(place) + "</code>\n\nТекущая погода в данном месте сейчас следующая : <code>" + str(status) + "</code>"
        message_loc += "\n\nТемпература :  <code>" + str(temp) + "</code>  ℃"
        message_loc += "\n\nОщущается как :  <code>" + str(temp_feels_like) + "</code>  ℃"
        message_loc += "\n\nСкорость ветра :  <code>" + str(wind) + "</code>  М/с"
        bot.send_message(message.chat.id, message_loc, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, 'Произошла неизвестная ошибка, пожалуйста, повторите запрос позже!')

@bot.message_handler(commands=['weather'])
def prg (message):
    observation = mgr.one_call(lat=message.location.latitude, lon=message.location.longitude)
    geolocation = Nominatim(user_agent="Rge")
    pos = str(message.location.latitude) + ',' + str(message.location.longitude)
    loc = geolocation.reverse(pos, exactly_one=True, timeout=1, addressdetails=True)
    place = loc.address
    wind_speed = observation.forecast_daily.wind().get('speed', 0)
    temp = observation.forecast_daily.temperature('celsius').get('temp', None)
    # temp_feels = weth.temperature('celsius')['feels_like']
    answer = "В городе <code>" + place + "</code>\nСейчас <code>" + weth.detailed_status + "</code>"
    answer += "\nТемпература :  <code>" + str(temp) + "</code>  ℃"
    # answer += "\nОщущается как :  <code>" + str(temp_feels) + "</code>  ℃"
    answer += "\nСкорость ветра :  <code>" + str(wind_speed) + "</code>  М/с"
    bot.send_message(message.chat.id, answer, parse_mode="HTML")



bot.polling(none_stop=True)

