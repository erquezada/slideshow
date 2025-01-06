import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def select_input_file():
    """Open a file dialog to select the input video file."""
    filepath = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.MOV"), ("All Files", "*.*")]
    )
    input_path.set(filepath)

def select_output_directory():
    """Open a file dialog to select or create the output directory."""
    directory = filedialog.askdirectory(title="Select Output Directory")
    output_path.set(directory)

def extract_frames():
    """Extract frames from the selected video file and save them to the output directory."""
    video_path = input_path.get()
    output_dir = output_path.get()

    if not video_path or not os.path.exists(video_path):
        messagebox.showerror("Error", "Invalid input video file path.")
        return
    if not output_dir:
        messagebox.showerror("Error", "Output directory is not specified.")
        return

    os.makedirs(output_dir, exist_ok=True)

    vidcap = cv2.VideoCapture(video_path)
    if not vidcap.isOpened():
        messagebox.showerror("Error", "Could not open video file.")
        return

    # Get the total frame count for progress bar
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress_bar["maximum"] = total_frames

    count = 0
    success, image = vidcap.read()
    while success:
        frame_filename = os.path.join(output_dir, f"{count}.jpg")
        cv2.imwrite(frame_filename, image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        count += 1
        success, image = vidcap.read()

        # Update progress bar
        progress_bar["value"] = count
        progress_bar.update()

    vidcap.release()
    messagebox.showinfo("Success", f"Extracted {count} frames to '{output_dir}'.")

# Initialize the GUI
root = tk.Tk()
root.title("Video Frame Extractor")

# Input video file path
input_path = tk.StringVar()
output_path = tk.StringVar()

# Input file selection
tk.Label(root, text="Input Video File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=input_path, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse...", command=select_input_file).grid(row=0, column=2, padx=10, pady=5)

# Output directory selection
tk.Label(root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=output_path, width=50).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse...", command=select_output_directory).grid(row=1, column=2, padx=10, pady=5)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=2, column=0, columnspan=3, pady=10)

# Extract frames button
tk.Button(root, text="Extract Frames", command=extract_frames, bg="green", fg="white").grid(row=3, column=1, pady=10)

# Run the GUI
root.mainloop()
