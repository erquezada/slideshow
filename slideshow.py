import os
import threading
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL, messagebox
from tkinter import ttk  # For progress bar
from PIL import Image, ImageTk
import random  # For shuffling images
from concurrent.futures import ThreadPoolExecutor


class SlideshowViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Slideshow")
        self.image_list = []
        self.current_index = 0
        self.image_cache = {}
        self.auto_play = False
        self.is_fullscreen = False
        self.zoom_factor = 1.0
        self.auto_play_interval = 2500
        self.is_shuffled = False
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.cache_lock = threading.Lock()
        self.inactivity_timer = None
        self.inactivity_delay = 5000  # 5 seconds

        # Create GUI components
        self.label = Label(self.root)
        self.label.pack(fill="both", expand=True)
        self.create_controls()
        self.load_images()

        # Bind keyboard and mouse events
        self.root.bind("<Left>", self.show_previous)
        self.root.bind("<Right>", self.show_next)
        self.root.bind("<space>", self.toggle_auto_play)
        self.root.bind("<Up>", lambda e: self.zoom_in())
        self.root.bind("<Down>", lambda e: self.zoom_out())
        self.root.bind("f", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.bind("<Motion>", self.reset_inactivity_timer)
        self.root.bind("<KeyPress>", self.reset_inactivity_timer)
        self.root.bind("<ButtonPress>", self.reset_inactivity_timer)

    def create_controls(self):
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.buttons = {
            "Previous": self.show_previous,
            "Play": self.toggle_auto_play,
            "Next": self.show_next,
            "Fullscreen": self.toggle_fullscreen,
            "Shuffle": self.toggle_shuffle,
            "Zoom In": self.zoom_in,
            "Zoom Out": self.zoom_out,
            "Close": self.root.quit,
        }

        for i, (text, command) in enumerate(self.buttons.items()):
            btn = Button(self.button_frame, text=text, command=command)
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=5)

        self.slider = Scale(
            self.root, from_=0, to=100, orient=HORIZONTAL, command=self.update_image
        )
        self.slider.pack(fill="x", pady=10)

        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", length=400, mode="determinate"
        )
        self.progress_bar.pack(pady=5)

        self.interval_slider = Scale(
            self.root, from_=1000, to=10000, orient=HORIZONTAL, label="Autoplay Interval (ms)",
        )
        self.interval_slider.set(self.auto_play_interval)
        self.interval_slider.pack(pady=10)

    def load_images(self):
        # Prompt the user to select a folder
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        if not folder_path:
            print("No folder selected. Exiting program.")
            self.root.quit()
            return

        supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
        self.image_list = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(supported_formats)
        ]

        if not self.image_list:
            print("No supported images found in the selected folder.")
            messagebox.showerror("Error", "No supported images found. Please try another folder.")
            self.load_images()
            return

        if self.is_shuffled:
            random.shuffle(self.image_list)

        self.slider.config(to=len(self.image_list) - 1)
        self.load_image(0)

    def load_image(self, index):
        with self.cache_lock:
            if index not in self.image_cache:
                self.executor.submit(self.cache_image, index)
            else:
                self.root.after(0, self.show_image, index)

    def cache_image(self, index):
        try:
            if index < 0 or index >= len(self.image_list):
                return

            img = Image.open(self.image_list[index])
            img_resized = self.resize_image(img)
            photo = ImageTk.PhotoImage(img_resized)

            with self.cache_lock:
                self.image_cache[index] = photo

            if index == self.current_index:
                self.root.after(0, self.show_image, index)
        except Exception as e:
            print(f"Error caching image at index {index} ({self.image_list[index]}): {e}")

    def resize_image(self, image):
        window_width, window_height = self.root.winfo_width(), self.root.winfo_height()
        img_width, img_height = image.size
        scale = min(window_width / img_width, window_height / img_height)
        new_width = int(img_width * scale * self.zoom_factor)
        new_height = int(img_height * scale * self.zoom_factor)
        return image.resize((new_width, new_height), Image.LANCZOS)

    def show_image(self, index):
        if index in self.image_cache:
            self.label.config(image=self.image_cache[index])
            self.label.image = self.image_cache[index]
            self.slider.set(index)
            self.update_progress_bar()

    def show_next(self, event=None):
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.load_image(self.current_index)
        print(f"{self.current_index + 1}/{len(self.image_list)} images shown")

    def show_previous(self, event=None):
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.load_image(self.current_index)

    def toggle_auto_play(self, event=None):
        self.auto_play = not self.auto_play
        if self.auto_play:
            self.auto_play_images()

    def auto_play_images(self):
        if not self.auto_play:
            return

        # Check if we reached the last image
        if self.current_index == len(self.image_list) - 1:
            self.auto_play = False  # Stop autoplay
            messagebox.showinfo("Slideshow Complete", "Slideshow has finished playing all images.")
            self.root.quit()  # Close the application
            return

        self.show_next()
        self.auto_play_interval = self.interval_slider.get()

        self.root.after(self.auto_play_interval, self.auto_play_images)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            self.button_frame.pack_forget()
        else:
            self.button_frame.pack(pady=10)

    def toggle_shuffle(self):
        self.is_shuffled = not self.is_shuffled
        if self.is_shuffled:
            random.shuffle(self.image_list)
        self.load_image(0)

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.load_image(self.current_index)

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.load_image(self.current_index)

    def update_image(self, value):
        self.current_index = int(value)
        self.load_image(self.current_index)

    def update_progress_bar(self):
        progress = (self.current_index + 1) / len(self.image_list) * 100
        self.progress_bar["value"] = progress

    def hide_cursor(self):
        """Hides the cursor after a period of inactivity."""
        self.root.config(cursor="none")

    def show_cursor(self):
        """Shows the cursor when there's activity."""
        self.root.config(cursor="")


    def reset_inactivity_timer(self, event=None):
        """Resets the inactivity timer and shows the cursor."""
        self.show_cursor()
        if self.inactivity_timer is not None:
            self.root.after_cancel(self.inactivity_timer)
        self.inactivity_timer = self.root.after(self.inactivity_delay, self.hide_cursor)


if __name__ == "__main__":
    root = Tk()
    app = SlideshowViewer(root)
    root.mainloop()
