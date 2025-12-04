import random
import win32gui
from PyQt5.QtCore import QThread
from KeyboardFunctions import *
from MouseFunctions import *
from MemoryFunctions import *
from GeneralFunctions import *

class EquipmentThread(QThread):

    def __init__(self, lowHP, lowSetOffset, highHP, highSetOffset, context):
        super().__init__()
        self.lowHP = lowHP
        self.lowSetOffset = lowSetOffset
        self.highHP = highHP
        self.highSetOffset = highSetOffset
        self.context = context
        self.running = True
        self.currentSet = None

    def update_vars(self, low, high, lSet, hSet):
        self.lowHP = low
        self.lowSetOffset = lSet
        self.highHP = high
        self.highSetOffset = hSet

    def run(self):
        while self.running and self.context.inventory[1]:
            try:
                if (self.context.hp / self.context.hp_max)*100 <= self.lowHP and self.currentSet != self.lowSetOffset:
                    self.currentSet = self.lowSetOffset
                    mouse_function(self.context.hwnd, self.context.inventory[1][0], self.context.inventory[1][1] + self.lowSetOffset*30, option=2)
                if (self.context.hp / self.context.hp_max)*100 >= self.highHP and self.currentSet != self.highSetOffset:
                    self.currentSet = self.highSetOffset
                    mouse_function(self.context.hwnd, self.context.inventory[1][0], self.context.inventory[1][1] + self.highSetOffset*30, option=2)
                QThread.msleep(200)
            except Exception as e:
                print("Exception: ", e)

    def stop(self):
        self.running = False

class MoneyChangerThread(QThread):
    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context

    def run(self):
        while self.running:
            rin = find_image_on_window(self.context.hwnd, "Images/rin.png", 0.95)
            sen = find_image_on_window(self.context.hwnd, "Images/sen.png", 0.95)
            QThread.msleep(50)
            if rin:
                mouse_function(self.context.hwnd, rin[0]+5, rin[1]+5, option=1)
                QThread.msleep(150)
            QThread.msleep(50)
            if sen:
                mouse_function(self.context.hwnd, sen[0]+5, sen[1]+5, option=1)
                QThread.msleep(150)

    def stop(self):
        self.running = False