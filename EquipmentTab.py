import json, os
import win32api
import win32gui
from win32con import VK_LBUTTON
from PyQt5.QtWidgets import (QWidget, QCheckBox, QComboBox, QLineEdit, QListWidget, QGridLayout, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
from EquipmentThread import EquipmentThread, MoneyChangerThread
from GeneralFunctions import *
from MemoryFunctions import *
from KeyboardFunctions import *
from MouseFunctions import *

class EquipmentTab(QWidget):

    def __init__(self, context):
        super().__init__()

        # Thread Variables
        self.context = context

        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.eq_thread = None
        self.money_thread = None

        self.setOffsetLow_comboBox = QComboBox(self)
        self.setOffsetLow_comboBox.addItems(["1", "2", "3", "4"])
        self.setOffsetHigh_comboBox = QComboBox(self)
        self.setOffsetHigh_comboBox.addItems(["1", "2", "3", "4"])

        # Check Boxes
        self.startSetChanger_checkBox = QCheckBox("Start Set Changer", self)
        self.startMoneyChanger_checkBox = QCheckBox("Start Money Changer", self)

        # Line Edits
        self.lowHP_lineEdit = QLineEdit(self)
        self.highHP_lineEdit = QLineEdit(self)
        self.profile_lineEdit = QLineEdit(self)
        int_validator_1 = QIntValidator(0, 2000, self)
        self.lowHP_lineEdit.setValidator(int_validator_1)
        self.highHP_lineEdit.setValidator(int_validator_1)

        # List Widgets
        self.profile_listWidget = QListWidget(self)

        # Layout
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

        # Initialize sections
        self.EQchange()
        self.profileList()
        self.layout.addWidget(self.status_label, 3, 0, 1, 2)

        for file in os.listdir("Save/Equipment"):
            if file.endswith(".json"):
                self.profile_listWidget.addItem(file.split('.')[0])

        existing_names = [
            self.profile_listWidget.item(i).text()
            for i in range(self.profile_listWidget.count())
        ]
        if self.context.nickname in existing_names:
            self.profile_listWidget.setCurrentRow(existing_names.index(self.context.nickname))
            self.load_profile()

    def updateName(self, newName) -> None:
        #print(newName)
        if self.name_thread:
            self.name_thread.update_name(newName)

    def EQchange(self) -> None:
        groupbox = QGroupBox("EQ Set Changer")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # CheckBox function
        self.startSetChanger_checkBox.stateChanged.connect(self.start_EQ_thread)
        self.startMoneyChanger_checkBox.stateChanged.connect(self.start_money_thread)

        # Layouts
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()

        update_button = QPushButton("Update Values")
        update_button.clicked.connect(lambda: self.updateVars)

        layout1.addWidget(QLabel("Low HP %:  ", self), alignment=Qt.AlignLeft)
        layout1.addWidget(self.lowHP_lineEdit)
        layout1.addWidget(QLabel("Set Nr.:", self), alignment=Qt.AlignLeft)
        layout1.addWidget(self.setOffsetLow_comboBox)
        layout2.addWidget(QLabel("High HP %: ", self), alignment=Qt.AlignLeft)
        layout2.addWidget(self.highHP_lineEdit)
        layout2.addWidget(QLabel("Set Nr.:", self), alignment=Qt.AlignLeft)
        layout2.addWidget(self.setOffsetHigh_comboBox)

        layout3.addWidget(self.startSetChanger_checkBox)
        layout3.addWidget(update_button)
        layout4.addWidget(self.startMoneyChanger_checkBox)

        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        groupbox_layout.addLayout(layout3)
        groupbox_layout.addLayout(layout4)
        self.layout.addWidget(groupbox, 1, 0, 1, 2)

    def updateVars(self) -> None:
        if self.eq_thread:
            self.eq_thread.update_vars(int(self.lowHP_lineEdit.text().strip()), int(self.highHP_lineEdit.text().strip()), self.setOffsetLow_comboBox.currentIndex(), self.setOffsetHigh_comboBox.currentIndex())

    def profileList(self) -> None:
        groupbox = QGroupBox("Save && Load")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Buttons
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_profile)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_profile)

        # Layouts
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        layout1.addWidget(QLabel("Name:", self))
        layout1.addWidget(self.profile_lineEdit)
        layout2.addWidget(save_button)
        layout2.addWidget(load_button)

        groupbox_layout.addWidget(self.profile_listWidget)
        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        self.layout.addWidget(groupbox, 2, 0)

    def save_profile(self):
        profile_name = self.profile_lineEdit.text().strip()
        if not profile_name:
            return
        data = {
            "Low_HP_Percent": self.lowHP_lineEdit.text().strip(),
            "High_HP_Percent": self.highHP_lineEdit.text().strip(),
            "Low_SetNr": self.setOffsetLow_comboBox.currentIndex(),
            "High_SetNr": self.setOffsetHigh_comboBox.currentIndex()
        }
        data_to_save = {
            "eq_changer": data,
        }

        if manage_profile("save", "Save/Equipment", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")
            existing_names = [
                self.profile_listWidget.item(i).text()
                for i in range(self.profile_listWidget.count())
            ]
            if profile_name not in existing_names:
                self.profile_listWidget.addItem(profile_name)

    def load_profile(self):
        profile_name = self.profile_listWidget.currentItem()
        if not profile_name:
            self.profile_listWidget.setStyleSheet("border: 2px solid red;")
            self.status_label.setText("Please select a profile from the list.")
            return
        else:
            self.profile_listWidget.setStyleSheet("")
        profile_name = profile_name.text()
        filename = f"Save/Equipment/{profile_name}.json"

        with open(filename, "r") as f:
            loaded_data = json.load(f)

        data = loaded_data.get("eq_changer", {})

        if data:
            self.lowHP_lineEdit.setText(data.get("Low_HP_Percent", 0))
            self.highHP_lineEdit.setText(data.get("High_HP_Percent", 0))
            self.setOffsetLow_comboBox.setCurrentIndex(int(data.get("Low_SetNr", 0)))
            self.setOffsetHigh_comboBox.setCurrentIndex(int(data.get("High_SetNr", 0)))

        self.profile_lineEdit.clear()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")

    def start_EQ_thread(self, state) -> None:
        if state == Qt.Checked:
            if not self.eq_thread:
                self.eq_thread = EquipmentThread(int(self.lowHP_lineEdit.text().strip()), self.setOffsetLow_comboBox.currentIndex(), int(self.highHP_lineEdit.text().strip()), self.setOffsetHigh_comboBox.currentIndex(), self.context)
                self.eq_thread.start()
        else:
            if self.eq_thread:
                self.eq_thread.stop()
                self.eq_thread = None

    def start_money_thread(self, state) -> None:
        if state == Qt.Checked:
            if not self.money_thread:
                self.money_thread = MoneyChangerThread(self.context)
                self.money_thread.start()
        else:
            if self.money_thread:
                self.money_thread.stop()
                self.money_thread = None
