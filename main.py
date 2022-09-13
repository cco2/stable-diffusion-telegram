import os
import telebot
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['Greet'])
def greet(message):
    bot.reply_to(message, "Hey! How's it going?")

@bot.message_handler(commands=['hello'])
def hello(message):
    bot.send_photo(message.chat.id, photo=open('../stable-diffusion/outputs/txt2img-samples/samples/00000.png','rb'))

bot.polling()
