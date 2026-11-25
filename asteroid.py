import random
import os
from tkinter import Canvas
from PIL import Image, ImageTk
from config import *


class Asteroid:
    _cached_images = {}
    _size_ranges = [(30, 50), (51, 70), (71, 90)] 
    _destroy_image_cache = {}

    @classmethod
    def _get_cached_image(cls, size, use_cache=True):
        size_range = next(r for r in cls._size_ranges if r[0] <= size <= r[1])
        if use_cache and size_range in cls._cached_images:
            return cls._cached_images[size_range]

        base_image = random.choice(ASTEROID_IMAGES)
        avg_size = sum(size_range) // 2
        resized_image = base_image.resize((avg_size, avg_size))
        if use_cache:
            cls._cached_images[size_range] = resized_image
        return resized_image

    def __init__(self, canvas: Canvas, x, y, speed_multiplier=1, game_running=False):
        self.canvas = canvas
        self.x = x
        self.y = y
        
        self.size = random.randint(30, 90)
        self.speed_multiplier = speed_multiplier
        
        self._init_speed()
        
        self.game_running = game_running
        
        self.image = self._get_cached_image(self.size)
        if self.size != self.image.size[0]:
            self.image = self.image.resize((self.size, self.size))
        self.image_tk = ImageTk.PhotoImage(self.image)
        
        self.id = self.canvas.create_image(x, y, image=self.image_tk)
        
        if self.size not in self._destroy_image_cache:
            self._destroy_image_cache[self.size] = ImageTk.PhotoImage(
                ASTEROID_DESTROY_IMAGE.resize((self.size, self.size))
            )
        self.image_destroy_tk = self._destroy_image_cache[self.size]
        
    def _init_speed(self):
        min_speed, max_speed = -3, 3
        min_abs_speed = 1
        
        self.speed_x = random.uniform(min_speed, max_speed)
        while abs(self.speed_x) < min_abs_speed:
            self.speed_x = random.uniform(min_speed, max_speed)
            
        self.speed_y = random.uniform(min_speed, max_speed)
        while abs(self.speed_y) < min_abs_speed:
            self.speed_y = random.uniform(min_speed, max_speed)
            
    def move(self):
        if not self.game_running:
            self.speed_x = -abs(self.speed_x)
            self.speed_y = 0
            
        self.x += self.speed_x * self.speed_multiplier
        if self.game_running:
            self.y += self.speed_y * self.speed_multiplier
            
        if self.canvas.winfo_exists():
            screen_width = self.canvas.winfo_width()
            screen_height = self.canvas.winfo_height()
        else:
            screen_width = 1920
            screen_height = 1080
        
        self.x = self.x % screen_width
        if self.game_running:
            self.y = self.y % screen_height
            
        try:
            self.canvas.coords(self.id, self.x, self.y)
            bbox = self.canvas.bbox(self.id)
            if bbox and self.game_running:
                self.x, self.y = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        except:
            return

    def destroy(self):
        self.canvas.itemconfig(self.id, image=self.image_destroy_tk)
        self.canvas.winfo_toplevel().after(800, self.delayed_destroy)

    def delayed_destroy(self):
        if self.canvas.winfo_exists():
            self.canvas.delete(self.id)
