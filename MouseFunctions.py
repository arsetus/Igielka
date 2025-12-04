import random
import threading
import math
import win32api, win32con, win32gui
mouse_lock = threading.Lock()


def mouse_function(hwnd, x_source, y_source, x_dest=0, y_dest=0, option=0) ->None:
    with mouse_lock:
        if option == 1: #  Right Click
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, 2, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, win32api.MAKELONG(x_source, y_source))
        if option == 2: #  Left Click
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 1, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(x_source, y_source))
        if option == 3: #  Collect Item
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 1, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x_dest, y_dest))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(x_dest, y_dest))
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x_dest, y_dest))
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, 2, win32api.MAKELONG(x_dest, y_dest))
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, win32api.MAKELONG(x_dest, y_dest))
        if option == 4: #  Drag'n'Drop
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 1, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 1, win32api.MAKELONG(x_dest, y_dest))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(x_dest, y_dest))
        if option == 5: #  Use on me
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, 2, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, win32api.MAKELONG(x_source, y_source))
            win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0,win32api.MAKELONG(x_dest, y_dest))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 1,win32api.MAKELONG(x_dest, y_dest))
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0,win32api.MAKELONG(x_dest, y_dest))

def useOnDir(context,dir) -> None:
    #multipierX = (context.screen_height/32)*1.5-8
    #multipierY = (context.screen_height/32)*2
    if dir == 5: #Center
        mouse_function(context.hwnd, context.centerX, context.centerY, option=1)
    elif dir == 1: #DownLeft
        mouse_function(context.hwnd, math.floor(context.centerX - (context.screen_height/32)*1.5)-8, math.floor(context.centerY + (context.screen_height/32)*2), option=1)
    elif dir == 2: #Down
        mouse_function(context.hwnd, context.centerX, math.floor(context.centerY + (context.screen_height/32)*2), option=1)
    elif dir == 3: #DownRight
        mouse_function(context.hwnd, math.floor(context.centerX + (context.screen_height/32)*1.5)-8, math.floor(context.centerY + (context.screen_height/32)*2), option=1)
    elif dir == 4: #Left
        mouse_function(context.hwnd, math.floor(context.centerX - (context.screen_height/32)*1.5)-8, context.centerY, option=1)
    elif dir == 6: #Right
        mouse_function(context.hwnd, math.floor(context.centerX + (context.screen_height/32)*1.5)-8, context.centerY, option=1)
    elif dir == 7: #UpLeft
        mouse_function(context.hwnd, math.floor(context.centerX - (context.screen_height/32)*1.5)-8, math.floor(context.centerY - (context.screen_height/32)*2), option=1)
    elif dir == 8: #Up
        mouse_function(context.hwnd, context.centerX, math.floor(context.centerY - (context.screen_height/32)*2), option=1)
    elif dir == 9: #UpRight
        mouse_function(context.hwnd, math.floor(context.centerX + (context.screen_height/32)*1.5)-8, math.floor(context.centerY - (context.screen_height/32)*2), option=1)
