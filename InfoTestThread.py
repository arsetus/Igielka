import random
import win32api, win32con, win32gui
import numpy as np
import time
from PyQt5.QtCore import QThread, QMutex, QMutexLocker
from context import *
from MemoryFunctions import *
import cv2 as cv

class InfoThread(QThread):
    def __init__(self, context, playerLabel,targetLabel):
        super().__init__()
        self.running = True
        self.playerLabel = playerLabel
        self.targetLabel = targetLabel
        self.context = context

    def run(self):
        while self.running:
            QThread.msleep(10)
            try:
                self.context.target_id = read_targeting_status(self.context.process_handle, self.context)
                if self.context.target_id:
                    self.context.target_x, self.context.target_y, self.context.target_z, self.context.target_name, self.context.target_hp = read_target_info(self.context.process_handle, self.context.target_id, self.context)
                else:
                    self.context.target_x = 0
                    self.context.target_y = 0
                    self.context.target_z = 0
                    self.context.target_name = None
                    self.context.target_hp = None
                self.context.x, self.context.y, self.context.z, self.context.hp, self.context.hp_max, self.context.mp, self.context.mp_max, self.context.rest = read_my_stats(self.context.process_handle, self.context)
                if self.context.x:
                    self.playerLabel.setText(f"Player\nX:{self.context.x} Y:{self.context.y} Z:{self.context.z}\nHP: {int(self.context.hp)} / {int(self.context.hp_max)}\nMP: {int(self.context.mp)} / {int(self.context.mp_max)}\nStamina: {int(self.context.rest)}")
                else:
                    self.playerLabel.setText(f"Player\nX: Y: Z:\nHP: 0/0\nMP: 0/0\nStamina:")
                if self.context.target_x:
                    self.targetLabel.setText(f"Target\nID: {self.context.target_id}\nName: {self.context.target_name}\nX:{self.context.target_x} Y:{self.context.target_y} Z:{self.context.target_z}\nHP: {self.context.target_hp} %")
                else:
                    self.targetLabel.setText(f"Target\nID: \nName: \nX: Y: Z:\nHP: %")

            except Exception as e:
                print(f"[InfoThread] Error: {e}")

    def stop(self):
        self.running = False
