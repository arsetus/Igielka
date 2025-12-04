import ctypes as c
from win32gui import IsWindowEnabled
import win32process
import time
import importlib.util
import sys
import os
import win32api, win32con
import requests
import types
import pymem
from GeneralFunctions import *
from MemoryFunctions import *
from MouseFunctions import *
from PyQt5.QtCore import QMutex, QMutexLocker

class ClientContext:
    def __init__(self, hwnd, nickname):
        self.hwnd = hwnd
        self.nickname = nickname
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.pid = pid
        self.process_handle = c.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
        modules = win32process.EnumProcessModules(self.process_handle)
        self.base_address = modules[0]
        self.baseModuleName = getBaseModuleName(pymem.process.enum_process_module(self.process_handle)).name.lower()

        self.Addresses = self.load_local_addresses()
        if not self.Addresses:
            self.Addresses = self.download_and_load_addresses("Offsets.py")

        if self.Addresses.my_stats_address and self.Addresses.attack_address:
            self.playerPointer = read_direct(self.process_handle, self.base_address, self.Addresses.my_stats_address, 2, label="playerPointer")
            self.attackPointer = self.base_address + self.Addresses.attack_address
        elif not self.Addresses.my_stats_address and self.baseModuleName == "nsclient_gl_x64.exe" or self.baseModuleName == "nsclient_dx_x64.exe":
            self.playerPointer, self.attackPointer = self.aob_scan_64()

        self.debug = False
        self.windowX, self.windowY, self.screen_width, self.screen_height = get_window_size(self.hwnd)
        self.centerX = round(self.screen_width/2)
        self.centerY = round(self.screen_height/2)
        self.hp = 0
        self.hp_max = 0
        self.mp = 0
        self.mp_max = 0
        self.rest = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.target_id = 0
        self.target_x = 0
        self.target_y = 0
        self.target_z = 0
        self.target_name = 0
        self.target_hp = 0
        self.zoomX = 7
        self.takeAll_x = 0
        self.takeAll_y = 0
        self.takeAllcolorR = 0
        self.takeAllcolorG = 0
        self.takeAllcolorB = 0
        self.takeAllDelay = 50
        self.loot_list = {}
        self.sparringOn = False
        self.autoJump = False
        self.autoJar = False
        self.autoJarKey = None
        self.autoJumpHPpercent = 0
        self.combatControls = [[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        self.inventory = [[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        self.last_monster_positions = []
        self.lock = QMutex()
        self.cavebot_lock = False
        self.lootCBLock = False
        self.updateGameUIcontrols()
        self.a = None
        self.b = None
        self.c = None
        self.d = None
        self.e = None
        self.f = None
        self.g = None
        self.h = None
        self.i = None
        self.j = None
        self.k = None
        self.l = None

        enable_debug_privilege_pywin32()
        
    def aob_scan_64(self):
        pm = pymem.Pymem()
        pm.open_process_from_id(self.pid)
        ss = AOB_Scan(self.process_handle,self.baseModuleName, self.Addresses.aob64)
        if ss:
            rip_displacement = pm.read_int(ss + 0x243 + 3)
            return pm.read_longlong(ss + 0x243+0x7+rip_displacement), ss + 0x243+0x7+rip_displacement+8


    def aob_scan_32(self):
        pm = pymem.Pymem()
        pm.open_process_from_id(self.pid)
        ss = AOB_Scan(self.process_handle,self.baseModuleName, self.Addresses.aob32)
        #localplayer = pm.read_int(ss + 0x7)
        print(ss)
        #print({hex(pm.read_int(localplayer))})

    def updateGameUIcontrols(self):
        cc = find_image_on_window(self.hwnd, "Images/combatcontrols.png", 0.90)
        inv = find_image_on_window(self.hwnd, "Images/inventory.png", 0.90)
        if cc:
            self.combatControls[0] = cc #0 top left corner
            self.combatControls[1] = (cc[0]+12,cc[1]+44) #1 walk
            self.combatControls[2] = (cc[0]+32,cc[1]+44) #2 run
            self.combatControls[3] = (cc[0]+62,cc[1]+44) #3 chase mode
            self.combatControls[4] = (cc[0]+93,cc[1]+44) #4 no pvp
            self.combatControls[5] = (cc[0]+112,cc[1]+44) #5 pvp
            self.combatControls[6] = (cc[0]+144,cc[1]+44) #6 area pvp
            self.combatControls[7] = (cc[0]+176,cc[1]+44) #7 remove summons
            self.combatControls[8] = (cc[0]+18,cc[1]+69) #8 no nature
            self.combatControls[9] = (cc[0]+48,cc[1]+69) #9 katon
            self.combatControls[10] = (cc[0]+78,cc[1]+69) #10 fuuton
            self.combatControls[11] = (cc[0]+108,cc[1]+69) #11, raiton
            self.combatControls[12] = (cc[0]+138,cc[1]+69) #12 doton
            self.combatControls[13] = (cc[0]+168,cc[1]+69) #13 suiton
        if inv:
            self.inventory[0] = inv #0 top left corner
            self.inventory[1] = (inv[0]+152,inv[1]+48) #1 eqpreset1
            self.inventory[2] = (inv[0]+152,inv[1]+165) #2 weaponpreset1
            self.inventory[3] = (inv[0]+110,inv[1]+55) #3 bp
            self.inventory[4] = (inv[0]+20,inv[1]+55) #4 necklace
            self.inventory[5] = (inv[0]+20,inv[1]+144) #5 belt
            self.inventory[6] = (inv[0]+20,inv[1]+188) #6 ring
            self.inventory[7] = (inv[0]+110,inv[1]+144) #7 extra slot
            self.inventory[8] = (inv[0]+20,inv[1]+100) #8 weapon left
            self.inventory[9] = (inv[0]+110,inv[1]+100) #9 weapon right
            self.inventory[10] = (inv[0]+66,inv[1]+55) #10 helmet
            self.inventory[11] = (inv[0]+66,inv[1]+100) #11 armor
            self.inventory[12] = (inv[0]+66,inv[1]+144) #12 legs
            self.inventory[13] = (inv[0]+66,inv[1]+188) #13 boots

    def changeNature(self, index):
        if self.combatControls[index+8] and win32gui.GetForegroundWindow() == self.hwnd:
            mouse_function(self.hwnd, self.combatControls[index+8][0], self.combatControls[index+8][1], option=2)

    def updateMonsters(self):
        """Refresh all monsters and mark dead ones."""
        with QMutexLocker(self.lock):
            for m in self.last_monster_positions:
                target_x, target_y, target_z, target_name, target_hp = read_target_info(self.process_handle, m.get("id"), self)
                if target_x == 65535 and target_y == 65535:
                    if not m.get("dead", False):
                        m.update({
                            "x": target_x,
                            "y": target_y,
                            "z": target_z,
                            "name": target_name,
                            "dead": True,
                            "looted": False,
                            "death_time": time.time()
                        })
                else:
                    m.update({
                        "x": target_x,
                        "y": target_y,
                        "z": target_z,
                        "lastX": target_x,
                        "lastY": target_y,
                        "lastZ": target_z,
                        "name": target_name,
                        "dead": False,
                        "looted": False,
                        "death_time": None
                    })

    def cleanup_dead_monsters(self):
        """Remove looted or expired (>60s dead) monsters."""
        now = time.time()
        with QMutexLocker(self.lock):
            self.last_monster_positions = [
                m for m in self.last_monster_positions
                if not m.get("looted", False) and (not m.get("dead", False) or (now - m.get("death_time", now)) < 25)
            ]

    def enable_debug_privilege_pywin32():
        try:
            hToken = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32con.TOKEN_ADJUST_PRIVILEGES | win32con.TOKEN_QUERY
            )
            privilege_id = win32security.LookupPrivilegeValue(None, win32security.SE_DEBUG_NAME)
            win32security.AdjustTokenPrivileges(hToken, False, [(privilege_id, win32con.SE_PRIVILEGE_ENABLED)])
            return True
        except Exception as e:
            print("Debug privilege error:", e)
            return False

    def addCreature(self, creature_id):
        """Add new creature if not already tracked."""
        with QMutexLocker(self.lock):
            if any(m["id"] == creature_id for m in self.last_monster_positions):
                return
            target_x, target_y, target_z, target_name, target_hp = read_target_info(self.process_handle, creature_id, self)
            self.last_monster_positions.append({
                "id": creature_id,
                "x": target_x,
                "y": target_y,
                "z": target_z,
                "lastX": target_x,
                "lastY": target_y,
                "lastZ": target_z,
                "name": target_name,
                "dead": False,
                "looted": False,
                "death_time": None
            })

    def download_and_load_addresses(self, file_name):
        RAW_BASE_URL = "https://raw.githubusercontent.com/arsetus/Igielka/main/"
        url = RAW_BASE_URL + file_name
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() 
            code_content = response.text
            module = types.ModuleType("Addresses") 
            exec(code_content, module.__dict__)
            return module
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {file_name} from GitHub: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error executing downloaded code for {file_name}: {e}", file=sys.stderr)
            return None

    def load_local_addresses(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.getcwd() 

        local_file_path = os.path.join(base_path, "customAddresses.py")
        if os.path.exists(local_file_path):
            try:
                spec = importlib.util.spec_from_file_location("Addresses_Local", local_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            except Exception as e:
                return None
        else:
            return None