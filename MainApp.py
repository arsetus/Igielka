from PyQt5.QtWidgets import QApplication
import os
from PyQt5.QtCore import Qt
from LoaderTab import LoaderTab

import sys
import datetime

#LOG_FILE_NAME = "Log_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"

#try:
    #sys.stdout = open(LOG_FILE_NAME, 'w', encoding='utf-8', buffering=1)
    #sys.stderr = sys.stdout
    #print(f"Log started at: {datetime.datetime.now()}")
    #print("-" * 50)

#except Exception as e:
    #print(f"FATAL: Could not redirect stdout/stderr: {e}", file=sys.__stderr__)


dark_theme = """
    QWidget {
        background-color: #2e2e2e;
        color: #ffffff;
    }

    QMainWindow {
        background-color: #2e2e2e;
    }

    QTabBar::tab:selected {
        background-color: #555555;
        border: 1px solid #DAA520;
        color: #ffffff;
        padding: 5px 5px 5px 5px;
        border-radius: 4px;
    }

    QTabBar::tab {
        background-color: #2e2e2e;
        border: 1px solid #5e5e5e;
        color: #ffffff;
        padding: 5px 5px 5px 5px;
        border-radius: 4px;
    }

    QPushButton {
        background-color: #444444;
        border: 1px solid #5e5e5e;
        color: #ffffff;
        padding: 3px;
        border-radius: 5px;
    }

    QPushButton:hover {
        background-color: #555555;
    }

    QPushButton:pressed {
        background-color: #666666;
    }

    QLineEdit, QTextEdit {
        background-color: #3e3e3e;
        border: 1px solid #5e5e5e;
        color: #ffffff;
    }

    QLabel {
        background-color: transparent;
        color: #ffffff;
    }

    QMenuBar {
        background-color: #3e3e3e;
    }

    QMenuBar::item {
        background-color: #3e3e3e;
        color: #ffffff;
    }

    QMenuBar::item:selected {
        background-color: #555555;
    }

    QMenu {
        background-color: #3e3e3e;
        color: #ffffff;
    }

    QMenu::item:selected {
        background-color: #555555;
    }

    QScrollBar:vertical {
        background-color: #2e2e2e;
        width: 12px;
    }

    QScrollBar::handle:vertical {
        background-color: #666666;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #888888;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background-color: #2e2e2e;
    }
"""

def main():
    os.makedirs("Save", exist_ok=True)
    os.makedirs("Save/Targeting", exist_ok=True)
    os.makedirs("Save/Settings", exist_ok=True)
    os.makedirs("Save/Waypoints", exist_ok=True)
    os.makedirs("Save/NameSkin", exist_ok=True)
    os.makedirs("Save/Equipment", exist_ok=True)
    os.makedirs("Save/Combos", exist_ok=True)
    app = QApplication([])
    app.setStyle('Fusion')
    app.setStyleSheet(dark_theme)
    login_window = LoaderTab()
    login_window.setWindowFlags(Qt.WindowStaysOnTopHint)
    login_window.show()

    app.exec()


if __name__ == '__main__':
    main()