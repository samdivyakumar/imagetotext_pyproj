"""
Image extraction utilities for Word documents
"""
import io
from typing import List, Tuple
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageInfo:
    """Class to store information about an image in the document"""
    
    def __init__(self, image_data: bytes, image_id: str, paragraph_index: int, run_index: int):
        self.image_data = image_data
        self.image_id = image_id
        self.paragraph_index = paragraph_index
        self.run_index = run_index
        self.pil_image = None
        
    def to_pil_image(self) -> Image.Image:
        """Convert image data to PIL Image"""
        if self.pil_image is None:
            self.pil_image = Image.open(io.BytesIO(self.image_data))
        return self.pil_image


class ImageExtractor:
    """Extract images from Word documents"""
    
    def __init__(self, doc_path: str):
        self.doc_path = doc_path
        self.document = None
        
    def load_document(self) -> Document:
        """Load the Word document"""
        try:
            self.document = Document(self.doc_path)
            logger.info(f"Successfully loaded document: {self.doc_path}")
            return self.document
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise
    
    def extract_images(self) -> List[ImageInfo]:
        """
        Extract all images from the document with their positions
        
        Returns:
            List of ImageInfo objects containing image data and position information
        """
        if self.document is None:
            self.load_document()
        
        images = []
        image_counter = 0
        
        # Iterate through all paragraphs
        for para_idx, paragraph in enumerate(self.document.paragraphs):
            # Iterate through all runs in the paragraph
            for run_idx, run in enumerate(paragraph.runs):
                # Check if run contains an image
                inline_shapes = run._element.findall(qn('w:drawing'))
                
                for drawing in inline_shapes:
                    # Get the image relationship ID
                    blips = drawing.findall('.//' + qn('a:blip'))
                    
                    for blip in blips:
                        rId = blip.get(qn('r:embed'))
                        if rId:
                            try:
                                # Get the image from the document's part
                                image_part = self.document.part.related_parts[rId]
                                image_data = image_part.blob
                                
                                # Create ImageInfo object
                                image_info = ImageInfo(
                                    image_data=image_data,
                                    image_id=f"image_{image_counter}",
                                    paragraph_index=para_idx,
                                    run_index=run_idx
                                )
                                
                                images.append(image_info)
                                image_counter += 1
                                logger.info(f"Extracted image {image_counter} from paragraph {para_idx}")
                                
                            except Exception as e:
                                logger.warning(f"Failed to extract image with rId {rId}: {e}")
        
        logger.info(f"Total images extracted: {len(images)}")
        return images
    
    def get_document(self) -> Document:
        """Get the loaded document"""
        if self.document is None:
            self.load_document()
        return self.document
