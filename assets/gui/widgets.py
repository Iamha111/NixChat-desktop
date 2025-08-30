from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
                               QPushButton, QLabel, QMenu, QSystemTrayIcon,
                               QMessageBox)
from PySide6.QtGui import QIcon, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize

import base64


class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon: QIcon, on_open, on_quit):
        super().__init__(icon)

        self.menu = QMenu()

        self.open_action = self.menu.addAction("Открыть")
        self.quit_action = self.menu.addAction("Выход")

        self.open_action.triggered.connect(on_open)
        self.quit_action.triggered.connect(on_quit)

        self.setContextMenu(self.menu)

        self.activated.connect(on_open)

        self.show()


class Splash(QLabel):
    def __init__(self, core):
        super().__init__(core.gui)

        self.core = core

        self.setObjectName("surface")

        self.move(0, 0)
        self.setFixedSize(self.core.gui.size())
        self.show()

        self.core.gui.windowHandle().widthChanged.connect(
            lambda: self.setFixedWidth(self.core.gui.size().width())
        )
        self.core.gui.windowHandle().heightChanged.connect(
            lambda: self.setFixedHeight(self.core.gui.size().height())
        )


class ImageViewer(Splash):
    def __init__(self, image: bytes | QPixmap, core):
        self.view = QLabel()
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if type(image) == QPixmap:
            self.pixmap = image
        else:
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(image)
        
        self.view.setPixmap(self.pixmap)
                
        super().__init__(core)

        self.layout = QVBoxLayout(self)
        self.tool_layout = QHBoxLayout()
        self.layout.addLayout(self.tool_layout)

        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.close)

        self.tool_layout.addStretch()
        self.tool_layout.addWidget(self.close_btn)

        self.layout.addStretch()
        self.layout.addWidget(self.view)
        self.layout.addStretch()

    def resizeEvent(self, event):
        "Redefintion of resize event"

        self.view.setPixmap(
            self.pixmap.scaled(
                event.size().width(),
                event.size().height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        super().resizeEvent(event)


class AddGroupMember(Splash):
    def __init__(self, core, group: str):
        super().__init__(core)

        self.core = core
        self.group = group

        self.layout = QHBoxLayout(self)
        self.layout2 = QVBoxLayout()

        self.lbl = QLabel("Имя пользователя")
        self.edit = QLineEdit()
        self.btn = QPushButton("Добавить")
        self.btn.clicked.connect(self.add_member)
        self.slbl = QLabel()
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setFlat(True)
        self.cancel_btn.clicked.connect(self.close)

        self.layout.addStretch()
        self.layout.addLayout(self.layout2)
        self.layout.addStretch()
        
        self.layout2.addStretch()

        for i in [self.lbl, self.edit, self.btn]:
            self.layout2.addWidget(i)

        self.layout2.addStretch()
        self.layout2.addWidget(self.slbl)
        self.layout2.addWidget(self.cancel_btn)

    def add_member(self):
        "Add group member"

        uname = str(self.edit.text())
        if uname:
            self.core.communicator.add_group_member(self.group, uname)
        self.edit.setText("")


class Panic(Splash):
    def __init__(self, core, text):
        super().__init__(core)

        self.setStyleSheet("background-color: black")

        self.layout = QHBoxLayout(self)
        self.layout2 = QVBoxLayout()

        self.layout.addStretch()
        self.layout.addLayout(self.layout2)
        self.layout.addStretch()

        self.lbl = QLabel(text)
        self.lbl.setWordWrap(True)

        self.layout2.addStretch()
        self.layout2.addWidget(self.lbl)
        self.layout2.addStretch()


class Background(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.load_bg()

    def load_bg(self, name: str = None):
        "Loads the background"

        if not name:
             name = self.parent.core.settings["background"]

        #prefix = self.parent.core.get_data_path("backgrounds/")
        prefix = "assets/backgrounds/"

        self.pixmap = QPixmap(prefix + name)
        self.refresh_size()

    def refresh_size(self):
        "Refreshes the size"

        s = self.parent.size()

        self.setGeometry(0, 0, s.width(), s.height())
        
        self.setPixmap(self.pixmap.scaled(s, 
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                        Qt.TransformationMode.SmoothTransformation)
        )
        self.lower()


class MessageContents(QWidget):
    def __init__(self, contents, date, core):
        super().__init__()

        self.core = core
        
        self.setObjectName("message")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        for c in contents:
            try:
                if c["type"] == "text":
                    lbl = QLabel(c["data"])
                    lbl.setWordWrap(True)
                    self.layout.addWidget(lbl)
                    
                elif c["type"] == "picture":
                    data = self.core.cachemgr.get(c["data"])
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)

                    pixmap2 = pixmap.scaled(
                        100, 100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    icon = QIcon(pixmap)
                    
                    btn = QPushButton(icon=icon)
                    btn.setIconSize(pixmap2.size())
                    btn.clicked.connect(
                        lambda ch, p=pixmap, c=self.core: ImageViewer(p, c)
                    )
                    
                    self.layout.addWidget(btn)
                    
            except:
                QMessageBox.warning(
                    self,
                    "Предупреждение",
                    "Не удалось обработать содержимое сообщения."
                )

        self.date_lbl = QLabel(date)
        self.date_lbl.setStyleSheet("font-size: 7pt")
        self.date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.date_lbl)


class Message(QWidget):
    def __init__(self, message, core):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.message = message
        self.on_right = self.message.on_right
        self.contents = self.message.contents
        self.time = self.message.time

        if self.on_right:
            self.layout.addStretch()

        self.mc = MessageContents(self.contents, self.time, core)
        self.layout.addWidget(self.mc)

        if not self.on_right:
            self.layout.addStretch()


class ChatButton(QPushButton):
    def __init__(self, username: str, pixmap: QPixmap,
                    menu: QMenu):
        super().__init__()

        self.menu = menu

        self.setFixedHeight(64)
        self.setObjectName("chatbutton")

        self.layout = QHBoxLayout(self)
        self.layout2 = QVBoxLayout()

        self.icon = QLabel()
        self.icon.setFixedSize(48, 48)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet("font-size: 24pt")
        
        self.layout.addWidget(self.icon)

        self.username = QLabel(username)
        self.layout2.addWidget(self.username)

        self.layout.addLayout(self.layout2)

        self.set_avatar(pixmap)

    def set_avatar(self, pixmap):
        "Sets avatar or ? if its missing"

        if not pixmap.isNull():
            self.icon.setPixmap(pixmap)
        else:
            self.icon.setText("?")

    def contextMenuEvent(self, event):
        "Shows context menu"

        self.menu.exec(event.globalPos())
