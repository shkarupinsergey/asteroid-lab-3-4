import tkinter as tk

from PIL import Image, ImageTk

from config import FULLSCREEN, GAME_TITLE, START_BACKGROUND_IMAGE


def main():
    window = tk.Tk()
    window.title(GAME_TITLE)
    window.attributes("-fullscreen", FULLSCREEN)
    window.bind("<Escape>", lambda event: window.destroy())

    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    background = START_BACKGROUND_IMAGE.resize(
        (width, height), Image.Resampling.LANCZOS
    )
    image = ImageTk.PhotoImage(background, master=window)

    canvas = tk.Canvas(window, bd=0, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_image(0, 0, anchor=tk.NW, image=image)
    canvas.create_text(width // 2, height // 2, text=GAME_TITLE.upper(),
                       font=("Arial", 52, "bold"), fill="white")
    window.mainloop()


if __name__ == "__main__":
    main()
