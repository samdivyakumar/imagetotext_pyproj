#!/bin/bash

# Setup script for Image2Text project
# This script automates the installation process

echo "=========================================="
echo "Image2Text Setup Script"
echo "=========================================="
echo ""

# Check if Tesseract is installed
echo "Step 1: Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null
then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo "✓ Tesseract is installed: $TESSERACT_VERSION"
else
    echo "✗ Tesseract OCR not found!"
    echo ""
    echo "Please install Tesseract OCR:"
    echo "  macOS:        brew install tesseract"
    echo "  Ubuntu:       sudo apt-get install tesseract-ocr"
    echo "  Windows:      https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    read -p "Do you want to install Tesseract now using Homebrew? (macOS only) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        if command -v brew &> /dev/null
        then
            brew install tesseract
        else
            echo "Homebrew not found. Please install Tesseract manually."
            exit 1
        fi
    else
        echo "Please install Tesseract and run this script again."
        exit 1
    fi
fi

echo ""

# Check Python version
echo "Step 2: Checking Python version..."
if command -v python3 &> /dev/null
then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python 3 is installed: $PYTHON_VERSION"
else
    echo "✗ Python 3 not found!"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo ""

# Create virtual environment
echo "Step 3: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "Step 4: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""

# Install dependencies
echo "Step 5: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""

# Run installation test
echo "Step 6: Running installation tests..."
python test_installation.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the test installation:"
echo "     python test_installation.py"
echo ""
echo "  3. Process a document:"
echo "     python main.py your_document.docx"
echo ""
echo "  4. Get help:"
echo "     python main.py --help"
echo ""
echo "For more information, see:"
echo "  - README.md for full documentation"
echo "  - QUICKSTART.md for quick start guide"
echo ""
