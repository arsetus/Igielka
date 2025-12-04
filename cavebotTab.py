import json
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QLineEdit, QTextEdit, QCheckBox, QComboBox, QVBoxLayout,
    QHBoxLayout, QGroupBox, QPushButton, QListWidgetItem, QLabel, QGridLayout
)
from GeneralFunctions import delete_item, manage_profile
from MemoryFunctions import *
from cavebotThread import cavebotThread, RecordThread

class cavebotTab(QWidget):
    def __init__(self, context):
        super().__init__()

        # Thread Variables
        self.record_thread = None
        self.cavebot_thread = None
        self.context = context

        # Other Variables
        self.labels_dictionary = {}

        # --- Status label at the bottom (behaves like a "status bar")
        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Widgets
        self.waypointList_listWidget = QListWidget(self)
        self.profile_listWidget = QListWidget(self)
        self.profile_lineEdit = QLineEdit(self)
        self.action_textEdit = QLineEdit(self)
        self.record_checkBox = QCheckBox("Auto Recording", self)
        self.start_checkBox = QCheckBox("Start cavebot", self)
        self.autoJump_checkBox = QCheckBox("Auto Jump", self)

        # Main Layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Initialize UI
        self.profileList()
        self.waypointList()
        self.actionsList()
        self.start_cavebot()

        # Finally add the status label (we'll place it at the bottom row)
        self.layout.addWidget(self.status_label, 3, 0, 1, 2)
        #print(self.base_address)

    def profileList(self) -> None:
        groupbox = QGroupBox("Save && Load")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Buttons
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_profile)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_profile)

        for file in os.listdir("Save/Waypoints"):
            if file.endswith(".json"):
                self.profile_listWidget.addItem(file.split(".")[0])

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

    def waypointList(self) -> None:
        groupbox = QGroupBox("Waypoints")
        groupbox_layout = QHBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Buttons
        clearWaypointList_button = QPushButton("Clear List", self)

        # Connect to add_waypoint with different indexes
        clearWaypointList_button.clicked.connect(self.clear_waypointList)
        
        # Double-click to delete
        self.waypointList_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.waypointList_listWidget, item)
        )

        # Layouts
        groupbox2_layout = QVBoxLayout()
        layout1 = QVBoxLayout()

        layout1.addWidget(self.waypointList_listWidget)
        layout1.addWidget(clearWaypointList_button)


        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(groupbox2_layout)
        self.layout.addWidget(groupbox, 0, 0)

    def start_cavebot(self) -> None:
        groupbox = QGroupBox("Start")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        self.start_checkBox.stateChanged.connect(self.start_cavebot_thread)
        self.record_checkBox.stateChanged.connect(self.start_record_thread)
        self.autoJump_checkBox.stateChanged.connect(self.start_autoJump)

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout1.addWidget(self.start_checkBox)
        layout2.addWidget(self.record_checkBox)
        layout3.addWidget(self.autoJump_checkBox)

        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        groupbox_layout.addLayout(layout3)
        self.layout.addWidget(groupbox, 2, 1)

    def actionsList(self) -> None:
        groupbox = QGroupBox("Actions")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        stand_waypoint_button = QPushButton("Stand")
        stand_waypoint_button.clicked.connect(lambda: self.add_waypoint(10))

        useCenter_button = QPushButton(" ", self)
        useCenter_button.clicked.connect(lambda: self.add_waypoint(5))
        useDown_button = QPushButton(" ", self)
        useDown_button.clicked.connect(lambda: self.add_waypoint(2))
        useUp_button = QPushButton(" ", self)
        useUp_button.clicked.connect(lambda: self.add_waypoint(8))
        useLeft_button = QPushButton(" ", self)
        useLeft_button.clicked.connect(lambda: self.add_waypoint(4))
        useRight_button = QPushButton(" ", self)
        useRight_button.clicked.connect(lambda: self.add_waypoint(6))
        useUpLeft_button = QPushButton(" ", self)
        useUpLeft_button.clicked.connect(lambda: self.add_waypoint(7))
        useUpRight_button = QPushButton(" ", self)
        useUpRight_button.clicked.connect(lambda: self.add_waypoint(9))
        useDownLeft_button = QPushButton(" ", self)
        useDownLeft_button.clicked.connect(lambda: self.add_waypoint(1))
        useDownRight_button = QPushButton(" ", self)
        useDownRight_button.clicked.connect(lambda: self.add_waypoint(3))

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        groupbox_layout.addLayout(layout3)
        groupbox_layout.addLayout(layout4)

        layout1.addWidget(useUpLeft_button)
        layout1.addWidget(useUp_button)
        layout1.addWidget(useUpRight_button)

        layout2.addWidget(useLeft_button)
        layout2.addWidget(useCenter_button)
        layout2.addWidget(useRight_button)

        layout3.addWidget(useDownLeft_button)
        layout3.addWidget(useDown_button)
        layout3.addWidget(useDownRight_button)

        layout4.addWidget(stand_waypoint_button)
        layout4.addWidget(QLabel("Delay:"))
        layout4.addWidget(self.action_textEdit)

        self.layout.addWidget(groupbox, 0, 1)

    def save_profile(self) -> None:
        profile_name = self.profile_lineEdit.text().strip()
        if not profile_name:
            return
        waypoint_list = [
            self.waypointList_listWidget.item(i).data(Qt.UserRole)
            for i in range(self.waypointList_listWidget.count())
        ]
        data_to_save = {
            "waypoints": waypoint_list,
        }
        if manage_profile("save", "Save/Waypoints", profile_name, data_to_save):
            existing_names = [
                self.profile_listWidget.item(i).text()
                for i in range(self.profile_listWidget.count())
            ]
            if profile_name not in existing_names:
                self.profile_listWidget.addItem(profile_name)
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_label.setText(f"Profile '{profile_name}' has been saved!")

    def load_profile(self) -> None:
        profile_name = self.profile_listWidget.currentItem()
        if not profile_name:
            self.profile_listWidget.setStyleSheet("border: 2px solid red;")
            self.status_label.setText("Please select a profile from the list.")
            return
        else:
            self.profile_listWidget.setStyleSheet("")
        profile_name = profile_name.text()
        filename = f"Save/Waypoints/{profile_name}.json"
        with open(filename, "r") as f:
            loaded_data = json.load(f)

        self.waypointList_listWidget.clear()
        for walk_data in loaded_data.get("waypoints", []):
            index = int(walk_data['Action'])
            walk_name = "Something"
            if index == 0:  # Walk
                walk_name = f"Walk: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 1:  # Use down left 
                walk_name = f"UseDL: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 2:  # Use down
                walk_name = f"UseD: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 3:  # Use down right
                walk_name = f"UseDR: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 4:  # Use left
                walk_name = f"UseL: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 5:  # Use center
                walk_name = f"UseC: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 6:  # Use right
                walk_name = f"UseR: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 7:  # Use up left
                walk_name = f"UseUL: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 8:  # Use up
                walk_name = f"UseU: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 9:  # Use up right
                walk_name = f"UseUR: {walk_data['X']} {walk_data['Y']} {walk_data['Z']}"
            elif index == 10:  # Stand
                delay = int(walk_data['Args'])
                walk_name = f"Stand: {walk_data['X']} {walk_data['Y']} {walk_data['Z']} {delay}"


            walk_item = QListWidgetItem(walk_name)
            walk_item.setData(Qt.UserRole, walk_data)
            self.waypointList_listWidget.addItem(walk_item)

        self.profile_lineEdit.clear()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText(f"Profile '{profile_name}' loaded successfully!")

    def add_waypoint(self, index):
        waypoint_data = {
            "X": self.context.x,
            "Y": self.context.y,
            "Z": self.context.z,
            "Action": index
        }

        self.status_label.setText("")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.action_textEdit.setStyleSheet("")

        if index == 0:  # Walk
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'Walk: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 1:  # Use down left
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseDL: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 2:  # Use down
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseD: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 3:  # Use down right
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseDR: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 4:  # Use left 
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseL: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 5:  # Use center
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseC: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 6:  # Use right 
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseR: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 7:  # Use up left
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseUL: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 8:  # Use up
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseU: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 9:  # Use up right
            waypoint_data["Action"] = index
            waypoint = QListWidgetItem(f'UseUR: {self.context.x} {self.context.y} {self.context.z}')

        elif index == 10:  # Stand
            action_text = self.action_textEdit.text().strip()
            waypoint_data["Args"] = action_text
            if not action_text:
                self.action_textEdit.setStyleSheet("border: 2px solid red;")
                self.status_label.setText("Please enter delay value.")
                return

            waypoint_data["Action"] = 10
            waypoint = QListWidgetItem(f'Stand: {x} {y} {z} {action_text}')
            self.action_textEdit.clear()

        waypoint.setData(Qt.UserRole, waypoint_data)
        self.waypointList_listWidget.addItem(waypoint)
        if self.waypointList_listWidget.currentRow() == -1:
            self.waypointList_listWidget.setCurrentRow(0)
        else:
            self.waypointList_listWidget.setCurrentRow(self.waypointList_listWidget.currentRow() + 1)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setText("Waypoint added successfully!")

    def clear_waypointList(self) -> None:
        self.waypointList_listWidget.clear()
        self.status_label.setText("")  # Clear status if you want

    def start_autoJump(self, state):
        if state == Qt.Checked:
            self.context.autoJump = True
        else:
            self.context.autoJump = False

    def start_record_thread(self, state):
        if state == Qt.Checked:
            self.record_thread = RecordThread(self.context)
            self.record_thread.wpt_update.connect(self.update_waypointList)
            self.record_thread.start()
        else:
            if self.record_thread:
                self.record_thread.stop()
                self.record_thread = None

    def start_cavebot_thread(self, state):
        if state == Qt.Checked:
            if not self.cavebot_thread:
                waypoints = [
                    self.waypointList_listWidget.item(i).data(Qt.UserRole)
                    for i in range(self.waypointList_listWidget.count())
                ]
                self.cavebot_thread = cavebotThread(waypoints,self.context)
                self.cavebot_thread.index_update.connect(self.update_waypointList)
                self.cavebot_thread.start()
        else:
            if self.cavebot_thread:
                self.cavebot_thread.stop()
                self.cavebot_thread = None

    def update_waypointList(self, option, waypoint):
        if option == 0:
            self.waypointList_listWidget.setCurrentRow(int(waypoint))
        elif option == 1:
            self.waypointList_listWidget.addItem(waypoint)
