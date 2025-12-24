# Quick Start Guide

Get up and running with Image2Text in 5 minutes!

## Step 1: Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

**Verify:**
```bash
tesseract --version
```

## Step 2: Setup Python Environment

```bash
# Navigate to project directory
cd /Users/divyakumar/workspace/dev_projects/image2text_pyproj

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Test Your Installation

```bash
python test_installation.py
```

You should see all tests passing ✓

## Step 4: Process Your First Document

**Single document:**
```bash
python main.py your_document.docx
```

**Output will be:** `your_document_processed.docx`

**Custom output location:**
```bash
python main.py input.docx -o output.docx
```

## Step 5: Explore Options

**Replace images instead of adding text below:**
```bash
python main.py input.docx --placement replace
```

**Better accuracy with enhanced mode:**
```bash
python main.py input.docx --enhanced
```

**Process multiple documents:**
```bash
python batch_process.py ./my_documents_folder
```

## Common Use Cases

### Articulate Storyline Exports
```bash
python main.py storyline_slides.docx --enhanced
```

### Multiple Documents at Once
```bash
python batch_process.py ./documents -o ./processed_documents
```

### Non-English Documents
```bash
# First install language pack
brew install tesseract-lang  # macOS

# Then process
python main.py french_doc.docx --lang fra
```

## Troubleshooting

**"Tesseract not found"**
- Make sure Tesseract is installed: `tesseract --version`
- Check your PATH includes Tesseract

**Poor text quality**
- Use `--enhanced` flag for better preprocessing
- Check image quality in source document
- Verify correct language is selected

**No images found**
- Ensure images are embedded (not linked)
- Check document isn't corrupted

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize settings in [config.py](config.py)
- Check `python main.py --help` for all options

## Support

Need help? Check the README or create an issue with:
- Your command
- Error message
- Sample document (if possible)

---

Happy OCR processing! 🚀
