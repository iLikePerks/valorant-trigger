from os import system, _exit
from time import sleep, perf_counter
from ctypes import WinDLL
from PIL.Image import frombytes
from mss import mss
from keyboard import is_pressed, add_hotkey, block_key, unblock_key

# Helper functions
def exit_():
    system("echo Press any key to exit . . . & pause >nul")
    _exit(0)

def find_matching_pixel(img_data, target_color, tolerance, zone):
    for y in range(0, zone * 2):
        for x in range(0, zone * 2):
            color = img_data[y][x]
            if all(target - tolerance <= c <= target + tolerance for c, target in zip(color, target_color)):
                return x, y
    return None, None

class HotkeyHandler:
    def __init__(self):
        self.active = False
        self.popoff_sound = lambda freq, dur: kernel32.Beep(freq, dur)
        self.keyboard = user32
        self.blocked_keys = []
        self.held_keys = []

    def toggle(self):
        self.active = not self.active
        self.popoff_sound(440, 75)
        self.popoff_sound(700 if self.active else 200, 100)

    def handle_hotkey(self):
        if self.active:
            x, y = find_matching_pixel(img_data, (R, G, B), TOLERANCE, ZONE)
            if x is not None and y is not None:
                print(f"{SUCCESS} Reaction time: {int((perf_counter() - start_time) * 1000)}ms")
                self.handle_blocked_keys()
                self.handle_mouse_events()
                self.reset_blocked_and_held_keys()

    def handle_blocked_keys(self):
        keys_to_block = {30: "a", 32: "d", 17: "w", 31: "s"}
        for vk, key in keys_to_block.items():
            if is_pressed(key):
                block_key(vk)
                self.blocked_keys.append(vk)
                self.keyboard.keybd_event(vk, 0, 0, 0)
                self.held_keys.append(vk)
        sleep(0.1)

    def handle_mouse_events(self):
        self.keyboard.mouse_event(2, 0, 0, 0, 0)
        sleep(0.005)
        self.keyboard.mouse_event(4, 0, 0, 0, 0)

    def reset_blocked_and_held_keys(self):
        for vk in self.blocked_keys:
            unblock_key(vk)
        for vk in self.held_keys:
            self.keyboard.keybd_event(vk, 0, 2, 0)
        self.blocked_keys.clear()
        self.held_keys.clear()

# Configuration
TRIGGER, HIGHLIGHT = [line.strip() for line in open("config.txt")]

# Color values
if HIGHLIGHT == "red":
    R, G, B = (152, 20, 37)
elif HIGHLIGHT == "purple":
    R, G, B = (250, 100, 250)

# Mode selection
MODE = input(f"{INFO} Mode\n\n[\x1b[35m1\x1b[38;5;255m] Hold\n[\x1b[35m2\x1b[38;5;255m] Toggle\n\n> ")
if MODE not in ["1", "2"]:
    print(f"{ERROR} Choose 1 or 2 retard.\n")
    exit_()

# Other setup
user32, kernel32, shcore = WinDLL("user32", use_last_error=True), WinDLL("kernel32", use_last_error=True), WinDLL("shcore", use_last_error=True)
shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
TOLERANCE, ZONE = 20, 5
GRAB_ZONE = (int(WIDTH / 2 - ZONE), int(HEIGHT / 2 - ZONE), int(WIDTH / 2 + ZONE), int(HEIGHT / 2 + ZONE))

# Main loop
o = system("cls")
if MODE == "1":
    pixel_analyzer = PixelAnalyzer(img_data)
    hotkey_handler = HotkeyHandler()
    hotkey_handler.toggle()
    hotkey_handler.handle_hotkey()
elif MODE == "2":
    pixel_analyzer = PixelAnalyzer(img_data)
    hotkey_handler = HotkeyHandler()
    add_hotkey(TRIGGER, hotkey_handler.toggle)
    while True:
        hotkey_handler.handle_hotkey()
        sleep(0.5)