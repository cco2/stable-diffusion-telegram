import os
import glob
import subprocess
import random
import telebot
import shutil
from dotenv import load_dotenv

TXT2IMG = "./scripts/txt2img.py "
PROMPTARG = "--prompt "
OTHERARG = "--plms --n_iter 1 --n_samples 1 --skip_grid "
SEEDARG = "--seed "
MIDAS_INPUT_PATH = "./input/"
MIDAS_OUTPUT_PATH = "./output/"
STITCH_PATH = "../stitch/"

load_dotenv()
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

def run_cmd(cmd):
    print(cmd)
    returned_output = subprocess.check_output(cmd)
    print("========")
    print(returned_output.decode())
    print("+++++++")


def send_prompt(message):
    seed = random.randint(0,4294967295)
    fullcmd = "python " + TXT2IMG + PROMPTARG + "\"" + message.text + "\" " + OTHERARG + SEEDARG + str(seed)
    run_cmd(fullcmd)
    return seed

def generate_ai_image_from_prompt(message):
    curdir = os.getcwd()
    os.chdir('../stable-diffusion')
    seed = send_prompt(message)
    list_of_files = glob.glob('./outputs/txt2img-samples/samples/*')
    latest_file = max(list_of_files, key=os.path.getctime)
    #bot.send_photo(message.chat.id, photo=open(latest_file,'rb'))
    bot.send_photo(message.chat.id, photo=open(latest_file,'rb'), caption="\n seed: {}".format(seed))
    os.chdir(curdir)
    return latest_file

def run_midas():
    fullcmd = "python run.py --model_type dpt_large"
    run_cmd(fullcmd)

def generate_depth_map(path):
    curdir = os.getcwd()
    os.chdir('../MiDaS')
    imagepath = "../stable-diffusion/" + path
    print("imagepath = " + imagepath)
    # Copy file to MiDaS input
    base = os.path.basename(imagepath)
    shutil.copyfile(imagepath, MIDAS_INPUT_PATH + base)
    # Run MiDaS
    run_midas()
    # Return depth map info
    outbase = "d-"+base
    print(STITCH_PATH + base) 
    print(STITCH_PATH + outbase)
    shutil.copyfile(MIDAS_INPUT_PATH + base, STITCH_PATH + base)
    shutil.copyfile(MIDAS_OUTPUT_PATH + base, STITCH_PATH + outbase)
    # clean up
    os.remove(MIDAS_INPUT_PATH + base)
    os.remove(MIDAS_OUTPUT_PATH + base)
    os.remove(MIDAS_OUTPUT_PATH + os.path.splitext(base)[0] + ".pfm")
    os.chdir(curdir)

@bot.message_handler()
def hello(message):
    print("chat id = " + str(message.chat.id))
    if message.chat.id == 5768325303:
        #imagepath = generate_ai_image_from_prompt(message)
        imagepath = './outputs/txt2img-samples/samples\\00301.png'
        generate_depth_map(imagepath)
    else:
        print("Unexpected user message")

bot.polling()
