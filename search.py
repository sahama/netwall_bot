from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
from telegram.bot import Bot
from telegram.update import Update
import telegram
import time
from orm import User, session, Advertising, Category
import json
import os
import jdatetime


back_button = 'برگشت'
menu_button = '/start'
skip_button = 'ردکردن'
agree_button = 'قبول'
cancel_button = '/cancel'
users = {}
with open('Province.json') as f:
    tmp = json.load(f)
    province = [i['name'].strip() for i in tmp]
    cities = {i['name']: [j['name'] for j in i['Cities']] for i in tmp}


CATEGORY, PROVINCE, CITY, COMMENT, PICTURE = range(5)

def next_step(bot, update, step):
    i = update.message.chat_id
    reply_keyboard = []

    if step == CATEGORY:
        reply_keyboard = [[c.comment] for c in session.query(Category).all()]
        text = 'از بین موضوعات زیر موضوع آگهی خود را انتخاب کنید'

    reply_keyboard.append([menu_button, cancel_button])
    print(reply_keyboard)
    bot.sendMessage(i,text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return step


def search_start(bot, update):
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    i = update.message.chat_id
    users[i] = user
    if not user:
        bot.sendMessage(i, text='شما در این سامانه ثبت نام نکرده اید. می توانید از طریق /register ثبت نام کرده و سپس به جستجوی آگهی خود بپردازید')
        return ConversationHandler.END
    elif not user.city:
        bot.sendMessage(i,
                        text='برای درج آگهی و جستجو در آگهی ها انتخاب شهر و استان الزامی است /register ثبت نام خود را تکمیل کرده و سپس به جستجوی آگهی خود بپردازید')
        return ConversationHandler.END
        # return next_step(bot, update, PROVINCE)
    else:
        return next_step(bot, update, CATEGORY)


def search_category(bot, update):
    i = update.message.chat_id

    user = users[i]
    ads = session.query(Advertising).filter(Advertising.province == user.province).filter(Advertising.city == user.city).filter(Category.comment == update.message.text).all()
    print(ads)
    for ad in ads:
        if os.path.exists('picture/{}-{}'.format(ad.user.chat_id, ad.id)):
            pic = 'picture/{}-{}'.format(ad.user.chat_id, ad.id)
        else:
            pic = None

        message = '''عنوان آگهی:
        {}
آگهی دهنده: {}
        شماره تماس: {}
'''.format(ad.comment, ad.user.first_name + ' ' + ad.user.last_name, ad.user.mobile)
        if pic:
            bot.sendPhoto(chat_id=i, photo=open(pic, 'rb'), caption=message)
        else:
            bot.sendMessage(i, text=message)

    # session.add(users[i])
    # session.commit()
    # bot.sendMessage(i, text='آگهی شما با موفقیت درج شد')
    return ConversationHandler.END
    # return next_step(bot,update, Category)


# def search(bot, update, args):
#     i = update.message.chat_id
#     for ad in session.query(Advertising).all():



def cancel(bot, update):
    i = update.message.chat_id
    user = update.message.from_user
    bot.sendMessage(i, text='شما از ادامه منصرف شده اید')

    return ConversationHandler.END


search_handler = ConversationHandler(
    entry_points=[CommandHandler('search', search_start)],
    allow_reentry=True,
    states={
        CATEGORY: [MessageHandler([Filters.text], search_category)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
