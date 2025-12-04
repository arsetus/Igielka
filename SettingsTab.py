import json
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QGroupBox,
    QGridLayout, QPushButton, QListWidget, QComboBox, QCheckBox
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import Qt
import keyboard
import os
import win32gui
from GeneralFunctions import *
from MouseFunctions import *
from SettingsThread import SettingsThread

class HotkeySignaler(QObject):
    hotkey_activated = pyqtSignal() 

class SettingsTab(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.settings_thread = None
        self.current_hotkey = None
        self.current_hotkey2 = None
        self.none_hotkey = None
        self.katon_hotkey = None
        self.fuuton_hotkey = None
        self.raiton_hotkey = None
        self.doton_hotkey = None
        self.suiton_hotkey = None

        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        self.profile_listWidget = QListWidget(self)
        self.autoDashHot_lineEdit = QLineEdit(self)
        self.autoDashHot_lineEdit.setPlaceholderText("F1")
        self.autoDashModifier_comboBox = QComboBox(self)
        self.autoDashModifier_comboBox.addItems(["","Ctrl", "Shift"])
        self.autoDashModifier2_comboBox = QComboBox(self)
        self.autoDashModifier2_comboBox.addItems(["","Ctrl", "Shift"])
        self.toggleDash_checkBox = QCheckBox("OFF", self)
        self.toggleDash_checkBox.setFixedWidth(45)
        self.chaseEnemyModifier_comboBox = QComboBox(self)
        self.chaseEnemyModifier_comboBox.addItems(["","Ctrl", "Shift"])
        self.chaseEnemy_lineEdit = QLineEdit(self)
        self.chaseEnemy_lineEdit.setPlaceholderText("F1")
        self.chaseEnemy_checkBox = QCheckBox("OFF", self)
        self.chaseEnemy_checkBox.setFixedWidth(45)

        #naturki
        self.noNature_lineEdit = QLineEdit(self)
        self.noNature_lineEdit.setPlaceholderText("None")
        self.Katon_lineEdit = QLineEdit(self)
        self.Katon_lineEdit.setPlaceholderText("Katon")
        self.Fuuton_lineEdit = QLineEdit(self)
        self.Fuuton_lineEdit.setPlaceholderText("Fuuton")
        self.Raiton_lineEdit = QLineEdit(self)
        self.Raiton_lineEdit.setPlaceholderText("Raiton")
        self.Doton_lineEdit = QLineEdit(self)
        self.Doton_lineEdit.setPlaceholderText("Doton")
        self.Suiton_lineEdit = QLineEdit(self)
        self.Suiton_lineEdit.setPlaceholderText("Suiton")
        self.nature_checkBox = QCheckBox("OFF", self)
        self.nature_checkBox.setFixedWidth(45)

        self.profile_lineEdit = QLineEdit(self)
        self.takealldelay_lineEdit = QLineEdit(self)

        int_validator_1 = QIntValidator(0, 9999, self)
        self.takealldelay_lineEdit.setValidator(int_validator_1)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.set_environment()
        self.profileList()

        self.layout.addWidget(self.status_label, 2, 0, 1, 2)

        for file in os.listdir("Save/Settings"):
            if file.endswith(".json"):
                self.profile_listWidget.addItem(file.split('.')[0])

        self.signaler = HotkeySignaler()
        self.signaler.hotkey_activated.connect(self.toggleAutoDash)
        self.signaler2 = HotkeySignaler()
        self.signaler2.hotkey_activated.connect(self.chaseEnemy)
        self.signaler3 = HotkeySignaler()
        self.toggleDash_checkBox.stateChanged.connect(self.toggleDash)
        self.chaseEnemy_checkBox.stateChanged.connect(self.toggleChaseHot)
        self.nature_checkBox.stateChanged.connect(self.toggleNature)
        self.chaseEnemy_lineEdit.textChanged.connect(self.toggleChase)
        self.chaseEnemyModifier_comboBox.currentIndexChanged.connect(self.toggleChase)
        self.autoDashHot_lineEdit.textChanged.connect(self.toggleDash)
        self.autoDashModifier_comboBox.currentIndexChanged.connect(self.toggleDash)
        self.autoDashModifier2_comboBox.currentIndexChanged.connect(self.toggleDash)

        existing_names = [
            self.profile_listWidget.item(i).text()
            for i in range(self.profile_listWidget.count())
        ]
        if self.context.nickname in existing_names:
            self.profile_listWidget.setCurrentRow(existing_names.index(self.context.nickname))
            self.load_profile()

    def toggleDash(self):
        if self.toggleDash_checkBox.isChecked():
            self.setup_global_hotkey()
            self.toggleDash_checkBox.setText("ON")
        else:
            self.unregister_global_hotkey()
            self.toggleDash_checkBox.setChecked(False)
            self.toggleDash_checkBox.setText("OFF")

    def toggleNature(self):
        if self.nature_checkBox.isChecked():
            self.setup_nature_hotkeys()
            self.nature_checkBox.setText("ON")
        else:
            self.unregister_nature_hotkeys()
            self.nature_checkBox.setChecked(False)
            self.nature_checkBox.setText("OFF")

    def toggleChase(self):
        if self.chaseEnemy_checkBox.isChecked():
            self.unregister_global_hotkey2()
            self.chaseEnemy_checkBox.setChecked(False)
            self.chaseEnemy_checkBox.setText("OFF")

    def toggleChaseHot(self):
        if self.chaseEnemy_checkBox.isChecked():
            self.setup_global_hotkey2()
            self.chaseEnemy_checkBox.setText("ON")  
        else:
            self.unregister_global_hotkey2()
            self.chaseEnemy_checkBox.setChecked(False)
            self.chaseEnemy_checkBox.setText("OFF")

    def chaseEnemy(self):
        if self.context.combatControls[3] and win32gui.GetForegroundWindow() == self.context.hwnd:
            mouse_function(self.context.hwnd, self.context.combatControls[3][0], self.context.combatControls[3][1], option=2)

    def setup_global_hotkey(self):
        modifier = self.autoDashModifier_comboBox.currentText().lower()
        modifier2 = self.autoDashModifier2_comboBox.currentText().lower()
        key = self.autoDashHot_lineEdit.text().strip().lower()
        if modifier != "" and modifier == modifier2:
            self.toggleDash_checkBox.setChecked(False)
            return
        if modifier != "" and modifier2 == "" and key == "":
            hotkey_string = f"{modifier}"
        if modifier == "" and modifier2 != "" and key == "":
            hotkey_string = f"{modifier2}"
        if modifier == "" and modifier2 == "" and key != "":
            hotkey_string = f"{key}"
        if modifier == "" and modifier2 != "" and key != "":
            hotkey_string = f"{modifier2}+{key}"
        if modifier != "" and modifier2 != "" and key != "":
            hotkey_string = f"{modifier}+{modifier2}+{key}"
        if modifier != "" and modifier2 == "" and key != "":
            hotkey_string = f"{modifier}+{key}"
        if modifier == "" and modifier2 == "" and key == "":
            self.toggleDash_checkBox.setChecked(False)
            return

        self.unregister_global_hotkey() 
        def hotkey_callback():
            self.signaler.hotkey_activated.emit()

        try:
            self.current_hotkey = hotkey_string
            if self.current_hotkey == "":
                return
            keyboard.add_hotkey(self.current_hotkey, hotkey_callback)
        except Exception as e:
            self.status_label.setText(f"Failed to register hotkey '{self.current_hotkey}': {e}")
            self.toggleDash_checkBox.setChecked(False)
            self.current_hotkey = None


    def unregister_global_hotkey(self):
        if self.current_hotkey:
            try:
                keyboard.remove_hotkey(self.current_hotkey)
                #print(f"Unregistered previous hotkey: {self.current_hotkey}")
            except Exception as e:
                print(f"Warning: Error during unregistration: {e}")
        self.current_hotkey = None 

    def setup_global_hotkey2(self):
        modifier = self.chaseEnemyModifier_comboBox.currentText().lower()
        key = self.chaseEnemy_lineEdit.text().strip().lower()
        if modifier == "" and key != "":
            hotkey_string = f"{key}"
        if modifier != "" and key != "":
            hotkey_string = f"{modifier}+{key}"
        if modifier == "" and key == "":
            self.chaseEnemy_checkBox.setChecked(False)
            return

        self.unregister_global_hotkey2() 
        def hotkey_callback():
            self.signaler2.hotkey_activated.emit()

        try:
            self.current_hotkey2 = hotkey_string
            if self.current_hotkey2 == "":
                return
            keyboard.add_hotkey(self.current_hotkey2, hotkey_callback)
        except Exception as e:
            self.status_label.setText(f"Failed to register hotkey '{self.current_hotkey2}': {e}")
            self.chaseEnemy_checkBox.setChecked(False)
            self.current_hotkey2 = None


    def unregister_global_hotkey2(self):
        if self.current_hotkey2:
            try:
                keyboard.remove_hotkey(self.current_hotkey2)
            except Exception as e:
                print(f"Warning: Error during unregistration: {e}")
        self.current_hotkey2 = None 

    def setup_nature_hotkeys(self):
        self.none_hotkey = self.noNature_lineEdit.text().strip().lower()
        self.katon_hotkey = self.Katon_lineEdit.text().strip().lower()
        self.fuuton_hotkey = self.Fuuton_lineEdit.text().strip().lower()
        self.raiton_hotkey = self.Raiton_lineEdit.text().strip().lower()
        self.doton_hotkey = self.Doton_lineEdit.text().strip().lower()
        self.suiton_hotkey = self.Suiton_lineEdit.text().strip().lower()

        #self.unregister_nature_hotkeys()
        nature_hotkeys = [
            (self.none_hotkey, 0),
            (self.katon_hotkey, 1),
            (self.fuuton_hotkey, 2),
            (self.raiton_hotkey, 3),
            (self.doton_hotkey, 4),
            (self.suiton_hotkey, 5),
        ]

        for hotkey_str, index in nature_hotkeys:
            if hotkey_str != "":
                hotkey_function = lambda i=index: self.context.changeNature(i)
                keyboard.add_hotkey(hotkey_str, hotkey_function)


    def unregister_nature_hotkeys(self):
        # Create a list of all current hotkey strings held in class variables
        hotkey_list = [
            self.none_hotkey,
            self.katon_hotkey,
            self.fuuton_hotkey,
            self.raiton_hotkey,
            self.doton_hotkey,
            self.suiton_hotkey,
        ]
        
        for hotkey_str in hotkey_list:
            # Only try to unregister if the variable holds a non-empty, non-None value
            if hotkey_str: 
                try:
                    keyboard.remove_hotkey(hotkey_str)
                except Exception as e:
                    # This warning is expected if you try to remove an invalid hotkey
                    print(f"Warning: Error during unregistration of '{hotkey_str}': {e}")
        
        # Reset the class variables to None after attempting to unregister
        self.none_hotkey = None
        self.katon_hotkey = None
        self.fuuton_hotkey = None
        self.raiton_hotkey = None
        self.doton_hotkey = None
        self.suiton_hotkey = None

    def toggleAutoDash(self):
        if win32gui.GetForegroundWindow() == self.context.hwnd:
            if self.settings_thread == None:
                self.startSet_thread(2)
            else:
                self.settings_thread.stop()
                self.settings_thread = None

    def closeEvent(self, event):
        hotkey_list = [
            self.current_hotkey,
            self.current_hotkey2,
            self.none_hotkey,
            self.katon_hotkey,
            self.fuuton_hotkey,
            self.raiton_hotkey,
            self.doton_hotkey,
            self.suiton_hotkey,
        ]
        for hotkey_str in hotkey_list:
            if hotkey_str: 
                keyboard.remove_hotkey(hotkey_str)
        super().closeEvent(event)

    def set_environment(self) -> None:
        groupbox = QGroupBox("", self)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        update_windows_button = QPushButton("Update EQ / Inv Window Position", self)
        update_windows_button.setFixedHeight(22)
        update_windows_button.clicked.connect(self.context.updateGameUIcontrols)

        layout = QHBoxLayout()
        layout.addWidget(update_windows_button)

        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel("TakeAll Delay: ", self))
        layout1.addWidget(self.takealldelay_lineEdit)

        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel("Dash Shortcut: ", self))
        layout2.addWidget(self.autoDashModifier_comboBox)
        layout2.addWidget(self.autoDashModifier2_comboBox)
        layout2.addWidget(self.autoDashHot_lineEdit)
        layout2.addWidget(self.toggleDash_checkBox)

        layout3 = QHBoxLayout()
        layout3.addWidget(QLabel("Chase Enemy Shortcut: ", self))
        layout3.addWidget(self.chaseEnemyModifier_comboBox)
        layout3.addWidget(self.chaseEnemy_lineEdit)
        layout3.addWidget(self.chaseEnemy_checkBox)

        layout4 = QHBoxLayout()
        layout4.addWidget(QLabel("Chakra Nature Change Hotkeys ", self))
        layout4.addWidget(self.nature_checkBox)

        layout5 = QHBoxLayout()
        layout5.addWidget(self.noNature_lineEdit)
        layout5.addWidget(self.Katon_lineEdit)
        layout5.addWidget(self.Fuuton_lineEdit)

        layout6 = QHBoxLayout()
        layout6.addWidget(self.Raiton_lineEdit)
        layout6.addWidget(self.Doton_lineEdit)
        layout6.addWidget(self.Suiton_lineEdit)
        
        self.takealldelay_lineEdit.setText(str(self.context.takeAllDelay))

        #groupbox_layout.addWidget(set_loot_screen_button)
        #groupbox_layout.addWidget(set_firstEQpreset_button)
        groupbox_layout.addLayout(layout)
        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        groupbox_layout.addLayout(layout3)
        groupbox_layout.addLayout(layout4)
        groupbox_layout.addLayout(layout5)
        groupbox_layout.addLayout(layout6)

        self.layout.addWidget(groupbox, 0, 0)

    def profileList(self) -> None:
        groupbox = QGroupBox("Save && Load", self)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        save_button = QPushButton("Save", self)
        load_button = QPushButton("Load", self)

        save_button.clicked.connect(self.save_profile)
        load_button.clicked.connect(self.load_profile)

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        layout1.addWidget(QLabel("Name:", self))
        layout1.addWidget(self.profile_lineEdit)
        layout2.addWidget(save_button)
        layout2.addWidget(load_button)

        groupbox_layout.addWidget(self.profile_listWidget)
        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)

        self.layout.addWidget(groupbox, 1, 0)

    def save_profile(self) -> None:
        profile_name = self.profile_lineEdit.text().strip()
        if not profile_name:
            return
        settings_data = {
            "takeAllX": self.context.takeAll_x,
            "takeAllY": self.context.takeAll_y,
            "takeAllcolorR": self.context.takeAllcolorR,
            "takeAllcolorG": self.context.takeAllcolorG,
            "takeAllcolorB": self.context.takeAllcolorB,
            "takeAllDelay": self.takealldelay_lineEdit.text().strip(),
            "eqSetX": self.context.eqSetX,
            "eqSetY": self.context.eqSetY,
            "dashHotModifier": self.autoDashModifier_comboBox.currentIndex(),
            "dashHotModifier2": self.autoDashModifier2_comboBox.currentIndex(),
            "dashHotkey": self.autoDashHot_lineEdit.text().strip(),
            "chaseHotModifier": self.chaseEnemyModifier_comboBox.currentIndex(),
            "chaseHotkey": self.chaseEnemy_lineEdit.text().strip(),
            "noNatureHot":  self.noNature_lineEdit.text().strip().lower(),
            "katonHot":  self.Katon_lineEdit.text().strip().lower(),
            "fuutonHot":  self.Fuuton_lineEdit.text().strip().lower(),
            "raitonHot":  self.Raiton_lineEdit.text().strip().lower(),
            "dotonHot":  self.Doton_lineEdit.text().strip().lower(),
            "suitonHot":  self.Suiton_lineEdit.text().strip().lower(),
        }
        data_to_save = {"settings_data": settings_data}

        if manage_profile("save", "Save/Settings", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")
            existing_names = [
                self.profile_listWidget.item(i).text()
                for i in range(self.profile_listWidget.count())
            ]
            if profile_name not in existing_names:
                self.profile_listWidget.addItem(profile_name)

    def load_profile(self) -> None:
        profile_name = self.profile_listWidget.currentItem()
        if not profile_name:
            self.profile_listWidget.setStyleSheet("border: 2px solid red;")
            self.status_label.setText("Please select a profile from the list to load.")
            return
        else:
            self.profile_listWidget.setStyleSheet("")

        profile_name = profile_name.text()
        filename = f"Save/Settings/{profile_name}.json"
        with open(filename, "r") as f:
            loaded_data = json.load(f)

        settings_data = loaded_data.get("settings_data", {})
        self.context.takeAll_x = settings_data.get("takeAllX", 0)
        self.context.takeAll_y = settings_data.get("takeAllY", 0)
        self.context.takeAllcolorR = settings_data.get("takeAllcolorR", 0)
        self.context.takeAllcolorG = settings_data.get("takeAllcolorG", 0)
        self.context.takeAllcolorB = settings_data.get("takeAllcolorB", 0)
        self.context.takeAllDelay = settings_data.get("takeAllDelay", 0)
        self.context.eqSetX = settings_data.get("eqSetX", 0)
        self.context.eqSetY = settings_data.get("eqSetY", 0)
        self.takealldelay_lineEdit.setText(str(self.context.takeAllDelay))
        self.autoDashModifier_comboBox.setCurrentIndex(int(settings_data.get("dashHotModifier", 0)))
        self.autoDashModifier2_comboBox.setCurrentIndex(int(settings_data.get("dashHotModifier2", 0)))
        self.autoDashHot_lineEdit.setText(str(settings_data.get("dashHotkey", 0)))
        self.chaseEnemyModifier_comboBox.setCurrentIndex(int(settings_data.get("chaseHotModifier", 0)))
        self.chaseEnemy_lineEdit.setText(str(settings_data.get("chaseHotkey", 0)))
        self.noNature_lineEdit.setText(str(settings_data.get("noNatureHot", 0)))
        self.Katon_lineEdit.setText(str(settings_data.get("katonHot", 0)))
        self.Fuuton_lineEdit.setText(str(settings_data.get("fuutonHot", 0)))
        self.Raiton_lineEdit.setText(str(settings_data.get("raitonHot", 0)))
        self.Doton_lineEdit.setText(str(settings_data.get("dotonHot", 0)))
        self.Suiton_lineEdit.setText(str(settings_data.get("suitonHot", 0)))

        self.profile_lineEdit.clear()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")

    def startSet_thread(self, index) -> None:
        self.settings_thread = SettingsThread(self.context, index, self.status_label, self.takealldelay_lineEdit.text().strip())
        self.settings_thread.start()
