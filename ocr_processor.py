"""
OCR processor using Tesseract
"""
import pytesseract
from PIL import Image
import logging
from typing import Optional
import config

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Process images using OCR to extract text"""
    
    def __init__(self, lang: str = None, ocr_config: str = None):
        """
        Initialize OCR processor
        
        Args:
            lang: Language code for OCR (e.g., 'eng', 'fra', 'deu')
            ocr_config: Tesseract configuration string
        """
        self.lang = lang or config.OCR_LANG
        self.ocr_config = ocr_config or config.OCR_CONFIG
        
        # Test if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception as e:
            logger.error(f"Tesseract not found. Please install Tesseract OCR: {e}")
            raise
    
    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from a PIL Image using OCR
        
        Args:
            image: PIL Image object
            
        Returns:
            Extracted text as string
        """
        try:
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=self.ocr_config
            )
            
            # Clean up the text
            text = text.strip()
            
            if text:
                logger.info(f"Successfully extracted {len(text)} characters")
            else:
                logger.warning("No text found in image")
            
            return text
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    def extract_text_from_bytes(self, image_data: bytes) -> str:
        """
        Extract text from image bytes
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Extracted text as string
        """
        import io
        
        try:
            image = Image.open(io.BytesIO(image_data))
            return self.extract_text(image)
        except Exception as e:
            logger.error(f"Failed to process image bytes: {e}")
            return ""
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # You can add more preprocessing steps here:
        # - Increase contrast
        # - Remove noise
        # - Binarization
        # - Deskewing
        
        return image
    
    def extract_text_enhanced(self, image: Image.Image) -> str:
        """
        Extract text with image preprocessing for better accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Extracted text as string
        """
        # Preprocess the image
        preprocessed_image = self.preprocess_image(image)
        
        # Extract text
        return self.extract_text(preprocessed_image)
