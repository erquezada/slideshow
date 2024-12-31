import os
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL, Toplevel
from tkinter import ttk
from PIL import Image, ImageTk
import random


class SlideshowViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Slideshow Viewer")

        # Initialize variables
        self.image_list = []
        self.current_index = 0
        self.auto_play = False
        self.is_fullscreen = False
        self.zoom_factor = 1.0
        self.auto_play_interval = 3000
        self.is_shuffled = False
        self.top_expansion = 0
        self.bottom_expansion = 0
        self.left_expansion = 0
        self.right_expansion = 0

        # Create GUI components
        self.label = Label(self.root)
        self.label.pack(fill="both", expand=True)

        # Manually place buttons
        self.create_buttons()

        # Create sliders and progress bar
        self.create_slider()
        self.create_progress_bar()

        # Create resizing sliders for top, bottom, left, right
        self.create_expansion_sliders()

        # Add keyboard bindings for navigation
        self.root.bind("<Left>", self.show_previous)
        self.root.bind("<Right>", self.show_next)
        self.root.bind("<space>", self.toggle_auto_play)

        self.load_images()

    def create_buttons(self):
        # Manually placing buttons using place()
        button_positions = {
            "prev": (10, 10),
            "next": (100, 10),
            "play": (200, 10),
            "fullscreen": (300, 10),
            "shuffle": (400, 10),
            "zoom_in": (500, 10),
            "zoom_out": (600, 10),
            "rotate": (700, 10),
            "close": (800, 10),
        }

        button_texts = {
            "prev": "Previous",
            "next": "Next",
            "play": "Play",
            "fullscreen": "Fullscreen",
            "shuffle": "Shuffle",
            "zoom_in": "Zoom In",
            "zoom_out": "Zoom Out",
            "rotate": "Rotate",
            "close": "Close"
        }

        self.buttons = {}
        for button_name, (x, y) in button_positions.items():
            button = Button(self.root, text=button_texts[button_name], command=getattr(self, f"command_{button_name}"))
            button.place(x=x, y=y)
            self.set_transparency(button)
            self.buttons[button_name] = button

        # Bind the hover events to make buttons visible when hovered over
        for button in self.buttons.values():
            button.bind("<Enter>", self.on_hover)
            button.bind("<Leave>", self.on_leave)

    def set_transparency(self, button):
        # Initially set the button background to transparent-like effect
        button.config(bg=self.root.cget("bg"))
        button.config(activebackground=self.root.cget("bg"))
        button.config(relief="flat")

    def on_hover(self, event):
        # Make the button fully visible on hover
        event.widget.config(bg="lightblue", activebackground="lightblue")

    def on_leave(self, event):
        # Return to the transparent state when the mouse leaves
        self.set_transparency(event.widget)

    def create_slider(self):
        self.speed_slider = Scale(self.root, from_=500, to_=5000, orient=HORIZONTAL, label="Slideshow Speed (ms)")
        self.speed_slider.set(self.auto_play_interval)
        self.speed_slider.place(x=10, y=50)

    def create_progress_bar(self):
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.place(x=10, y=100)

        self.remaining_label = Label(self.root, text="")
        self.remaining_label.place(x=10, y=150)

    def create_expansion_sliders(self):
        # Create sliders for expanding the image on each side (top, bottom, left, right)
        self.top_slider = Scale(self.root, from_=0, to_=300, orient=HORIZONTAL, label="Top Expansion")
        self.top_slider.place(x=10, y=200)
        self.top_slider.set(self.top_expansion)

        self.bottom_slider = Scale(self.root, from_=0, to_=300, orient=HORIZONTAL, label="Bottom Expansion")
        self.bottom_slider.place(x=10, y=250)
        self.bottom_slider.set(self.bottom_expansion)

        self.left_slider = Scale(self.root, from_=0, to_=300, orient=HORIZONTAL, label="Left Expansion")
        self.left_slider.place(x=10, y=300)
        self.left_slider.set(self.left_expansion)

        self.right_slider = Scale(self.root, from_=0, to_=300, orient=HORIZONTAL, label="Right Expansion")
        self.right_slider.place(x=10, y=350)
        self.right_slider.set(self.right_expansion)

    def load_images(self):
        folder_window = Toplevel(self.root)
        folder_window.title("Select Folder")
        folder_window.geometry("300x100")

        select_button = Button(folder_window, text="Select Folder", command=self.select_folder)
        select_button.pack(pady=10)

        close_button = Button(folder_window, text="Close Program", command=self.root.quit)
        close_button.pack(pady=5)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        if not folder_path:
            print("No folder selected.")
            return

        supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
        self.image_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(supported_formats)]

        if not self.image_list:
            print("No supported image files found.")
            return

        if self.is_shuffled:
            random.shuffle(self.image_list)

        # Directly cache the resized images (resize only if needed)
        self.image_cache = [ImageTk.PhotoImage(self.resize_image(Image.open(image_path))) for image_path in self.image_list]

        self.update_progress_bar()
        self.show_image()

    def resize_image(self, image):
        # Resize the image with new dimensions, using the slider values
        top_expansion = self.top_slider.get()
        bottom_expansion = self.bottom_slider.get()
        left_expansion = self.left_slider.get()
        right_expansion = self.right_slider.get()

        width, height = image.size
        new_width = width + left_expansion + right_expansion
        new_height = height + top_expansion + bottom_expansion

        expanded_image = Image.new("RGB", (new_width, new_height), (255, 255, 255))  # White background
        expanded_image.paste(image, (left_expansion, top_expansion))
        return expanded_image

    def show_image(self):
        if self.image_list:
            photo = self.image_cache[self.current_index]
            self.label.config(image=photo)
            self.label.image = photo
        self.update_progress_bar()

    def update_progress_bar(self):
        if self.image_list:
            progress = (self.current_index + 1) / len(self.image_list) * 100
            self.progress_bar["value"] = progress
            remaining = len(self.image_list) - (self.current_index + 1)
            self.remaining_label.config(text=f"{remaining} images remaining")

    def show_next(self, event=None):
        if self.image_list:
            self.current_index = (self.current_index + 1) % len(self.image_list)
            self.show_image()

    def show_previous(self, event=None):
        if self.image_list:
            self.current_index = (self.current_index - 1) % len(self.image_list)
            self.show_image()

    def toggle_auto_play(self):
        self.auto_play = not self.auto_play
        self.buttons["play"].config(text="Stop" if self.auto_play else "Play")
        if self.auto_play:
            self.auto_play_interval = self.speed_slider.get()
            self.auto_play_images()

    def auto_play_images(self):
        if self.auto_play and self.image_list:
            self.show_next()
            self.root.after(self.auto_play_interval, self.auto_play_images)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        self.root.geometry("1040x720" if not self.is_fullscreen else "")
        self.show_image()

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.show_image()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.show_image()

    def rotate_image(self):
        image = Image.open(self.image_list[self.current_index])
        rotated_image = image.rotate(90, expand=True)
        self.image_cache[self.current_index] = ImageTk.PhotoImage(rotated_image)
        self.show_image()

    def toggle_shuffle(self):
        self.is_shuffled = not self.is_shuffled
        if self.is_shuffled:
            random.shuffle(self.image_list)
        self.show_image()

    def close_application(self):
        self.root.quit()


if __name__ == "__main__":
    root = Tk()
    app = SlideshowViewer(root)
    root.mainloop()
