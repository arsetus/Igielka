from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QListWidget, QComboBox, QPushButton,
    QLabel, QCheckBox, QLineEdit, QHBoxLayout, QGroupBox,QVBoxLayout
)
from PyQt5.QtCore import Qt
from GeneralFunctions import *
from MouseFunctions import *
from KeyboardFunctions import *
from SmartHotkeysThread import SmartHotkeysThread, SetSmartHotkeyThread, ChakraTreeThread

class SmartHotkeysTab(QWidget):
    def __init__(self, context):
        super().__init__()

        # Thread Variables
        self.smart_hotkeys_thread = None
        self.set_smart_hotkey_thread = None
        self.chakraTree_thread = None
        self.context = context

        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: Red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Main layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        # List Widgets
        self.Clicks_listWidget = QListWidget(self)
        self.Clicks_listWidget.setFixedHeight(80)
        self.Clicks_listWidget.itemDoubleClicked.connect(
            lambda item: delete_item(self.Clicks_listWidget, item)
        )

        # Combo Boxes
        self.hotkey_lineEdit = QLineEdit(self)
        self.clickDelay_option_lineEdit = QLineEdit(self)
        self.hotkeyDelay_option_lineEdit = QLineEdit(self)

        self.mouseButton_combobox = QComboBox(self)
        self.mouseButton_combobox.addItem("Left Click")
        self.mouseButton_combobox.addItem(f"Right Click")

        # Buttons
        self.coordinates_button = QPushButton("Set Mouse Click", self)


        # Checkbox
        self.start_hotkeys_checkbox = QCheckBox("Start Clicks", self)
        self.chakraTreeTrain_checkbox = QCheckBox("ChakraTree Train", self)

        # Button functions
        self.coordinates_button.clicked.connect(self.start_set_hotkey_thread)

        # Checkbox function
        self.start_hotkeys_checkbox.stateChanged.connect(self.start_smart_hotkeys_thread)
        self.chakraTreeTrain_checkbox.stateChanged.connect(self.chakraTreeTrain)

        self.mouseClickList()
        self.hotkeyList()

        # Place the checkbox in row 2, col 0..1
        self.layout.addWidget(self.start_hotkeys_checkbox, 3, 0, 1, 1)
        self.layout.addWidget(self.chakraTreeTrain_checkbox, 3, 0, 5, 1)

        # Finally, add the status label in row 3 (spanning all columns)
        self.layout.addWidget(self.status_label, 4, 0, 1, 3)

    def mouseClickList(self) -> None:
        groupbox = QGroupBox("Click List")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Layouts
        layout1 = QVBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()

        layout1.addWidget(self.Clicks_listWidget) 
        layout2.addWidget(QLabel("Button: "))
        layout2.addWidget(self.mouseButton_combobox)
        layout3.addWidget(QLabel("Delay: "))
        self.clickDelay_option_lineEdit.setText(str(50))
        layout3.addWidget(self.clickDelay_option_lineEdit)
        layout3.addWidget(self.coordinates_button)

        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        groupbox_layout.addLayout(layout3)
        groupbox_layout.addLayout(layout4)

        self.layout.addWidget(groupbox, 1, 0)

    def hotkeyList(self) -> None:
        groupbox = QGroupBox("Hotkey Clicks")
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Buttons
        addHotkey_button = QPushButton("Add Hotkey")
        addHotkey_button.clicked.connect(self.addHotkey)

        # Layouts
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout2.addWidget(QLabel("Hotkey: "))
        layout2.addWidget(self.hotkey_lineEdit)
        layout3.addWidget(QLabel("Delay:"))
        layout3.addWidget(self.hotkeyDelay_option_lineEdit)
        layout3.addWidget(addHotkey_button)

        groupbox_layout.addLayout(layout1)
        groupbox_layout.addLayout(layout2)
        groupbox_layout.addLayout(layout3)
        self.layout.addWidget(groupbox, 2, 0)

    def start_set_hotkey_thread(self):
        mouseClick = True
        self.set_smart_hotkey_thread = SetSmartHotkeyThread(self.Clicks_listWidget, self.mouseButton_combobox.currentText(),
                                                            self.clickDelay_option_lineEdit, self.status_label,self.context, mouseClick)
        self.set_smart_hotkey_thread.start()

    def addHotkey(self):
        mouseClick = False
        self.set_smart_hotkey_thread = SetSmartHotkeyThread(self.Clicks_listWidget, self.hotkey_lineEdit.text(), self.hotkeyDelay_option_lineEdit, self.status_label,self.context,mouseClick)
        self.set_smart_hotkey_thread.start()

    def start_smart_hotkeys_thread(self, state):
        if state == Qt.Checked:
            if not self.smart_hotkeys_thread:
                self.smart_hotkeys_thread = SmartHotkeysThread(self.Clicks_listWidget,self.context)
                self.smart_hotkeys_thread.start()
        else:
            if self.smart_hotkeys_thread:
                self.smart_hotkeys_thread.stop()
                self.smart_hotkeys_thread = None

    def chakraTreeTrain(self, state):
        if state == Qt.Checked:
            if not self.chakraTree_thread:
                self.chakraTree_thread = ChakraTreeThread(self.context)
                self.chakraTree_thread.start()
        else:
            if self.chakraTree_thread:
                self.chakraTree_thread.stop()
                self.chakraTree_thread = None