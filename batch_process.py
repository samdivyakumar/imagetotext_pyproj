#!/usr/bin/env python3
"""
Batch processor for multiple Word documents
"""
import argparse
import os
import sys
from pathlib import Path
import logging

from main import process_document, setup_logging
import config


def process_directory(input_dir: str, output_dir: str = None, **kwargs):
    """
    Process all .docx files in a directory
    
    Args:
        input_dir: Directory containing .docx files
        output_dir: Directory to save processed files (optional)
        **kwargs: Additional arguments for process_document
    """
    logger = logging.getLogger(__name__)
    
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        logger.error(f"Input directory not found: {input_dir}")
        return False
    
    # Find all .docx files
    docx_files = list(input_path.glob('*.docx'))
    docx_files = [f for f in docx_files if not f.name.startswith('~')]  # Skip temp files
    
    if not docx_files:
        logger.warning(f"No .docx files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(docx_files)} documents to process")
    
    # Setup output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path / 'processed'
        output_path.mkdir(exist_ok=True)
    
    # Process each file
    success_count = 0
    failed_files = []
    
    for idx, doc_file in enumerate(docx_files, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing file {idx}/{len(docx_files)}: {doc_file.name}")
        logger.info(f"{'='*60}")
        
        output_file = output_path / f"{doc_file.stem}_processed.docx"
        
        try:
            success = process_document(
                input_path=str(doc_file),
                output_path=str(output_file),
                **kwargs
            )
            
            if success:
                success_count += 1
            else:
                failed_files.append(doc_file.name)
                
        except Exception as e:
            logger.error(f"Failed to process {doc_file.name}: {e}")
            failed_files.append(doc_file.name)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("Batch Processing Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Total files: {len(docx_files)}")
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Failed: {len(failed_files)}")
    
    if failed_files:
        logger.warning(f"Failed files: {', '.join(failed_files)}")
    
    logger.info(f"Output directory: {output_path}")
    logger.info(f"{'='*60}")
    
    return len(failed_files) == 0


def main():
    """Main entry point for batch processing"""
    parser = argparse.ArgumentParser(
        description='Batch process multiple Word documents for OCR text extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_process.py ./documents
  python batch_process.py ./documents -o ./output
  python batch_process.py ./documents --placement replace --enhanced
        """
    )
    
    parser.add_argument(
        'input_dir',
        help='Directory containing Word documents to process'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='Directory to save processed documents (default: input_dir/processed)',
        default=None
    )
    
    parser.add_argument(
        '-p', '--placement',
        choices=['below', 'replace'],
        default=config.TEXT_PLACEMENT,
        help=f'How to place extracted text (default: {config.TEXT_PLACEMENT})'
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
    
    # Process directory
    success = process_directory(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        text_placement=args.placement,
        lang=args.lang,
        enhanced=args.enhanced
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
