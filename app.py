from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import logging
from ocr_processing import process_license_plate

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

UPLOAD_FOLDER = 'Uploads'
STATIC_IMAGES = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_IMAGES, exist_ok=True)

# Serve Uploads folder
@app.route('/Uploads/<path:filename>')
def serve_uploaded_file(filename):
    try:
        logging.debug(f"Serving file: {filename} from {UPLOAD_FOLDER}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logging.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': f'File not found: {filename}'}), 404

@app.route('/')
def index():
    try:
        car_images = [f for f in os.listdir(STATIC_IMAGES) if f.endswith(('.jpg', '.jpeg', '.png'))]
        logging.info(f"Found {len(car_images)} images in static/images")
        return render_template('index.html', car_images=car_images)
    except Exception as e:
        logging.error(f"Error in index route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_image():
    try:
        logging.debug(f"Request form: {request.form}, Files: {request.files}")
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                logging.warning("No file selected for upload")
                return jsonify({'error': 'No file selected'}), 400
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logging.info(f"Saved uploaded file: {filepath}")
        else:
            filename = request.form.get('selected_image')
            if not filename:
                logging.warning("No image selected")
                return jsonify({'error': 'No image selected'}), 400
            filepath = os.path.join(STATIC_IMAGES, filename)
            if not os.path.exists(filepath):
                logging.error(f"Image not found: {filepath}")
                return jsonify({'error': f'Image {filename} not found'}), 400
            logging.info(f"Selected image: {filepath}")

        # Process the image
        result = process_license_plate(filepath)
        if result['error']:
            logging.error(f"Processing error: {result['error']}")
            return jsonify({'error': result['error']}), 400

        logging.info(f"Successfully processed image. Text: {result['text']}")
        base_filename = os.path.basename(filepath)
        return jsonify({
            'text': result['text'],
            'processed_image': f'/Uploads/processed_{base_filename}',
            'steps': {
                'original': f'/Uploads/original_{base_filename}',
                'grayscale': f'/Uploads/grayscale_{base_filename}',
                'edge': f'/Uploads/edge_{base_filename}',
                'contoured': f'/Uploads/contoured_{base_filename}',
                'cropped': f'/Uploads/cropped_{base_filename}',
                'annotated': f'/Uploads/processed_{base_filename}'
            }
        })
    except Exception as e:
        logging.error(f"Error in process_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)