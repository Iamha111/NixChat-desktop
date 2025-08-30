from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon

from assets.gui.normal_ui import NormalUI
from assets.gui.login_ui import LoginUI
from assets.gui.widgets import TrayIcon


class GUI(QMainWindow):
    def __init__(self, core):
        super().__init__()

        self.core = core

        self.load_logo()

        self.setWindowIcon(self.icon)
        self.setWindowTitle("NixChat")
        
        self.ui_mode = "normal"
        self.normal_ui = NormalUI(self.core)
        self.goto_normal_ui()


        self.icon = TrayIcon(
            self.icon_symbolic,
            lambda: self.core.set_gui_status(True),
            quit
        )

        if not self.core.conf["enable-bg-worker"]:
            self.icon.hide()

        self.setup_theming()

    def goto_normal_ui(self):
        "Switch to the normal ui"
        self.normal_ui = NormalUI(self.core)
        self.setCentralWidget(self.normal_ui)
        self.ui_mode = "normal"

    def goto_login_ui(self):
        "Switch to the login ui"
        self.login_ui = LoginUI(self.core)
        self.setCentralWidget(self.login_ui)
        self.ui_mode = "login"

    def setup_theming(self):
        "Setups theming"

        self.core.app.setStyle("fusion")
        
        self.setStyleSheet("""
            QWidget#surface
            {
                background-color: rgba(0, 0, 0, 200)
            }

            QWidget#rsurface
            {
                background-color: rgba(0, 0, 0, 200);
                border-radius: 20
            }

            QWidget#tsurface
            {
                background-color: rgba(0, 0, 0, 0)
            }

            QScrollArea
            {
                background-color: rgba(0, 0, 0, 0)
            }

            QPushButton#chatbutton
            {
                border-radius: 0
            }

            QPushButton::flat
            {
                border-radius: 0;
            }

            QPushButton::flat:hover, QPushButton::flat:pressed
            {
                background-color: rgba(0, 0, 0, 0);
            }

            QPushButton
            {
                background-color: rgba(0, 0, 0, 0);
                color: #FFFFFF;
                border: 1;
                padding: 4px, 4px;
                padding-right: 4px;
                padding-left: 4px;
                border-radius: 10
            }

            QPushButton:hover
            {
                background-color: rgba(255, 255, 255, 50);
            }

            QPushButton:pressed
            {
                background-color: rgba(0, 0, 0, 100);
            }

            /*QPushButton:focus
            {   
                outline: none;
                background-color: rgba(255, 255, 255, 50)
            */

            QWidget#message
            {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                padding: 4px, 4px;
                padding-right: 4px;
                padding-left: 4px;
                border-radius: 10
            }

            QLineEdit
            {
                background-color: rgba(0, 0, 0, 0);
            }

            QLineEdit:focus
            {
                border: none;
                border-bottom: 1px solid white;
            }

            QScrollBar
            {
                background-color: transparent;
                color: transparent; 
            }

            QScrollBar::handle
            {
                background-color: rgba(0, 0, 0, 200);
            }

            QScrollBar::add-line, QScrollBar::sub-line
            {
                background-color: transparent;
                color: transparent;
                width: 0px
            }

            QWidget:focus
            {
                outline: none;
                border-bottom: 1px solid white
            }
        """)

    def closeEvent(self, event):
        "Redefine the close event"

        if self.core.conf["enable-bg-worker"]:
            self.core.set_gui_status(False)
            event.ignore()
        else:
            super().closeEvent(event)

    def load_logo(self):
        "Loads logo"

        self.icon = QIcon("assets/logo.png")
        self.icon_symbolic = QIcon("assets/logo-symbolic.png")