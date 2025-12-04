import json
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QGroupBox,
    QGridLayout, QPushButton, QListWidget, QComboBox, QCheckBox
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import Qt, QThread
import keyboard
import os
import keyboard._keyboard_tests
import win32gui
from GeneralFunctions import manage_profile
from context import *
from MemoryFunctions import *
from KeyboardFunctions import *
from MouseFunctions import *

class HotkeySignaler(QObject):
    hotkey_activated = pyqtSignal() 

class ComboTab(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.current_hotkey = None
        self.target_id = 0
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        self.profile_listWidget = QListWidget(self)
        self.Combo1Hot_lineEdit = QLineEdit(self)
        self.Combo1Modifier_comboBox = QComboBox(self)
        self.Combo1Modifier_comboBox.addItems(["","Ctrl", "Shift"])
        self.Combo1Modifier2_comboBox = QComboBox(self)
        self.Combo1Modifier2_comboBox.addItems(["","Ctrl", "Shift"])
        self.targetON_checkBox = QCheckBox("Target", self)
        self.startCombo_checkBox = QCheckBox("Start Combo", self)

        int_validator_1 = QIntValidator(0, 29999, self)
        self.profile_lineEdit = QLineEdit(self)
        #Combo1
        self.C1Hot1delay_lineEdit = QLineEdit(self)
        self.C1Hot1delay_lineEdit.setValidator(int_validator_1)
        self.C1Hot1delay_lineEdit.setPlaceholderText("Delay")
        self.C1Hot2delay_lineEdit = QLineEdit(self)
        self.C1Hot2delay_lineEdit.setValidator(int_validator_1)
        self.C1Hot2delay_lineEdit.setPlaceholderText("Delay")
        self.C1Hot3delay_lineEdit = QLineEdit(self)
        self.C1Hot3delay_lineEdit.setValidator(int_validator_1)
        self.C1Hot3delay_lineEdit.setPlaceholderText("Delay")
        self.C1Hot4delay_lineEdit = QLineEdit(self)
        self.C1Hot4delay_lineEdit.setValidator(int_validator_1)
        self.C1Hot4delay_lineEdit.setPlaceholderText("Delay")
        self.C1Hot5delay_lineEdit = QLineEdit(self)
        self.C1Hot5delay_lineEdit.setValidator(int_validator_1)
        self.C1Hot5delay_lineEdit.setPlaceholderText("Delay")
        self.C1Hot6delay_lineEdit = QLineEdit(self)
        self.C1Hot6delay_lineEdit.setValidator(int_validator_1)
        self.C1Hot6delay_lineEdit.setPlaceholderText("Delay")
        self.C1Hot7delay_lineEdit = QLineEdit(self)
        self.C1Hot7delay_lineEdit.setValidator(int_validator_1)
        self.C1Hot7delay_lineEdit.setPlaceholderText("Delay")

        #----------------
        self.C1Hot1_lineEdit = QLineEdit(self)
        self.C1Hot1_lineEdit.setPlaceholderText("Hot1")
        self.C1Hot2_lineEdit = QLineEdit(self)
        self.C1Hot2_lineEdit.setPlaceholderText("Hot2")
        self.C1Hot3_lineEdit = QLineEdit(self)
        self.C1Hot3_lineEdit.setPlaceholderText("Hot3")
        self.C1Hot4_lineEdit = QLineEdit(self)
        self.C1Hot4_lineEdit.setPlaceholderText("Hot4")
        self.C1Hot5_lineEdit = QLineEdit(self)
        self.C1Hot5_lineEdit.setPlaceholderText("Hot5")
        self.C1Hot6_lineEdit = QLineEdit(self)
        self.C1Hot6_lineEdit.setPlaceholderText("Hot6")
        self.C1Hot7_lineEdit = QLineEdit(self)
        self.C1Hot7_lineEdit.setPlaceholderText("Hot7")
        self.C1Hot8_lineEdit = QLineEdit(self)
        self.C1Hot8_lineEdit.setPlaceholderText("Hot8")

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.combo1()
        self.profileList()

        self.layout.addWidget(self.status_label, 2, 0, 1, 2)

        for file in os.listdir("Save/Combos"):
            if file.endswith(".json"):
                self.profile_listWidget.addItem(file.split('.')[0])

        self.signaler = HotkeySignaler()
        if win32gui.GetForegroundWindow() == self.context.hwnd:
            self.signaler.hotkey_activated.connect(self.toggleCombo1)
        self.startCombo_checkBox.stateChanged.connect(self.startCombo)
        existing_names = [
            self.profile_listWidget.item(i).text()
            for i in range(self.profile_listWidget.count())
        ]
        if self.context.nickname in existing_names:
            self.profile_listWidget.setCurrentRow(existing_names.index(self.context.nickname))
            self.load_profile()

        self.Combo1Modifier_comboBox.currentIndexChanged.connect(self.startCombo)
        self.Combo1Modifier2_comboBox.currentIndexChanged.connect(self.startCombo)
        self.Combo1Hot_lineEdit.textChanged.connect(self.startCombo)

    def startCombo(self):
        if self.startCombo_checkBox.isChecked():
            self.setup_global_hotkey()
        else:
            self.unregister_global_hotkey()
            self.startCombo_checkBox.setChecked(False)

    def setup_global_hotkey(self):
        modifier = self.Combo1Modifier_comboBox.currentText().lower()
        modifier2 = self.Combo1Modifier2_comboBox.currentText().lower()
        key = self.Combo1Hot_lineEdit.text().strip().lower()
        if modifier != "" and modifier == modifier2:
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
            self.startCombo_checkBox.setChecked(False)
            self.current_hotkey = None


    def unregister_global_hotkey(self):
        if self.current_hotkey:
            try:
                keyboard.remove_hotkey(self.current_hotkey)
            except Exception as e:
                print(f"Warning: Error during unregistration: {e}")
        self.current_hotkey = None 

    def toggleCombo1(self):
        QThread.msleep(100)
        self.target_id = read_targeting_status(self.context.process_handle, self.context)
        if (self.targetON_checkBox.isChecked() and self.target_id != 0) or (not self.targetON_checkBox.isChecked() and self.target_id == 0):
            QThread.msleep(100)
            press_key(self.context.hwnd, self.C1Hot1_lineEdit.text().strip())
            if self.C1Hot1delay_lineEdit.text():
                QThread.msleep(int(self.C1Hot1delay_lineEdit.text().strip()))
                press_key(self.context.hwnd, self.C1Hot2_lineEdit.text().strip())
            if self.C1Hot2delay_lineEdit.text():
                QThread.msleep(int(self.C1Hot2delay_lineEdit.text().strip()))
                press_key(self.context.hwnd, self.C1Hot3_lineEdit.text().strip())           
            if self.C1Hot3delay_lineEdit.text():
                QThread.msleep(int(self.C1Hot3delay_lineEdit.text().strip()))
                press_key(self.context.hwnd, self.C1Hot4_lineEdit.text().strip())            
            if self.C1Hot4delay_lineEdit.text():
                QThread.msleep(int(self.C1Hot4delay_lineEdit.text().strip()))
                press_key(self.context.hwnd, self.C1Hot5_lineEdit.text().strip())           
            if self.C1Hot5delay_lineEdit.text():
                QThread.msleep(int(self.C1Hot5delay_lineEdit.text().strip()))
                press_key(self.context.hwnd, self.C1Hot6_lineEdit.text().strip())
            if self.C1Hot6delay_lineEdit.text():
                QThread.msleep(int(self.C1Hot6delay_lineEdit.text().strip()))
                press_key(self.context.hwnd, self.C1Hot7_lineEdit.text().strip())
            if self.C1Hot7delay_lineEdit.text():
                QThread.msleep(int(self.C1Hot7delay_lineEdit.text().strip()))
                press_key(self.context.hwnd, self.C1Hot8_lineEdit.text().strip())

    def closeEvent(self, event):
        keyboard.remove_hotkey(self.current_hotkey)
        super().closeEvent(event)

    def combo1(self) -> None:
        groupbox = QGroupBox("Combo", self)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()

        layout1.addWidget(self.C1Hot1_lineEdit)
        layout1.addWidget(self.C1Hot1delay_lineEdit)
        layout1.addWidget(self.C1Hot2_lineEdit)
        layout1.addWidget(self.C1Hot2delay_lineEdit)
        layout1.addWidget(self.C1Hot3_lineEdit)
        layout1.addWidget(self.C1Hot3delay_lineEdit)
        layout2.addWidget(self.C1Hot4_lineEdit)
        layout2.addWidget(self.C1Hot4delay_lineEdit)
        layout2.addWidget(self.C1Hot5_lineEdit)
        layout2.addWidget(self.C1Hot5delay_lineEdit)
        layout2.addWidget(self.C1Hot6_lineEdit)
        layout2.addWidget(self.C1Hot6delay_lineEdit)
        layout3.addWidget(self.C1Hot7_lineEdit)
        layout3.addWidget(self.C1Hot7delay_lineEdit)
        layout3.addWidget(self.C1Hot8_lineEdit)

        layout3.addWidget(self.targetON_checkBox)
        layout3.addWidget(self.startCombo_checkBox)

        layout4.addWidget(QLabel("Combo Shortcut: ", self))
        layout4.addWidget(self.Combo1Modifier_comboBox)
        layout4.addWidget(self.Combo1Modifier2_comboBox)
        layout4.addWidget(self.Combo1Hot_lineEdit)

        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        groupbox_layout.addLayout(layout3)
        groupbox_layout.addLayout(layout4)

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
        combo_data = {
            "hot1": self.C1Hot1_lineEdit.text().strip(),
            "hot1delay": self.C1Hot1delay_lineEdit.text().strip(),
            "hot2": self.C1Hot2_lineEdit.text().strip(),
            "hot2delay": self.C1Hot2delay_lineEdit.text().strip(),
            "hot3": self.C1Hot3_lineEdit.text().strip(),
            "hot3delay": self.C1Hot3delay_lineEdit.text().strip(),
            "hot4": self.C1Hot4_lineEdit.text().strip(),
            "hot4delay": self.C1Hot4delay_lineEdit.text().strip(),
            "hot5": self.C1Hot5_lineEdit.text().strip(),
            "hot5delay": self.C1Hot5delay_lineEdit.text().strip(),
            "hot6": self.C1Hot6_lineEdit.text().strip(),
            "hot6delay": self.C1Hot6delay_lineEdit.text().strip(),
            "hot7": self.C1Hot7_lineEdit.text().strip(),
            "hot7delay": self.C1Hot7delay_lineEdit.text().strip(),
            "hot8": self.C1Hot8_lineEdit.text().strip(),
            "modifier": self.Combo1Modifier_comboBox.currentIndex(),
            "modifier2": self.Combo1Modifier2_comboBox.currentIndex(),
            "comboHot": self.Combo1Hot_lineEdit.text().strip().lower(),
            "onTarget": self.targetON_checkBox.isChecked()
        }
        data_to_save = {"combo_data": combo_data}

        if manage_profile("save", "Save/Combos", profile_name, data_to_save):
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
        filename = f"Save/Combos/{profile_name}.json"
        with open(filename, "r") as f:
            loaded_data = json.load(f)

        combo_data = loaded_data.get("combo_data", {})

        self.C1Hot1_lineEdit.setText(combo_data.get("hot1", 0))
        self.C1Hot1delay_lineEdit.setText(combo_data.get("hot1delay", 0))
        self.C1Hot2_lineEdit.setText(combo_data.get("hot2", 0))
        self.C1Hot2delay_lineEdit.setText(combo_data.get("hot2delay", 0))
        self.C1Hot3_lineEdit.setText(combo_data.get("hot3", 0))
        self.C1Hot3delay_lineEdit.setText(combo_data.get("hot3delay", 0))
        self.C1Hot4_lineEdit.setText(combo_data.get("hot4", 0))
        self.C1Hot4delay_lineEdit.setText(combo_data.get("hot4delay", 0))
        self.C1Hot5_lineEdit.setText(combo_data.get("hot5", 0))
        self.C1Hot5delay_lineEdit.setText(combo_data.get("hot5delay", 0))
        self.C1Hot6_lineEdit.setText(combo_data.get("hot6", 0))
        self.C1Hot6delay_lineEdit.setText(combo_data.get("hot6delay", 0))
        self.C1Hot7_lineEdit.setText(combo_data.get("hot7", 0))
        self.C1Hot7delay_lineEdit.setText(combo_data.get("hot7delay", 0))
        self.C1Hot8_lineEdit.setText(combo_data.get("hot8", 0))
        self.targetON_checkBox.setChecked(combo_data.get("onTarget", 0))
        self.Combo1Hot_lineEdit.setText(combo_data.get("comboHot", 0))
        self.Combo1Modifier_comboBox.setCurrentIndex(combo_data.get("modifier", 0))
        self.Combo1Modifier2_comboBox.setCurrentIndex(combo_data.get("modifier2", 0))

        self.profile_lineEdit.clear()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")

