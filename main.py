from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QStackedLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from send2trash import send2trash
import shutil

import sys
import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "mode_index": 0,
    "x": 100,
    "y": 100
}

MODES = [
    {
        "name": "Trash",
        "destination": "trash"
    },
    {
        "name": "Test Folder",
        "destination": "PUT YOUR PATH HERE"
    },
    {
        "name": "CD-Playlists",
        "destination": "PUT YOUR PATH HERE"
    },
    {
        "name": "Downloads",
        "destination": "PUT YOUR PATH HERE"
    },
    {
        "name": "Projects",
        "destination": "PUT YOUR PATH HERE"
    },
]

TAG_WIDTH = 240
TAG_HEIGHT = 80

class SharkWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.current_mode_index = 0
        self.shark_image_label = QLabel()
        self.nameplate_label = QPushButton(MODES[self.current_mode_index]["name"])
        self.nametag_image_label = QLabel()
        nametag_image = QPixmap("assets/nametag2.png")
        self.nametag_image_label.setAlignment(Qt.AlignCenter)
        nametag_image = nametag_image.scaled(
            TAG_WIDTH,
            TAG_HEIGHT,
            Qt.KeepAspectRatio,
            Qt.FastTransformation
        )
        self.nametag_image_label.setPixmap(nametag_image)
        self.nameplate_label.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: white;
                font-weight: bold;
                text-align: center;
                padding-top: 5px;
            }
        """)
        self.nametag_image_label.setFixedSize(TAG_WIDTH, TAG_HEIGHT)
        self.nameplate_label.setFixedSize(TAG_WIDTH, TAG_HEIGHT)
        self.nameplate_label.clicked.connect(self.cycle_mode)

        nameplate_container = QWidget()
        nameplate_stack = QStackedLayout()
        nameplate_stack.setStackingMode(QStackedLayout.StackAll)

        nameplate_stack.addWidget(self.nametag_image_label)
        nameplate_stack.addWidget(self.nameplate_label)

        nameplate_stack.setAlignment(self.nametag_image_label, Qt.AlignCenter)
        nameplate_stack.setAlignment(self.nameplate_label, Qt.AlignCenter)

        nameplate_container.setLayout(nameplate_stack)

        layout = QVBoxLayout()
        layout.addWidget(self.shark_image_label)
        layout.addWidget(nameplate_container)
        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                settings = json.load(file)
        else:
            settings = DEFAULT_SETTINGS

        self.current_mode_index = settings["mode_index"]

        current_mode = MODES[self.current_mode_index]
        self.nameplate_label.setText(current_mode["name"])

        self.move(settings["x"], settings["y"])

    def save_settings(self):

        settings = {
            "mode_index": self.current_mode_index,
            "x": self.x(),
            "y": self.y(),
        }

        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file)

        
    def closeEvent(self, event):
        self.save_settings()
        event.accept()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        self.set_shark_image("assets/shark_swim.png")
        self.nameplate_label.hide()
        self.nametag_image_label.hide()

    def mouseReleaseEvent(self, event):
        self.open_mouth()
        self.nameplate_label.show()
        self.nametag_image_label.show()

    def mouseMoveEvent(self, event):
        self.move(event.globalPosition().toPoint() - self.drag_position)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            #print("File detected!")
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.open_mouth()

    def set_shark_image(self, image_path):
        image = QPixmap(image_path)
        image = image.scaled(
            200,
            200,
            Qt.KeepAspectRatio,
            Qt.FastTransformation
        )
        self.shark_image_label.setPixmap(image)

    def open_mouth(self):
        self.set_shark_image("assets/shark_open.png")

    def close_mouth(self):
        self.set_shark_image("assets/shark_closed.png")

    def dropEvent(self, event):
        #print("dropEvent triggered")

        if event.mimeData().hasUrls():
            #print("File Dropped!")
            self.close_mouth()
            QTimer.singleShot(1000, self.open_mouth)
            event.acceptProposedAction()

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            #print(file_path)
            current_mode = MODES[self.current_mode_index]
            destination = current_mode["destination"]

            if destination == "trash":
                send2trash(file_path)

            else:
                shutil.move(file_path, destination)
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            #print("Dragging over shark...")
            event.acceptProposedAction()

    def cycle_mode(self):
        self.current_mode_index = (self.current_mode_index + 1) % len(MODES)
        
        self.nameplate_label.setText(MODES[self.current_mode_index]["name"])


app = QApplication(sys.argv)

shark_label = SharkWindow()

shark_label.setAcceptDrops(True)
shark_label.open_mouth()

shark_label.setWindowFlags(
    Qt.FramelessWindowHint |
    Qt.WindowStaysOnTopHint
)

shark_label.setAttribute(Qt.WA_TranslucentBackground)


shark_label.show()
sys.exit(app.exec())
