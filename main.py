import os
import glob
import telebot
from dotenv import load_dotenv

TXT2IMG = "../stable-diffusion/scripts/txt2img.py "
PROMPTARG = "--prompt "
OTHERARG = "--plms --n_iter 1 --n_samples 1 --skip_grid --seed -1"

load_dotenv()
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['Greet'])
def greet(message):
    bot.reply_to(message, "Hey! How's it going?")

def send_prompt(message):
    fullcmd = "python " + TXT2IMG + PROMPTARG + "\"" + message.text + "\" " + OTHERARG
    print(fullcmd)
    os.system(fullcmd)

@bot.message_handler()
def hello(message):
    send_prompt(message)
    list_of_files = glob.glob('../stable-diffusion/outputs/txt2img-samples/samples/*')
    latest_file = max(list_of_files, key=os.path.getctime)
    bot.send_photo(message.chat.id, photo=open(latest_file,'rb'))

bot.polling()
