from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
from telegram.bot import Bot
from telegram.update import Update
import telegram
import time
from orm import User, session
import json
import os
import jdatetime

users = {}
ads = {}

back_button = 'برگشت'
menu_button = '/start'
skip_button = 'رد کردن'
agree_button = 'قبول'
cancel_button = 'انصراف'

with open('Province.json') as f:
    tmp = json.load(f)
    province = [i['name'].strip() for i in tmp]
    cities = {i['name']: [j['name'] for j in i['Cities']] for i in tmp}


PROVINCE, CITY, PICTURE, COMMENT = range(4)

def next_step(bot, update, step):
    i = update.message.chat_id
    reply_keyboard = []

    if step == PROVINCE:
        reply_keyboard = [[i] for i in province]
        text='استان محل زندگی خود را وارد کنید'

    elif step == CITY:
        reply_keyboard = [[i] for i in cities[users[i].province]]
        text = 'شهر محل سکونت خود را مشخص کنید'

    elif step == COMMENT:
        text='توضیحات تبلغ خود را وارد کنید'

    elif step == PICTURE:
        text = 'عکس محصول خود را ارسال کنید فقط یک عکس می توانید ارسال کنید'

    reply_keyboard.append([back_button, skip_button, menu_button, cancel_button])
    print(reply_keyboard)
    bot.sendMessage(i,text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return step


def add_start(bot, update):
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    i = update.message.chat_id
    users[i] = user
    if not user:
        bot.sendMessage(i, text='شما در این سامانه ثبت نام نکرده اید. می توانید از طریق /register ثبت نام کرده و سپس به افزدون آگهی خود بپردازید')
        return ConversationHandler.END
    else:
        pass
    return next_step(bot, update, AGGREGATION)

