import math
from tkinter import Canvas
from PIL import Image, ImageTk

class Rocket:
    def __init__(self, canvas: Canvas, x, y, angle):
        self.canvas = canvas
        self.x = x
        self.y = y
        
        angle_rad = math.radians(angle)
        self.sin_angle = math.sin(angle_rad)
        self.cos_angle = math.cos(angle_rad)
        
        self.speed = 10
        self.lifetime = 50
        
        radius = 5
        self.id = self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill="red",
            outline="red"
        )
        
        self.dx = self.speed * self.sin_angle
        self.dy = -self.speed * self.cos_angle
        
    def move(self):
        if self.lifetime <= 0:
            self.destroy()
            return
            
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        
        self.canvas.move(self.id, self.dx, self.dy)
        
    def collides_with(self, asteroid):
        dx = self.x - asteroid.x
        dy = self.y - asteroid.y
        distance_squared = dx * dx + dy * dy
        collision_distance = asteroid.size
        return distance_squared < collision_distance * collision_distance

    def destroy(self):
        self.canvas.delete(self.id)
