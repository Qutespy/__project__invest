import telebot
from telebot import types
import account

bot = telebot.TeleBot('5542015608:AAEOCFXlcwEnnqxyj2sScMOmgiQep8V4C1s')

@bot.message_handler(commands = ['start'])
def starting(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Свой кошелек")
    item2 = types.KeyboardButton("Свои счета")
    item3 = types.KeyboardButton("Транзакции")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Добро пожаловать. Я бот, предназначенный для информарованния по курсам валют, акций, а также своего баланса.".format(message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)
    print(message.chat.id)

@bot.message_handler(content_types=["text"])
def chatting(message):
    if message.chat.type == 'private':
        if message.text == 'Свой кошелек':
            'что-то нужно сделать с кошельком'
        elif message.text == 'Свои счета':
            doc = open('C:/Users/A138/PycharmProjects/pythonProject2/output.xlsx', 'rb')
            bot.send_document(message.chat.id, doc)
            bot.send_document(message.chat.id, "FILEID")
        elif message.text == 'Транзакции':
            bot.send_message(message.chat.id, '2')
        else:
            bot.send_message(message.chat.id, 'Я не знаю, что ответить(')
    print(message.chat.id)

bot.polling (none_stop = True)
