import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import datetime
import os
import time

import pytesseract
import mss
from PIL import Image
import pygetwindow as gw

from caption_logic import (
    parse_region, region_to_monitor, preprocess_image,
    extract_text, is_new_text, get_output_filename,
    save_caption, validate_output_folder
)
from config import (
    TESSERACT_PATH, DEFAULT_REGION, CAPTURE_INTERVAL,
    DEFAULT_OUTPUT_FOLDER, WINDOW_TITLE, WINDOW_SIZE, HOTKEY
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class CaptionSaverApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.running = False
        self.capture_thread = None
        self.output_folder = DEFAULT_OUTPUT_FOLDER
        self.last_text = ""
        self.setup_interface()
        self.root.bind(HOTKEY, lambda e: self.toggle_capture())

    def setup_interface(self):
        pad = {"padx": 8, "pady": 3}

        tk.Label(self.root, text="Caption Region (x, y, width, height):").pack(**pad)
        self.region_entry = tk.Entry(self.root, width=40)
        self.region_entry.insert(0, ", ".join(map(str, DEFAULT_REGION)))
        self.region_entry.pack(**pad)

        btn_frame1 = tk.Frame(self.root)
        btn_frame1.pack(**pad)
        tk.Button(btn_frame1, text="Auto-Detect Window", command=self.detect_window).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame1, text="Choose Output Folder", command=self.choose_folder).pack(side=tk.LEFT, padx=4)

        self.status_label = tk.Label(self.root, text="Status: Idle", fg="blue", font=("Arial", 10, "bold"))
        self.status_label.pack(**pad)

        # Live preview with auto-scroll
        tk.Label(self.root, text="Live Preview:").pack(**pad)
        preview_frame = tk.Frame(self.root)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=8)

        self.preview_text = tk.Text(preview_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, bg="#1e1e1e", fg="white")
        scrollbar = tk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame2 = tk.Frame(self.root)
        btn_frame2.pack(**pad)
        tk.Button(btn_frame2, text="▶ Start (F9)", command=self.start_capture, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame2, text="⏹ Stop (F9)", command=self.stop_capture, bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=4)

        tk.Label(self.root, text="Tip: Press F9 to toggle capturing", fg="grey", font=("Arial", 8)).pack()

    def toggle_capture(self):
        if self.running:
            self.stop_capture()
        else:
            self.start_capture()

    def start_capture(self):
        if self.running:
            return

        try:
            region = parse_region(self.region_entry.get())
        except ValueError as e:
            messagebox.showerror("Invalid Region", str(e))
            return

        valid, reason = validate_output_folder(self.output_folder)
        if not valid:
            messages = {
                "empty": "Please choose an output folder first.",
                "not_found": f"Folder not found: {self.output_folder}",
                "not_writable": f"Cannot write to folder: {self.output_folder}"
            }
            messagebox.showerror("Folder Error", messages.get(reason, "Invalid output folder."))
            return

        self.region = region
        self.running = True
        self.last_text = ""
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        self.status_label.config(text="Status: Capturing", fg="green")

    def stop_capture(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", fg="red")

    def capture_loop(self):
        filename = get_output_filename(self.output_folder)
        monitor = region_to_monitor(self.region)

        with mss.mss() as sct:
            while self.running:
                try:
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                    processed = preprocess_image(img)
                    text = extract_text(processed)

                    if is_new_text(text, self.last_text):
                        line = save_caption(text, filename)
                        self.last_text = text
                        print(line)
                        self.root.after(0, self.append_preview, line)

                except RuntimeError as e:
                    self.root.after(0, lambda: self.status_label.config(text=f"OCR Error: {e}", fg="orange"))
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(text=f"Error: {e}", fg="orange"))

                time.sleep(CAPTURE_INTERVAL)

    def append_preview(self, line):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.insert(tk.END, line + "\n")
        self.preview_text.see(tk.END)
        self.preview_text.config(state=tk.DISABLED)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            messagebox.showinfo("Output Folder Set", f"Captions will be saved to:\n{folder}")

    def detect_window(self):
        try:
            win = gw.getWindowsWithTitle("Live Captions")[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            region_str = f"{win.left}, {win.top}, {win.width}, {win.height}"
            self.region_entry.delete(0, tk.END)
            self.region_entry.insert(0, region_str)
            messagebox.showinfo("Window Detected", f"Region set to: {region_str}")
        except IndexError:
            messagebox.showerror("Window Not Found", "Could not find 'Live Captions' window.\nMake sure it's open and visible.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not detect window: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptionSaverApp(root)
    root.mainloop()