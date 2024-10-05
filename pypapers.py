import os
import configparser
import ctypes
import random
import argparse
from send2trash import send2trash
from PIL import Image

folder_path = os.path.dirname(__file__)
log_file    = os.path.join(folder_path, 'wallpapers.log')
supported   = ('.jpg', '.jpeg', '.png')
paintdotnet = "C:\\Program Files\\paint.net\\paintdotnet.exe"
safe        = ""

def not_seen(path):
    with open(log_file, 'r') as file:
        return path not in file.read()

def remove_last():
    with open(log_file, "r") as file:
        lines = file.readlines()
    if lines:
        with open(log_file, "w") as file:
            file.writelines(lines[:-1]) 

def get_last():
    with open(log_file, 'r') as file:
        lines = file.readlines()
        return lines[-1].strip() if lines else None
        
def append_to_file(entry):
    with open(log_file, "a") as file:
        file.write(entry + "\n")

def set_wallpaper(new_wallpaper):
    if os.path.isfile(new_wallpaper):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, new_wallpaper , 0)
        
def next_wallpaper():
    backgrounds = [f for f in os.listdir(folder_path) if f.lower().endswith(supported)]
    if backgrounds:
        while True:
            new_wallpaper = os.path.join(folder_path, random.choice(backgrounds)).lower()
            if not_seen(new_wallpaper):
                set_wallpaper(new_wallpaper)
                append_to_file(new_wallpaper)
                return

def previous_wallpaper():
    remove_last()
    set_wallpaper(get_last())

def delete_wallpaper():
    send2trash(get_last())
    remove_last()
    next_wallpaper()

def load_safe():
    if os.path.isfile(safe):
        set_wallpaper(safe)

def flip(axis):
    img = get_last()
    if os.path.isfile(img):
        current_image = Image.open(img)
        new_image = current_image.transpose(method=axis)
        send2trash(img)
        new_image.save(img)
        set_wallpaper(img)

def paint():
    if os.path.isfile(paintdotnet):
        subprocess.run([paintdotnet, get_last()])

def run_main():
    config = configparser.ConfigParser()
    # Initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--delete", action="store_true")        
    parser.add_argument("-H", "--hor", action="store_true")
    parser.add_argument("-V", "--ver", action="store_true")
    parser.add_argument("-P", "--previous", action="store_true")
    parser.add_argument("-E", "--edit", action="store_true")
    parser.add_argument("-S", "--safe", action="store_true")
    # Read arguments from the command line
    args = parser.parse_args()
    if args.delete:
        delete_wallpaper()
    elif args.safe:
        load_safe()
    elif args.previous:
        previous_wallpaper()
    elif args.edit:
        paint()
    elif args.hor:
        flip(Image.FLIP_LEFT_RIGHT)
    elif args.ver:
        flip(Image.FLIP_TOP_BOTTOM)
    else:
        next_wallpaper()

if __name__ == "__main__":
    run_main()
