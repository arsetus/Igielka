import win32api
import win32gui
from PyQt5.QtCore import QThread, QTime, QDateTime
from win32con import VK_LBUTTON
from KeyboardFunctions import *

class SettingsThread(QThread):

    def __init__(self, context, index, status_label, takeAlldelay):
        super().__init__()
        self.index = index
        self.status_label = status_label
        self.running = True
        self.context = context
        self.delay = takeAlldelay
        self.lastDashTime = QTime.currentTime()
        self.lastDashTime.start()

    def run(self):
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        while self.running:
            cur_x, cur_y = win32gui.ScreenToClient(self.context.hwnd, win32api.GetCursorPos())
            QThread.msleep(10)
            #if self.index == 0: # set take all button
            #    self.status_label.setText(f"Current: X={cur_x}  Y={cur_y}")
            #    if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
            #        self.setTakeAll(cur_x+1, cur_y+1)
            #        self.status_label.setStyleSheet("color: green; font-weight: bold;")
            #        self.status_label.setText(f"Coordinates set at X={self.context.takeAll_x}, Y={self.context.takeAll_y}")
            #        self.running = False
            #        return
            #if self.index == 1: # set first eq set change button
            #    self.status_label.setText(f"Current: X={cur_x}  Y={cur_y}")
            #    if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
            #        self.context.eqSetX = cur_x+1
            #        self.context.eqSetY = cur_y+1
            #        self.status_label.setStyleSheet("color: green; font-weight: bold;")
            #        self.status_label.setText(f"Coordinates set at X={self.context.eqSetX}, Y={self.context.eqSetY}")
            #        self.running = False
            #        return
            if self.index == 2: # dash to pos 
                if self.lastDashTime.elapsed() >= 800:#self.context.a:
                    if win32gui.GetForegroundWindow() == self.context.hwnd:
                        if win32api.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                            dashJumpToPos(self.context,cur_x,cur_y)
                            self.lastDashTime.restart()

        QThread.msleep(200)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

    #def setTakeAll(self,x,y):
     #   hdc = win32gui.GetDC(self.context.hwnd)
     #   color = win32gui.GetPixel(hdc, x, y)
     #   win32gui.ReleaseDC(self.context.hwnd, hdc)

      #  self.context.takeAll_x = x
      #  self.context.takeAll_y = y
      #  self.context.takeAllcolorR = color & 0xff
      #  self.context.takeAllcolorG = (color >> 8) & 0xff
      #  self.context.takeAllcolorB = (color >> 16) & 0xff
      #  self.context.takeAllDelay = int(self.delay)

    def stop(self):
        self.running = False