import math
import random
import tkinter as tk
from tkinter import font as tkfont

from PIL import Image, ImageTk

from spaceship import Spaceship
from asteroid import Asteroid
from rocket import Rocket
from config import *

class AsteroidGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", FULLSCREEN)
        self.title(GAME_TITLE)

        self._cache_resources()

        self._bind_events()

        self._init_game_vars()

        self.start_screen()

    def _cache_resources(self):
        self.ui_font = tkfont.nametofont("TkDefaultFont", root=self).actual("family")
        self.load_background_image()

        self.life_image_tk = ImageTk.PhotoImage(LIFE_IMAGE)

    def _bind_events(self):
        self.protocol("WM_DELETE_WINDOW", self.exit_game)
        self.bind("<Escape>", self.exit_game)
        self.bind("<Return>", self.game_screen)

    def _init_game_vars(self):
        self.start_frame = None
        self.game_frame = None
        self.rockets = []
        self.asteroids = []
        self.asteroid_speed_multiplier = ASTEROID_SPEED_MULTIPLIER
        self.score = 0
        self.lives = 3
        self.life_images = []
        self.game_running = True

    def exit_game(self, event=None):
        if self.start_frame is not None:
            self.start_frame.after_cancel(self.start_animation)
        self.destroy()

    def load_background_image(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        scaled_image = START_BACKGROUND_IMAGE.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(scaled_image)
        scaled_image = GAME_BACKGROUND_IMAGE.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.game_bg_image = ImageTk.PhotoImage(scaled_image)

    def start_screen(self):
        self.start_frame = tk.Canvas(self, bd=0, highlightthickness=0)
        self.start_frame.pack(fill=tk.BOTH, expand=True)

        self.asteroids_on_start_screen = []

        self.start_frame.create_image(0, 0, anchor=tk.NW, image=self.bg_image)


        for _ in range(15):
            x = self.winfo_screenwidth() - 1
            y = random.randint(0, self.winfo_screenheight())
            asteroid = Asteroid(self.start_frame, x, y,
                                game_running=False)
            asteroid.image = asteroid.image.convert("RGBA")
            data = asteroid.image.getdata()
            new_data = []
            for item in data:
                new_data.append((item[0], item[1], item[2], int(item[3] * 0.45)))
            asteroid.image.putdata(new_data)

            asteroid.image_tk = ImageTk.PhotoImage(asteroid.image)
            asteroid.id = self.start_frame.create_image(asteroid.x, asteroid.y,
                                                        image=asteroid.image_tk)
            self.asteroids_on_start_screen.append(asteroid)


        def move_asteroids():
            for asteroid in self.asteroids_on_start_screen:
                asteroid.move()
            self.start_animation = self.start_frame.after(10, move_asteroids)

        self.start_animation = self.start_frame.after(100, move_asteroids)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        title_size = min(64, max(20, screen_width // 20))
        self.start_frame.create_text(
            screen_width // 2,
            screen_height // 2 - 63,
            text=GAME_TITLE.upper(),
            font=(self.ui_font, -title_size, "bold"),
            width=screen_width * 9 // 10,
            justify=tk.CENTER,
            fill="white",
            tags="start"
        )

        self.start_frame.tag_bind(
            "start", "<Button-1>", self.game_screen
        )

        self.start_frame.create_text(
            screen_width // 2,
            screen_height // 2 + 55,
            text="Enter — начать игру",
            font=(self.ui_font, 24),
            fill="white"
        )

    def game_screen(self, event=None):
        if self.game_frame is not None:
            return
        self.unbind("<Return>")
        if self.start_frame is not None:
            self.start_frame.after_cancel(self.start_animation)
            self.start_frame.destroy()
            self.start_frame = None

        self.game_frame = tk.Canvas(self, bd=0, highlightthickness=0)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        self.game_frame.create_image(0, 0, anchor=tk.NW, image=self.game_bg_image)

        for i in range(self.lives):
            life_image = self.game_frame.create_image(
                40 + i * 40, 40,
                anchor=tk.NW,
                image=self.life_image_tk
            )
            self.life_images.append(life_image)

        self.spaceship = Spaceship(self.game_frame, self.winfo_screenwidth() // 2,
                                   self.winfo_screenheight() // 2, 0)

        self.score_label = self.game_frame.create_text(
            self.winfo_screenwidth() - 40, 40,
            text=f"Счёт: {self.score}", fill="white",
            font=(self.ui_font, 24, "bold"), anchor=tk.E
        )

        self.bind("<Left>", lambda e: self.spaceship.rotate(-15))
        self.bind("<Right>", lambda e: self.spaceship.rotate(15))
        self.bind("<Up>", lambda e: self.spaceship.accelerate())
        self.bind("<KeyRelease-Up>", lambda e: self.spaceship.decelerate())
        self.bind("<space>", self.fire_rocket)

        self.update_game()

    def update_lives(self):
        for i, life_image in enumerate(self.life_images):
            if i < self.lives:
                self.game_frame.itemconfigure(life_image, state='normal')
            else:
                self.game_frame.itemconfigure(life_image, state='hidden')

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1
            self.update_lives()

            if self.lives <= 0:
                self.game_over()
            else:
                self.reset_player_position()


    def reset_player_position(self):
        self.spaceship.x = self.winfo_screenwidth() // 2
        self.spaceship.y = self.winfo_screenheight() // 2
        self.spaceship.speed = 0
        self.spaceship.angle = 0
        self.spaceship.set_image(SPACESHIP_IMAGE)
        self.game_frame.coords(self.spaceship.id, self.spaceship.x, self.spaceship.y)

    def update_score(self):
        self.score += 1
        if self.score % 5 == 0:
            self.asteroid_speed_multiplier += 1
        self.game_frame.itemconfig(self.score_label, text=f"Счёт: {self.score}")



    def fire_rocket(self, event=None):
        current_coords = self.game_frame.coords(self.spaceship.id)
        if not current_coords:
            return

        x, y = current_coords

        angle_rad = math.radians(self.spaceship.angle)

        nose_x = x + (SPACESHIP_IMAGE.width / 2 + 22) * math.sin(angle_rad)
        nose_y = y - (SPACESHIP_IMAGE.height / 2) * math.cos(angle_rad)

        rocket = Rocket(self.game_frame, nose_x, nose_y, self.spaceship.angle)
        self.rockets.append(rocket)

    def check_collisions(self):
        rockets_to_remove = []
        asteroids_to_remove = []

        for rocket in self.rockets:
            for asteroid in self.asteroids:
                if rocket.collides_with(asteroid):
                    rockets_to_remove.append(rocket)
                    asteroids_to_remove.append(asteroid)
                    self.update_score()
                    break

        for asteroid in self.asteroids:
            if self.spaceship.collides_with(asteroid):
                self.lose_life()
                asteroids_to_remove.append(asteroid)
                break

        for rocket in rockets_to_remove:
            if rocket in self.rockets:
                rocket.destroy()
                self.rockets.remove(rocket)

        for asteroid in asteroids_to_remove:
            if asteroid in self.asteroids:
                asteroid.destroy()
                self.asteroids.remove(asteroid)

    def update_game(self):
        if not self.game_running:
            return

        self.spaceship.move()

        self._update_rockets()

        self._update_asteroids()

        self.check_collisions()

        if self.game_running:
            self.after(16, self.update_game)

    def _update_rockets(self):
        for rocket in self.rockets[:]:
            if rocket.lifetime > 0:
                rocket.move()
            else:
                rocket.destroy()
                self.rockets.remove(rocket)

    def _update_asteroids(self):
        if len(self.asteroids) < 10 + self.score // 10:
            self._spawn_asteroid()

        for asteroid in self.asteroids[:]:
            asteroid.move()

    def _spawn_asteroid(self):
        x = self._spawn_coordinate(self.winfo_screenwidth(), 100)
        y = self._spawn_coordinate(self.winfo_screenheight(), 150)
        asteroid = Asteroid(self.game_frame, x, y, self.asteroid_speed_multiplier, game_running=True)
        self.asteroids.append(asteroid)

    @staticmethod
    def _spawn_coordinate(length, margin):
        center = length // 2
        margin = min(margin, length // 4)
        if random.choice((True, False)):
            return random.randint(0, center - margin)
        return random.randint(center + margin, length)

    def game_over(self):
        self.game_running = False

        for asteroid in self.asteroids:
            if asteroid.id in self.game_frame.find_all():
                asteroid.delayed_destroy()
                self.game_frame.delete(asteroid.id)
        self.asteroids.clear()

        for rocket in self.rockets:
            rocket.destroy()
        self.rockets.clear()

        self.game_frame.delete(self.spaceship.id)

        self.game_frame.delete("all")
        self.game_frame.create_image(0, 0, anchor=tk.NW, image=self.bg_image)

        self.game_frame.create_text(
            self.winfo_screenwidth() // 2,
            self.winfo_screenheight() // 2 - 50,
            text=f"Игра окончена\nСчёт: {self.score}",
            font=(self.ui_font, 36),
            fill="white",
            justify=tk.CENTER
        )

        self.game_frame.create_text(
            self.winfo_screenwidth() // 2,
            self.winfo_screenheight() // 2 + 100,
            text="Enter — сыграть снова, Esc — выйти",
            font=(self.ui_font, 20),
            fill="white"
        )

        self.bind("<Return>", self.restart_game)
        self.bind("<Escape>", self.exit_game)

    def restart_game(self, event=None):
        self.game_frame.destroy()
        self.game_frame = None

        self.score = 0
        self.lives = 3
        self.asteroid_speed_multiplier = ASTEROID_SPEED_MULTIPLIER
        self.life_images = []

        self.asteroids = []
        self.rockets = []

        self.game_running = True
        self.game_screen()


if __name__ == "__main__":
    game = AsteroidGame()
    game.mainloop()
