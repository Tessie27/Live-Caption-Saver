# 🗣️ Live Caption Saver (Windows)

This Python app captures real-time text from the **Windows Live Captions** window and saves it with timestamps to a text file — perfect for accessibility, transcription, and meeting notes.

---

## ✅ Features

- Auto-detect the "Live Captions" window
- Extracts only **new** caption text with timestamps
- Saves to a readable `.txt` file (organized by date)
- Lightweight GUI with start/stop buttons
- Advanced OCR preprocessing for high accuracy

---

## 📦 Requirements

- Windows 10 or 11
- Python 3.8+
- [Tesseract OCR (UB Mannheim Build)](https://github.com/UB-Mannheim/tesseract/wiki)

---

## 🛠 Installation Guide

### 1. 🔤 Install Tesseract OCR

Download & install the **UB Mannheim Tesseract OCR** build:

➡️ [Download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

> 📍 Default install path (leave this as-is):  
> `C:\Program Files\Tesseract-OCR\tesseract.exe`

---

### 2. 💻 Install Python Packages

Open CMD or PowerShell:

```bash
pip install pytesseract pillow mss opencv-python pygetwindow pywin32
