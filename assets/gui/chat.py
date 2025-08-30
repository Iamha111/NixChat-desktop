from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QMenu,
                               QScrollArea, QPushButton, QLabel, QLineEdit)
from PySide6.QtCore import Qt, QPoint

from assets.gui.widgets import Message
from assets.contentsmgr import ContentsManager
from assets.cachemgr import cache_contents

import time


class EmojiPicker(QLabel):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
    
        self.setFixedHeight(64)
        self.setObjectName("rsurface")
        self.layout = QHBoxLayout(self)

        self.emoji_area_widget = QWidget()
        self.emoji_area_widget.setObjectName("tsurface")
        self.emoji_area_layout = QHBoxLayout(self.emoji_area_widget)
        self.emoji_area_layout.setContentsMargins(0, 0, 0, 0)

        self.emoji_scroller = QScrollArea()
        self.emoji_scroller.setObjectName("tsurface")
        self.emoji_scroller.setWidgetResizable(True)
        self.emoji_scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.emoji_scroller.setWidget(self.emoji_area_widget)

        self.layout.addWidget(self.emoji_scroller)


        for i in [
            ":)", ":>", ":D", "=D", ":3", "=3", "XD", ";)",
            "=)", "B)", ":(", ":c", ":<", ":'(", ":')", ":'D",
            ">:(", ">:O", ">:P", ":P", ":o", ":O",
            ">:3", ":*", ":/", ">:/", ":s", ":|", "O:)",
            "><>", "^_^", "^3^", "._.", "v_v", "v.v", "T_T",
            "x_x", "o_o", "O_O", ">_<", ">.<", "^o^",
            "\\^o^/"
        ]:
            btn = QPushButton(i)
            btn.clicked.connect(
                lambda c, t = i: self.parent.append_msgedit_text(t)
            )
            self.emoji_area_layout.addWidget(btn)

    def toggle_visibility(self, checked: bool):
        "Toggle visibility"

        if checked:
            #self.emoji_widget.setFixedHeight(self.edit_widget.height())
            self.parent.layout.insertWidget(1, self)
        else:
            self.setParent(None)


class Chat(QWidget):
    def __init__(self, parent, chat, username: str, group: bool = False):
        super().__init__()

        self.core = parent.core
        self.parent = parent
        self.chat = chat

        self.username = username
        self.group_mode = group

        self.setMinimumSize(300, 300)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)


        self.emoji_picker = EmojiPicker(self)


        self.cmgr = ContentsManager()
        

        self.edit_widget = QWidget()
        self.edit_widget.setObjectName("rsurface")
        self.edit_layout = QHBoxLayout(self.edit_widget)

        self.pin_menu = QMenu()
        self.pin_menu_image = self.pin_menu.addAction("Изображение")
        # self.pin_menu_file = self.pin_menu.addAction("Файл")

        self.pin_menu_image.triggered.connect(
            self.cmgr.add_picture
        )

        # self.pin_menu_file.triggered.connect(
        #     self.cmgr.add_file
        # )
        
        self.emoji_btn = QPushButton(":-)")
        self.emoji_btn.setCheckable(True)
        self.emoji_btn.toggled.connect(
            self.emoji_picker.toggle_visibility
        )

        self.pin_btn = QPushButton("o--")
        self.pin_btn.clicked.connect(
            lambda c, b = self.pin_btn: self.pin_menu.exec(
                b.mapToGlobal(b.rect().bottomLeft())
            )
        )
        
        self.msg_edit = QLineEdit()
        
        self.msg_send = QPushButton("=>")
        self.msg_send.clicked.connect(self.send_message)

        for i in [self.emoji_btn, self.pin_btn,
                  self.msg_edit, self.msg_send]:
            self.edit_layout.addWidget(i)


        self.scroller = QScrollArea()
        self.scroller.setObjectName("tsurface")
        self.scroller.setWidgetResizable(True)
        self.scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.history_widget = QWidget()
        self.history_widget.setObjectName("tsurface")
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroller.setWidget(self.history_widget)

        self.layout.addWidget(self.scroller)

        self.layout.addWidget(self.edit_widget)

    def add_message(self, message):
        "Adds a message"
        
        msg = Message(message, self.core)

        self.history_layout.addWidget(msg)

        self.scroller.verticalScrollBar().setValue(
            self.scroller.verticalScrollBar().maximum()
        )

    def send_message(self):
        "Sends message"

        text = self.msg_edit.text()
        if text:
            self.cmgr.add_text(text)

        if self.cmgr.contents:
            data = self.cmgr.export_contents()
            
            self.msg_edit.setText("")
            self.cmgr.clear()

            data2 = cache_contents(data, self.core)

            self.core.messagemgr.add_message(0, data2, 
                time.strftime("%H:%M"), self.core.username, self.username)
            
            #self.add_message(data2, time.strftime("%H:%M"), True)

            if self.group_mode:
                self.core.send_group(self.username, data)
            else:
                self.core.send(self.username, data)

    def append_msgedit_text(self, text: str):
        "Append text to msgedit's one"

        t = self.msg_edit.text()
        self.msg_edit.setText(t + text)


class ChannelView(QWidget):
    def __init__(self, parent, name: str):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.scroller = QScrollArea()
        self.scroller.setObjectName("tsurface")
        self.scroller.setWidgetResizable(True)
        self.scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.history_widget = QWidget()
        self.history_widget.setObjectName("tsurface")
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroller.setWidget(self.history_widget)

        self.layout.addWidget(self.scroller)

    def add_message(self, text: str, time: str):
        "Adds a message"

        msg = Message(text, time, False)

        self.history_layout.addWidget(msg)

        self.scroller.verticalScrollBar().setValue(
            self.scroller.verticalScrollBar().maximum()
        )
