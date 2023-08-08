# Importing necessary modules
from os import system, _exit
from time import sleep, perf_counter
from ctypes import WinDLL

# Defining a function for clean exit
def exit_():
    system("echo Press any key to exit . . . & pause >nul")
    _exit(0)

# Color constants
ERROR = "\x1b[38;5;255m[\x1b[31m-\x1b[38;5;255m]"
SUCCESS = "\x1b[38;5;255m[\x1b[32m+\x1b[38;5;255m]"
INFO = "\x1b[38;5;255m[\x1b[35m*\x1b[38;5;255m]"

# Installing required modules if not present
try:
    from PIL.Image import frombytes
    from mss import mss
    from keyboard import is_pressed, add_hotkey, unblock_key
except ModuleNotFoundError:
    print(f"{INFO} Installing required modules.")
    o = system("pip3 install keyboard mss pillow --quiet --no-warn-script-location --disable-pip-version-check")

# Handling config.txt
try:
    TRIGGER, HIGHLIGHT = [line.strip() for line in open("config.txt")]
    print(f"{SUCCESS} Hotkey: {TRIGGER}\n{SUCCESS} Enemy highlight colour: {HIGHLIGHT}\n")
except (FileNotFoundError, ValueError):
    print(f"{ERROR} Missing or invalid config.txt\n")
    HIGHLIGHT = input(f"{INFO} Enemy highlight colour\n\n[\x1b[35m1\x1b[38;5;255m] Red (default)\n[\x1b[35m2\x1b[38;5;255m] Purple\n\n> ")
    if HIGHLIGHT not in ["1", "2"]:
        print(f"{ERROR} Choose 1 or 2, buddy.\n")
        exit_()
    if HIGHLIGHT == "1":
        HIGHLIGHT = "red"
    elif HIGHLIGHT == "2":
        HIGHLIGHT = "purple"
    print(f"\n{SUCCESS} Wrote enemy highlight colour to config.txt\n{INFO} Now write your hotkey in config.txt\n")
    with open("config.txt", "w") as f:
        f.write(f"Replace this first line with your hotkey.  e.g.  c   or   `   or even   ctrl + alt + z\n{HIGHLIGHT}")
    exit_()

# Setting highlight colors
if HIGHLIGHT == "red":
    R, G, B = (152, 20, 37)
elif HIGHLIGHT == "purple":
    R, G, B = (250, 100, 250)

# Getting mode input
MODE = input(f"{INFO} Mode\n\n[\x1b[35m1\x1b[38;5;255m] Hold\n[\x1b[35m2\x1b[38;5;255m] Toggle\n\n> ")
if MODE not in ["1", "2"]:
    print(f"{ERROR} Choose 1 or 2, pal.\n")
    exit_()

# Windows API setup
user32, kernel32, shcore = WinDLL("user32", use_last_error=True), WinDLL("kernel32", use_last_error=True), WinDLL("shcore", use_last_error=True)
shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
TOLERANCE, ZONE = 20, 5
GRAB_ZONE = (int(WIDTH / 2 - ZONE), int(HEIGHT / 2 - ZONE), int(WIDTH / 2 + ZONE), int(HEIGHT / 2 + ZONE))

# Main PopOff class
class PopOff:
    def __init__(self):
        self.active = False
        kernel32.Beep(440, 75), kernel32.Beep(200, 100)

    def switch(self):
        self.active = not self.active
        kernel32.Beep(440, 75), kernel32.Beep(700, 100) if self.active else kernel32.Beep(440, 75), kernel32.Beep(200, 100)

    def search(self):
        start_time = perf_counter()
        with mss() as sct:
            img = sct.grab(GRAB_ZONE)
        pmap = frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        for x in range(0, ZONE * 2):
            for y in range(0, ZONE * 2):
                r, g, b = pmap.getpixel((x, y))
                if R - TOLERANCE < r < R + TOLERANCE and G - TOLERANCE < g < G + TOLERANCE and B - TOLERANCE < b < B + TOLERANCE:
                    print(f"\x1b[2A{SUCCESS} Reaction time: {int((perf_counter() - start_time) * 1000)}ms")
                    blocked, held = [], []
                    if is_pressed("w"):
                        blocked.append(87)
                    if is_pressed("a"):
                        blocked.append(65)
                    if is_pressed("s"):
                        blocked.append(83)
                    if is_pressed("d"):
                        blocked.append(68)
                    if blocked:
                        user32.mouse_event(2, 0, 0, 0, 0)
                        sleep(0.005)
                        user32.mouse_event(4, 0, 0, 0, 0)
                        sleep(0.1)
                        for b in blocked:
                            user32.keybd_event(b, 0, 2, 0)
                        sleep(0.005)
                        user32.mouse_event(2, 0, 0, 0, 0)
                        sleep(0.005)
                        user32.mouse_event(4, 0, 0, 0, 0)
                    break

    def hold(self):
        while 1:
            if is_pressed(TRIGGER):
                while is_pressed(TRIGGER):
                    self.search()
            else:
                sleep(0.1)

    def toggle(self):
        add_hotkey(TRIGGER, self.switch)
        while 1:
            self.search() if self.active else sleep(0.5)


o = system("cls")
if MODE == "1":
    PopOff().hold()
elif MODE == "2":
    PopOff().toggle()
