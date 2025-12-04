import random
import time
import win32api
import win32gui
import win32con
import math
from MouseFunctions import mouse_function
from GeneralFunctions import *
from context import *
from PyQt5.QtCore import QThread

# Mapping for special keys
SPECIAL_KEYS = {
    "F1": win32con.VK_F1,
    "F2": win32con.VK_F2,
    "F3": win32con.VK_F3,
    "F4": win32con.VK_F4,
    "F5": win32con.VK_F5,
    "F6": win32con.VK_F6,
    "F7": win32con.VK_F7,
    "F8": win32con.VK_F8,
    "F9": win32con.VK_F9,
    "F10": win32con.VK_F10,
    "F11": win32con.VK_F11,
    "F12": win32con.VK_F12,
    }

VK_CODES = {
    "LEFT": 0x25,
    "UP": 0x26,
    "RIGHT": 0x27,
    "DOWN": 0x28,
    "NUMPAD1": win32con.VK_NUMPAD1,
    "NUMPAD3": win32con.VK_NUMPAD3,
    "NUMPAD7": win32con.VK_NUMPAD7,
    "NUMPAD9": win32con.VK_NUMPAD9,
}

SCAN_CODES = {
    "NUMPAD1": win32con.VK_NUMPAD1,
    "NUMPAD3": win32con.VK_NUMPAD3,
    "NUMPAD7": win32con.VK_NUMPAD7,
    "NUMPAD9": win32con.VK_NUMPAD9,
    "LEFT": 0x4B,
    "RIGHT": 0x4D,
    "UP": 0x48,
    "DOWN": 0x50,
}

def send_key(hwnd, key_name):
    vk_code = VK_CODES.get(key_name.upper())
    scan = SCAN_CODES.get(key_name.upper())
    if not vk_code or not scan:
        raise ValueError(f"Unknown key: {key_name}")

    extended = 0
    if key_name.upper() in ["LEFT", "UP", "RIGHT", "DOWN"]:
        extended = 1 << 24  # extended bit

    lParam_down = (1 | (scan << 16) | extended)
    lParam_up   = (1 | (scan << 16) | extended | (1 << 31) | (1 << 30))

    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, lParam_down)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, lParam_up)

def walk(context, my_x, my_y, my_z, map_x, map_y, map_z) -> None:
    x = map_x - my_x
    y = map_y - my_y
    multipierX = 83
    multipierY = 83
    #multipierX = math.floor(context.centerX - (context.screen_height/32)*1.5)-8, 
    #multipierY = math.floor(context.centerY + (context.screen_height/32)*2)
    if map_z != 0:
        z = map_z - my_z
    else:
        z = 0

    if x == 0 and y == -1 and z == 0:  # Walk Up
        send_key(context.hwnd, "UP")
        return
    if x == 0 and y == 1 and z == 0:  # Walk Down
        send_key(context.hwnd, "DOWN")
        return
    if x == -1 and y == 0 and z == 0:  # Walk Left
        send_key(context.hwnd, "LEFT")
        return
    if x == 1 and y == 0 and z == 0:  # Walk Right
        send_key(context.hwnd, "RIGHT")
        return
    if x == -1 and y == -1 and z == 0:  # Walk Up Left
        #send_key(context.hwnd, "NUMPAD7")
        mouse_function(context.hwnd, context.centerX + x * multipierX, context.centerY + y * multipierY, option=2)
        return
    if x == 1 and y == -1 and z == 0:  # Walk Up Right
        #send_key(context.hwnd, "NUMPAD9")
        mouse_function(context.hwnd, context.centerX + x * multipierX, context.centerY + y * multipierY, option=2)
        return
    if x == -1 and y == 1 and z == 0:  # Walk Down Left
        #send_key(context.hwnd, "NUMPAD1")
        mouse_function(context.hwnd, context.centerX + x * multipierX, context.centerY + y * multipierY, option=2)
        return
    if x == 1 and y == 1 and z == 0:  # Walk Down Right
        #send_key(context.hwnd, "NUMPAD3")
        mouse_function(context.hwnd, context.centerX + x * multipierX, context.centerY + y * multipierY, option=2)
        return

    if abs(x) <= 11 and abs(y) <= 7 and z == 0:  # Map click
        mouse_function(context.hwnd, context.centerX + x * multipierX, context.centerY + y * multipierY, option=2)
        return

def mapClick(context, my_x, my_y, my_z, map_x, map_y, map_z) -> None:
    x = map_x - my_x
    y = map_y - my_y
    multipierX = 83
    multipierY = 83
    if abs(x) <= 11 and abs(y) <= 7:  # Map click
        mouse_function(context.hwnd, context.centerX + x * multipierX, context.centerY + y * multipierY, option=2)
        return

def press_key(hwnd, key) -> None:
    if len(key.upper()) == 1:  # single char (letters, numbers, symbols)
        vk_code = win32api.VkKeyScan(key.upper())
        if vk_code != -1:
            scan_code = win32api.MapVirtualKey(vk_code & 0xFF, 0)
            keydown_lparam = (scan_code << 16) | 0x0001
            keyup_lparam = keydown_lparam | (0x3 << 30)
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code & 0xFF, keydown_lparam)
            win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code & 0xFF, keyup_lparam)

    elif key.upper() in SPECIAL_KEYS:  # handle F1, F2, etc.
        vk_code = SPECIAL_KEYS[key.upper()]
        scan_code = win32api.MapVirtualKey(vk_code, 0)
        keydown_lparam = (scan_code << 16) | 0x0001
        keyup_lparam = keydown_lparam | (0x3 << 30)
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, keydown_lparam)
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, keyup_lparam)

    else:
        print(f"Unsupported key: {key.upper()}")

def turnDir(hwnd, key) -> None:
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.03) 
    send_key(hwnd, key)
    time.sleep(0.03) 
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)


def press_hotkey(hwnd, hotkey) -> None:
    hotkey_index = win32api.MapVirtualKey(hotkey & 0xFF, 0)
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, 0x6F + hotkey, hotkey_index)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, 0x6F + hotkey, hotkey_index)

def dashJumpToPos(context,x,y):
    send_key(context.hwnd, get_main_direction(x, y, context.centerX, context.centerY))
    QThread.msleep(60)
    send_key(context.hwnd, get_main_direction(x, y, context.centerX, context.centerY))
    QThread.msleep(60)
    mouse_function(context.hwnd, x, y, option=2)
    QThread.msleep(60)
    press_key(context.hwnd, ' ')

def get_main_direction(mouse_x, mouse_y, center_x, center_y):
    Dx = mouse_x - center_x
    Dy = mouse_y - center_y
    if Dx == 0 and Dy == 0:
        return
    if abs(Dx) > abs(Dy):
        if Dx > 0:
            return "RIGHT"
        else:
            return "LEFT"
    else:
        if Dy > 0:
            return "DOWN"
        else:
            return "UP"