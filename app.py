"""
Flask Web Application for Image to Text Converter
Production-ready web interface for document processing
"""
import os
import uuid
import logging
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename

from image_extractor import ImageExtractor
from ocr_processor import OCRProcessor
from document_processor import DocumentProcessor
import config

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload settings
UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('outputs')
ALLOWED_EXTENSIONS = {'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create folders if they don't exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent overwrites"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(original_filename)
    return f"{secure_filename(name)}_{timestamp}_{unique_id}{ext}"


def process_document(input_path: str, output_path: str, text_placement: str = 'below',
                     lang: str = 'eng', enhanced: bool = False):
    """
    Process a Word document to extract text from images
    
    Returns:
        tuple: (success: bool, message: str, images_processed: int)
    """
    try:
        # Step 1: Extract images from document
        logger.info(f"Processing document: {input_path}")
        extractor = ImageExtractor(input_path)
        images = extractor.extract_images()
        
        if not images:
            return False, "No images found in the document", 0
        
        logger.info(f"Found {len(images)} images")
        
        # Step 2: Perform OCR on each image
        ocr = OCRProcessor(lang=lang)
        image_texts = {}
        processed_count = 0
        
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
                processed_count += 1
                logger.info(f"Extracted {len(text)} characters from {img_info.image_id}")
        
        # Step 3: Create output document with extracted text
        doc_processor = DocumentProcessor(extractor.document, text_placement=text_placement)
        modified_doc = doc_processor.add_text_to_document(image_texts, images)
        
        # Step 4: Save the modified document
        modified_doc.save(output_path)
        logger.info(f"Saved processed document to: {output_path}")
        
        return True, f"Successfully processed {processed_count} images", processed_count
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return False, f"Error processing document: {str(e)}", 0


def cleanup_old_files(folder: Path, max_age_hours: int = 24):
    """Remove files older than max_age_hours"""
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in folder.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")


@app.route('/')
def index():
    """Home page with upload form"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    # Cleanup old files periodically
    cleanup_old_files(UPLOAD_FOLDER)
    cleanup_old_files(OUTPUT_FOLDER)
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a .docx file', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get processing options
        text_placement = request.form.get('text_placement', 'below')
        language = request.form.get('language', 'eng')
        enhanced = request.form.get('enhanced', 'false') == 'true'
        
        # Save uploaded file
        unique_filename = generate_unique_filename(file.filename)
        input_path = UPLOAD_FOLDER / unique_filename
        file.save(str(input_path))
        logger.info(f"File uploaded: {input_path}")
        
        # Generate output filename
        output_filename = unique_filename.replace('.docx', '_processed.docx')
        output_path = OUTPUT_FOLDER / output_filename
        
        # Process the document
        success, message, images_processed = process_document(
            str(input_path),
            str(output_path),
            text_placement=text_placement,
            lang=language,
            enhanced=enhanced
        )
        
        if success:
            flash(f'{message}', 'success')
            return render_template('result.html', 
                                   filename=output_filename,
                                   original_filename=file.filename,
                                   images_processed=images_processed,
                                   message=message)
        else:
            flash(message, 'error')
            # Clean up uploaded file on failure
            if input_path.exists():
                input_path.unlink()
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    """Download processed file"""
    try:
        file_path = OUTPUT_FOLDER / secure_filename(filename)
        
        if not file_path.exists():
            flash('File not found or expired', 'error')
            return redirect(url_for('index'))
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))


@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for programmatic access"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        # Get options from JSON or form
        text_placement = request.form.get('text_placement', 'below')
        language = request.form.get('language', 'eng')
        enhanced = request.form.get('enhanced', 'false').lower() == 'true'
        
        # Save and process
        unique_filename = generate_unique_filename(file.filename)
        input_path = UPLOAD_FOLDER / unique_filename
        file.save(str(input_path))
        
        output_filename = unique_filename.replace('.docx', '_processed.docx')
        output_path = OUTPUT_FOLDER / output_filename
        
        success, message, images_processed = process_document(
            str(input_path),
            str(output_path),
            text_placement=text_placement,
            lang=language,
            enhanced=enhanced
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'images_processed': images_processed,
                'download_url': url_for('download_file', filename=output_filename, _external=True)
            })
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File is too large. Maximum size is 16MB', 'error')
    return redirect(url_for('index'))


@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    logger.error(f"Server error: {str(e)}")
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
