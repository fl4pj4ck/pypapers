import ctypes
import random
import argparse
import subprocess
from pathlib import Path
from send2trash import send2trash
from PIL import Image
from typing import List, Optional

# Use Path for better cross-platform compatibility
FOLDER_PATH = Path(__file__).parent
LOG_FILE = FOLDER_PATH / 'wallpapers.log'
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png')
PAINT_DOT_NET = Path("C:/Program Files/paint.net/paintdotnet.exe")
SAFE_WALLPAPER = ""  # Consider moving this to a config file

def not_seen(path: str) -> bool:
    path_lower = path.lower()
    with LOG_FILE.open('r') as file:
        return path_lower not in (line.strip().lower() for line in file)

def remove_last() -> None:
    lines = LOG_FILE.read_text().splitlines()
    if lines:
        LOG_FILE.write_text('\n'.join(lines[:-1]))

def get_last() -> Optional[str]:
    lines = LOG_FILE.read_text().splitlines()
    return lines[-1] if lines else None

def append_to_file(entry: str) -> None:
    with LOG_FILE.open("a") as file:
        file.write(f"{entry}\n")

def set_wallpaper(new_wallpaper: str) -> None:
    if Path(new_wallpaper).is_file():
        ctypes.windll.user32.SystemParametersInfoW(20, 0, new_wallpaper, 0)

def next_wallpaper() -> None:
    backgrounds = [f for f in FOLDER_PATH.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    if backgrounds:
        while True:
            new_wallpaper = random.choice(backgrounds)
            if not_seen(str(new_wallpaper)):
                set_wallpaper(str(new_wallpaper))
                append_to_file(str(new_wallpaper))
                return

def previous_wallpaper() -> None:
    remove_last()
    set_wallpaper(get_last())

def delete_wallpaper() -> None:
    send2trash(get_last())
    remove_last()
    next_wallpaper()

def load_safe() -> None:
    if Path(SAFE_WALLPAPER).is_file():
        set_wallpaper(SAFE_WALLPAPER)

def flip(axis) -> None:
    img = get_last()
    if Path(img).is_file():
        current_image = Image.open(img)
        new_image = current_image.transpose(method=axis)
        send2trash(img)
        new_image.save(img)
        set_wallpaper(img)

def paint() -> None:
    if Path(PAINT_DOT_NET).is_file():
        subprocess.Popen([str(PAINT_DOT_NET), get_last()])

def run_main() -> None:
    parser = argparse.ArgumentParser(description="Wallpaper management script")
    parser.add_argument("-D", "--delete", action="store_true", help="Delete current wallpaper")
    parser.add_argument("-H", "--horizontal", action="store_true", help="Flip wallpaper horizontally")
    parser.add_argument("-V", "--vertical", action="store_true", help="Flip wallpaper vertically")
    parser.add_argument("-P", "--previous", action="store_true", help="Set previous wallpaper")
    parser.add_argument("-E", "--edit", action="store_true", help="Edit wallpaper in Paint.NET")
    parser.add_argument("-S", "--safe", action="store_true", help="Load safe wallpaper")

    args = parser.parse_args()

    actions = {
        'delete': delete_wallpaper,
        'safe': load_safe,
        'previous': previous_wallpaper,
        'edit': paint,
        'horizontal': lambda: flip(Image.FLIP_LEFT_RIGHT),
        'vertical': lambda: flip(Image.FLIP_TOP_BOTTOM)
    }

    for arg, action in actions.items():
        if getattr(args, arg):
            action()
            return

    next_wallpaper()

if __name__ == "__main__":
    run_main()
