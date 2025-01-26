from itertools import product
from datetime import datetime
from telebot import *
import sqlite3

bot = TeleBot('7416499319:AAGx8Fz9nwtejDFeasslAnjQ67KcEutjX2o')

klav = types.ReplyKeyboardMarkup(resize_keyboard=True)
buy = types.KeyboardButton("Купили")
eated = types.KeyboardButton("Сьели")
now = types.KeyboardButton('Сейчас лежит')

klav.add(buy,now,eated)

connection = sqlite3.connect('Fridger_database')
cursor=connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory(
id INTEGER PRIMARY KEY AUTOINCREMENT,
product TEXT NOT NULL,
action TEXT NOT NULL,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
connection.commit()
connection.close()

def addproduct(message):
    product_name = message.text.strip()
    connection = sqlite3.connect('Fridger_database')
    cursor=connection.cursor()
    cursor.execute('INSERT INTO inventory (product,action,timestamp) VALUES (?,?,?)', (product_name,"added",datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
    connection.close
    bot.send_message(message.chat.id, f"{product_name} добавлен в холодильник")


def delproduct(message):
    product_name = message.text.strip()
    connection = sqlite3.connect('Fridger_database')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE product = ?", (product_name,))
    count = cursor.fetchone()[0]
    if count > 0:
        cursor.execute('INSERT INTO inventory (product,action,timestamp) VALUES (?,?,?)', (product_name,"removed",datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, f"{product_name} успешно удалён из холодильника")
    else:
        bot.send_message(message.chat.id, "Такого продукта в холодильнике нет")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"Холодильник заработал", reply_markup=klav)


@bot.message_handler(func = lambda message: message.text == "Купили")
def bought(message):
    bot.send_message(message.chat.id,"Напишите название купленного продукта")
    bot.register_next_step_handler(message,addproduct)


@bot.message_handler(func = lambda message: message.text == "Сейчас лежит")
def nowlej(message):
    stri = ""
    connection = sqlite3.connect('Fridger_database')
    cursor = connection.cursor()
    cursor.execute('''SELECT product FROM inventory GROUP BY product HAVING SUM(CASE WHEN action = 'added' THEN 1 ELSE 0 END) > SUM(CASE WHEN action = 'removed' THEN 1 ELSE 0 END);''')
    current_products = cursor.fetchall()
    connection.close()
    if not current_products:
        bot.send_message(message.chat.id, "В холодильнике нет продуктов.")
        return
    stri = "\n".join(product[0] for product in current_products)
    bot.send_message(message.chat.id, f"Сейчас лежат:\n{stri}")


@bot.message_handler(func = lambda message: message.text == "Сьели")
def eated_product(message):
    bot.send_message(message.chat.id,"Напишите точно имя продукта")
    bot.register_next_step_handler(message,delproduct)


bot.polling(non_stop=True)