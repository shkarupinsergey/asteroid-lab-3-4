"""Обработка изображений средствами стандартной библиотеки Python."""
import math
import struct
import zlib
import base64
import tkinter as tk
from pathlib import Path


def chunk(name, data):
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xffffffff)


class Image:
    class Resampling:
        LANCZOS = 1

    def __init__(self, width, height, rows):
        self.width = width
        self.height = height
        self.size = (width, height)
        self.rows = rows

    @classmethod
    def open(cls, path):
        # Tk декодирует PNG, включая прозрачность и палитру.
        photo = tk.PhotoImage(file=str(path))
        data = photo.tk.call(photo.name, "data", "-format", "png")
        if isinstance(data, str):
            data = base64.b64decode(data)
        pos = 8
        compressed = []
        while pos < len(data):
            n = struct.unpack_from(">I", data, pos)[0]
            kind = data[pos+4:pos+8]
            body = data[pos+8:pos+8+n]
            pos += n + 12
            if kind == b"IHDR":
                w, h, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
            elif kind == b"IDAT":
                compressed.append(body)
        channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color)
        if depth != 8 or interlace or channels is None:
            # Запасной вариант для редких форматов PNG.
            rows = []
            for y in range(photo.height()):
                row = bytearray()
                for x in range(photo.width()):
                    row.extend((*photo.get(x, y), 0 if photo.transparency_get(x, y) else 255))
                rows.append(bytes(row))
            return cls(photo.width(), photo.height(), rows)
        raw = zlib.decompress(b"".join(compressed))
        stride = w * channels
        rows = []
        prev = bytearray(stride)
        for y in range(h):
            start = y * (stride + 1)
            mode = raw[start]
            row = bytearray(raw[start+1:start+1+stride])
            if mode:
                for i in range(stride):
                    a = row[i-channels] if i >= channels else 0
                    b = prev[i]
                    c = prev[i-channels] if i >= channels else 0
                    if mode == 1:
                        v = a
                    elif mode == 2:
                        v = b
                    elif mode == 3:
                        v = (a+b)//2
                    else:
                        p = a+b-c
                        pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                        v = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                    row[i] = (row[i]+v) & 255
            prev = row
            if color == 6:
                rows.append(bytes(row))
            elif color == 2:
                rgba = bytearray(w*4)
                rgba[0::4], rgba[1::4], rgba[2::4] = row[0::3], row[1::3], row[2::3]
                rgba[3::4] = b"\xff"*w
                rows.append(bytes(rgba))
            else:
                rgba = bytearray(w*4)
                gray = row[::channels]
                rgba[0::4] = rgba[1::4] = rgba[2::4] = gray
                rgba[3::4] = row[1::2] if channels == 2 else b"\xff"*w
                rows.append(bytes(rgba))
        return cls(w, h, rows)

    def resize(self, size, resample=None):
        w, h = size
        if size == self.size:
            return self
        xs = [min(self.width-1, x*self.width//w)*4 for x in range(w)]
        cache = {}
        rows = []
        for y in range(h):
            sy = min(self.height-1, y*self.height//h)
            if sy not in cache:
                row = self.rows[sy]
                cache[sy] = b"".join(row[x:x+4] for x in xs)
            rows.append(cache[sy])
        return Image(w, h, rows)

    def rotate(self, angle, expand=True):
        a = math.radians(angle)
        c, s = math.cos(a), math.sin(a)
        w = max(1, math.ceil(abs(self.width*c)+abs(self.height*s)-1e-9))
        h = max(1, math.ceil(abs(self.width*s)+abs(self.height*c)-1e-9))
        rows = []
        for y in range(h):
            row = bytearray(w*4)
            dy = y-(h-1)/2
            for x in range(w):
                dx = x-(w-1)/2
                sx = round(c*dx-s*dy+(self.width-1)/2)
                sy = round(s*dx+c*dy+(self.height-1)/2)
                if 0 <= sx < self.width and 0 <= sy < self.height:
                    row[x*4:x*4+4] = self.rows[sy][sx*4:sx*4+4]
            rows.append(bytes(row))
        return Image(w, h, rows)

    def convert(self, mode):
        return Image(self.width, self.height, self.rows[:])

    def getdata(self):
        return [tuple(row[i:i+4]) for row in self.rows for i in range(0, len(row), 4)]

    def putdata(self, data):
        raw = bytes(v for pixel in data for v in pixel)
        stride = self.width*4
        self.rows = [raw[i:i+stride] for i in range(0, len(raw), stride)]

    def png(self):
        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0)
        raw = b"".join(b"\x00"+row for row in self.rows)
        return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR", header)+chunk(b"IDAT", zlib.compress(raw, 1))+chunk(b"IEND", b"")


class ImageTk:
    @staticmethod
    def PhotoImage(image):
        return tk.PhotoImage(data=base64.b64encode(image.png()).decode("ascii"), format="png")
