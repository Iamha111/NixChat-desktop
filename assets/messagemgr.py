from PySide6.QtWidgets import QMessageBox

from assets.contentsmgr import ContentsManager
from assets.cachemgr import cache_contents


class Message:
    def __init__(self, message_id, contents, time, sender, on_right):
        self.id = message_id,
        self.time = time
        self.sender = sender
        self.on_right = on_right

        if type(contents) != list:
            self.contents = ContentsManager().import_contents(contents)
        else:
            self.contents = contents


class Chat:
    def __init__(self, username, core, is_group):
        self.username = username
        self.is_group = is_group
        self.history = []
        if self.is_group:
            self.widget = core.gui.normal_ui.add_group(self)
        else:
            self.widget = core.gui.normal_ui.add_chat(self)

    def add_message(self, message: Message):
        "Add a message"

        self.history.append(message)
        self.widget.add_message(message)


class MessageManager:
    def __init__(self, core):
        self.core = core
        self.chats = []
        self.messages = []

    def add_message(self, msg_id: int, contents, time: str, sender: str,
                        to: str = None):
        "Add a message"

        msg = Message(msg_id, contents, time, sender,
            True if sender == self.core.username else False)
        
        self.messages.append(msg)

        for c in self.chats:
            if c.username == msg.sender or c.username == to:
                c.add_message(msg)

    def add_chat(self, name: str, is_group: bool = False):
        "Add a chat (or group)"

        c = Chat(name, self.core, is_group)
        self.chats.append(c)
        return c

    def remove_chat(self, name: str, is_group: bool = False):
        "Removes a chat"

        for c in self.chats:
            if c.is_group == is_group:
                if c.username == name:
                    c.widget.button.close()
                    c.widget.close()
                    self.chats.remove(c)

    def send_message(self, message):
        "Sends a message"

    def process_message(self, msg_id, contents, date, sender):
        "Process received message"

        try:
            contents = self.core.secretmgr.decrypt_by_pk(
                contents,
                self.core.private_key
            ).decode()
        except:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось расшифровать сообщение от {sender}."
            )
            return None
        contents = cache_contents(contents, self)

        if not self.core.gui.isActiveWindow():
            text = "Сообщение"

            for i in contents:
                try:
                    if i["type"] == "text":
                        text = i["data"]
                except:
                    pass
                                    
            self.core.gui.icon.showMessage(
                sender,
                text
            )

        self.add_message(msg_id, contents, date, sender)


    def process_sync(self, messages: list):
        "Process synced messages"

        for m in messages:
            self.process_message(0, m["contents"], m["date"], m["from"])
