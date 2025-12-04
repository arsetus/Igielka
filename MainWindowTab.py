from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QApplication, QLabel, QTabBar
)
from PyQt5.QtCore import QObject, pyqtSignal
import keyboard
from NameSkinTab import NameSkinTab
from EquipmentTab import EquipmentTab
from TargetLootTab import TargetLootTab
from SettingsTab import SettingsTab
from ComboTab import ComboTab
from SmartHotkeysTab import SmartHotkeysTab
from cavebotTab import cavebotTab
from InfoTestTab import InfoTestTab
from context import ClientContext

class MainWindowTab(QWidget):
    def __init__(self, nickname, hwnd, debug):
        super().__init__()
        self.nickname = nickname
        self.hwnd = hwnd

        # load process context
        self.context = ClientContext(hwnd, nickname)
        if self.context.Addresses != None or debug:
            self.load_content()
            
    def closeEvent(self, event):
        # Clean up the hotkey when the app closes
        keyboard.remove_hotkey(self.optionsTabs.widget(3).current_hotkey)
        keyboard.remove_hotkey(self.optionsTabs.widget(6).current_hotkey)
        super().closeEvent(event)

    def load_content(self):
        self.base_address = self.context.base_address

        # main layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # left-side tab widget (for Cavebot, Settings, etc.)
        self.optionsTabs = QTabWidget()
        self.optionsTabs.setTabPosition(QTabWidget.West)  # vertical tabs on left
        layout.addWidget(self.optionsTabs)
        # Add all option tabs
        self.optionsTabs.addTab(TargetLootTab(self.context),"")
        self.optionsTabs.tabBar().setTabButton(0, QTabBar.LeftSide, QLabel("Targetting"))
        #-----------------
        self.optionsTabs.addTab(cavebotTab(self.context),"")
        self.optionsTabs.tabBar().setTabButton(1, QTabBar.LeftSide, QLabel("Cavebot"))
        #-----------------
        self.optionsTabs.addTab(NameSkinTab(self.context),"")
        self.optionsTabs.tabBar().setTabButton(2, QTabBar.LeftSide, QLabel("Name/Skin"))
        #-----------------
        self.optionsTabs.addTab(SettingsTab(self.context),"")
        self.optionsTabs.tabBar().setTabButton(3, QTabBar.LeftSide, QLabel("Settings"))
        #-----------------
        self.optionsTabs.addTab(SmartHotkeysTab(self.context),"")
        self.optionsTabs.tabBar().setTabButton(4, QTabBar.LeftSide, QLabel("Clicker"))
        #-----------------
        self.optionsTabs.addTab(EquipmentTab(self.context),"")
        self.optionsTabs.tabBar().setTabButton(5, QTabBar.LeftSide, QLabel("Equipment"))
        #-----------------
        self.optionsTabs.addTab(ComboTab(self.context),"")
        self.optionsTabs.tabBar().setTabButton(6, QTabBar.LeftSide, QLabel("Combos"))
        #-----------------
        self.optionsTabs.addTab(InfoTestTab(self.context,True),"")
        self.optionsTabs.tabBar().setTabButton(7, QTabBar.LeftSide, QLabel("Info"))
        # set window props
        self.setWindowTitle(f"Igielka - {self.nickname}")