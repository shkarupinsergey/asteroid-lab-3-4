import math
import os
from tkinter import Canvas
from graphics import ImageTk
import config
from config import *


class Spaceship:
    _image_cache = {}
    _angle_cache = {}

    @classmethod
    def _get_rotated_image(cls, base_image, angle):
        cache_key = (id(base_image), angle)
        if cache_key not in cls._angle_cache:
            rotated = base_image.rotate(-angle, expand=True)
            cls._angle_cache[cache_key] = ImageTk.PhotoImage(rotated)
        return cls._angle_cache[cache_key]

    def __init__(self, canvas: Canvas, x, y, angle):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0
        self.max_speed = MAX_SPEED
        self.lifetime = SPACESHIP_LIFETIME
        self.engine_on = False

        self._init_images()

        self.id = self.canvas.create_image(
            self.x, self.y, image=self.current_image
        )

        self.deceleration_factor = 0.98
        self.min_speed = 0.1
        self.acceleration_step = 0.5

    def _init_images(self):
        self.current_image = self._get_rotated_image(
            config.SPACESHIP_IMAGE, self.angle
        )
        self.active_image = self._get_rotated_image(
            config.SPACESHIP_ACTIVE_IMAGE, self.angle
        )

    def set_image(self, image_change):
        self.current_image = self._get_rotated_image(image_change, self.angle)
        self.canvas.itemconfig(self.id, image=self.current_image)

    def accelerate(self):
        self.speed = min(self.speed + self.acceleration_step, self.max_speed)
        if not self.engine_on:
            self.set_image(config.SPACESHIP_ACTIVE_IMAGE)
            self.engine_on = True

    def decelerate(self):
        if self.engine_on:
            self.set_image(config.SPACESHIP_IMAGE)
            self.engine_on = False

    def rotate(self, delta_angle):
        self.angle = (self.angle + delta_angle) % 360
        self.set_image(
            config.SPACESHIP_ACTIVE_IMAGE if self.engine_on else config.SPACESHIP_IMAGE
        )

    def move(self):
        if self.speed == 0:
            return

        angle_rad = math.radians(self.angle)
        sin_angle = math.sin(angle_rad)
        cos_angle = math.cos(angle_rad)

        dx = self.speed * sin_angle
        dy = -self.speed * cos_angle

        self.x += dx
        self.y += dy

        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()
        self.x = self.x % screen_width
        self.y = self.y % screen_height

        self.canvas.coords(self.id, self.x, self.y)

        if not self.engine_on:
            self.speed *= self.deceleration_factor
            if self.speed < self.min_speed:
                self.speed = 0

    def collides_with(self, asteroid):
        dx = self.x - asteroid.x
        dy = self.y - asteroid.y
        distance_squared = dx * dx + dy * dy
        collision_distance = asteroid.size
        return distance_squared < collision_distance * collision_distance

    def destroy(self):
        self.canvas.delete(self.id)
