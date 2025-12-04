import random
import win32gui
from PyQt5.QtCore import QThread
from KeyboardFunctions import *
from MemoryFunctions import *
from MouseFunctions import mouse_function
from MemoryFunctions import *

class NameThread(QThread):

    def __init__(self, name, context):
        super().__init__()
        self.newName = name
        self.context = context
        self.running = True

    def update_name(self, new):
        self.newName = new

    def run(self):
        while self.running:
            try:
                nick = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_name_offset, 5, label="nick")
                if nick != self.newName:
                    write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_name_offset, self.newName, "string")
                    win32gui.SetWindowText(self.context.hwnd, "Naruto Story - " + self.newName)
                QThread.msleep(random.randint(500, 1000))
            except Exception as e:
                print("Exception: ", e)

    def stop(self):
        if self.newName != self.context.nickname:
            write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_name_offset, self.context.nickname, "string")
            win32gui.SetWindowText(self.context.hwnd, "Naruto Story - " + self.context.nickname)
        self.running = False

class SkinThread(QThread):

    def __init__(self, skinID, skinOffset, context):
        super().__init__()
        self.newSkin = skinID
        self.newOffset = skinOffset
        self.context = context
        self.running = True

    def update_skin(self, ID, offset):
        self.newSkin = ID
        self.newOffset = offset

    def run(self):
        while self.running:
            try:
                skinID = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_skinID_offset, 1, label="skinID")
                skinOffset = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_skin_offset, 1, label="skinID")
                if skinID != self.newSkin:
                    write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_skinID_offset, self.newSkin, "int")
                if skinOffset != self.newOffset:
                    write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_skin_offset, self.newOffset, "int")
                QThread.msleep(random.randint(100, 200))
            except Exception as e:
                print("Exception: ", e)

    def stop(self,ID,offset):
        write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_skinID_offset, ID, "int")
        write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_skin_offset, offset, "int")
        self.running = False
