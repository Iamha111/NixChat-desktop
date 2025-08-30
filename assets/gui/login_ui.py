from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                               QStackedWidget, QLabel, QLineEdit,
                               QPushButton, QMessageBox)


class LoginUI(QWidget):
    def __init__(self, core):
        super().__init__()
        self.core = core

        self.layout = QHBoxLayout(self)
        self.layout.addStretch()

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        self.layout.addStretch()

        self.login_widget = QWidget()
        self.login_layout = QVBoxLayout(self.login_widget)
        self.lbl1 = QLabel("Имя пользователя")
        self.lbl2 = QLabel("Пароль")
        self.uname_edit = QLineEdit()
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)
        self.login_register_btn = QPushButton("Нет учётной записи?")
        self.login_register_btn.setFlat(True)
        self.login_register_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )
        
        self.login_layout.addStretch()
        
        for i in [self.lbl1, self.uname_edit, self.lbl2,
                    self.pwd_edit, self.login_btn,
                    self.login_register_btn]:
            self.login_layout.addWidget(i)
            
        self.login_layout.addStretch()
        
        self.stack.addWidget(self.login_widget)


        self.register_widget = QWidget()
        self.register_layout = QVBoxLayout(self.register_widget)
        self.lbl3 = QLabel("Имя пользователя")
        self.lbl4 = QLabel("Пароль")
        self.lbl5 = QLabel("Повторить пароль")
        self.uname_edit2 = QLineEdit()
        self.pwd_edit2 = QLineEdit()
        self.pwd_edit2.setEchoMode(QLineEdit.Password)
        self.pwd_edit3 = QLineEdit()
        self.pwd_edit3.setEchoMode(QLineEdit.Password)
        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.register)
        self.register_login_btn = QPushButton("Есть учётная запись?")
        self.register_login_btn.setFlat(True)
        self.register_login_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.register_layout.addStretch()

        for i in [self.lbl3, self.uname_edit2, self.lbl4,
                    self.pwd_edit2, self.lbl5, self.pwd_edit3,
                    self.register_btn, self.register_login_btn]:
            self.register_layout.addWidget(i)

        self.register_layout.addStretch()

        self.stack.addWidget(self.register_widget)

    def login(self):
        "Logins"

        uname = self.uname_edit.text()
        pwd = self.pwd_edit.text()

        r = self.core.login(uname, pwd)

        self.uname_edit.setText("")
        self.pwd_edit.setText("")

        if not r:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось войти."
            )

    def register(self):
        "Registers"

        uname = self.uname_edit2.text()
        pwd = self.pwd_edit2.text()
        pwd2 = self.pwd_edit3.text()
        if pwd and pwd2 and uname:
            if pwd == pwd2:
                r = self.core.register(uname, pwd)
                if not r[0]:
                    if r[1] == "Username was taken already":
                        e = "Имя пользователя уже занято."
                    else:
                        e = "Не удалось зарегистрироваться."
                    QMessageBox.critical(self, "Ошибка", e)
            else:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    "Пароли не совпадают."
                )
        else:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не все поля заполнены."
            )
            

        for i in [self.uname_edit2, self.pwd_edit2, self.pwd_edit3]:
            i.setText("")
