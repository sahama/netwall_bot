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

users = {}
ads = {}

back_button = 'برگشت'
menu_button = '/start'
skip_button = 'ردکردن'
agree_button = 'قبول'
cancel_button = '/cancel'

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

    elif step == COMMENT:
        # reply_keyboard = [[back_button]]
        text='توضیحات آگهی خود را وارد کنید'

    elif step == PICTURE:
        reply_keyboard = [[back_button, skip_button]]
        text = 'عکس محصول خود را ارسال کنید فقط یک عکس می توانید ارسال کنید'

    reply_keyboard.append([menu_button, cancel_button])
    print(reply_keyboard)
    bot.sendMessage(i,text=text, reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return step


def ad_start(bot, update):
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    i = update.message.chat_id
    users[i] = user
    if not user:
        bot.sendMessage(i, text='شما در این سامانه ثبت نام نکرده اید. می توانید از طریق /register ثبت نام کرده و سپس به افزدون آگهی خود بپردازید')
        return ConversationHandler.END
    elif not user.city:
        bot.sendMessage(i,
                        text='برای درج آگهی و جستجو در آگهی ها انتخاب شهر و استان الزامی است /register ثبت نام خود را تکمیل کرده و سپس به افزدون آگهی خود بپردازید')
        return ConversationHandler.END
        # return next_step(bot, update, PROVINCE)
    else:
        return next_step(bot, update, CATEGORY)


def ad_category(bot, update):
    i = update.message.chat_id
    # if update.message.text == back_button:
    #     return next_step(bot, update, CITY)

    category = session.query(Category).filter_by(comment = update.message.text).one()
    ad = Advertising()
    ad.category = category
    ad.city = users[i].city
    ad.province = users[i].province
    ads[i] = ad
    ad.user = users[i]

    # session.add(users[i])
    # session.commit()
    # bot.sendMessage(i, text='آگهی شما با موفقیت درج شد')
    # return ConversationHandler.END
    return next_step(bot,update, COMMENT)

def ad_comment(bot, update):
    i = update.message.chat_id
    # if update.message.text == back_button:
    #     return next_step(bot, update, CATEGORY)


    ad = ads[i]
    ad.comment = update.message.text
    session.add(ad)
    session.commit()
    # bot.sendMessage(i, text='آگهی شما با موفقیت درج شد')
    # return ConversationHandler.END
    return next_step(bot,update, PICTURE)

def ad_picture(bot, update):
    if False:
        bot = Bot()
        update = Update()

    i = update.message.chat_id
    if update.message.text == back_button:
        return next_step(bot, update, COMMENT)
    if update.message.text == skip_button:
        pass
        # return next_step(bot, update, COMMENT)
    if update.message.photo:
        try:
            os.makedirs('picture')
        except:
            pass
        # print(update.message.photo)

        # file_id = update.message.photo[-1].file_id
        file_id = update.message.photo[1].file_id
        newFile = bot.get_file(file_id)
        tmp = os.path.join('picture', '{}-{}'.format(i, ads[i].id))
        newFile.download(tmp)

    bot.sendMessage(i, text='آگهی شما با موفقیت درج شد')

    # i = update.message.chat_id
    # if update.message.photo:
    #     if not users[i].id:
    #         session.add(users[i])
    #         session.commit()
    #     try:
    #         os.makedirs(os.path.join('photo',str(users[i].id)))
    #     except:
    #         pass
    #     print(update.message.photo)
    #
    #     file_id = update.message.photo[-1].file_id
    #     newFile = bot.get_file(file_id)
    #     newFile.download(os.path.join('photo',str(users[i].id), str(int(time.time()))))

    return ConversationHandler.END


def cancel(bot, update):
    i = update.message.chat_id
    user = update.message.from_user
    bot.sendMessage(i, text='شما از ادامه منصرف شده اید')

    return ConversationHandler.END




# def ad_picture(bot, update):
#     i = update.message.chat_id
#     if update.message.text == back_button:
#         return next_step(bot, update, CITY)
#
#     session.add(users[i])
#     session.commit()
#     bot.sendMessage(i,text=finish_msg)
#     return ConversationHandler.END


ad_handler = ConversationHandler(
    entry_points=[CommandHandler('ad', ad_start)],
    allow_reentry=True,
    states={
        COMMENT: [MessageHandler([Filters.text], ad_comment)],
        PICTURE: [MessageHandler([Filters.text, Filters.photo], ad_picture)],
        CATEGORY: [MessageHandler([Filters.text], ad_category)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
