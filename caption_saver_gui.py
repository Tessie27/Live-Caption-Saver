import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import pytesseract
import mss
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import datetime
import os
import time
import pygetwindow as gw

# Update this to your tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class CaptionSaverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Caption Saver")

        self.running = False
        self.capture_thread = None
        self.output_folder = os.getcwd()
        self.last_text = ""

        # --- UI Layout ---
        tk.Label(root, text="Caption Region (x, y, width, height):").pack()
        self.region_entry = tk.Entry(root)
        self.region_entry.insert(0, "3561, 1172, 1000, 100")
        self.region_entry.pack()

        tk.Button(root, text="Auto-Detect 'Live Captions' Window", command=self.detect_window).pack(pady=3)
        tk.Button(root, text="Choose Output Folder", command=self.choose_folder).pack()

        self.status_label = tk.Label(root, text="Status: Idle", fg="blue")
        self.status_label.pack(pady=5)

        tk.Button(root, text="Start Capturing", command=self.start_capture).pack(pady=5)
        tk.Button(root, text="Stop", command=self.stop_capture).pack(pady=5)

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
            region = (win.left, win.top, win.width, win.height)
            self.region_entry.delete(0, tk.END)
            self.region_entry.insert(0, f"{region[0]}, {region[1]}, {region[2]}, {region[3]}")
            messagebox.showinfo("Window Detected", f"Region set to: {region}")
        except IndexError:
            messagebox.showerror("Window Not Found", "Could not find a window titled 'Live Captions'. Make sure it's open.")

    def start_capture(self):
        if self.running:
            return

        try:
            self.region = tuple(map(int, self.region_entry.get().split(",")))
            if len(self.region) != 4:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid region. Use format: x, y, width, height")
            return

        self.running = True
        self.last_text = ""
        self.capture_thread = threading.Thread(target=self.capture_loop)
        self.capture_thread.start()
        self.status_label.config(text="Status: Capturing", fg="green")

    def stop_capture(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", fg="red")

    def capture_loop(self):
        date_str = datetime.date.today().isoformat()
        filename = os.path.join(self.output_folder, f"live_captions_{date_str}.txt")

        with mss.mss() as sct:
            monitor = {
                "top": self.region[1],
                "left": self.region[0],
                "width": self.region[2],
                "height": self.region[3]
            }

            while self.running:
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

                # Advanced image preprocessing
                gray = ImageOps.grayscale(img)
                enhanced = ImageEnhance.Contrast(gray).enhance(2.5)
                sharpened = enhanced.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
                resized = sharpened.resize((sharpened.width * 2, sharpened.height * 2), Image.LANCZOS)

                # Improved Tesseract config for more flexible segmentation
                config = r'--oem 3 --psm 4'
                text = pytesseract.image_to_string(resized, config=config, lang='eng').strip()

                if text and text != self.last_text:
                    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(f"{timestamp} {text}\n")
                    print(f"{timestamp} {text}")
                    self.last_text = text

                time.sleep(1.5)

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptionSaverApp(root)
    root.mainloop()
