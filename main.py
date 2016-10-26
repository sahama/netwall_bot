from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
from telegram.bot import Bot
from telegram.update import Update
import telegram
import time
from orm import User, session, Advertising
from register import register_handler
from advertising import ad_handler
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update, args):
    if False:
        bot = Bot()
        update = Update()
    telegram_user = update.message.from_user
    user = session.query(User).filter_by(telegram_id = telegram_user.id).first()
    if user:
        if user.username == telegram_user.username:
            bot.sendMessage(chat_id=update.message.chat_id, text='خوش آمدید {}'.format(user.first_name))
            bot.sendMessage(chat_id=update.message.chat_id, text='برای بروز رسانی پروفایل خود از /register و برای جستجو در آگهی های موجود از /search استفاده کنید همچنین برای درج آگهی می توانید از /ad استفاده کنید')
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='به نظر می رسد شما نام کاربری خود را تغییر داده اید. در این صورت اطلاعات خود را به روز کنید')

    else:
        bot.sendMessage(chat_id=update.message.chat_id, text='سلام {} شما هنوز در این سامانه ثبت نام نکرده اید. در صورتی که می خواهید از امکانات این سامانه استفاده کنید باید ابتدا ثبت نام خود را کامل کنید. برای شروع ثبت نام روی /register کلیک کنید'.format(telegram_user.username if telegram_user.username else "مهمان"))




    # bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    # bot.sendMessage(chat_id=update.message.chat_id,text='برای شروع /register را بزنید')
    # bot.sendMessage(chat_id=update.message.chat_id,text='یکی از موارد زیر را انتخاب کنبد',reply_markup=reply_markup)
    # bot.sendPhoto(chat_id=update.message.chat_id, photo='https://telegram.org/img/t_logo.png')
    # echo(bot,update)
    # print(update.message)#('Hi!')


def echo(bot, update):
    if False:
        bot = Bot()
        update = Update()
    i = update.message.chat_id
    bot.sendMessage(i, text='این دستور هنوز پیاده سازی نشده است.')

update = {'update_id': 322708031, 'message': {'message_id': 206, 'from': {'id': 288911713, 'last_name': '', 'type': '', 'first_name': 'فرهاد', 'username': 'farhamous'}, 'supergroup_chat_created': False, 'group_chat_created': False, 'caption': '', 'new_chat_photo': [], 'migrate_to_chat_id': 0, 'channel_chat_created': False, 'delete_chat_photo': False, 'date': 1476337723, 'chat': {'id': 288911713, 'last_name': '', 'first_name': 'فرهاد', 'title': '', 'type': 'private', 'username': 'farhamous'}, 'migrate_from_chat_id': 0, 'new_chat_title': '', 'entities': [{'type': 'bot_command', 'offset': 0, 'length': 9}], 'text': '/register', 'photo': []}}


def search(bot, update, args):
    i = update.message.chat_id
    for ad in session.query(Advertising).all():
        if os.path.exists('picture/{}-{}'.format(ad.user.chat_id,ad.id)):
            pic = 'picture/{}-{}'.format(ad.user.chat_id,ad.id)
        else:
            pic = None

        message = '{}\n{}'.format(ad.comment, ad.user.username)
        if pic:
            bot.sendPhoto(chat_id=i, photo=open(pic, 'rb'), caption=message)
        else:
            bot.sendMessage(i, text=message)


def error(bot, update, error):
    print('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater('201813174:AAHHa_Hhsxlit4FGxkX8cQDT2F4kSnrq2L0')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_args=True))

    dp.add_handler(CommandHandler("search", search, pass_args=True))

    dp.add_handler(register_handler)
    dp.add_handler(ad_handler)
    # dp.add_handler(search_handler)
    # dp.add_handler(CallbackQueryHandler(button))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([], echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    print('running')
    main()
