# System Architecture

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT: Word Document (.docx)                 │
│                     (Contains embedded images)                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP 1: Image Extraction                         │
│                    (image_extractor.py)                             │
│                                                                     │
│  • Opens Word document using python-docx                           │
│  • Traverses document structure (paragraphs, runs)                 │
│  • Identifies embedded images via XML elements                     │
│  • Extracts image binary data                                      │
│  • Records position (paragraph index, run index)                   │
│  • Creates ImageInfo objects                                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    List of ImageInfo Objects                        │
│                                                                     │
│  ImageInfo {                                                        │
│    image_data: bytes                                                │
│    image_id: "image_0"                                              │
│    paragraph_index: 5                                               │
│    run_index: 0                                                     │
│  }                                                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP 2: OCR Processing                           │
│                    (ocr_processor.py)                               │
│                                                                     │
│  For each image:                                                    │
│    • Convert bytes to PIL Image                                    │
│    • [Optional] Preprocess image:                                  │
│      - Convert to grayscale                                        │
│      - Enhance contrast                                            │
│      - Remove noise                                                │
│    • Pass to Tesseract OCR                                         │
│    • Extract text string                                           │
│    • Store in dictionary: image_id → text                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Dictionary of Extracted Text                     │
│                                                                     │
│  {                                                                  │
│    "image_0": "Welcome to the Course\nModule 1: Introduction",     │
│    "image_1": "Learning Objectives\n• Understand basics\n...",     │
│    "image_2": "Key Concepts\n1. First concept\n2. Second..."      │
│  }                                                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP 3: Document Reconstruction                  │
│                    (document_processor.py)                          │
│                                                                     │
│  For each image (in reverse order to avoid index shifting):        │
│                                                                     │
│    MODE A: "below" (default)                                       │
│    • Keep the original image                                       │
│    • Insert new paragraph after image                              │
│    • Add prefix: "[Extracted Text from Image]"                     │
│    • Add the extracted text                                        │
│    • Add suffix: "[End of Extracted Text]"                         │
│    • Format with green color, specific font                        │
│                                                                     │
│    MODE B: "replace"                                               │
│    • Remove the image from the run                                 │
│    • Replace with extracted text                                   │
│    • Add prefix and suffix                                         │
│    • Format appropriately                                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STEP 4: Save Modified Document                     │
│                                                                     │
│  • Save using python-docx                                          │
│  • Write to output path                                            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   OUTPUT: Processed Word Document                   │
│             (Original images + Extracted text OR Text only)         │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         main.py (CLI)                               │
│  • Argument parsing                                                 │
│  • Logging setup                                                    │
│  • Orchestration                                                    │
│  • Error handling                                                   │
└───────┬───────────────────────┬───────────────────────┬─────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│image_extractor│    │  ocr_processor   │    │document_processor   │
│               │    │                  │    │                     │
│ ImageExtractor│    │  OCRProcessor    │    │ DocumentProcessor   │
│ ImageInfo     │    │  • Tesseract     │    │ • Text insertion    │
│ • Extract imgs│    │  • Preprocessing │    │ • Formatting        │
│ • Track pos.  │    │  • Multi-lang    │    │ • Save document     │
└───────┬───────┘    └──────────┬───────┘    └──────────┬──────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │   config.py   │
                        │               │
                        │ • OCR_LANG    │
                        │ • TEXT_PLACE  │
                        │ • PREFIXES    │
                        │ • MIN_SIZE    │
                        │ • LOG_LEVEL   │
                        └───────────────┘
```

## Class Relationships

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ImageExtractor                              │
├─────────────────────────────────────────────────────────────────────┤
│ - doc_path: str                                                     │
│ - document: Document                                                │
├─────────────────────────────────────────────────────────────────────┤
│ + load_document() → Document                                        │
│ + extract_images() → List[ImageInfo]                                │
│ + get_document() → Document                                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ creates
                             ▼
                    ┌──────────────────┐
                    │    ImageInfo     │
                    ├──────────────────┤
                    │ - image_data     │
                    │ - image_id       │
                    │ - paragraph_idx  │
                    │ - run_index      │
                    │ - pil_image      │
                    ├──────────────────┤
                    │ + to_pil_image() │
                    └──────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         OCRProcessor                                │
├─────────────────────────────────────────────────────────────────────┤
│ - lang: str                                                         │
│ - ocr_config: str                                                   │
├─────────────────────────────────────────────────────────────────────┤
│ + extract_text(Image) → str                                         │
│ + extract_text_from_bytes(bytes) → str                              │
│ + preprocess_image(Image) → Image                                   │
│ + extract_text_enhanced(Image) → str                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DocumentProcessor                              │
├─────────────────────────────────────────────────────────────────────┤
│ - document: Document                                                │
│ - text_placement: str                                               │
├─────────────────────────────────────────────────────────────────────┤
│ + add_text_to_document(Dict, List[ImageInfo]) → Document            │
│ + save_document(str) → None                                         │
│ - _add_text_below_image(int, str) → None                            │
│ - _replace_image_with_text(int, int, str) → None                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Execution Flow

```
User runs: python main.py input.docx --enhanced

    │
    ├─> Parse arguments
    │   └─> input_path = "input.docx"
    │       output_path = "input_processed.docx"
    │       enhanced = True
    │
    ├─> Setup logging (INFO level)
    │
    ├─> Validate input file exists and is .docx
    │
    ├─> Create ImageExtractor("input.docx")
    │   └─> extractor.extract_images()
    │       ├─> Open document
    │       ├─> For each paragraph:
    │       │   └─> For each run:
    │       │       └─> Check for drawing elements
    │       │           └─> Extract image blob
    │       │               └─> Create ImageInfo
    │       └─> Return List[ImageInfo]
    │
    ├─> Create OCRProcessor(lang='eng')
    │   └─> Test Tesseract availability
    │
    ├─> For each ImageInfo:
    │   ├─> Convert to PIL Image
    │   ├─> Check minimum size
    │   ├─> If enhanced:
    │   │   ├─> Preprocess (grayscale, contrast, etc.)
    │   │   └─> OCR preprocessed image
    │   ├─> Else:
    │   │   └─> OCR original image
    │   └─> Store text in dictionary
    │
    ├─> Create DocumentProcessor(document, 'below')
    │   └─> add_text_to_document(image_texts, images)
    │       └─> For each image (reverse order):
    │           ├─> Get paragraph at index
    │           ├─> Insert new paragraph after
    │           ├─> Add formatted text
    │           └─> Move to next image
    │
    ├─> Save document to output path
    │
    └─> Report success and statistics
```

## Module Dependencies

```
main.py
  ├─> image_extractor
  │     └─> docx (python-docx)
  │     └─> PIL (Pillow)
  │
  ├─> ocr_processor
  │     └─> pytesseract
  │     └─> PIL (Pillow)
  │     └─> config
  │
  ├─> document_processor
  │     └─> docx (python-docx)
  │     └─> config
  │     └─> image_extractor (ImageInfo)
  │
  └─> config
```

## Error Handling Flow

```
Try:
  └─> Process document
      │
      ├─> File not found?
      │   └─> Log error, return False
      │
      ├─> Not .docx file?
      │   └─> Log error, return False
      │
      ├─> Image extraction fails?
      │   └─> Log warning, continue with next image
      │
      ├─> OCR fails?
      │   └─> Log warning, store empty string
      │
      ├─> Document save fails?
      │   └─> Log error, raise exception
      │
      └─> Success
          └─> Log success, return True
Except:
  └─> Log full traceback
      └─> Return False
```

## Performance Characteristics

```
Time Complexity:
  • Image Extraction: O(n) where n = number of paragraphs
  • OCR Processing: O(m) where m = number of images
  • Document Reconstruction: O(m)
  • Overall: O(n + m)

Space Complexity:
  • O(m * size_per_image) for storing extracted images
  • Optimized by processing one image at a time

Bottlenecks:
  • OCR processing (2-5 seconds per image)
  • Large document parsing
  • Image preprocessing in enhanced mode
```

---

This architecture ensures:
- ✅ Separation of concerns
- ✅ Easy to test and maintain
- ✅ Extensible for new features
- ✅ Robust error handling
- ✅ Efficient resource usage
