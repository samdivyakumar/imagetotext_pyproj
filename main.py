#!/usr/bin/env python3
"""
Image to Text Converter for Word Documents
Main entry point for the application
"""
import argparse
import logging
import sys
import os
from pathlib import Path

from image_extractor import ImageExtractor
from ocr_processor import OCRProcessor
from document_processor import DocumentProcessor
import config


def setup_logging(log_level: str = None):
    """Setup logging configuration"""
    level = getattr(logging, log_level or config.LOG_LEVEL)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def process_document(input_path: str, output_path: str = None, text_placement: str = None, 
                     lang: str = None, enhanced: bool = False):
    """
    Process a Word document to extract text from images
    
    Args:
        input_path: Path to input .docx file
        output_path: Path to output .docx file (optional)
        text_placement: 'below' or 'replace'
        lang: OCR language code
        enhanced: Use enhanced OCR with preprocessing
    """
    logger = logging.getLogger(__name__)
    
    # Validate input file
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return False
    
    if not input_path.endswith('.docx'):
        logger.error("Input file must be a .docx file")
        return False
    
    # Set output path if not provided
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_processed.docx")
    
    logger.info(f"Processing document: {input_path}")
    logger.info(f"Output will be saved to: {output_path}")
    
    try:
        # Step 1: Extract images from document
        logger.info("Step 1: Extracting images from document...")
        extractor = ImageExtractor(input_path)
        images = extractor.extract_images()
        
        if not images:
            logger.warning("No images found in the document")
            return False
        
        logger.info(f"Found {len(images)} images")
        
        # Step 2: Perform OCR on each image
        logger.info("Step 2: Performing OCR on images...")
        ocr = OCRProcessor(lang=lang)
        image_texts = {}
        
        for idx, img_info in enumerate(images, 1):
            logger.info(f"Processing image {idx}/{len(images)} - {img_info.image_id}")
            
            pil_image = img_info.to_pil_image()
            
            # Check minimum image size
            if (pil_image.width < config.MIN_IMAGE_SIZE[0] or 
                pil_image.height < config.MIN_IMAGE_SIZE[1]):
                logger.warning(f"Image {img_info.image_id} is too small, skipping")
                continue
            
            # Extract text
            if enhanced:
                text = ocr.extract_text_enhanced(pil_image)
            else:
                text = ocr.extract_text(pil_image)
            
            image_texts[img_info.image_id] = text
            
            if text:
                logger.info(f"Extracted {len(text)} characters from {img_info.image_id}")
            else:
                logger.warning(f"No text extracted from {img_info.image_id}")
        
        # Step 3: Reconstruct document with extracted text
        logger.info("Step 3: Reconstructing document with extracted text...")
        document = extractor.get_document()
        processor = DocumentProcessor(document, text_placement=text_placement)
        processor.add_text_to_document(image_texts, images)
        
        # Step 4: Save the modified document
        logger.info("Step 4: Saving modified document...")
        processor.save_document(output_path)
        
        logger.info("=" * 60)
        logger.info("Processing completed successfully!")
        logger.info(f"Output saved to: {output_path}")
        logger.info(f"Total images processed: {len(image_texts)}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Convert images in Word documents to text using OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input.docx
  python main.py input.docx -o output.docx
  python main.py input.docx --placement replace
  python main.py input.docx --lang fra --enhanced
        """
    )
    
    parser.add_argument(
        'input',
        help='Path to input Word document (.docx)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Path to output Word document (default: input_processed.docx)',
        default=None
    )
    
    parser.add_argument(
        '-p', '--placement',
        choices=['below', 'replace'],
        default=config.TEXT_PLACEMENT,
        help=f'How to place extracted text: below image or replace image (default: {config.TEXT_PLACEMENT})'
    )
    
    parser.add_argument(
        '-l', '--lang',
        default=config.OCR_LANG,
        help=f'OCR language code (default: {config.OCR_LANG})'
    )
    
    parser.add_argument(
        '-e', '--enhanced',
        action='store_true',
        help='Use enhanced OCR with image preprocessing'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=config.LOG_LEVEL,
        help=f'Logging level (default: {config.LOG_LEVEL})'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Process document
    success = process_document(
        input_path=args.input,
        output_path=args.output,
        text_placement=args.placement,
        lang=args.lang,
        enhanced=args.enhanced
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
