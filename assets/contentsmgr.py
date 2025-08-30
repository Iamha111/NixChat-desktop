from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QBuffer, QByteArray, QIODevice

import json
import base64
import lzma


class ContentsManager:
    def __init__(self):
        self.contents = []

    def add_text(self, data: str):
        "Adds text content"

        c = {
            "type": "text",
            "data": data
        }

        self.contents.append(c)

    def add_picture(self):
        "Select and add a picture"

        pathes, _ = QFileDialog.getOpenFileNames(
            caption="Выберите картинки",
            dir=""
        )

        if pathes:
            for path in pathes:
                try:
                    pixmap = QPixmap(path)
                    byte_array = QByteArray()
                    buffer = QBuffer(byte_array)
                    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                    pixmap.save(buffer, path.split(".")[-1].upper())
                    buffer.close()

                    c = {
                        "type": "picture",
                        "data": base64.b64encode(byte_array).decode()
                    }

                    self.contents.append(c)
                except ArithmeticError:
                    pass

    def add_file(self):
        "Select and add a file"

    def export_contents(self):
        "Exports and compresses contents"

        data = json.dumps(self.contents)
        data = lzma.compress(data.encode(), preset=9 | lzma.PRESET_EXTREME)
        
        return base64.b64encode(data).decode()

    def import_contents(self, contents: bytes):
        "Imports contents"

        try:
            contents = base64.b64decode(contents)
            data = json.loads(lzma.decompress(contents))
        except ArithmeticError:
            data = []

        return data

    def clear(self):
        "Clear"

        self.contents = []
