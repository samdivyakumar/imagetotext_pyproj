# Image2Text Project - Examples

This directory contains example scripts and use cases for the Image2Text converter.

## Example 1: Basic Single Document Processing

```python
from image_extractor import ImageExtractor
from ocr_processor import OCRProcessor
from document_processor import DocumentProcessor

# Process a document programmatically
def process_my_document():
    # Extract images
    extractor = ImageExtractor("input.docx")
    images = extractor.extract_images()
    
    # Perform OCR
    ocr = OCRProcessor(lang='eng')
    image_texts = {}
    
    for img_info in images:
        pil_image = img_info.to_pil_image()
        text = ocr.extract_text(pil_image)
        image_texts[img_info.image_id] = text
    
    # Reconstruct document
    document = extractor.get_document()
    processor = DocumentProcessor(document, text_placement='below')
    processor.add_text_to_document(image_texts, images)
    processor.save_document("output.docx")

# Run it
process_my_document()
```

## Example 2: Custom OCR Configuration

```python
from ocr_processor import OCRProcessor
from PIL import Image

# Create OCR processor with custom settings
ocr = OCRProcessor(
    lang='eng',
    ocr_config='--psm 6 --oem 3'  # Different page segmentation mode
)

# Load and process an image
image = Image.open("screenshot.png")
text = ocr.extract_text_enhanced(image)  # Use enhanced mode

print(text)
```

## Example 3: Processing Multiple Languages

```python
import config

# French document
config.OCR_LANG = 'fra'
# Run main.py or use OCRProcessor

# Or specify at runtime:
from ocr_processor import OCRProcessor
ocr_french = OCRProcessor(lang='fra')
ocr_german = OCRProcessor(lang='deu')
ocr_spanish = OCRProcessor(lang='spa')
```

## Example 4: Custom Text Placement

```python
from document_processor import DocumentProcessor
from docx import Document

# Load document
doc = Document("input.docx")

# Create processor that replaces images
processor = DocumentProcessor(doc, text_placement='replace')

# Process...
```

## Example 5: Batch Processing with Custom Logic

```python
from pathlib import Path
from main import process_document

# Process all documents in a directory with custom logic
documents_dir = Path("./documents")

for doc_file in documents_dir.glob("*.docx"):
    if doc_file.stat().st_size > 1_000_000:  # Only large files
        print(f"Processing {doc_file.name}...")
        
        output_file = documents_dir / "processed" / f"{doc_file.stem}_ocr.docx"
        
        process_document(
            input_path=str(doc_file),
            output_path=str(output_file),
            enhanced=True,  # Use enhanced OCR
            lang='eng'
        )
```

## Example 6: Error Handling and Logging

```python
import logging
from main import setup_logging, process_document

# Setup detailed logging
setup_logging('DEBUG')

# Get logger
logger = logging.getLogger(__name__)

try:
    success = process_document(
        input_path="presentation.docx",
        output_path="presentation_ocr.docx",
        enhanced=True
    )
    
    if success:
        logger.info("Document processed successfully!")
    else:
        logger.error("Processing failed")
        
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
```

## Example 7: Extracting Images Only

```python
from image_extractor import ImageExtractor
from pathlib import Path

# Extract images without OCR
extractor = ImageExtractor("document.docx")
images = extractor.extract_images()

# Save images to disk
output_dir = Path("extracted_images")
output_dir.mkdir(exist_ok=True)

for img_info in images:
    pil_image = img_info.to_pil_image()
    output_path = output_dir / f"{img_info.image_id}.png"
    pil_image.save(output_path)
    print(f"Saved {output_path}")
```

## Example 8: Image Preprocessing

```python
from ocr_processor import OCRProcessor
from PIL import Image, ImageEnhance, ImageFilter

def custom_preprocess(image):
    """Custom image preprocessing for better OCR"""
    # Convert to grayscale
    image = image.convert('L')
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)
    
    # Denoise
    image = image.filter(ImageFilter.MedianFilter(size=3))
    
    return image

# Use it
ocr = OCRProcessor()
image = Image.open("noisy_image.png")
preprocessed = custom_preprocess(image)
text = ocr.extract_text(preprocessed)
```

## Example 9: Configuration Customization

```python
import config

# Customize settings before processing
config.OCR_LANG = 'eng'
config.OCR_CONFIG = '--psm 6 --oem 1'
config.TEXT_PLACEMENT = 'below'
config.TEXT_PREFIX = '\n--- START OCR TEXT ---\n'
config.TEXT_SUFFIX = '\n--- END OCR TEXT ---\n'
config.MIN_IMAGE_SIZE = (100, 100)

# Now run your processing
from main import process_document
process_document("input.docx", "output.docx")
```

## Example 10: Integration with Other Tools

```python
import subprocess
from main import process_document

# Process document
process_document("input.docx", "output.docx")

# Convert to PDF using other tools
subprocess.run([
    "libreoffice",
    "--headless",
    "--convert-to", "pdf",
    "output.docx"
])

print("Processed and converted to PDF!")
```

## Tips for Best Results

1. **High-Quality Images**: Use documents with high-resolution images
2. **Clean Text**: Images with clear, well-contrasted text work best
3. **Correct Language**: Always specify the correct OCR language
4. **Enhanced Mode**: Use `--enhanced` for difficult images
5. **Page Segmentation**: Adjust `OCR_CONFIG` for different layouts

## Tesseract Page Segmentation Modes

```python
# Common PSM values:
# --psm 0  # Orientation and script detection only
# --psm 1  # Automatic page segmentation with OSD
# --psm 3  # Fully automatic page segmentation (default)
# --psm 6  # Assume a single uniform block of text
# --psm 11 # Sparse text. Find as much text as possible
```

## Common Issues and Solutions

**Issue**: Text not detected
**Solution**: Try enhanced mode and different PSM values

**Issue**: Wrong characters detected
**Solution**: Verify correct language, improve image quality

**Issue**: Slow processing
**Solution**: Reduce image resolution or process in batches

---

For more examples and documentation, visit the main README.md
