import json, os
from PyQt5.QtWidgets import (QWidget, QCheckBox, QComboBox, QLineEdit, QListWidget, QGridLayout, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QListWidgetItem, QFormLayout, QSizePolicy)
from PyQt5.QtGui import QPixmap, QIntValidator
from PyQt5.QtCore import Qt
from NameSkinThread import NameThread, SkinThread
from GeneralFunctions import delete_item, manage_profile
from MemoryFunctions import *

class NameSkinTab(QWidget):

    def __init__(self, context):
        super().__init__()

        # Thread Variables
        self.context = context
        self.skin_thread = None
        self.name_thread = None
        self.skinID = 0
        self.skinOffset = 0
        if self.context.debug == False:
            self.skinID = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_skinID_offset, 1, label="skinID")
            self.skinOffset = read_direct(self.context.process_handle, self.context.playerPointer, self.context.Addresses.my_skin_offset, 1, label="skinOffset")

        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Check Boxes
        self.startName_checkBox = QCheckBox("Start Nick Changer", self)
        self.startSetChanger_checkBox = QCheckBox("Start Skin Changer", self)

        # Line Edits
        self.name_lineEdit = QLineEdit(self)

        # Attack
        self.skinID_lineEdit = QLineEdit(self)
        self.skinOffset_comboBox = QComboBox(self)
        self.skinOffset_comboBox.addItems(["0", "1", "2", "3"])
        if self.skinOffset:
            self.skinOffset_comboBox.setCurrentIndex(int(self.skinOffset))
        self.profile_lineEdit = QLineEdit(self)

        int_validator_1 = QIntValidator(0, 9999, self)

        self.skinID_lineEdit.setValidator(int_validator_1)
        self.name_lineEdit.setMaxLength(len(self.context.nickname))

        # List Widgets
        self.profile_listWidget = QListWidget(self)

        # Layout
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

        # Initialize sections
        self.namechange()
        self.skinchange()
        self.profileList()
        self.layout.addWidget(self.status_label, 3, 0, 1, 2)

        for file in os.listdir("Save/NameSkin"):
            if file.endswith(".json"):
                self.profile_listWidget.addItem(file.split('.')[0])

        existing_names = [
            self.profile_listWidget.item(i).text()
            for i in range(self.profile_listWidget.count())
        ]
        if self.context.nickname in existing_names:
            self.profile_listWidget.setCurrentRow(existing_names.index(self.context.nickname))
            self.load_profile()

    def namechange(self) -> None:
        groupbox = QGroupBox("Nickname Changer")
        groupbox_layout = QHBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # CheckBox function
        self.startName_checkBox.stateChanged.connect(self.startName_thread)
        self.name_lineEdit.textChanged.connect(lambda: self.updateName(self.name_lineEdit.text().strip()))
        # Layouts
        groupbox2_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        # Add Widgets
        layout1.addWidget(QLabel("Nickname:  ", self))

        layout1.addWidget(self.name_lineEdit)
        layout2.addWidget(self.startName_checkBox)

        self.name_lineEdit.setPlaceholderText(self.context.nickname)

        groupbox2_layout.addLayout(layout1)
        groupbox2_layout.addLayout(layout2)

        groupbox_layout.addLayout(groupbox2_layout)
        self.layout.addWidget(groupbox, 0, 0, 1, 2)

    def updateName(self, newName) -> None:
        #print(newName)
        if self.name_thread:
            self.name_thread.update_name(newName)

    def skinchange(self) -> None:
        groupbox = QGroupBox("Skin Changer")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # CheckBox function
        self.startSetChanger_checkBox.stateChanged.connect(self.start_Skin_thread)
        self.skinOffset_comboBox.currentIndexChanged.connect(lambda: self.updateSkinID(0))

        plus_button = QPushButton("+")
        plus_button.clicked.connect(lambda: self.updateSkinID(1))
        minus_button = QPushButton("-")
        minus_button.clicked.connect(lambda: self.updateSkinID(-1))

        # Layouts
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        layout1.addWidget(QLabel("Skin ID: ", self), alignment=Qt.AlignLeft)
        layout1.addWidget(self.skinID_lineEdit)
        layout1.addWidget(QLabel("Skin Offset: ", self), alignment=Qt.AlignLeft)
        layout1.addWidget(self.skinOffset_comboBox)

        self.skinID_lineEdit.setText(str(self.skinID))
        layout2.addWidget(self.startSetChanger_checkBox)
        layout2.addWidget(plus_button)
        layout2.addWidget(minus_button)

        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        self.layout.addWidget(groupbox, 1, 0, 1, 2)

    def updateSkinID(self, newID) -> None:
        newskin = int(self.skinID_lineEdit.text().strip()) + newID
        self.skinID_lineEdit.setText(str(newskin))
        if self.skin_thread:
            self.skin_thread.update_skin(newskin,self.skinOffset_comboBox.currentIndex())

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
            "Skin": self.skinID_lineEdit.text().strip(),
            "SkinOffset": self.skinOffset_comboBox.currentIndex(),
            "Name": self.name_lineEdit.text().strip()
        }
        data_to_save = {
            "name_skin": data,
        }

        if manage_profile("save", "Save/NameSkin", profile_name, data_to_save):
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
        filename = f"Save/NameSkin/{profile_name}.json"

        with open(filename, "r") as f:
            loaded_data = json.load(f)

        data = loaded_data.get("name_skin", {})

        if data:
            name = data.get("Name", "")
            self.name_lineEdit.setText(name)
            self.skinID_lineEdit.setText(str(data.get("Skin", "")))
            self.skinOffset_comboBox.setCurrentIndex(data.get("SkinOffset", 0))

        self.profile_lineEdit.clear()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")

    def startName_thread(self, state) -> None:
        if state == Qt.Checked:
            if not self.name_thread:
                self.name_thread = NameThread(self.name_lineEdit.text().strip(), self.context)
                self.name_thread.start()
        else:
            if self.name_thread:
                self.name_thread.stop()
                self.name_thread = None

    def start_Skin_thread(self, state) -> None:
        if state == Qt.Checked:
            if not self.skin_thread:
                self.skin_thread = SkinThread(int(self.skinID_lineEdit.text().strip()), self.skinOffset_comboBox.currentIndex(), self.context)
                self.skin_thread.start()
        else:
            if self.skin_thread:
                self.skin_thread.stop(self.skinID,self.skinOffset)
                self.skinID_lineEdit.setText(str(self.skinID))
                self.skinOffset_comboBox.setCurrentIndex(self.skinOffset)
                self.skin_thread = None
