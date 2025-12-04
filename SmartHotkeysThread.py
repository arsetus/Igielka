import random
import win32api
import win32con
import win32gui
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QListWidgetItem
from MemoryFunctions import *
from MouseFunctions import mouse_function
from KeyboardFunctions import *

class SetSmartHotkeyThread(QThread):
    def __init__(self, hotkeys_listWidget, hotkey, delay_option_lineEdit, status_label, context, mouseClick):
        super().__init__()
        self.running = True
        self.hotkeys_listWidget = hotkeys_listWidget
        self.context = context
        self.status_label = status_label
        self.hotkey = hotkey
        self.delay_option_lineEdit = delay_option_lineEdit
        self.mouseClick = mouseClick

    def run(self):
        if self.mouseClick:
            self.status_label.setStyleSheet("color: blue; font-weight: bold;")
            while self.running:
                x, y = win32gui.ScreenToClient(self.context.hwnd, win32api.GetCursorPos())
                self.status_label.setText(
                    f"Current: X={x}  Y={y}"
                )
                if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.status_label.setText(f"Coordinates set at X={x}, Y={y}")
                    self.running = False
                    smart_hotkey_data = {
                        "Hotkey": self.hotkey,
                        "Delay": self.delay_option_lineEdit.text(),
                        "X": x,
                        "Y": y
                    }
                    hotkey_item = QListWidgetItem(f"Delay: {self.delay_option_lineEdit.text()}, {self.hotkey} at X={x}, Y={y}")
                    hotkey_item.setData(Qt.UserRole, smart_hotkey_data)
                    self.hotkeys_listWidget.addItem(hotkey_item)
                    return
        else:
            smart_hotkey_data = {
                "Hotkey": self.hotkey,
                "Delay": self.delay_option_lineEdit.text(),
                "X": 0,
                "Y": 0
            }
            hotkey_item = QListWidgetItem(f"Hotkey: {self.hotkey}, Delay: {self.delay_option_lineEdit.text()}")
            hotkey_item.setData(Qt.UserRole, smart_hotkey_data)
            self.hotkeys_listWidget.addItem(hotkey_item)


class SmartHotkeysThread(QThread):

    def __init__(self, hotkeys_listWidget, context):
        super().__init__()
        self.running = True
        self.hotkeys_listWidget = hotkeys_listWidget
        self.context = context
        self.timerList = []
        for index in range(self.hotkeys_listWidget.count()):
            if not self.running:
                break  # Stop gracefully
            item = self.hotkeys_listWidget.item(index)
            data = item.data(Qt.UserRole)
            if not data:
                continue
            try:
                delay = int(data["Delay"])
                self.timerList.append(delay)
            except Exception as e:
                print(f"Error parsing delay data: {e}")
                continue

    def run(self):
        while self.running:
            for index in range(self.hotkeys_listWidget.count()):
                if not self.running:
                    break  # Stop gracefully
                item = self.hotkeys_listWidget.item(index)
                data = item.data(Qt.UserRole)
                if not data:
                    continue
                try:
                    hotkey = data["Hotkey"]
                    delay = int(data["Delay"])
                    x = int(data["X"])
                    y = int(data["Y"])
                    #print(self.timerList)
                except Exception as e:
                    print(f"Error parsing hotkey data: {e}")
                    continue
                #print(self.timerList[index])
                if self.timerList[index] <= 0:
                    if hotkey == "Left Click" and x != 0:
                        mouse_function(self.context.hwnd, x, y, option=2)
                        QThread.msleep(10)
                        self.timerList[index] = delay
                    elif hotkey == "Right Click" and x != 0:
                        mouse_function(self.context.hwnd, x, y, option=1)
                        QThread.msleep(10)
                        self.timerList[index] = delay
                    elif hotkey != None and x == 0:
                        press_key(self.context.hwnd, hotkey)
                        QThread.msleep(10)
                        self.timerList[index] = delay
                else:
                    self.timerList[index] -= 10
                    continue
            QThread.msleep(10)

    def stop(self):
        self.running = False

class ChakraTreeThread(QThread):

    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context

    def run(self):
        while self.running:
            direction = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_dir_offset, 7, label="my_dir")
            z = read_memory_address(self.context.process_handle, self.context.base_address, self.context.Addresses.my_z_address, 0, 7, label="my_y")
            if z == 7 and direction != 0:
                turnDir(self.context.hwnd, "UP")
                QThread.msleep(50)
            if z == 7 and direction == 0:
                press_key(self.context.hwnd, ' ')
                QThread.msleep(100)
            if z == 6 and direction != 2:
                turnDir(self.context.hwnd, "DOWN")
                QThread.msleep(50)
            if z == 6 and direction == 2:
                press_key(self.context.hwnd, ' ')
                QThread.msleep(100)

    def stop(self):
        self.running = False