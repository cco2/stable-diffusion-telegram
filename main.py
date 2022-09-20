import os
import glob
import subprocess
import random
import telebot
import shutil
from PIL import Image
import cv2
import numpy as np
from dotenv import load_dotenv

TXT2IMG = "./scripts/txt2img.py "
PROMPTARG = "--prompt "
OTHERARG = "--plms --n_iter 1 --n_samples 1 --skip_grid "
SEEDARG = "--seed "
MIDAS_INPUT_PATH = "./input/"
MIDAS_OUTPUT_PATH = "./output/"
STITCH_PATH = "../stitch/"
LKG_PATH = "../LKG/"

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

def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def do_stitch(imagepath):
    base = os.path.basename(imagepath)
    curdir = os.getcwd()
    os.chdir('../stitch')
    im1 = Image.open(base)
    # Turns out PIL does not actually convert "I" to "RGB" accurately...
    # See:
    #  https://github.com/python-pillow/Pillow/issues/3159
    #  https://github.com/python-pillow/Pillow/issues/5642
    #
    # so instead, use opencv to convert "I" to "BGR" and then
    # convert "BGR" to "RGB" so PIL can concatenate easily
    #
    #im1 = Image.open("d-" + base)
    #print(im1.getbands())
    #arr=np.array(im1)
    #im = Image.fromarray(arr, mode="RGBA")
    #im = im1.convert("I")

    image = cv2.imread("d-" + base)
    im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im2 = Image.fromarray(im_rgb)
    outbase = "s-" + base
    get_concat_h(im1, im2).save(outbase)
    shutil.copyfile(outbase, LKG_PATH + outbase)
    os.chdir(curdir)
    return LKG_PATH + outbase

lastpath = ""

@bot.message_handler(commands=['convert'])
def convert(message):
    print("lkg")
    print("chat id = " + str(message.chat.id))
    if message.chat.id == 5768325303:
        if lastpath == "":
            bot.send_message(message.chat.id, "Submit prompt first")
        else:
            generate_depth_map(lastpath)
            outpath = do_stitch(lastpath)
            bot.send_photo(message.chat.id, photo=open(outpath,'rb'))
    else:
        print("Unexpected user message")

@bot.message_handler()
def hello(message):
    print("chat id = " + str(message.chat.id))
    if message.chat.id == 5768325303:
        global lastpath
        lastpath = generate_ai_image_from_prompt(message)
    else:
        print("Unexpected user message")


bot.polling()
