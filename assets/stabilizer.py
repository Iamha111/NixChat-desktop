def check_sync_data(info):
    "Checks synced data"

    r = "unknown"

    if type(info) == dict:
        if "msg" in info:
            if info["msg"] == "Signature verification failed":
                r = "jwt_fail"
        elif "chats" in info and "messages" in info:
            r = "ok"
    else:
        if info == "Communication failed":
            r = "comm_failed"
    return r


def check_getuserinfo_resp(data):
    "Checks getuserinfo's response"

    r = True

    if data:
        for i in ["username", "rank", "publickey", "msg"]:
            if not i in data:
                r = False
            else:
                if i == "msg":
                    if data["msg"] != "Success":
                        r = False
    else:
        r = False

    return r


def check_server_resp(response, core):
    "Checks server's common response"
    r = True

    if response != None and response.status_code != 500:
        data = response.json()

        if not "msg" in data:
            r = False
        else:
            if data["msg"] == "Unsupported API version":
                r = False
                core.panic("unsupported_version")
    else:
        r = False
        core.panic("failed_to_connect")
            
    return r
