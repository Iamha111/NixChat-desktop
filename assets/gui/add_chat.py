from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QStackedWidget, QPushButton, QLabel,
                               QLineEdit)


class AddChat(QLabel):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.setObjectName("rsurface")

        self.setMinimumSize(300, 300)

        self.main_layout = QVBoxLayout(self)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.add_chat_container = QWidget()
        self.add_group_container = QWidget()

        self.stack.addWidget(self.add_chat_container)
        self.stack.addWidget(self.add_group_container)
        

        self.layout = QHBoxLayout(self.add_chat_container)

        self.layout2 = QVBoxLayout()

        self.layout.addStretch()
        self.layout.addLayout(self.layout2)
        self.layout.addStretch()

        self.lbl = QLabel("Имя пользователя")
        self.edit = QLineEdit()
        self.btn = QPushButton("Добавить беседу")
        self.btn.clicked.connect(self.add_chat)
        self.goto_group_btn = QPushButton("Создать группу?")
        self.goto_group_btn.setFlat(True)
        self.goto_group_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )
        self.s_lbl = QLabel()
        
        self.layout2.addStretch()

        for i in [self.lbl, self.edit, self.btn]:
            self.layout2.addWidget(i)

        self.layout2.addStretch()
        self.layout2.addWidget(self.s_lbl)
        self.layout2.addWidget(self.goto_group_btn)
        

        self.layout3 = QHBoxLayout(self.add_group_container)

        self.layout4 = QVBoxLayout()

        self.layout3.addStretch()
        self.layout3.addLayout(self.layout4)
        self.layout3.addStretch()

        self.lbl2 = QLabel("Название группы")
        self.edit2 = QLineEdit()
        self.btn2 = QPushButton("Создать группу")
        self.btn2.clicked.connect(self.add_group)
        self.s_lbl2 = QLabel()
        self.goto_chat_btn = QPushButton("Добавить беседу?")
        self.goto_chat_btn.setFlat(True)
        self.goto_chat_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.layout4.addStretch()
        
        for i in [self.lbl2, self.edit2, self.btn2]:
            self.layout4.addWidget(i)
        
        self.layout4.addStretch()
        self.layout4.addWidget(self.s_lbl2)
        self.layout4.addWidget(self.goto_chat_btn)

    def add_chat(self):
        "Add a chat"

        u = self.edit.text()

        self.edit.setText("")

        r = self.parent.core.communicator.get_user_info(u)

        if r["msg"] == "Success":
            self.parent.core.messagemgr.add_chat(u)
            self.s_lbl.setText("")
        else:
            self.s_lbl.setText("Такого пользователя нет")

    def add_group(self):
        "Adds a group"

        n = self.edit2.text()
        self.edit2.setText("")

        self.parent.core.communicator.add_group(
            self.parent.core.token, n
        )
