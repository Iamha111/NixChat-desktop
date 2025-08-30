from assets.stabilizer import check_server_resp

import requests


class Communicator:
    def __init__(self, server, core):
        self.core = core
        self.server = server
        
    def contact(self, method: str, payload: dict = {}, headers: dict = {}):
        "Contacts the server"

        json = {
            "version": "1.0.0",
            "method": method,
            "payload": payload
        }

        try:
            r = requests.post(self.server, json=json, headers=headers)
        except:
            r = None

        check_server_resp(r, self.core)
        return r
        

    def register(self, username: str,
                       password: str):
        "Register an user"

        payload = {"username": username,
                   "password": password}
        resp = self.contact("register", payload)
                                        
        return resp.json() if resp else {}

    def login(self, username: str,
                    password: str):
        "Logins"

        payload = {"username": username,
                   "password": password}
                   
        resp = self.contact("login", payload)

        token = None
        if resp:
            if resp.json()["msg"] == "Success":
                token = resp.json()["token"]

        return token

    def sync(self, token):
        "Get basic user information"

        headers = {"Authorization": f"Bearer {token}"}
        
        resp = self.contact("sync", headers=headers)
        
        return resp.json() if resp else {}

    def get_my_info(self, token):
        "Get info about user"

        headers = {"Authorization": f"Bearer {token}"}

        resp = self.contact("get_my_info", headers=headers)

        return resp.json() if resp else {}

    def set_my_info(self, token, payload: dict):
        "Get info about user"
    
        headers = {"Authorization": f"Bearer {token}"}
    
        resp = self.contact("set_my_info", payload, headers)
    
        return resp.json() if resp else {}

    def clear_messages(self, token):
        "Clears messages"
        
        headers = {"Authorization": f"Bearer {token}"}

        resp = self.contact("clear_messages", headers=headers)

        return resp.json() if resp else {}

    def send(self, token, text: str, user: str, date: str,
                usertype: str = "user"):
        "Sends message"

        payload = {"message": {"to": user,
                               "contents": text,
                               "date": date},
                   "receiver_type": usertype}

        headers = {"Authorization": f"Bearer {token}"}

        resp = self.contact("send", payload, headers)

        return resp.json() if resp else {}

    def get_user_info(self, username: str):
        "Return user's public info"

        resp = self.contact(
            "get_user_info",
            payload={"user": username}
        )

        return resp.json() if resp else {}
        
    def remove_user(self, token):
        "Removes user"

        headers = {"Authorization": f"Bearer {token}"}
        
        resp = self.contact("remove_user", headers=headers)

        return resp.json() if resp else {}

    def remove_chat(self, name: str, token):
        "Removes a chat"

        headers = {"Authorization": f"Bearer {token}"}

        payload = {"name": name}

        resp = self.contact("remove_chat", payload, headers)
        
        return resp.json() if resp else {}

    def add_group(self, token, name: str, pixmap = None):
        "Adds a group"
    
        headers = {"Authorization": f"Bearer {token}"}
    
        payload = {"name": name}

        if pixmap:
            payload["pixmap"] = pixmap
                    
        resp = self.contact("add_group", payload, headers)
            
        return resp.json() if resp else {}

    def remove_group(self, token, name: str):
        "Removes a group"
    
        headers = {"Authorization": f"Bearer {token}"}
    
        payload = {"name": name}
                    
        resp = self.contact("remove_group", payload, headers)
            
        return resp.json() if resp else {}
    
    def get_group_info(self, name: str):
        "Return group info"

        payload = {"name": name}

        resp = self.contact("get_group_info", payload)

        return resp.json() if resp else {}

    def add_group_member(self, group: str, username: str):
        "Adds a group member"

        payload = {"group": group, "user": username}

        resp = self.contact("add_group_member", payload)

        return resp.json() if resp else {}

    def ping(self):
        "Pings server"

        resp = self.contact("ping")
        return resp.json() if resp else {}
