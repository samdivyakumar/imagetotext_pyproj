"""
Configuration settings for the Image2Text converter
"""

# OCR Settings
OCR_LANG = 'eng'  # Language for Tesseract OCR (can be 'eng', 'fra', 'deu', etc.)
OCR_CONFIG = '--psm 3'  # Page Segmentation Mode (3 = Fully automatic page segmentation)

# Output Settings
TEXT_PLACEMENT = 'below'  # Options: 'below' (keep image and add text below) or 'replace' (replace image with text)
TEXT_PREFIX = '\n[Extracted Text from Image]\n'  # Prefix added before extracted text
TEXT_SUFFIX = '\n[End of Extracted Text]\n'  # Suffix added after extracted text

# Image Processing
MIN_IMAGE_SIZE = (50, 50)  # Minimum image size (width, height) to process
IMAGE_FORMAT = 'PNG'  # Format for temporary image files

# Logging
LOG_LEVEL = 'INFO'  # Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
