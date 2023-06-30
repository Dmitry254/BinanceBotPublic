import json
import traceback
import time
from json import JSONDecodeError
import random

import requests
import telebot  # pip install PyTelegramBotAPI
from threading import Thread
from key import api_key_tg
from datetime import datetime, timedelta


bot = telebot.TeleBot(api_key_tg)


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('/demo')
        bot.send_message(message, "Что делаем?", reply_markup=user_markup)
    except:
        traceback.print_exc()
        pass


@bot.message_handler(commands=['demo'])
def start_message(message):
    try:
        bot.send_message(message, "Я жив")
    except:
        traceback.print_exc()
        pass


def send_text_message(message, text):
    bot.send_message(message, text, parse_mode='Markdown')


def bot_polling():
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        traceback.print_exc()
        time.sleep(60)


op = Thread(target=bot_polling, args=())
op.start()

message = 0
