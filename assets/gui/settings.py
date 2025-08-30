from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                               QScrollArea, QPushButton, QFileDialog,
                               QStackedWidget, QLineEdit)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize, Qt, QBuffer, QIODevice, QByteArray

import os


class AccountSettings(QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.layout = QVBoxLayout(self)
        
        self.lbl1 = QLabel("Ваша учётная запись")

        self.acc_layout = QHBoxLayout()
        self.acc_layout2 = QVBoxLayout()

        self.acc_pixmap = QPushButton()
        self.acc_pixmap.clicked.connect(self.acc_pixmap_select)
        self.acc_pixmap.setFixedSize(64, 64)
        self.acc_pixmap.setIconSize(QSize(64, 64))
        self.acc_name = QLabel(self.core.username)

        pixmap = QPixmap()
        pixmap.loadFromData(self.core.get_acc_pixmap(self.core.username))

        self.acc_pixmap.setIcon(QIcon(pixmap))

        self.exit_btn = QPushButton("Выйти")
        self.exit_btn.clicked.connect(self.core.exit)
        self.del_acc_btn = QPushButton("Удалить")
        self.del_acc_btn.clicked.connect(self.core.remove_user)

        self.layout.addWidget(self.lbl1)

        for i in [self.acc_name, self.exit_btn, self.del_acc_btn]:
            self.acc_layout2.addWidget(i)

        self.layout.addLayout(self.acc_layout)
        self.acc_layout.addWidget(self.acc_pixmap)
        self.acc_layout.addLayout(self.acc_layout2)

        self.layout.addStretch()

    def acc_pixmap_select(self):
        "Account pixmap selection"

        path, _ = QFileDialog.getOpenFileName(
            caption="Выберите аватарку",
            dir=""
        )
        #filter="Images (*.png, *.jpg, *.jpeg, *.bmp, *.gif, *.tiff, *.webp)"

        if path:
            pixmap = QPixmap(path)
        
            pixmap = pixmap.scaled(48, 48,
                                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                Qt.TransformationMode.SmoothTransformation
            )
            
            self.acc_pixmap.setIcon(QIcon(pixmap))

            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            pixmap.save(buffer, path.split(".")[-1].upper())
            buffer.close()

            self.core.set_acc_pixmap(byte_array)


class AppearanceSettings(QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.layout = QVBoxLayout(self)

        self.bg_scroller = QScrollArea()
        self.bg_scroller.setWidgetResizable(True)
        self.bg_sc_container = QWidget()
        self.bg_sc_container.setObjectName("tsurface")
        self.bg_scroller.setWidget(self.bg_sc_container)

        self.bg_layout = QHBoxLayout(self.bg_sc_container)

        self.lbl1 = QLabel("Обои")

        for i in [self.lbl1, self.bg_scroller]:
            self.layout.addWidget(i)

        self.layout.addStretch()

        self.refresh_bgs()

    def refresh_bgs(self):
        "Refreshes backgrounds"

        try:
            #prefix = self.core.get_data_path("backgrounds") <=== for production
            prefix = "assets/backgrounds/"
            for i in os.listdir(prefix):

                img = QPixmap(prefix + i)

                btn = QPushButton(icon=QIcon(img))
                btn.setIconSize(QSize(64, 64))
                btn.setFixedSize(74, 74)

                btn.clicked.connect(
                    lambda c, n=i: self.apply_bg(n)
                )

                self.bg_layout.addWidget(btn)

        except ArithmeticError:
            pass

    def apply_bg(self, name: str):
        "Applies the background"
        
        self.core.settings["background"] = name
        self.core.save_settings()
        self.core.gui.normal_ui.bg.load_bg()


class ServerSettings(QWidget):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.layout = QVBoxLayout(self)

        self.lbl1 = QLabel(
            "Введите адрес сервера. Формат: {URL сервера}:{порт}."
        )
        self.lbl1.setWordWrap(True)
        self.lbl2 = QLabel(
            "Внимание! Настоятельно рекомендуется использовать протокол HTTPS."
        )
        self.lbl2.setWordWrap(True)
        
        self.url_edit = QLineEdit(self.core.settings["server"])

        self.apply_btn = QPushButton("Применить")
        self.apply_btn.clicked.connect(self.apply)

        for i in [self.lbl1, self.url_edit, self.apply_btn, self.lbl2]:
            self.layout.addWidget(i)

        self.layout.addStretch()

    def apply(self):
        "Apply server settings"

        url = str(self.url_edit.text())

        self.core.communicator.server = url
        self.core.settings["server"] = url
        self.core.save_settings()


class About(QWidget):
    def __init__(self, core):
        super().__init__()

        text = """NixChat, версия 1.0.0
Copyright 2025 Iamha111

Это свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной          
лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3         
лицензии, либо (по вашему выбору) любой более поздней версии.                                                            
                                                                                                                              
Эта программа распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии     
ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.            
                                                                                                                              
Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см.       
<https://www.gnu.org/licenses/>."""

        self.layout = QVBoxLayout(self)

        self.lbl = QLabel(text)
        self.lbl.setWordWrap(True)
        self.lbl.setObjectName("tsurface")

        self.scroller = QScrollArea()
        self.scroller.setWidgetResizable(True)
        self.scroller.setWidget(self.lbl)
        self.layout.addWidget(self.scroller)


class Settings(QLabel):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.setObjectName("rsurface")
        self.setMinimumSize(300, 300)

        self.layout = QVBoxLayout(self)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.nav = QWidget()
        self.nav_layout = QVBoxLayout(self.nav)

        self.stack.addWidget(self.nav)

        self.view = QWidget()
        self.view_layout = QVBoxLayout(self.view)
        self.back_btn = QPushButton("Назад")
        self.back_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )
        self.view_layout.addWidget(self.back_btn)

        self.stack.addWidget(self.view)
        

        pages = {
            "Учётная запись": AccountSettings,
            "Внешний вид": AppearanceSettings,
            "Сервер": ServerSettings,
            "О программе": About
        }
        
        for i in pages:
        
            btn = QPushButton(i)
            btn.clicked.connect(
                lambda c, w=pages[i]: self.set_view(w)
            )

            self.nav_layout.addWidget(btn)

        self.nav_layout.addStretch()

    def set_view(self, widget: QWidget):
        "Sets current settings page"

        widget = widget(self.parent.core)

        for i in range(self.view_layout.count()):
            w = self.view_layout.itemAt(i).widget()
            if not w is self.back_btn:
                w.close()

        self.view_layout.addWidget(widget)

        self.stack.setCurrentIndex(1)
        
