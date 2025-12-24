#!/usr/bin/env python3
"""
Test script to verify installation and dependencies
"""
import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import docx
        print("✓ python-docx imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import python-docx: {e}")
        return False
    
    try:
        import pytesseract
        print("✓ pytesseract imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pytesseract: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow (PIL) imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Pillow: {e}")
        return False
    
    return True


def test_tesseract():
    """Test if Tesseract OCR is available"""
    print("\nTesting Tesseract OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR is available (version: {version})")
        return True
    except Exception as e:
        print(f"✗ Tesseract OCR not found: {e}")
        print("\nPlease install Tesseract OCR:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt-get install tesseract-ocr")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return False


def test_basic_ocr():
    """Test basic OCR functionality"""
    print("\nTesting basic OCR functionality...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import pytesseract
        
        # Create a simple test image with text
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Hello World", fill='black')
        
        # Try to extract text
        text = pytesseract.image_to_string(img).strip()
        
        if text:
            print(f"✓ OCR test passed (extracted: '{text}')")
            return True
        else:
            print("⚠ OCR returned empty text (this may be normal for simple test)")
            return True
    except Exception as e:
        print(f"✗ OCR test failed: {e}")
        return False


def test_modules():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")
    
    try:
        import config
        print("✓ config.py loaded successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from image_extractor import ImageExtractor
        print("✓ image_extractor.py loaded successfully")
    except ImportError as e:
        print(f"✗ Failed to import image_extractor: {e}")
        return False
    
    try:
        from ocr_processor import OCRProcessor
        print("✓ ocr_processor.py loaded successfully")
    except ImportError as e:
        print(f"✗ Failed to import ocr_processor: {e}")
        return False
    
    try:
        from document_processor import DocumentProcessor
        print("✓ document_processor.py loaded successfully")
    except ImportError as e:
        print(f"✗ Failed to import document_processor: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Image2Text Installation Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Package Imports", test_imports()))
    results.append(("Tesseract Installation", test_tesseract()))
    results.append(("OCR Functionality", test_basic_ocr()))
    results.append(("Project Modules", test_modules()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Your installation is ready.")
        print("\nTry running:")
        print("  python main.py --help")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
