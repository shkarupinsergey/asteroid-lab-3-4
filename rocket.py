import math
from tkinter import Canvas
from config import ROCKET_MAX_TICKS, ROCKET_SPEED


class Rocket:
    def __init__(self, canvas: Canvas, x, y, angle):
        self.canvas = canvas
        self.width = canvas.winfo_width()
        self.height = canvas.winfo_height()
        self.x = x % self.width
        self.y = y % self.height

        angle_rad = math.radians(angle)
        self.sin_angle = math.sin(angle_rad)
        self.cos_angle = math.cos(angle_rad)

        self.speed = ROCKET_SPEED
        shortest_side = min(self.width, self.height)
        self.lifetime = min(
            ROCKET_MAX_TICKS, (shortest_side - 1) // self.speed
        )

        self.radius = 5
        self.id = self.canvas.create_oval(
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
            fill="red",
            outline="red"
        )

        self.dx = self.speed * self.sin_angle
        self.dy = -self.speed * self.cos_angle

    def move(self):
        self.x = (self.x + self.dx) % self.width
        self.y = (self.y + self.dy) % self.height
        self.lifetime -= 1

        self.canvas.coords(
            self.id,
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
        )

    def collides_with(self, asteroid):
        dx = abs(self.x - asteroid.x) % self.width
        dy = abs(self.y - asteroid.y) % self.height
        dx = min(dx, self.width - dx)
        dy = min(dy, self.height - dy)
        distance_squared = dx * dx + dy * dy
        collision_distance = asteroid.size
        return distance_squared < collision_distance * collision_distance

    def destroy(self):
        self.canvas.delete(self.id)
