import win32gui
import win32process, win32api
import win32con
import os, sys
from PyQt5.QtWidgets import (QWidget, QLabel, QListWidget, QLineEdit, QGridLayout, QPushButton, QApplication, QMainWindow, QTabWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from MainWindowTab import MainWindowTab

nicks = None
debug = False
def find_windows_matching():
    results = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            h_proc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            exe_path = win32process.GetModuleFileNameEx(h_proc, 0)
            win32api.CloseHandle(h_proc)
            if os.path.basename(exe_path).lower() == "nsclient_dx_x64.exe" or os.path.basename(exe_path).lower() == "nsclient_gl_x64.exe":
                if title != "Naruto Story" or debug:
                    results.append((hwnd, title.replace("Naruto Story - ","")))
        except:
            pass

    win32gui.EnumWindows(callback, None)
    return results

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class LoaderTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.debug = True

        # Set window icon
        icon_path = resource_path('Icon.png')
        self.setWindowIcon(QIcon(icon_path)) 
        self.setWindowTitle("Igielka")
        self.setFixedSize(430, 430)

        # Layout
        self.layout = QGridLayout()
        self.tabs = QTabWidget()

        nicks = find_windows_matching()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.tabs.tabBarDoubleClicked.connect(self.tab_bar_double_clicked)
        self.setCentralWidget(self.tabs)
        for name in nicks:
            client_tab = MainWindowTab(name[1], name[0], debug) 
            if client_tab.context.Addresses != None:
                self.tabs.addTab(client_tab, name[1])
            if client_tab.context.debug:
                self.tabs.addTab(client_tab, str(name[0]))


    def on_tab_changed(self, index):
        if index == -1:
            return
        current_tab = self.tabs.widget(index)
        nickname = self.tabs.tabText(index)
        self.setWindowTitle("Igielka - " + nickname)
        print(f"Switched to {nickname}")

    def tab_bar_double_clicked(self, index):
        if index == -1:
            return

        current_tab = self.tabs.widget(index)
        nickname = self.tabs.tabText(index)
        self.setWindowTitle("Igielka - " + nickname)
        print(f"{nickname} functions stopped")

        if current_tab.optionsTabs.widget(0).target_thread != None:
            current_tab.optionsTabs.widget(0).target_thread.stop()
        if current_tab.optionsTabs.widget(0).sparring_thread != None:
            current_tab.optionsTabs.widget(0).sparring_thread.stop()
        if current_tab.optionsTabs.widget(0).loot_thread != None:
            current_tab.optionsTabs.widget(0).loot_thread.stop()
        if current_tab.optionsTabs.widget(1).record_thread != None:
            current_tab.optionsTabs.widget(1).record_thread.stop()
        if current_tab.optionsTabs.widget(1).cavebot_thread != None:
            current_tab.optionsTabs.widget(1).cavebot_thread.stop()
        if current_tab.optionsTabs.widget(2).name_thread != None:
            current_tab.optionsTabs.widget(2).name_thread.stop()
        if current_tab.optionsTabs.widget(3).settings_thread != None:
            current_tab.optionsTabs.widget(3).settings_thread.stop()
        if current_tab.optionsTabs.widget(2).skin_thread != None:
            current_tab.optionsTabs.widget(2).skin_thread.stop()
        if current_tab.optionsTabs.widget(4).smart_hotkeys_thread != None:
            current_tab.optionsTabs.widget(4).smart_hotkeys_thread.stop()
        if current_tab.optionsTabs.widget(4).chakraTree_thread != None:
            current_tab.optionsTabs.widget(4).chakraTree_thread.stop()
        if current_tab.optionsTabs.widget(5).eq_thread != None:
            current_tab.optionsTabs.widget(5).eq_thread.stop()

    def loadTabs(self):
        print()
