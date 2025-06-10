License Plate Detection
A Flask-based web application for detecting and extracting license plate numbers from car images using OpenCV and EasyOCR.
Features

Upload a car image or select from 20 predefined images.
Detects license plates using contour detection and extracts text using OCR.
Modern, responsive interface built with Tailwind CSS.
Error handling for robust processing.

Installation

Clone the repository:git clone https://github.com/yourusername/license-plate-detection.git
cd license-plate-detection


Install dependencies:pip install flask opencv-python-headless imutils easyocr numpy


Place car images in the static/images/ directory.
Run the application:python app.py


Open http://localhost:5000 in your browser.

Usage

Upload Image: Upload a car image from your device.
Select Image: Choose from predefined car images.
The processed image with the detected license plate and extracted text will be displayed.

Requirements

Python 3.8+
Flask
OpenCV
EasyOCR
Imutils
NumPy

License
MIT License
