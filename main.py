import os
import glob
import subprocess
import random
import telebot
from dotenv import load_dotenv

TXT2IMG = "../stable-diffusion/scripts/txt2img.py "
PROMPTARG = "--prompt "
OTHERARG = "--plms --n_iter 1 --n_samples 1 --skip_grid "
SEEDARG = "--seed "

load_dotenv()
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

def send_prompt(message):
    seed = random.randint(0,4294967295)
    fullcmd = "python " + TXT2IMG + PROMPTARG + "\"" + message.text + "\" " + OTHERARG + SEEDARG + str(seed)
    print(fullcmd)
    returned_output = subprocess.check_output(fullcmd)
    print("========")
    print(returned_output.decode())
    print("+++++++")
    return seed

@bot.message_handler()
def hello(message):
    print("chat id = " + str(message.chat.id))
    if message.chat.id == 5768325303:
        seed = send_prompt(message)
        list_of_files = glob.glob('../stable-diffusion/outputs/txt2img-samples/samples/*')
        latest_file = max(list_of_files, key=os.path.getctime)
        #bot.send_photo(message.chat.id, photo=open(latest_file,'rb'))
        bot.send_photo(message.chat.id, photo=open(latest_file,'rb'), caption="\n seed: {}".format(seed))
    else:
        print("Unexpected user message")

bot.polling()
