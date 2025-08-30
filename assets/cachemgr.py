from assets.contentsmgr import ContentsManager

import hashlib
import base64
import os


def cache_contents(data, core):
    "Caches contents"

    contents = ContentsManager().import_contents(data)
    
    for i in contents:
        try:
            if i["type"] == "picture":
                i["data"] = core.cachemgr.add(
                    base64.b64decode(i["data"])
                )
        except:
            pass

    return contents


class CacheManager:
    def __init__(self, core):
        self.core = core
        self.data = {}
        self.load()

    def add(self, data: bytes):
        "Add some data"
        
        data_hash = hashlib.sha256(data).hexdigest()
        self.data[data_hash] = data
        self.save()
        return data_hash

    def get(self, data_hash: str):
        "Get data by its hash"

        try:
            return self.data[data_hash]
        except:
            return None

    def save(self):
        "Save cache"

        path = self.core.get_data_path("cache/")

        if not "cache" in os.listdir(self.core.get_data_path()):
            os.mkdir(path)
                    
        for item in self.data:
            try:
                with open(path + item, "wb") as f:
                    f.write(self.data[item])
            except:
                pass

    def load(self):
        "Load cache"

        path = self.core.get_data_path("cache/")

        if not "cache" in os.listdir(self.core.get_data_path()):
            os.mkdir(path)

        for item in os.listdir(path):
            try:
                with open(path + item, "rb") as f:
                    self.data[item] = f.read()
            except:
                pass
