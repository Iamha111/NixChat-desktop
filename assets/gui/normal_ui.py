from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                               QScrollArea, QPushButton, QMenu)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

from assets.gui.widgets import Background, ChatButton, AddGroupMember
from assets.gui.chat import Chat
from assets.gui.add_chat import AddChat
from assets.gui.settings import Settings


class NormalUI(QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.bg = Background(self)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.hat = QHBoxLayout()
        self.hat.setContentsMargins(11, 11, 11, 11)
        
        self.sidebar = QWidget()
        self.sidebar.setObjectName("surface")
        self.sidebar.setMaximumWidth(300)
        self.sidebar.setMinimumWidth(150)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(0)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_scroller = QScrollArea()
        self.sidebar_scroller.setWidgetResizable(True)
        self.sidebar_scroller.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        
        self.layout.addWidget(self.sidebar)

        self.contacts_widget = QWidget()
        self.contacts_widget.setObjectName("tsurface")
        self.sidebar_scroller.setWidget(self.contacts_widget)
        self.contacts_layout = QVBoxLayout(self.contacts_widget)
        self.contacts_layout.setContentsMargins(0, 0, 0, 0)
        self.contacts_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.contents_view = QWidget()
        self.contents_layout = QVBoxLayout(self.contents_view)
        self.layout.addWidget(self.contents_view)

        self.plain_content = QWidget()
        self.plain_content.setMinimumSize(300, 300)
        self.set_cv_widget(self.plain_content)

        self.settings = Settings(self)
        self.settings_btn = QPushButton()
        self.settings_btn.setFlat(True)
        self.settings_btn.clicked.connect(
            lambda: self.set_cv_widget(self.settings)
        )
        self.sidebar_layout.addWidget(self.settings_btn)

        self.add_chat_ui = AddChat(self)
        self.add_chat_btn = QPushButton("+")
        self.add_chat_btn.setFlat(True)
        self.add_chat_btn.clicked.connect(
            lambda: self.set_cv_widget(self.add_chat_ui)
        )

        self.hat.addWidget(self.settings_btn)
        self.hat.addStretch()
        self.hat.addWidget(self.add_chat_btn)
        self.sidebar_layout.addLayout(self.hat)
        

        self.sidebar_layout.addWidget(self.sidebar_scroller)

    def open_settings(self):
        "Open settings properly"

        pixmap = QPixmap()
        pixmap.loadFromData(self.core.get_acc_pixmap(self.core.username))
        
        self.settings.acc_pixmap.setIcon(QIcon(pixmap))

        self.set_cv_widget(self.settings)

    def set_cv_widget(self, widget: QWidget):
        "Sets contents view widget"

        for i in range(self.contents_layout.count()):
            w = self.contents_layout.takeAt(i).widget()
            w.setParent(None)

        self.contents_layout.addWidget(widget)

    def add_chat(self, chat):
        "Adds a chat"

        username = chat.username


        pixmap = QPixmap()
        pixmap.loadFromData(self.core.get_acc_pixmap(username))

        menu = QMenu()

        a1 = menu.addAction("Удалить беседу")
        a1.triggered.connect(
            lambda: self.core.rmchat(username)
        )

        btn = ChatButton(str(username), pixmap, menu)

        cui = Chat(self, chat, username)

        cui.button = btn

        btn.chat = cui

        self.contacts_layout.addWidget(btn)

        btn.clicked.connect(
            lambda c, w = cui: self.set_cv_widget(w)
        )

        return cui

    def add_group(self, chat):
        "Adds a group chat"

        name = chat.username

        pixmap = QPixmap()

        menu = QMenu()

        a1 = menu.addAction("Добавить участника")
        a2 = menu.addAction("Удалить группу")

        a1.triggered.connect(
            lambda: AddGroupMember(self.core, name)
        )

        a2.triggered.connect(
            lambda: self.core.rmchat(name, True)
        )

        btn = ChatButton(str(name), pixmap, menu)

        cui = Chat(self, chat, name, group=True)

        cui.button = btn

        btn.chat = cui

        self.contacts_layout.addWidget(btn)

        btn.clicked.connect(
            lambda c, w = cui: self.set_cv_widget(w)
        )

        return cui

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.refresh_size()
