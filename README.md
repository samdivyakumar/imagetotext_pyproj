# Image2Text - Word Document OCR Converter

A comprehensive Python application that automatically extracts text from images embedded in Word documents using OCR (Optical Character Recognition).

## Features

✨ **Automated Processing**
- Automatically detects all images in a Word document
- Extracts each image and runs OCR
- Converts detected text to editable text
- Inserts text back into the document

🎯 **Flexible Options**
- **Text Placement**: Choose to add text below images or replace images with text
- **Language Support**: Support for multiple OCR languages (English, French, German, etc.)
- **Enhanced Mode**: Optional image preprocessing for better OCR accuracy
- **Configurable**: Easy-to-modify configuration file

📋 **Easy to Use**
- Simple command-line interface
- Detailed logging for tracking progress
- Comprehensive error handling

## Prerequisites

Before installing, make sure you have:

1. **Python 3.7+** installed
2. **Tesseract OCR** installed on your system

### Installing Tesseract OCR

**macOS (using Homebrew):**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your PATH

**Verify installation:**
```bash
tesseract --version
```

### Installing Additional Languages (Optional)

For languages other than English:

**macOS:**
```bash
brew install tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-spa  # Spanish
```

## Installation

1. **Clone or download this project**
   ```bash
   cd /Users/divyakumar/workspace/dev_projects/image2text_pyproj
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Process a Word document with default settings:
```bash
python main.py your_document.docx
```

This will create `your_document_processed.docx` with extracted text added below each image.

### Advanced Options

**Specify output file:**
```bash
python main.py input.docx -o output.docx
```

**Replace images with text instead of adding below:**
```bash
python main.py input.docx --placement replace
```

**Use a different OCR language:**
```bash
python main.py input.docx --lang fra  # French
python main.py input.docx --lang deu  # German
```

**Enable enhanced OCR with preprocessing:**
```bash
python main.py input.docx --enhanced
```

**Combine multiple options:**
```bash
python main.py input.docx -o output.docx --placement replace --lang eng --enhanced
```

**Enable debug logging:**
```bash
python main.py input.docx --log-level DEBUG
```

### Command-Line Help

View all available options:
```bash
python main.py --help
```

## Configuration

You can customize the default behavior by editing `config.py`:

```python
# OCR Settings
OCR_LANG = 'eng'  # Default language
OCR_CONFIG = '--psm 3'  # Page segmentation mode

# Output Settings
TEXT_PLACEMENT = 'below'  # 'below' or 'replace'
TEXT_PREFIX = '\n[Extracted Text from Image]\n'
TEXT_SUFFIX = '\n[End of Extracted Text]\n'

# Image Processing
MIN_IMAGE_SIZE = (50, 50)  # Skip images smaller than this

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
```

## How It Works

1. **Image Extraction**: The application opens the Word document and identifies all embedded images
2. **OCR Processing**: Each image is processed through Tesseract OCR to extract text
3. **Document Reconstruction**: The extracted text is inserted back into the document at the appropriate locations
4. **Output**: A new Word document is created with the OCR results

## Project Structure

```
image2text_pyproj/
├── main.py                  # Main entry point and CLI
├── image_extractor.py       # Extract images from Word documents
├── ocr_processor.py         # OCR processing with Tesseract
├── document_processor.py    # Reconstruct documents with text
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore patterns
└── README.md               # This file
```

## Dependencies

- **python-docx**: Word document manipulation
- **pytesseract**: Python wrapper for Tesseract OCR
- **Pillow**: Image processing library

## Troubleshooting

### "Tesseract not found" error

Make sure Tesseract is installed and in your PATH:
```bash
tesseract --version
```

If installed but not found, you may need to set the path manually in your code:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'  # Adjust path
```

### Poor OCR accuracy

Try these solutions:
1. Use enhanced mode: `--enhanced`
2. Ensure images have good resolution
3. Try different page segmentation modes in `config.py`
4. Verify correct language is selected

### No images found

Make sure your Word document contains embedded images (not just linked images).

## Examples

**Example 1: Process presentation slides**
```bash
python main.py presentation_slides.docx --enhanced
```

**Example 2: Convert to French and replace images**
```bash
python main.py french_document.docx --lang fra --placement replace
```

**Example 3: Debug processing issues**
```bash
python main.py problem_doc.docx --log-level DEBUG
```

## License

This project is open source and available for personal and commercial use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Future Enhancements

- [ ] GUI interface
- [ ] Batch processing multiple documents
- [ ] Support for other document formats (PDF, etc.)
- [ ] Advanced image preprocessing options
- [ ] Custom OCR model integration
- [ ] Progress bar for long operations

## Support

For issues or questions, please create an issue in the project repository.

---

**Note**: OCR accuracy depends on image quality, text clarity, and language support. Best results are achieved with high-resolution, clear images containing standard fonts.
