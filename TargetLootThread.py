import random
import win32api, win32con, win32gui
import numpy as np
import time
from PyQt5.QtCore import QThread, QMutex, QMutexLocker
from context import *
from MemoryFunctions import *
from KeyboardFunctions import *
from MouseFunctions import *
import cv2 as cv

class TargetThread(QThread):
    def __init__(self, dist, loot_state, spar_delay, context):
        super().__init__()
        self.running = True
        self.dist = dist
        self.loot_state = loot_state
        if (spar_delay):
            self.spar_delay = int(spar_delay)
        else:
            self.spar_delay = 0
        self.context = context
        self.timer = 0
        self.state_lock = QMutex()
        self.last_target_pos = (None, None, None)

    def run(self):
        phandle = self.context.process_handle
        while self.running:
            QThread.msleep(10)
            try:
                if self.context.target_id == 0:
                    press_key(self.context.hwnd, "F")
                    QThread.msleep(200)
                    #if self.loot_state:             #do karpia
                        #press_key(self.context.hwnd, "1")
                    self.timer += 200
                    if not self.context.lootCBLock and self.context.cavebot_lock and self.timer > 800:
                        self.context.cavebot_lock = False
                        self.timer = 0

                    if self.timer > self.spar_delay:
                        self.context.sparringOn = True
                    else:
                        self.context.sparringOn = False

                if self.context.target_id != 0 and(self.context.x != None and self.context.target_x!= None and self.context.y != None and self.context.target_y != None and self.context.z != None and self.context.target_z != None):
                    QThread.msleep(30)
                    self.context.addCreature (self.context.target_id)
                    self.context.sparringOn = True

                    dist_x = abs(self.context.x - self.context.target_x); dist_y = abs(self.context.y - self.context.target_y); dist_z = abs(self.context.z - self.context.target_z)
                    if (self.dist >= dist_x and self.dist >= dist_y) or self.dist == 0:
                        self.context.cavebot_lock = True
                        QThread.msleep(250)
                    else:
                        press_key(self.context.hwnd, "F")
                        QThread.msleep(100)
                        if self.context.cavebot_lock and self.context.lootCBLock == False:
                            self.context.cavebot_lock = False
                if not self.loot_state and self.context.autoJar and self.getCorpsesAmountAround(self.context.x,self.context.y)==0:
                    press_key(self.context.hwnd, self.context.autoJarKey)
                    self.removeCorpsesFromListAround(self.context.x,self.context.y)
                    QThread.msleep(100)

            except Exception as e:
                print(f"[TargetThread] Error: {e}")

    def update_states(self, option, state):
        with QMutexLocker(self.state_lock):
            if option == 0:
                self.loot_state = state

    def getCorpsesAmountAround(self, x, y):
        n = 0
        for monster in self.context.last_monster_positions:
            if monster.get("dead", 0):
                dx = abs(monster.get("lastX", 0) - x)
                dy = abs(monster.get("lastY", 0) - y)
                if dx <= 1 and dy <= 1:
                    n += 1
        return n

    def removeCorpsesFromListAround(self, x, y):
        n = 0
        for monster in self.context.last_monster_positions:
            if monster.get("dead", 0):
                dx = abs(monster.get("lastX", 0) - x)
                dy = abs(monster.get("lastY", 0) - y)
                if dx <= 1 and dy <= 1:
                    monster["looted"] = True
        self.context.cleanup_dead_monsters()

    def stop(self):
        self.context.cavebot_lock = False
        self.running = False

class JumpThread(QThread):
    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context

    def run(self):
        while self.running:
            QThread.msleep(10)
            try:
                if self.context.target_id != 0:
                    QThread.msleep(30)
                    if self.context.rest >= 15 and (self.context.hp / self.context.hp_max)*100 <= self.context.autoJumpHPpercent:
                        press_key(self.context.hwnd, ' ')
                    QThread.msleep(100)

            except Exception as e:
                print(f"[JumpThread] Error: {e}")

    def stop(self):
        self.running = False

class TurnToMonsterThread(QThread):
    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context

    def run(self):
        while self.running:
            if self.context.target_id != 0 and(self.context.x != None and self.context.target_x!= None and self.context.y != None and self.context.target_y != None and self.context.z != None and self.context.target_z != None):
                direction = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_dir_offset, 7, label="my_dir")
                dist_x = abs(self.context.x - self.context.target_x)
                dist_y = abs(self.context.y - self.context.target_y)
                if dist_x <=3 and dist_y <=3:
                    targetDir = getDirToPos(self.context.x, self.context.y, self.context.target_x, self.context.target_y, False)
                    QThread.msleep(100)
                    if (targetDir == 7 or targetDir == 8) and direction != 0:
                        turnDir(self.context.hwnd, "UP")
                        QThread.msleep(100)
                    if (targetDir == 9 or targetDir == 6) and direction != 1:
                        turnDir(self.context.hwnd, "RIGHT")
                        QThread.msleep(100)
                    if (targetDir == 3 or targetDir == 2) and direction != 2:
                        turnDir(self.context.hwnd, "DOWN")
                        QThread.msleep(100)
                    if (targetDir == 1 or targetDir == 4) and direction != 3:
                        turnDir(self.context.hwnd, "LEFT")
                        QThread.msleep(100)
                else:
                    QThread.msleep(100)

    def stop(self):
        self.running = False

class LootThread(QThread):
    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context
        self.state_lock = QMutex()
        self.last_target_pos = (None, None, None)

    def run(self):
        while self.running:
            self.trackCurrentTarget()
            self.lootNearbyCorpses()
            self.context.updateMonsters()
            if self.get_unlooted_bodies_nearby():
                self.context.lootCBLock = True
            else:
                self.context.lootCBLock = False
            if self.context.autoJar and self.getAmountLootedAround() > 0:
                    press_key(self.context.hwnd, self.context.autoJarKey)
                    QThread.msleep(100)
            self.context.cleanup_dead_monsters()
            #self.takeAllcheck()
            QThread.msleep(30)

    def stop(self):
        self.running = False

    def takeAllcheck(self):
        takeAll = find_image_on_window(self.context.hwnd, "Images/takeAll.png", 0.90)
        if takeAll:
            takeAll = find_image_on_window(self.context.hwnd, "Images/takeAll.png", 0.90)
            QThread.msleep(self.context.takeAllDelay)
            if takeAll:
                mouse_function(self.context.hwnd, takeAll[0]+5, takeAll[1]+5, option=2)
                return True

    def get_unlooted_bodies_nearby(self, radius=1):
        unlooted_ids = []
        self.context.x, self.context.y
        for monster in list(self.context.last_monster_positions):
            if not monster.get("dead", False):
                continue 

            if monster.get("looted", False):
                continue

            monster_x = monster.get("lastX", 0)
            monster_y = monster.get("lastY", 0)
        
            dist_x = abs(self.context.x - monster_x)
            dist_y = abs(self.context.y - monster_y)

            if dist_x <= radius and dist_y <= radius:
                if monster.get("id"):
                    unlooted_ids.append(monster.get("id"))
            
        return unlooted_ids

    def setCorpsesLootedOnPos(self, x, y):
        for monster in list(self.context.last_monster_positions):
            if (monster.get("lastX", 0) == x) and (monster.get("lastY", 0) == y):
                monster["looted"] = True

    def getAmountLootedAround(self):
        n = 0
        for monster in self.context.last_monster_positions:
            if monster.get("dead", 0) and monster.get("looted", 0):
                dx = abs(monster.get("lastX", 0) - self.context.x)
                dy = abs(monster.get("lastY", 0) - self.context.y)
                if dx <= 1 and dy <= 1:
                    n += 1
        return n

    def trackCurrentTarget(self):
        target_id = read_targeting_status(self.context.process_handle, self.context)
        if not target_id:
            return

        with QMutexLocker(self.context.lock):
            found = any(m["id"] == target_id for m in self.context.last_monster_positions)

        if not found:
            self.context.addCreature(target_id)

    def lootNearbyCorpses(self):
        with QMutexLocker(self.context.lock):
            for m in self.context.last_monster_positions:
                if not m.get("dead", False) or m.get("looted", False):
                    continue  # skip alive or already looted

                dx = abs(m.get("lastX", 0) - self.context.x)
                dy = abs(m.get("lastY", 0) - self.context.y)
                if dx <= 1 and dy <= 1:
                    self.context.lootCBLock = True
                    QThread.msleep(100)
                    x, y = self.context.centerX + (m.get("lastX", 0) - self.context.x) * 90, self.context.centerY + (m.get("lastY", 0) - self.context.y) * 90
                    if self.context.a:
                        mouse_function(self.context.hwnd, x, y, self.context.centerX, self.context.centerY, option=4)
                        QThread.msleep(100)
                        mouse_function(self.context.hwnd, self.context.centerX, self.context.centerY, option=1)
                        QThread.msleep(150)
                        if self.takeAllcheck():
                            m["looted"] = True
                        break  # loot one corpse at a time
                    else:
                        mouse_function(self.context.hwnd, x, y, option=1)
                        QThread.msleep(150)
                        if self.takeAllcheck():
                            self.setCorpsesLootedOnPos(m.get("lastX", 0), m.get("lastY", 0))
                        break  # loot one corpse at a time

class TakeAllThread(QThread):
    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context

    def run(self):
        while self.running:
            takeAll = find_image_on_window(self.context.hwnd, "Images/takeAll.png", 0.90)
            if takeAll:
                takeAll = find_image_on_window(self.context.hwnd, "Images/takeAll.png", 0.90)
                QThread.msleep(50)
                if takeAll:
                    mouse_function(self.context.hwnd, takeAll[0]+5, takeAll[1]+5, option=2)
                    QThread.msleep(self.context.takeAllDelay)

    def stop(self):
        self.running = False

class SparringThread(QThread):

    def __init__(self, hotkey, delay, context):
        super().__init__()
        if (delay):
            self.delay = int(delay)
        else:
            self.delay = 0
        self.hotkey = hotkey
        self.running = True
        self.context = context

    def run(self):
        while self.running:
            
            if not self.context.sparringOn:
                QThread.msleep(100)   # pause until sparring is allowed again
                continue

            try:
                QThread.msleep(self.delay)
                press_key(self.context.hwnd, self.hotkey)
                QThread.msleep(1500)
                press_key(self.context.hwnd, self.hotkey)
                QThread.msleep(random.randint(500, 600))
            except Exception as e:
                print(f"[SparringThread] Error: {e}")

    def stop(self):
        self.running = False
        self.context.sparringOn = True  # reset so sparring isn’t permanently stuck off

def useOnPos(context, direction, x, y, z, map_x, map_y):
        QThread.msleep(50)
        if (x==map_x and y==map_y):
            QThread.msleep(100)
            useOnDir(context, direction)

class CollectorThread(QThread):
    def __init__(self, context):
        super().__init__()
        self.running = True
        self.context = context
        self.picked = True
        self.target_worldX = None
        self.target_worldY = None
        self.itemsFound = None
        # We need to be exactly on the tile or adjacent for the directional pickup to work.
        self.ARRIVAL_TOLERANCE = 1.1 # Reduced tolerance to ensure we are on the adjacent tile or the target tile.

    def run(self):
        while self.running:
            try:
                my_mapX_dest = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_mapX_dest_offset, 1, label="myMapDestX")
                self.itemsFound = match_template_multiscale(self.context.hwnd, "Images/flower.png", 0.7)
                # --- PHASE 2: PURSUE OR COLLECT (If a target is set) ---
                if self.target_worldX is not None and self.target_worldY is not None:
                    # Calculate distance to target
                    distance = ((self.context.x - self.target_worldX)**2 + (self.context.y - self.target_worldY)**2)**0.5
                    if distance <= self.ARRIVAL_TOLERANCE:
                        direction = calculate_direction(self.context.x, self.context.y, self.target_worldX, self.target_worldY)
                        # 2. Use directional right-click to pick up
                        QThread.msleep(50) 
                        useOnPos(self.context, direction,self.context.x, self.context.y, self.context.z, self.target_worldX, self.target_worldY) 

                        self.itemsFound = self.itemsFound[1:] 

                        self.target_worldX = None 
                        self.target_worldY = None
                        self.picked = False 
                        
                    else:
                        # --- STILL WALKING ---
                        # If distance is > 1.1, keep calling walk to ensure movement.
                        
                        if my_mapX_dest !=65535:
                            QThread.msleep(50)  
                        elif self.picked and self.itemsFound.any():
                            print(self.itemsFound[0][0], self.itemsFound[0][1])
                            mouse_function(self.context.hwnd, int(self.itemsFound[0][0]), int(self.itemsFound[0][1]), option=2)
                            #mapClick(self.context, player_x, player_y, player_z, self.target_worldX, self.target_worldY, 0)
                            QThread.msleep(50) 
                    continue 
                #else:
                    #self.itemsFound = match_template_multiscale(self.context.hwnd, "Images/flower.png", 0.7)

                # --- PHASE 1: SEARCH & SET TARGET (If no target is set) ---
                #itemsFound = match_template_multiscale(self.context.hwnd, "flower.png", 0.7)

                if self.itemsFound.any():
                    # Calculate world coordinates for the first found item
                    self.target_worldX = player_x + int((self.itemsFound[0][0] - self.context.centerX) / self.itemsFound[0][3])
                    self.target_worldY = player_y + int((self.itemsFound[0][1] - self.context.centerY) / self.itemsFound[0][3])
                    self.picked = True

                else:
                    QThread.msleep(50) 
                    
            except Exception as e:
                QThread.msleep(100)

    def stop(self):
        self.running = False

