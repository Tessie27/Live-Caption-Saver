import pytest
import datetime
import os
from PIL import Image
from caption_logic import (
    parse_region,
    region_to_monitor,
    preprocess_image,
    is_new_text,
    is_quality_text,
    get_output_filename,
    format_caption_line,
    save_caption,
    validate_output_folder,
)

# --- Region Parsing Tests ---

def test_parse_region_valid():
    region = parse_region("100, 200, 300, 400")
    assert region == (100, 200, 300, 400)

def test_parse_region_no_spaces():
    region = parse_region("100,200,300,400")
    assert region == (100, 200, 300, 400)

def test_parse_region_too_few_values():
    with pytest.raises(ValueError, match="exactly 4"):
        parse_region("100, 200, 300")

def test_parse_region_too_many_values():
    with pytest.raises(ValueError, match="exactly 4"):
        parse_region("100, 200, 300, 400, 500")

def test_parse_region_non_integer():
    with pytest.raises(ValueError):
        parse_region("100, abc, 300, 400")

def test_parse_region_zero_width():
    with pytest.raises(ValueError, match="greater than 0"):
        parse_region("100, 200, 0, 400")

def test_parse_region_zero_height():
    with pytest.raises(ValueError, match="greater than 0"):
        parse_region("100, 200, 300, 0")

def test_parse_region_negative_dimensions():
    with pytest.raises(ValueError, match="greater than 0"):
        parse_region("100, 200, -10, 400")

# --- Region to Monitor Tests ---

def test_region_to_monitor_keys():
    monitor = region_to_monitor((100, 200, 300, 400))
    assert "left" in monitor
    assert "top" in monitor
    assert "width" in monitor
    assert "height" in monitor

def test_region_to_monitor_values():
    monitor = region_to_monitor((100, 200, 300, 400))
    assert monitor["left"] == 100
    assert monitor["top"] == 200
    assert monitor["width"] == 300
    assert monitor["height"] == 400

# --- Image Preprocessing Tests ---

def test_preprocess_returns_image():
    img = Image.new("RGB", (200, 50), color=(200, 200, 200))
    result = preprocess_image(img)
    assert isinstance(result, Image.Image)

def test_preprocess_upscales_image():
    img = Image.new("RGB", (200, 50), color=(200, 200, 200))
    result = preprocess_image(img)
    assert result.width > img.width
    assert result.height > img.height

def test_preprocess_outputs_grayscale():
    img = Image.new("RGB", (200, 50), color=(200, 200, 200))
    result = preprocess_image(img)
    assert result.mode == "L"

# --- Text Deduplication Tests ---

def test_is_new_text_different():
    assert is_new_text("Hello world this is a sentence", "Previous text here") == True

def test_is_new_text_same():
    assert is_new_text("Same text here again", "Same text here again") == False

def test_is_new_text_empty():
    assert is_new_text("", "Previous") == False

def test_is_new_text_both_empty():
    assert is_new_text("", "") == False

def test_is_new_text_first_capture():
    assert is_new_text("First caption of the session", "") == True

# --- Text Quality Filter Tests ---

def test_quality_filter_rejects_single_letter():
    assert is_new_text("x", "") == False

def test_quality_filter_rejects_two_letters():
    assert is_new_text("eu", "") == False

def test_quality_filter_rejects_short_text():
    assert is_new_text("hi", "") == False

def test_quality_filter_accepts_real_sentence():
    assert is_new_text("They have the houses but", "") == True

def test_quality_filter_rejects_symbols_only():
    assert is_new_text("!!! ???", "") == False

def test_quality_filter_rejects_subset_of_last():
    # If new text is contained within the last saved text, skip it
    assert is_new_text("houses but", "They have the houses but are still waiting") == False

# --- File Output Tests ---

def test_get_output_filename_contains_date(tmp_path):
    date = datetime.date(2026, 3, 12)
    filename = get_output_filename(str(tmp_path), date)
    assert "2026-03-12" in filename

def test_get_output_filename_contains_prefix(tmp_path):
    filename = get_output_filename(str(tmp_path))
    assert "live_captions" in filename

def test_get_output_filename_is_txt(tmp_path):
    filename = get_output_filename(str(tmp_path))
    assert filename.endswith(".txt")

def test_format_caption_line():
    ts = datetime.datetime(2026, 3, 12, 14, 32, 1)
    line = format_caption_line("Hello world", ts)
    assert "[14:32:01]" in line
    assert "Hello world" in line

def test_save_caption_creates_file(tmp_path):
    filename = str(tmp_path / "test_captions.txt")
    save_caption("Test caption", filename)
    assert os.path.exists(filename)

def test_save_caption_content(tmp_path):
    filename = str(tmp_path / "test_captions.txt")
    save_caption("Hello world", filename)
    with open(filename, "r") as f:
        content = f.read()
    assert "Hello world" in content

def test_save_caption_appends(tmp_path):
    filename = str(tmp_path / "test_captions.txt")
    save_caption("Line one", filename)
    save_caption("Line two", filename)
    with open(filename, "r") as f:
        lines = f.readlines()
    assert len(lines) == 2

def test_save_caption_returns_formatted_line(tmp_path):
    filename = str(tmp_path / "test_captions.txt")
    line = save_caption("Test text", filename)
    assert "Test text" in line

# --- Folder Validation Tests ---

def test_validate_folder_valid(tmp_path):
    valid, reason = validate_output_folder(str(tmp_path))
    assert valid == True
    assert reason == "ok"

def test_validate_folder_empty():
    valid, reason = validate_output_folder("")
    assert valid == False
    assert reason == "empty"

def test_validate_folder_not_found():
    valid, reason = validate_output_folder("/nonexistent/path/xyz")
    assert valid == False
    assert reason == "not_found"

def test_validate_folder_whitespace():
    valid, reason = validate_output_folder("   ")
    assert valid == False
    assert reason == "empty"