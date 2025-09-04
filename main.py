from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

from cryptography.hazmat.primitives import serialization

from assets import (gui, communicator, stabilizer,
                    secretmgr)
from assets.contentsmgr import ContentsManager
from assets.messagemgr import MessageManager
from assets.cachemgr import CacheManager, cache_contents
from assets.gui.widgets import Panic

import json
import os
import sys
import socket
import base64
import time
import lzma


class Core:
    def __init__(self, conf):

        self.conf = conf

        self.load_settings()

        self.app = QApplication()

        if self.conf["enable-bg-worker"]:
                    self.setup_bg_worker()

        self.gui = gui.GUI(self)
        self.messagemgr = MessageManager(self)
        self.communicator = communicator.Communicator(
            self.settings["server"], self
        )
        self.secretmgr = secretmgr.SecretMgr()
        self.cachemgr = CacheManager(self)

        self.setup_user()
        self.setup_timer()
        self.load_chats()

        if self.conf["enable-bg-worker"]:
            self.app.setQuitOnLastWindowClosed(False)

        if not self.token:
            self.gui.goto_login_ui()

        if self.conf["start-hidden"]:
            self.set_gui_status(False)
        else:
            self.gui.show()

        self.communicator.ping()

        self.app.exec()

    def setup_timer(self):
        "Setups timer"

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(3000)

    def tick(self):
        "There we will check account and more"

        if self.token:

            try:
                info = self.communicator.sync(self.token)
            except:
                info = "Communication failed"

            data_status = stabilizer.check_sync_data(info)

            if data_status == "ok":

                if info["messages"]:
                    self.communicator.clear_messages(self.token)

                # Process chats

                chats = info["chats"]
                old_chats = [chat.username for chat in self.messagemgr.chats]

                for u in chats:
                    if u not in old_chats:
                        self.messagemgr.add_chat(u)

                # Process groups

                groups = info["groups"]
                
                for g in groups:
                    if g not in old_chats:
                        self.messagemgr.add_chat(g, True)

                # Process messages

                self.messagemgr.process_sync(info["messages"])

                # Save messages
                if info["messages"]:
                    self.save_chats()

                # Set settings button text
                if False:
                    pass
                else:
                    self.gui.normal_ui.settings_btn.setText(
                        "Вы " + self.username
                    )

                # Go to normal ui

                if self.gui.ui_mode != "normal":
                    self.gui.goto_normal_ui()
            elif data_status == "jwt_fail":
                self.exit()
            elif data_status == "comm_failed":
                self.online = False
                self.gui.normal_ui.settings_btn.setText(
                    "Сервер недоступен"
                )
        else:
            if self.gui.ui_mode != "login":
                self.gui.goto_login_ui()

    def set_gui_status(self, opened: bool):
        "Set gui status (opened or closed)"

        if opened:
            self.gui.show()
            self.timer.setInterval(3000)
        else:
            self.gui.hide()
            self.timer.setInterval(5000)

    def check_socket(self):
        "Checks socket"
        
        try:
            self.bg_socket.settimeout(0)
            data, _ = self.bg_socket.recvfrom(1024)

            if data == b"open":
                self.set_gui_status(True)
        except:
            pass

    def setup_bg_worker(self):
        "Setups the background worker"

        try:
            self.bg_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.bg_socket.bind(("0.0.0.0", 50505))

            self.s_timer = QTimer()
            self.s_timer.timeout.connect(self.check_socket)
            self.s_timer.start(1000)
        except:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(b"open", ("localhost", 50505))
                s.close()
                quit()
            except:
                quit()
        
    def setup_user(self):
        "Sets up some user related things"

        self.token = None
        self.username = None
        self.logined = False
        self.private_key = None

    def login(self, username: str, password: str):
        "Login"

        self.token = self.communicator.login(username, password)

        if self.token:
            self.username = username
            if self.gui.ui_mode == "login":
                self.gui.goto_normal_ui()
                self.update_keys()
                self.save_chats()
            return True

        return False

    def register(self, username: str, password: str,
                    login: bool = True):
        "Register"

        r = self.communicator.register(
            username, password
        )

        if r["msg"] == "Success":
            if login:
                self.login(username, password)
            return True, None
            
        return False, r["msg"]

    def exit(self):
        "Exits account"

        self.token = None
        self.username = None
        self.logined = False

        self.messagemgr = MessageManager(self)

        os.remove(self.get_data_path("data"))

        cache_path = self.get_data_path("cache/")
        for i in os.listdir(cache_path):
            os.remove(cache_path + i)

        self.gui.goto_login_ui()

    def remove_user(self):
        "Removes user"

        c = QMessageBox.question(
            self.gui,
            "Подтвердите действие",
            "Вы уверены, что хотите удалить учётную запись?",
            QMessageBox.Yes | QMessageBox.Cancel
        )

        if c == QMessageBox.Yes:
            self.communicator.remove_user(self.token)
            self.exit()

    def load_chats(self):
        "Load chats data"

        if os.path.exists(self.get_data_path("data")):
            try:
                data = json.loads(
                    self.secretmgr.load_data(self.get_data_path("data"))
                )

                self.token = data["token"]
                self.username = data["username"]
                self.private_key = serialization.load_pem_private_key(
                    data["private_key"].encode(),
                    password=None
                )

                for chat in data["chats"]:
                
                    if chat["group"]:
                        c = self.messagemgr.add_chat(chat["name"], True)
                    else:
                        c = self.messagemgr.add_chat(chat["name"])

                    for msg in chat["messages"]:
                        self.messagemgr.add_message(
                            0, msg["contents"], msg["time"], chat["name"]
                        )
            except:
                QMessageBox.critical(
                    self.gui,
                    "Ошибка",
                    "Не удалось загрузить данные."
                )
                self.exit()

            try:
                self.tick()
            except:
                pass

    def save_chats(self):
        "Save chats data"

        data = {"chats": []}

        for c in self.messagemgr.chats:

            d = {"name": c.username, "messages": [], "group": c.is_group}

            for m in c.history:

                cont = base64.b64encode(
                    lzma.compress(json.dumps(m.contents).encode(),
                        preset = 9 | lzma.PRESET_EXTREME)
                ).decode()
                
                d["messages"].append({"contents": cont,
                                      "time": m.time,
                                      "on_right": m.on_right})

            data["chats"].append(d)

        data["token"] = self.token
        data["username"] = self.username
        data["private_key"] = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        self.secretmgr.save_data(json.dumps(data, indent=4),
                                 self.get_data_path("data"))
                

    def send(self, username: str, text: str):
        "Sends message"

        uinfo = self.communicator.get_user_info(username)

        if uinfo["publickey"]:

            text = self.secretmgr.encrypt_by_pem(text, uinfo["publickey"])

            self.save_chats()

            self.communicator.send(self.token, text, username, 
                                   time.strftime("%H:%M"), "user")

    def send_group(self, groupname: str, text: str):
        "Sends message to group"

        ginfo = self.communicator.get_group_info(groupname)

        contents = {}

        for user in ginfo["members"]:

            if user != self.username:
                uinfo = self.communicator.get_user_info(user)

                try:
                    if uinfo["publickey"]:
                        e_text = self.secretmgr.encrypt_by_pem(text, uinfo["publickey"])
                        contents[user] = e_text
                except:
                    pass

        self.save_chats()

        self.communicator.send(self.token, contents, groupname,
                               time.strftime("%H:%M"), "group")

        
    def get_data_path(self, filename: str = None):
        "Returns some path to data directory"

        if os.name == "nt":
            path = os.path.join(os.getenv("LOCALAPPDATA"),
                        "NixChat")
        elif os.name == "posix":
            path = os.path.join(os.getenv("HOME"),
                        ".local", "share", "NixChat")
        else:
            path = os.path.join("~", "NixChat")

        os.makedirs(path, exist_ok=True)

        if filename:
            path = os.path.join(path, filename)
        
        return path

    def update_keys(self):
        "Updates keys"

        if not self.private_key:
            self.private_key, public_key = self.secretmgr.make_msg_keys()
        else:
            _, public_key = self.secretmgr.make_msg_keys(self.private_key)

        self.communicator.set_my_info(self.token, {"publickey": public_key})

    def set_acc_pixmap(self, pixmap: bytes):
        "Set account pixmap"

        b64 = base64.b64encode(pixmap).decode()
        data = {"pixmap": b64}

        self.communicator.set_my_info(self.token, data)

    def get_acc_pixmap(self, username: str):
        "Get account pixmap"

        data = self.communicator.get_user_info(username)
        
        if stabilizer.check_getuserinfo_resp(data):
        
            pixmap = base64.b64decode(data["pixmap"])
            
            return pixmap

        return None

    def load_settings(self):
        "Loads settings"

        path = self.get_data_path("settings.json")

        self.settings = {
            "background": "1.jpg",
            "server": "https://Iamha111.pythonanywhere.com"
        }

        try:
            with open(path, "r") as f:
                data = json.load(f)

                for i in data:
                    self.settings[i] = data[i]

        except FileNotFoundError:
            self.save_settings()
            self.load_settings()
        except:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось прочитать конфигурацию."
            )

    def save_settings(self):
        "Saves settings"

        path = self.get_data_path("settings.json")
        
        try:
            with open(path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось сохранить конфигурацию."
            )

    def rmchat(self, name: str, group: bool = False):
        "Removes a chat"

        if group:
            self.messagemgr.remove_chat(name)
            self.communicator.remove_group(self.token, name)

        else:
            self.messagemgr.remove_chat(name)
            self.communicator.remove_chat(name, self.token)

    def panic(self, reason: str):
        "Panic"

        self.gui.show()

        if reason == "unsupported_version":
            Panic(self, "Неподдерживаемая версия клиента :(")
        elif reason == "failed_to_connect":
            Panic(self, "Не удалось подключиться к серверу :(")

        self.timer.stop()
            
            
        
if __name__ == "__main__":

    conf = {
        "enable-bg-worker": True,
        "start-hidden": False
    }

    # Here we will process arguments

    for arg in sys.argv:
        if arg in ["--help", "-h"]:
            print("NixChat version raw")
            print("Usage: nixchat [arguments]")
            print("Possible arguments:")
            print("  -h, --help: show this help")
            print("  -v, --version: display version")
            print("  -H, --start-hidden: start in hidden mode")
            print("      --disable-bg-worker: disable the background worker")
            quit()
        
        elif arg in ["--version", "-v"]:
            print("v1.0.1")
            quit()

        elif arg in ["--start-hidden", "-H"]:
            conf["start-hidden"] = True
            
        elif arg == "--disable-bg-worker":
            conf["enable-bg-worker"] = False
    
    core = Core(conf)
