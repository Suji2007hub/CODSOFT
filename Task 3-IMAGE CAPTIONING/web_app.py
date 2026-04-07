"""
web_app.py
Flask backend for Multi-Mode Caption Studio
Handles upload, caption generation, history, and reload.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from caption_modes import RealImageCaptioning, MultiModeFormatter, simple_image_analysis
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load models once at startup
caption_model = RealImageCaptioning()
formatter = MultiModeFormatter()

# In-memory history (max 20 entries)
caption_history = []


@app.route('/')
def index():
    """Serve the main HTML interface."""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve uploaded images."""
    return send_from_directory('static', filename)


@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Handle image upload, generate captions, return JSON.
    Steps:
    1. Save uploaded image.
    2. Generate base caption using BLIP (vision + language).
    3. Format into six styles.
    4. Add metadata.
    5. Store in history.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Secure filename
    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    image_url = f"/static/uploads/{filename}"
    
    try:
        # 1. Generate base caption (CNN + Transformer)
        caption_data = caption_model.generate_caption(filepath)
        base_caption = caption_data['caption']
        keywords = caption_data['keywords']
        confidence = caption_data['confidence']
        
        # 2. Multi-mode styling (NLP post-processing)
        styled_captions = formatter.format_all(base_caption, keywords, confidence)
        
        # 3. Extra metadata (not required but nice for UI)
        image_info = simple_image_analysis(filepath)
        
        result = {
            'success': True,
            'image_url': image_url,
            'base_caption': base_caption,
            'modes': styled_captions,
            'metadata': {
                'objects_detected': keywords,
                'image_analysis': image_info,
                'confidence': confidence
            }
        }
        
        # Store in history
        history_entry = {
            'id': len(caption_history),
            'image_url': image_url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'result': result
        }
        caption_history.insert(0, history_entry)
        while len(caption_history) > 20:
            caption_history.pop()
        
        return jsonify(result)
        
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f"Caption generation failed: {str(e)}"}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """Return list of previous uploads (image URL + timestamp)."""
    history_list = [
        {'id': entry['id'], 'image_url': entry['image_url'], 'timestamp': entry['timestamp']}
        for entry in caption_history
    ]
    return jsonify({'history': history_list})


@app.route('/reload/<int:history_id>', methods=['GET'])
def reload_history(history_id):
    """Return full caption result for a previous upload (without reprocessing)."""
    for entry in caption_history:
        if entry['id'] == history_id:
            return jsonify(entry['result'])
    return jsonify({'error': 'History entry not found'}), 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎨 MULTI-MODE CAPTION STUDIO - REAL IMAGE CAPTIONING")
    print("="*60)
    print("Using BLIP: Vision Transformer (CNN) + Transformer Decoder (RNN replacement)")
    print("Model will download on first run (~1.5GB)")
    print("Server: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)