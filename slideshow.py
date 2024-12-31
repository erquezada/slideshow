import os
import threading
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL, Toplevel
from tkinter import ttk  # Import ttk for progress bar
from PIL import Image, ImageTk
import random  # Import random for shuffling


class SlideshowViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Slideshow Viewer")

        # Initialize variables
        self.image_list = []
        self.current_index = 0
        self.image_cache = {}
        self.auto_play = False
        self.is_fullscreen = False
        self.zoom_factor = 1.0  # To track zoom level
        self.auto_play_interval = 3000  # Default autoplay interval (in ms)
        self.is_shuffled = False

        # Create GUI components
        self.label = Label(self.root)
        self.label.pack(fill="both", expand=True)

        # Create a frame for the buttons and center them
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        # Manually place buttons in the frame
        self.create_buttons()

        # Create slider and progress bar
        self.create_slider()
        self.create_progress_bar()

        # Add keyboard bindings for navigation
        self.root.bind("<Left>", self.show_previous)
        self.root.bind("<Right>", self.show_next)
        self.root.bind("<space>", self.toggle_auto_play)

        self.load_images()

    def create_buttons(self):
        # Dictionary to hold buttons for easy access
        self.buttons = {}

        # Create buttons inside the button frame
        self.prev_button = Button(self.button_frame, text="Previous", command=self.show_previous)
        self.set_transparency(self.prev_button)
        self.buttons['prev'] = self.prev_button

        self.next_button = Button(self.button_frame, text="Next", command=self.show_next)
        self.set_transparency(self.next_button)
        self.buttons['next'] = self.next_button

        self.play_button = Button(self.button_frame, text="Play", command=self.toggle_auto_play)
        self.set_transparency(self.play_button)
        self.buttons['play'] = self.play_button

        self.fullscreen_button = Button(self.button_frame, text="Fullscreen", command=self.toggle_fullscreen)
        self.set_transparency(self.fullscreen_button)
        self.buttons['fullscreen'] = self.fullscreen_button

        self.shuffle_button = Button(self.button_frame, text="Shuffle", command=self.toggle_shuffle)
        self.set_transparency(self.shuffle_button)
        self.buttons['shuffle'] = self.shuffle_button

        self.zoom_in_button = Button(self.button_frame, text="Zoom In", command=self.zoom_in)
        self.set_transparency(self.zoom_in_button)
        self.buttons['zoom_in'] = self.zoom_in_button

        self.zoom_out_button = Button(self.button_frame, text="Zoom Out", command=self.zoom_out)
        self.set_transparency(self.zoom_out_button)
        self.buttons['zoom_out'] = self.zoom_out_button

        self.rotate_button = Button(self.button_frame, text="Rotate", command=self.rotate_image)
        self.set_transparency(self.rotate_button)
        self.buttons['rotate'] = self.rotate_button

        self.close_button = Button(self.button_frame, text="Close", command=self.close_application)
        self.set_transparency(self.close_button)
        self.buttons['close'] = self.close_button

        # Use grid to center the buttons
        self.prev_button.grid(row=0, column=0, padx=10)
        self.play_button.grid(row=0, column=1, padx=10)
        self.next_button.grid(row=0, column=2, padx=10)
        self.fullscreen_button.grid(row=0, column=3, padx=10)
        self.shuffle_button.grid(row=0, column=4, padx=10)
        self.zoom_in_button.grid(row=1, column=0, padx=10)
        self.zoom_out_button.grid(row=1, column=1, padx=10)
        self.rotate_button.grid(row=1, column=2, padx=10)
        self.close_button.grid(row=2, column=0, columnspan=5, pady=10)  # Place close button in a separate row

        # Center the grid in the frame by adjusting column and row weights
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)
        self.button_frame.grid_columnconfigure(4, weight=1)

    def set_transparency(self, button):
        # Initially set the button background to transparent-like effect
        button.config(bg=self.root.cget("bg"))  # Set background to match the root window
        button.config(activebackground=self.root.cget("bg"))  # Disable active background to maintain transparency
        button.config(relief="flat")  # Flat button appearance for minimal style

    def on_hover(self, event):
        # Make the button fully visible on hover
        event.widget.config(bg="lightblue", activebackground="lightblue")  # Change to the desired hover color

    def on_leave(self, event):
        # Return to the transparent state when the mouse leaves
        self.set_transparency(event.widget)

    def create_slider(self):
        # Create a slider for image navigation
        self.slider = Scale(self.button_frame, from_=0, to=len(self.image_list) - 1, orient=HORIZONTAL, command=self.update_image)
        self.set_transparency(self.slider)

        # Place the slider in the center using grid
        self.slider.grid(row=1, column=0, columnspan=5, pady=10, padx=10)

        # Center the slider by configuring column weights
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)
        self.button_frame.grid_columnconfigure(4, weight=1)

    def create_progress_bar(self):
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.place(x=10, y=100)  # Place progress bar at coordinates (10, 100)

        self.remaining_label = Label(self.root, text="")
        self.remaining_label.place(x=10, y=150)  # Place remaining label at coordinates (10, 150)

    def load_images(self):
        # Create a custom window to select folder with an exit option
        folder_window = Toplevel(self.root)
        folder_window.title("Select Folder")
        folder_window.geometry("300x100")

        def close_program():
            self.root.quit()

        # Folder selection prompt with "Close" button
        select_button = Button(folder_window, text="Select Folder", command=self.select_folder)
        select_button.pack(pady=10)

        close_button = Button(folder_window, text="Close Program", command=close_program)
        close_button.pack(pady=5)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        if not folder_path:
            print("No folder selected. Please select a valid folder.")
            return

        supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
        self.image_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(supported_formats)]

        if not self.image_list:
            print("No supported image files found in the selected folder. Please select a different folder.")
            return

        # Shuffle images if needed
        if self.is_shuffled:
            random.shuffle(self.image_list)

        # Start loading the first image asynchronously
        self.load_image(self.current_index)

        self.update_progress_bar()
        self.show_image()

    def load_image(self, index):
        # Check if the image is already in the cache
        if index not in self.image_cache:
            threading.Thread(target=self.cache_image, args=(index,)).start()

    def cache_image(self, index):
        try:
            image_path = self.image_list[index]
            image = Image.open(image_path)
            image_resized = self.resize_image(image)
            photo = ImageTk.PhotoImage(image_resized)

            # Update the cache and the UI in the main thread
            self.image_cache[index] = photo
            if index == self.current_index:
                self.show_image()  # Show image when it's ready
        except Exception as e:
            print(f"Error loading image {index}: {e}")

    def resize_image(self, image):
        if self.is_fullscreen:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            new_size = (screen_width, screen_height)
        else:
            width, height = image.size
            new_size = (int(width * self.zoom_factor), int(height * self.zoom_factor))
        return image.resize(new_size)

    def show_image(self):
        # Only show the image if it's in the cache
        if self.current_index in self.image_cache:
            photo = self.image_cache[self.current_index]
            self.label.config(image=photo)
            self.label.image = photo

        self.slider.set(self.current_index)

    def update_image(self, value):
        # Update current index based on slider value
        self.current_index = int(value)
        self.load_image(self.current_index)

    def show_next(self, event=None):
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.load_image(self.current_index)

    def show_previous(self, event=None):
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.load_image(self.current_index)

    def update_progress_bar(self):
        # Update progress bar
        progress = (self.current_index + 1) / len(self.image_list) * 100
        self.progress_bar["value"] = progress
        self.remaining_label.config(text=f"Remaining: {len(self.image_list) - self.current_index - 1} images")

    def toggle_auto_play(self, event=None):
        self.auto_play = not self.auto_play
        if self.auto_play:
            self.play_button.config(text="Pause")
            self.auto_play_images()
        else:
            self.play_button.config(text="Play")

    def auto_play_images(self):
        if self.auto_play:
            self.show_next()
            self.root.after(self.auto_play_interval, self.auto_play_images)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.show_image()

    def toggle_shuffle(self):
        self.is_shuffled = not self.is_shuffled
        if self.is_shuffled:
            random.shuffle(self.image_list)
            self.image_cache = {}  # Clear image cache
            self.load_image(self.current_index)
        else:
            self.load_image(self.current_index)

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.show_image()

    def zoom_out(self):
        self.zoom_factor -= 0.1
        self.show_image()

    def rotate_image(self):
        if self.image_list:
            current_image = Image.open(self.image_list[self.current_index])
            rotated_image = current_image.rotate(90, expand=True)
            photo = ImageTk.PhotoImage(self.resize_image(rotated_image))
            self.label.config(image=photo)
            self.label.image = photo  # Keep a reference to avoid garbage collection

    def close_application(self):
        self.root.quit()


if __name__ == "__main__":
    root = Tk()
    viewer = SlideshowViewer(root)
    root.mainloop()
