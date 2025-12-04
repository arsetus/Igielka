import random
import math
import traceback
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMutexLocker
from PyQt5.QtWidgets import QListWidgetItem
from MemoryFunctions import *
from KeyboardFunctions import *
from MouseFunctions import *
from GeneralFunctions import *

class cavebotThread(QThread):
    index_update = pyqtSignal(int, object)
    
    def __init__(self, waypoints, context):
        super().__init__()
        self.waypoints = waypoints
        self.running = True
        self.context = context
        self.current_wpt = 0

    def run(self):
        my_mapX_dest = None
        delay = 0
        timer = 0
        mapClickWait = False
        
        while self.running:
            try:
                self.index_update.emit(0, self.current_wpt)
                wpt_data = self.waypoints[self.current_wpt]
                wpt_action = wpt_data['Action']
                map_x = wpt_data['X']
                map_y = wpt_data['Y']
                map_z = wpt_data['Z']
                my_mapX_dest = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_mapX_dest_offset, 1, label="myMapDestX")
                if self.context.cavebot_lock and my_mapX_dest != 65535:
                    mapClickWait = False
                    write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_mapX_dest_offset, 65535, "int")
                    timer = 0
                    QThread.msleep(50) 
                    continue

                if abs(self.context.x - map_x) == 0 and abs(self.context.y - map_y) == 0 and (map_z == 0 or abs(self.context.z - map_z) == 0) and wpt_action == 0:
                    mapClickWait = False
                    self.current_wpt = (self.current_wpt + 1) % len(self.waypoints)
                    continue

                if my_mapX_dest != 65535:
                    mapClickWait = True
                    QThread.msleep(100)
                    timer += 100
                else:
                    mapClickWait = False

                if not self.context.cavebot_lock and mapClickWait == False:
                    QThread.msleep(30)
                    if self.context.rest == 0 and self.context.autoJump:
                        press_key(self.context.hwnd, ' ')
                        QThread.msleep(8000)

                    if wpt_action == 0:
                        walk(self.context, self.context.x, self.context.y, self.context.z, map_x, map_y, map_z)
                        QThread.msleep(100)
                         
                    elif 1 <= wpt_action <= 9 and (self.context.x==map_x and self.context.y==map_y): #Use on pos
                        self.useOnPos(wpt_action, self.context.x, self.context.y, self.context.z, map_x, map_y, map_z)     
                        
                    elif 1 <= wpt_action <= 9 and (self.context.x!=map_x or self.context.y!=map_y): #if need to use on pos but incorrect pos
                        QThread.msleep(50)
                        walk(self.context, self.context.x, self.context.y, self.context.z, map_x, map_y, map_z) 

                    elif wpt_action == 10: #Wait
                        delay = wpt_data['Args']
                        if delay != 0:
                            QThread.msleep(int(delay))
                        self.current_wpt = (self.current_wpt + 1) % len(self.waypoints)

                if timer >= 1000:
                    mapClickWait = False
                    timer = 0
                    write_memory(self.context.process_handle, self.context.playerPointer + self.context.Addresses.my_mapX_dest_offset, 65535, "int")

            except Exception as e:
                print("Loop crashed:", e)
                traceback.print_exc()

    def useOnPos(self, direction, x, y, z, map_x, map_y, map_z):
        QThread.msleep(300)
        if (x==map_x and y==map_y):
            QThread.msleep(100)
            useOnDir(self.context, direction)
            self.current_wpt = (self.current_wpt + 1) % len(self.waypoints) 

    def stop(self):
        if self.running:
            self.running = False
        #else:
            #self.running = True
            #self.run()

class RecordThread(QThread):
    wpt_update = pyqtSignal(int, object)

    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context
        

    def run(self):
        waypoint_data = {
            "Action": 0,
            "X": self.context.x,
            "Y": self.context.y,
            "Z": self.context.z
        }
        waypoint = QListWidgetItem(f'Walk: {self.context.x} {self.context.y} {self.context.z}')
        waypoint.setData(Qt.UserRole, waypoint_data)
        self.wpt_update.emit(1, waypoint)
        old_x, old_y, old_z = self.context.x, self.context.y, self.context.z
        while self.running:
            try:
                if self.context.z != old_z:
                    if self.context.y > old_y and self.context.x == old_x:  # Move Down
                        waypoint_data = {
                            "Action": 2,
                            "X": old_x,
                            "Y": old_y,
                            "Z": old_z
                        }
                        waypoint = QListWidgetItem(f'Floor Change: {self.context.x} {self.context.y} {self.context.z}')
                        waypoint.setData(Qt.UserRole, waypoint_data)
                        self.wpt_update.emit(1, waypoint)
                    if self.context.y < old_y and self.context.x == old_x:  # Move Up
                        waypoint_data = {
                            "Action": 8,
                            "X": old_x,
                            "Y": old_y,
                            "Z": old_z
                        }
                        waypoint = QListWidgetItem(f'Floor Change: {self.context.x} {self.context.y} {self.context.z}')
                        waypoint.setData(Qt.UserRole, waypoint_data)
                        self.wpt_update.emit(1, waypoint)
                    if self.context.y == old_y and self.context.x > old_x:  # Move Right
                        waypoint_data = {
                            "Action": 6,
                            "X": old_x,
                            "Y": old_y,
                            "Z": old_z
                        }
                        waypoint = QListWidgetItem(f'Floor Change: {self.context.x} {self.context.y} {self.context.z}')
                        waypoint.setData(Qt.UserRole, waypoint_data)
                        self.wpt_update.emit(1, waypoint)
                    if self.context.y == old_y and self.context.x < old_x:  # Move Left
                        waypoint_data = {
                            "Action": 4,
                            "X": old_x,
                            "Y": old_y,
                            "Z": old_z
                        }
                        waypoint = QListWidgetItem(f'Floor Change: {self.context.x} {self.context.y} {self.context.z}')
                        waypoint.setData(Qt.UserRole, waypoint_data)
                        self.wpt_update.emit(1, waypoint)

                if (self.context.x != old_x or self.context.y != old_y) and self.context.z == old_z:
                    waypoint_data = {
                        "Action": 0,
                        "X": self.context.x,
                        "Y": self.context.y,
                        "Z": self.context.z
                    }
                    waypoint = QListWidgetItem(f'Walk: {self.context.x} {self.context.y} {self.context.z}')
                    waypoint.setData(Qt.UserRole, waypoint_data)
                    self.wpt_update.emit(1, waypoint)
                old_x, old_y, old_z = self.context.x, self.context.y, self.context.z
                QThread.msleep(100)
            except Exception as e:
                print(e)

    def stop(self):
        self.running = False

    def useOnPos(self, direction):
        QThread.msleep(random.randint(110, 150))
        useOnDir(self.context, direction)
        QThread.msleep(50)
