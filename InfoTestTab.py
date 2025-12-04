import os
import json
from GeneralFunctions import *
from MemoryFunctions import *
from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QComboBox, QLineEdit, QListWidget, QGridLayout,
    QGroupBox, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread
from InfoTestThread import InfoThread

class InfoTestTab(QWidget):
    def __init__(self, context, debug):
        super().__init__()
        self.context = context

        self.status_label = QLabel(self)
        self.player_label = QLabel(self)
        self.target_label = QLabel(self)
        self.lootingTest_checkBox = QCheckBox("Looting Test Feature", self)
        self.lootingTest_checkBox.stateChanged.connect(self.lootTest)
        self.a_lineEdit = QLineEdit(self)
        self.b_lineEdit = QLineEdit(self)
        self.c_lineEdit = QLineEdit(self)
        self.d_lineEdit = QLineEdit(self)
        self.e_lineEdit = QLineEdit(self)
        self.f_lineEdit = QLineEdit(self)
        self.g_lineEdit = QLineEdit(self)
        self.h_lineEdit = QLineEdit(self)
        self.i_lineEdit = QLineEdit(self)
        self.j_lineEdit = QLineEdit(self)
        self.k_lineEdit = QLineEdit(self)
        self.l_lineEdit = QLineEdit(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.infotest()

        # Check Boxes
        self.test_checkBox = QCheckBox("Test", self)
        self.test_checkBox.stateChanged.connect(self.infotest)
        self.update_button = QPushButton("Update Values")
        self.update_button.clicked.connect(self.updateVars)

        if self.context.debug:
            QThread.msleep(10)
        else:
            self.info_thread = InfoThread(self.context, self.player_label,self.target_label)
            self.info_thread.start()
        # Main Layout
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        if self.context.debug:
            self.controlList()
        self.gameinfo()
        self.layout.addWidget(self.status_label, 3, 0, 1, 2)

    def gameinfo(self) -> None:
        groupbox = QGroupBox("Game Info", self)
        groupbox_layout = QHBoxLayout()
        groupbox.setLayout(groupbox_layout)
        if self.context.debug:
            QThread.msleep(10)
        # Layouts
        groupbox2_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout1.addWidget(self.player_label)
        layout1.addWidget(self.target_label)
        layout2.addWidget(self.lootingTest_checkBox)
        groupbox2_layout.addLayout(layout1)
        groupbox2_layout.addLayout(layout2)
        groupbox_layout.addLayout(groupbox2_layout)
        self.layout.addWidget(groupbox, 2, 0)

    def controlList(self) -> None:
        groupbox = QGroupBox("Test Controls", self)
        groupbox_layout = QHBoxLayout()
        groupbox.setLayout(groupbox_layout)

        # Layouts
        groupbox2_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()

        layout1.addWidget(QLabel("A", self))
        layout1.addWidget(self.a_lineEdit)
        layout1.addWidget(QLabel("B", self))
        layout1.addWidget(self.b_lineEdit)
        layout1.addWidget(QLabel("C", self))
        layout1.addWidget(self.c_lineEdit)
        layout1.addWidget(QLabel("D", self))
        layout1.addWidget(self.d_lineEdit)
        layout2.addWidget(QLabel("E", self))
        layout2.addWidget(self.e_lineEdit)
        layout2.addWidget(QLabel("F", self))
        layout2.addWidget(self.f_lineEdit)
        layout2.addWidget(QLabel("G", self))
        layout2.addWidget(self.g_lineEdit)
        layout2.addWidget(QLabel("H", self))
        layout2.addWidget(self.h_lineEdit)
        layout3.addWidget(QLabel("I", self))
        layout3.addWidget(self.i_lineEdit)
        layout3.addWidget(QLabel("J", self))
        layout3.addWidget(self.j_lineEdit)
        layout3.addWidget(QLabel("K", self))
        layout3.addWidget(self.k_lineEdit)
        layout3.addWidget(QLabel("L", self))
        layout3.addWidget(self.l_lineEdit)
        layout4.addWidget(self.update_button)
        layout4.addWidget(self.test_checkBox)
        groupbox2_layout.addLayout(layout1)
        groupbox2_layout.addLayout(layout2)
        groupbox2_layout.addLayout(layout3)
        groupbox2_layout.addLayout(layout4)

        groupbox_layout.addLayout(groupbox2_layout)
        self.layout.addWidget(groupbox, 3, 0)

    def infotest(self):
        QThread.msleep(10)

    def lootTest(self):
        if self.context.a:
            self.context.a = False
        else:
            self.context.a = True

    def updateVars(self):
        QThread.msleep(10)
        self.context.a = self.a_lineEdit.text().strip()
        self.context.b = self.b_lineEdit.text().strip()
        self.context.c = self.c_lineEdit.text().strip()
        self.context.d = self.d_lineEdit.text().strip()
        self.context.e = self.e_lineEdit.text().strip()
        self.context.f = self.f_lineEdit.text().strip()
        self.context.g = self.g_lineEdit.text().strip()
        self.context.h = self.h_lineEdit.text().strip()
        self.context.i = self.i_lineEdit.text().strip()
        self.context.j = self.j_lineEdit.text().strip()
        self.context.k = self.k_lineEdit.text().strip()
        self.context.l = self.l_lineEdit.text().strip()