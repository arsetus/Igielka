import os
import json
from GeneralFunctions import delete_item, manage_profile
from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QComboBox, QLineEdit, QListWidget, QGridLayout,
    QGroupBox, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidgetItem
)
from PyQt5.QtCore import Qt
from TargetLootThread import TargetThread, LootThread, SparringThread, CollectorThread, JumpThread, TakeAllThread, TurnToMonsterThread


class TargetLootTab(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context   # 👈 store context here
        self.target_thread = None
        self.loot_thread = None
        self.jump_thread = None
        self.sparring_thread = None
        self.collector_thread = None
        self.takeall_thread = None
        self.autoTurn_thread = None

        # --- Status "bar" label at the bottom
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Check Boxes
        self.takeAllOnly_checkBox = QCheckBox("TakeAll", self)
        self.takeAllOnly_checkBox.stateChanged.connect(self.start_takeall_thread)
        self.startLoot_checkBox = QCheckBox("Looting", self)
        self.startLoot_checkBox.stateChanged.connect(self.start_loot_thread)
        self.startTarget_checkBox = QCheckBox("Targeting", self)
        self.startTarget_checkBox.stateChanged.connect(self.start_target_thread)
        self.sparring_checkBox = QCheckBox("Sparring", self)
        self.sparring_checkBox.stateChanged.connect(self.start_autoSparring)
        self.startJar_checkBox = QCheckBox("Auto Jar", self)
        self.startJar_checkBox.stateChanged.connect(self.start_autoJar)
        self.autoJump_checkBox = QCheckBox("AutoJump", self)
        self.autoJump_checkBox.stateChanged.connect(self.start_autoJump)
        self.autoTurn_checkBox = QCheckBox("Auto Turn", self)
        self.autoTurn_checkBox.stateChanged.connect(self.start_autoTurn)

        # Combo Boxes
        self.attackDist_comboBox = QComboBox(self)
        self.attackDist_comboBox.addItems(["All", "1", "2", "3", "4", "5", "6", "7"])
        self.sparKey_comboBox = QComboBox(self)
        self.sparKey_comboBox.addItems(f'F{i}' for i in range(1, 13))
        self.jarKey_comboBox = QComboBox(self)
        self.jarKey_comboBox.addItems(f'F{i}' for i in range(1, 13))
        #self.attackKey_comboBox = QComboBox(self)
        #self.attackKey_comboBox.addItems(["F"])
        #self.attackKey_comboBox.addItems(f'F{i}' for i in range(1, 13))


        # Line Edits
        self.profile_lineEdit = QLineEdit(self)
        self.targetName_lineEdit = QLineEdit(self)
        self.sparDelay_lineEdit = QLineEdit(self)
        self.autoJumpPercent_lineEdit = QLineEdit(self)

        # List Widgets
        self.profile_listWidget = QListWidget(self)
        self.targetList_listWidget = QListWidget(self)
        self.targetList_listWidget.setFixedSize(180, 50)
        self.profile_listWidget.setFixedSize(180, 50)

        # Main Layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.controlList()
        self.profileList()

        self.layout.addWidget(self.status_label, 3, 0, 1, 2)

    def controlList(self) -> None:
        groupbox = QGroupBox("Controls", self)
        groupbox_layout = QHBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Layouts
        groupbox2_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()
        layout1.addWidget(QLabel("Auto Sparring Hotkey:", self))
        layout1.addWidget(self.sparKey_comboBox)
        layout1.addWidget(QLabel("Jar Hotkey:", self))
        layout1.addWidget(self.jarKey_comboBox)
        layout2.addWidget(QLabel("Auto Sparring Delay:", self))
        layout2.addWidget(self.sparDelay_lineEdit)
        layout2.addWidget(self.sparring_checkBox)

        #layout3.addWidget(QLabel("Attack Key:", self))
        #layout3.addWidget(self.attackKey_comboBox)

        layout3.addWidget(QLabel("Auto Jump HP %:", self))
        self.autoJumpPercent_lineEdit.setText(str(70))
        layout3.addWidget(self.autoJumpPercent_lineEdit)

        layout3.addWidget(QLabel("Attack Dist:", self))
        layout3.addWidget(self.attackDist_comboBox)
        layout4.addWidget(self.startTarget_checkBox)
        layout4.addWidget(self.startLoot_checkBox)
        layout4.addWidget(self.startJar_checkBox)
        layout5.addWidget(self.autoTurn_checkBox)
        layout5.addWidget(self.autoJump_checkBox)
        layout5.addWidget(self.takeAllOnly_checkBox)



        groupbox2_layout.addLayout(layout1)
        groupbox2_layout.addLayout(layout2)
        groupbox2_layout.addLayout(layout3)
        groupbox2_layout.addLayout(layout4)
        groupbox2_layout.addLayout(layout5)
        groupbox_layout.addLayout(groupbox2_layout)
        self.layout.addWidget(groupbox, 2, 0)

    def profileList(self) -> None:
        groupbox = QGroupBox("Save && Load", self)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Buttons
        save_target_loot_button = QPushButton("Save", self)
        load_target_loot_button = QPushButton("Load", self)

        # Button functions
        save_target_loot_button.clicked.connect(self.save_profile)
        load_target_loot_button.clicked.connect(self.load_profile)

        # Populate the profile list with existing files
        for file in os.listdir("Save/Targeting"):
            if file.endswith(".json"):
                self.profile_listWidget.addItem(file.split('.')[0])

        existing_names = [
            self.profile_listWidget.item(i).text()
            for i in range(self.profile_listWidget.count())
        ]
        if self.context.nickname in existing_names:
            self.profile_listWidget.setCurrentRow(existing_names.index(self.context.nickname))
            self.load_profile()

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        layout1.addWidget(QLabel("Name:", self))
        layout1.addWidget(self.profile_lineEdit)
        layout2.addWidget(save_target_loot_button)
        layout2.addWidget(load_target_loot_button)

        groupbox_layout.addWidget(self.profile_listWidget)
        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        self.layout.addWidget(groupbox, 3, 0)

    def save_profile(self) -> None:
        profile_name = self.profile_lineEdit.text().strip()
        if not profile_name:
            return

        data_to_save = {
            "sparHotkey": self.sparKey_comboBox.currentIndex(),
            "jarHotkey": self.jarKey_comboBox.currentIndex(),
            "sparDelay": self.sparDelay_lineEdit.text().strip(),
            "jumpHPPercent": self.autoJumpPercent_lineEdit.text().strip(),
            "attackDist": self.attackDist_comboBox.currentIndex()
        }

        if manage_profile("save", "Save/Targeting", profile_name, data_to_save):
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")
            existing_names = [
                self.profile_listWidget.item(i).text()
                for i in range(self.profile_listWidget.count())
            ]
            if profile_name not in existing_names:
                self.profile_listWidget.addItem(profile_name)
            self.profile_lineEdit.clear()

    def load_profile(self) -> None:
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.profile_listWidget.setStyleSheet("")

        profile_name = self.profile_listWidget.currentItem()
        if not profile_name:
            self.profile_listWidget.setStyleSheet("border: 2px solid red;")
            self.status_label.setText("Please select a profile from the list.")
            return
        else:
            self.profile_listWidget.setStyleSheet("")
        profile_name = profile_name.text()
        filename = f"Save/Targeting/{profile_name}.json"
        with open(filename, "r") as f:
            loaded_data = json.load(f)
            self.sparKey_comboBox.setCurrentIndex(int(loaded_data.get("sparHotkey", 0)))
            self.jarKey_comboBox.setCurrentIndex(int(loaded_data.get("jarHotkey", 0)))
            self.attackDist_comboBox.setCurrentIndex(int(loaded_data.get("attackDist", 0)))
            self.sparDelay_lineEdit.setText(loaded_data.get("sparDelay", 0))
            self.autoJumpPercent_lineEdit.setText(loaded_data.get("jumpHPPercent", 0))

    def start_autoSparring(self, state):
        if state == Qt.Checked:
            self.sparring_thread = SparringThread(
                self.sparKey_comboBox.currentText(),
                self.sparDelay_lineEdit.text().strip(),
                self.context
            )
            self.sparring_thread.start()
        else:
            if self.sparring_thread:
                self.sparring_thread.stop()
                self.sparring_thread = None

    def start_autoJump(self, state):
        self.context.autoJumpHPpercent = int(self.autoJumpPercent_lineEdit.text().strip())
        if state == Qt.Checked:
            self.context.autoJump = True
            self.jump_thread = JumpThread(self.context)
            self.jump_thread.start()
        else:
            self.context.autoJump = False
            if self.jump_thread:
                self.jump_thread.stop()
                self.jump_thread = None

    def start_autoTurn(self, state):
        if state == Qt.Checked:
            self.autoTurn_thread = TurnToMonsterThread(self.context)
            self.autoTurn_thread.start()
        else:
            if self.autoTurn_thread:
                self.autoTurn_thread.stop()
                self.autoTurn_thread = None            

    def start_autoJar(self, state):
        self.context.autoJumpHPpercent = int(self.autoJumpPercent_lineEdit.text().strip())
        if state == Qt.Checked:
            self.context.autoJar = True
            self.context.autoJarKey = self.jarKey_comboBox.currentText()
        else:
            self.context.autoJar = False
            self.context.autoJarKey = None

    def start_target_thread(self, state) -> None:
        if state == Qt.Checked:
            self.target_thread = TargetThread(
                self.attackDist_comboBox.currentIndex(),
                self.startLoot_checkBox.checkState(),
                self.sparDelay_lineEdit.text().strip(),
                self.context
            )
            self.target_thread.start()
        else:
            if self.target_thread:
                self.target_thread.stop()
                self.target_thread = None

    def xxxstart_loot_thread(self, state) -> None:
        if state == Qt.Checked:
            self.loot_thread = CollectorThread(self.context)
            self.loot_thread.start()
        else:
            if self.loot_thread:
                self.loot_thread.stop()
                self.loot_thread = None

    def start_loot_thread(self, state) -> None:
        if state == Qt.Checked:
            self.loot_thread = LootThread(self.context)
            self.loot_thread.start()
        else:
            if self.loot_thread:
                self.loot_thread.stop()
                self.loot_thread = None

    def start_takeall_thread(self, state) -> None:
        if state == Qt.Checked:
            self.takeall_thread = TakeAllThread(self.context)
            self.takeall_thread.start()
        else:
            if self.takeall_thread:
                self.takeall_thread.stop()
                self.takeall_thread = None