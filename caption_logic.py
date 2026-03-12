import datetime
import os
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from config import (
    OCR_CONFIG, OCR_LANGUAGE, OCR_SCALE_FACTOR,
    OCR_CONTRAST, OCR_UNSHARP_RADIUS, OCR_UNSHARP_PERCENT,
    OCR_UNSHARP_THRESHOLD, TIMESTAMP_FORMAT, DATE_FORMAT,
    CAPTION_FILE_PREFIX
)

def parse_region(region_str):
    try:
        parts = [int(p.strip()) for p in region_str.split(",")]
    except ValueError:
        raise ValueError("Region values must be integers. Use format: x, y, width, height")

    if len(parts) != 4:
        raise ValueError(f"Region must have exactly 4 values (x, y, width, height), got {len(parts)}")

    x, y, width, height = parts

    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be greater than 0")

    return tuple(parts)

def region_to_monitor(region):
    return {
        "left": region[0],
        "top": region[1],
        "width": region[2],
        "height": region[3]
    }

def preprocess_image(img):
    # Convert to grayscale and enhance for better OCR accuracy
    gray = ImageOps.grayscale(img)
    enhanced = ImageEnhance.Contrast(gray).enhance(OCR_CONTRAST)
    sharpened = enhanced.filter(
        ImageFilter.UnsharpMask(
            radius=OCR_UNSHARP_RADIUS,
            percent=OCR_UNSHARP_PERCENT,
            threshold=OCR_UNSHARP_THRESHOLD
        )
    )
    resized = sharpened.resize(
        (sharpened.width * OCR_SCALE_FACTOR, sharpened.height * OCR_SCALE_FACTOR),
        Image.LANCZOS
    )
    return resized

def extract_text(img):
    try:
        import pytesseract
        text = pytesseract.image_to_string(img, config=OCR_CONFIG, lang=OCR_LANGUAGE)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")

def is_quality_text(text):
    if not text:
        return False
    # Must be at least 10 characters
    if len(text.strip()) < 10:
        return False
    # Must contain at least 2 words
    words = [w for w in text.split() if len(w) > 1]
    if len(words) < 2:
        return False
    # Must be mostly letters/numbers, not random symbols
    letters = sum(1 for c in text if c.isalpha())
    if letters / max(len(text), 1) < 0.5:
        return False
    return True

def is_new_text(text, last_text):
    if not is_quality_text(text):
        return False
    # Avoid saving text that is just a slight variation of the last line
    if last_text and text in last_text:
        return False
    return text != last_text

def get_output_filename(output_folder, date=None):
    if date is None:
        date = datetime.date.today()
    date_str = date.strftime(DATE_FORMAT)
    filename = f"{CAPTION_FILE_PREFIX}_{date_str}.txt"
    return os.path.join(output_folder, filename)

def format_caption_line(text, timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now()
    ts = timestamp.strftime(TIMESTAMP_FORMAT)
    return f"{ts} {text}"

def save_caption(text, filename, timestamp=None):
    line = format_caption_line(text, timestamp)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line

def validate_output_folder(folder):
    if not folder or not folder.strip():
        return False, "empty"
    if not os.path.exists(folder):
        return False, "not_found"
    if not os.access(folder, os.W_OK):
        return False, "not_writable"
    return True, "ok"