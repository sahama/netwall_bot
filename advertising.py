from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
from telegram.bot import Bot
from telegram.update import Update
import telegram
import time
from orm import User, session, Advertising
import json
import os
import jdatetime

users = {}
ads = {}

back_button = 'برگشت'
menu_button = '/start'
skip_button = '/cancel'
agree_button = 'قبول'
cancel_button = 'انصراف'

with open('Province.json') as f:
    tmp = json.load(f)
    province = [i['name'].strip() for i in tmp]
    cities = {i['name']: [j['name'] for j in i['Cities']] for i in tmp}


PROVINCE, CITY, COMMENT, PICTURE = range(4)

def next_step(bot, update, step):
    i = update.message.chat_id
    reply_keyboard = []

    if step == PROVINCE:
        reply_keyboard = [[i] for i in province]
        text='استان محل زندگی خود را وارد کنید'

    elif step == CITY:
        reply_keyboard = [[i] for i in cities[users[i].province]] + [[back_button]]
        text = 'شهر محل سکونت خود را مشخص کنید'

    elif step == COMMENT:
        reply_keyboard = [[back_button]]
        text='توضیحات تبلغ خود را وارد کنید'

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
        return next_step(bot, update, PROVINCE)
    else:
        return next_step(bot, update, COMMENT)

def ad_province(bot, update):
    i = update.message.chat_id
    users[i].province = update.message.text

    return next_step(bot, update, CITY)

def ad_city(bot, update):
    if update.message.text == back_button:
        return next_step(bot,update,PROVINCE)

    i = update.message.chat_id
    users[i].city = update.message.text
    return next_step(bot,update, COMMENT)


def ad_comment(bot, update):
    i = update.message.chat_id
    if update.message.text == back_button:
        return next_step(bot, update, CITY)

    ad = Advertising()
    ad.comment = update.message.text
    ads[i] = ad
    users[i].advertisings.append(ad)
    session.add(users[i])
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
        PROVINCE: [MessageHandler([Filters.text], ad_province)],
        CITY: [MessageHandler([Filters.text], ad_city)],
        COMMENT: [MessageHandler([Filters.text], ad_comment)],
        PICTURE: [MessageHandler([Filters.text, Filters.photo], ad_picture)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
