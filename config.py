import os

# Tesseract path
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Capture settings
DEFAULT_REGION = (3561, 1172, 1000, 100)
CAPTURE_INTERVAL = 1.5

# OCR settings
OCR_CONFIG = r'--oem 3 --psm 4'
OCR_LANGUAGE = 'eng'
OCR_SCALE_FACTOR = 2
OCR_CONTRAST = 2.5
OCR_UNSHARP_RADIUS = 2
OCR_UNSHARP_PERCENT = 150
OCR_UNSHARP_THRESHOLD = 3

# Output settings
DEFAULT_OUTPUT_FOLDER = os.getcwd()
CAPTION_FILE_PREFIX = "live_captions"
TIMESTAMP_FORMAT = "[%H:%M:%S]"
DATE_FORMAT = "%Y-%m-%d"

# GUI settings
WINDOW_TITLE = "Live Caption Saver"
WINDOW_SIZE = "420x400"
HOTKEY = "<F9>"