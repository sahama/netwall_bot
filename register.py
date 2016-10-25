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

with open('Province.json') as f:
    tmp = json.load(f)
    province = [i['name'].strip() for i in tmp]
    cities = {i['name']: [j['name'] for j in i['Cities']] for i in tmp}

AGGREGATION, FIRST_NAME, LAST_NAME, MOBILE, PROVINCE, CITY, COMMENT = range(7)
back_button = 'برگشت'
menu_button = '/start'
skip_button = 'رد کردن'
agree_button = 'قبول'
cancel_button = '/cancel'
finish_msg = 'پایان'
agree_msg = 'توافق نامه با ثبت نام در این سامانه شما می پذیرید که ...'
users = {}

def next_step(bot, update, step):
    i = update.message.chat_id
    reply_keyboard = []
    if step == AGGREGATION:
        reply_keyboard = [[agree_button, cancel_button]]
        bot.sendMessage(i,
                        text=agree_msg,
                        reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return step

    elif step == FIRST_NAME:
        text='نام کوچک شما؟'

    elif step == LAST_NAME:
        text='نام خانوادگی شما؟'

    elif step == MOBILE:
        text='شماره موبایل شما؟'

    elif step == PROVINCE:
        reply_keyboard = [[i] for i in province]
        text='استان محل زندگی خود را وارد کنید'

    elif step == CITY:
        reply_keyboard = [[i] for i in cities[users[i].province]]
        text = 'شهر محل سکونت خود را مشخص کنید'

    elif step == COMMENT:
        text='توضیحات اضافی خود را وارد کنید'

    reply_keyboard.append([back_button, skip_button, menu_button, cancel_button])
    print(reply_keyboard)
    bot.sendMessage(i,text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return step


def register_start(bot, update):
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    i = update.message.chat_id
    if user:
        bot.sendMessage(i, text='شما قبلا در این سامانه ثبت نام کرده اید ادامه این فرآیند پروفایل شما را به روز می کند در صورت انصراف می توانید /cancel را بزنید')
        users[i] = user
        return next_step(bot, update, FIRST_NAME)
    else:
        pass
    return next_step(bot, update, AGGREGATION)


def register_aggregation(bot, update):
    aggregation = update.message.text
    i = update.message.chat_id
    telegram_user = update.message.from_user
    if aggregation == agree_button :
        user = User()
        user.chat_id = i
        user.telegram_id = telegram_user.id
        user.username = telegram_user.username if telegram_user.username else ''
        user.first_name = telegram_user.first_name if telegram_user.first_name else ''
        user.last_name = telegram_user.last_name if telegram_user.last_name else ''
        users[i] = user
        session.add(user)
        session.commit()
        bot.sendMessage(i,
                        text='ثبت نام اولیه شما انجام شد. در ادامه اطلاعات تکمیلی از شما گرفته می شود')

        return next_step(bot, update, FIRST_NAME)
    else:
        bot.sendMessage(i,text='امکان ثبت نام شما و دسترسی به سامانه وجود ندارد. شما شرایط مندرج در توافق نامه را نپذیرفته اید.')
        return ConversationHandler.END

def register_first_name(bot, update):
    if update.message.text == skip_button:
        return next_step(bot, update, LAST_NAME)

    i = update.message.chat_id
    users[i].first_name = update.message.text
    return next_step(bot, update, LAST_NAME)

def register_last_name(bot, update):
    if update.message.text == back_button:
        return next_step(bot, update, FIRST_NAME)

    if update.message.text == skip_button:
        return next_step(bot, update, MOBILE)

    i = update.message.chat_id
    users[i].last_name = update.message.text
    return next_step(bot, update, MOBILE)

def register_mobile(bot, update):
    if update.message.text == back_button:
        return next_step(bot, update, LAST_NAME)

    if update.message.text == skip_button:
        return next_step(bot, update, PROVINCE)

    i = update.message.chat_id
    users[i].mobile = update.message.text
    return next_step(bot, update, PROVINCE)

def register_province(bot, update):
    if update.message.text == back_button:
        return next_step(bot, update, MOBILE)
    if update.message.text == skip_button:
        return next_step(bot, update, COMMENT)

    i = update.message.chat_id
    users[i].province = update.message.text

    return next_step(bot, update, CITY)

def register_city(bot, update):
    if update.message.text == back_button:
        return next_step(bot,update,PROVINCE)
    if update.message.text == skip_button:
        return next_step(bot, update, COMMENT)

    i = update.message.chat_id
    users[i].city = update.message.text
    return next_step(bot,update, COMMENT)


def register_comment(bot, update):
    i = update.message.chat_id
    if update.message.text == back_button:
        return next_step(bot, update, CITY)
    if update.message.text == skip_button:
        pass
    else:
        users[i].comment = update.message.text

    session.add(users[i])
    session.commit()
    bot.sendMessage(i,text=finish_msg)
    return ConversationHandler.END


def cancel(bot, update):
    i = update.message.chat_id
    user = update.message.from_user
    bot.sendMessage(i, text='شما از ادامه منصرف شده اید')

    return ConversationHandler.END


register_handler = ConversationHandler(
    entry_points=[CommandHandler('register', register_start)],
    allow_reentry=True,
    states={
        AGGREGATION: [MessageHandler([Filters.text], register_aggregation)],
        FIRST_NAME: [MessageHandler([Filters.text], register_first_name)],
        LAST_NAME: [MessageHandler([Filters.text], register_last_name)],
        MOBILE: [MessageHandler([Filters.text], register_mobile)],
        PROVINCE: [MessageHandler([Filters.text], register_province)],
        CITY: [MessageHandler([Filters.text], register_city)],
        COMMENT: [MessageHandler([Filters.text], register_comment)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
