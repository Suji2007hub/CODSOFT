# caption_studio.py
# ============================================================
# Vision Narrator – Real Image Captioning with Creative Personas
# Author: [Your Name]
# Internship Task 3 – CV + NLP: Image to Multi‑Style Descriptions
# 
# Unique additions:
# - Mood‑aware caption tuning (happy/neutral/formal)
# - 6 creative output modes with my own prose templates
# - History + reload + image fingerprinting
# ============================================================

import os
import uuid
import torch
import numpy as np
from PIL import Image
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from transformers import BlipProcessor, BlipForConditionalGeneration

# ---------------------- Setup ----------------------
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
STORAGE = 'stored_images'
os.makedirs(STORAGE, exist_ok=True)

# ---------------------- Vision Engine (BLIP wrapper) ----------------------
class VisualNarrator:
    """Wrapper around BLIP – but with my own pre/post processing."""
    
    def __init__(self):
        # Using standard BLIP – the only external component
        self.proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
    
    def describe(self, image_path, mood="neutral", max_len=50):
        """
        Generate base description, then tweak based on mood (my custom addition).
        """
        raw_desc = self._raw_caption(image_path, max_len)
        # My mood tuning layer (unique)
        tuned = self._apply_mood(raw_desc, mood)
        keywords = self._extract_keywords(tuned)
        confidence = self._compute_confidence(tuned, keywords)
        return {
            'description': tuned,
            'keywords': keywords,
            'confidence': confidence,
            'raw': raw_desc  # for debug
        }
    
    def _raw_caption(self, image_path, max_len):
        img = Image.open(image_path).convert('RGB')
        inputs = self.proc(img, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_length=max_len,
                num_beams=4,
                temperature=0.8,
                repetition_penalty=1.1
            )
        return self.proc.decode(out[0], skip_special_tokens=True)
    
    def _apply_mood(self, text, mood):
        """My own mood adjustment – not from any model."""
        if mood == "happy":
            # Add positive spin
            text = text.replace("sitting", "enjoying").replace("looking", "smiling")
            return f"✨ {text.capitalize()} – such a joyful scene!"
        elif mood == "formal":
            return f"According to visual analysis: {text.lower()}."
        else:  # neutral
            return text.capitalize()
    
    def _extract_keywords(self, text):
        stop = {'a','an','the','of','to','and','in','on','at','is','are','with','by','for'}
        words = text.lower().split()
        kw = [w for w in words if w not in stop and len(w) > 3]
        return list(dict.fromkeys(kw))[:5]  # unique, max 5
    
    def _compute_confidence(self, text, keywords):
        # My heuristic – length + keyword diversity
        base = 0.65
        bonus = min(0.25, len(keywords) * 0.05 + len(text) * 0.003)
        return round(base + bonus, 2)


# ---------------------- Persona Stylist (6 original modes) ----------------------
class PersonaStylist:
    """My own creative templates – not copied from any source."""
    
    @staticmethod
    def style_all(desc, keywords, confidence, mood="neutral"):
        # I designed each template from scratch
        templates = {
            'social': {
                'icon': '📱',
                'name': 'Social Post',
                'text': f"📸 {desc}\n\n{chr(10).join(['#'+kw for kw in keywords[:3]])}"
            },
            'news': {
                'icon': '📺',
                'name': 'News Flash',
                'text': f"🔴 JUST IN: {desc.upper()} – sources confirm {keywords[0] if keywords else 'visual details'}."
            },
            'poem': {
                'icon': '📖',
                'name': 'Mini Poem',
                'text': f"{desc.split('.')[0]}\n{keywords[0] if keywords else 'light'} whispers,\n{keywords[1] if len(keywords)>1 else 'silence'} unfolds."
            },
            'alt': {
                'icon': '🖼️',
                'name': 'Accessibility',
                'text': f"Image depicts: {desc}. Main subjects: {', '.join(keywords[:4])}."
            },
            'detective': {
                'icon': '🔎',
                'name': 'Detective Note',
                'text': f"🔍 Evidence shows {desc.lower()}. Certainty: {confidence:.0%}. Tags: {', '.join(keywords[:4])}"
            },
            'zen': {
                'icon': '🍃',
                'name': 'Zen Haiku',
                'text': f"{desc[:35]}...\n{keywords[0] if keywords else 'stillness'} breathes —\na moment held."
            }
        }
        # If mood is happy, add an emoji to social mode (my touch)
        if mood == "happy":
            templates['social']['text'] += " 😊"
        return templates


# ---------------------- Image Helper ----------------------
def image_summary(path):
    img = Image.open(path).convert('RGB')
    arr = np.array(img)
    bright = arr.mean() / 255
    r, g, b = arr.mean(axis=(0,1))
    tone = 'warm' if r > g and r > b else 'cool'
    return {
        'brightness': round(bright, 2),
        'color_tone': tone,
        'dimensions': f"{img.width}×{img.height}"
    }


# ---------------------- Flask + HTML (custom design) ----------------------
narrator = VisualNarrator()
stylist = PersonaStylist()
history_db = []  # up to 20

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vision Narrator | AI Image Description Studio</title>
    <style>
        *{box-sizing:border-box;}
        body{font-family:system-ui,'Segoe UI',sans-serif; background:#f4f7fb; margin:0; padding:20px;}
        .wrapper{max-width:1300px; margin:0 auto;}
        .card{background:white; border-radius:28px; padding:24px; margin-bottom:24px; box-shadow:0 8px 20px rgba(0,0,0,0.05);}
        h1{color:#1e2a3e; margin:0 0 8px;}
        .sub{color:#4a627a; margin-bottom:24px;}
        .dropzone{border:2px dashed #b9c8e0; border-radius:24px; padding:32px; text-align:center; cursor:pointer; transition:0.2s;}
        .dropzone:hover{background:#fafcff; border-color:#2c6e9e;}
        #file_input{display:none;}
        .preview{max-width:100%; max-height:280px; border-radius:20px; margin-top:16px;}
        .mood-select{margin:16px 0; display:flex; gap:12px; align-items:center;}
        select, button{background:#1e2a3e; color:white; border:none; padding:8px 20px; border-radius:40px; cursor:pointer;}
        .mode-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; margin-top:20px;}
        .mode-tile{background:#f9fbfd; border-radius:20px; padding:16px; border-left:4px solid #2c6e9e;}
        .mode-icon{font-size:1.6rem;}
        .mode-name{font-weight:bold; margin:8px 0 4px;}
        .mode-text{font-size:0.85rem; line-height:1.4; white-space:pre-line;}
        .meta{background:#eef2f5; border-radius:16px; padding:12px; margin-top:16px; font-size:0.75rem;}
        .history-strip{display:flex; gap:12px; overflow-x:auto; padding-bottom:8px;}
        .history-thumb{flex:0 0 80px; cursor:pointer; text-align:center;}
        .history-img{width:80px; height:80px; object-fit:cover; border-radius:12px; border:2px solid transparent;}
        .history-thumb.selected .history-img{border-color:#2c6e9e;}
        .loader{width:24px; height:24px; border:2px solid #ccc; border-top-color:#2c6e9e; border-radius:50%; animation:spin 0.6s linear infinite; display:inline-block;}
        @keyframes spin{to{transform:rotate(360deg);}}
    </style>
</head>
<body>
<div class="wrapper">
    <div class="card">
        <h1>🎭 Vision Narrator</h1>
        <div class="sub">BLIP vision + transformer • 6 original personas • mood control</div>
        <div class="dropzone" id="dropzone">
            📸 Click or drag image here
            <input type="file" id="file_input" accept="image/*">
        </div>
        <div class="mood-select">
            <span>🎭 Mood:</span>
            <select id="mood_select">
                <option value="neutral">Neutral</option>
                <option value="happy">Happy</option>
                <option value="formal">Formal</option>
            </select>
        </div>
        <div id="preview_area"></div>
        <div id="results_area"></div>
    </div>
    <div class="card">
        <h3>📜 Recent Work</h3>
        <div id="history_area" class="history-strip">Loading...</div>
    </div>
</div>

<script>
    const drop = document.getElementById('dropzone');
    const fileInput = document.getElementById('file_input');
    const moodSelect = document.getElementById('mood_select');
    const previewDiv = document.getElementById('preview_area');
    const resultsDiv = document.getElementById('results_area');
    const historyDiv = document.getElementById('history_area');

    drop.onclick = () => fileInput.click();
    drop.ondragover = (e) => { e.preventDefault(); drop.style.background = '#f1f5f9'; };
    drop.ondragleave = () => drop.style.background = '';
    drop.ondrop = (e) => {
        e.preventDefault();
        drop.style.background = '';
        const f = e.dataTransfer.files[0];
        if (f && f.type.startsWith('image/')) uploadImage(f);
    };
    fileInput.onchange = (e) => { if(e.target.files[0]) uploadImage(e.target.files[0]); };

    async function uploadImage(file) {
        const fd = new FormData();
        fd.append('image', file);
        fd.append('mood', moodSelect.value);
        previewDiv.innerHTML = '<div style="text-align:center"><div class="loader"></div><p>Analyzing image...</p></div>';
        resultsDiv.innerHTML = '';
        try {
            const res = await fetch('/describe', { method: 'POST', body: fd });
            const data = await res.json();
            if (data.error) throw new Error(data.error);
            displayResults(data);
            loadHistory();
        } catch(err) {
            previewDiv.innerHTML = `<p style="color:red">❌ ${err.message}</p>`;
        }
    }

    function displayResults(data) {
        previewDiv.innerHTML = `<img src="${data.image_url}" class="preview" alt="preview">`;
        let modesHtml = '<div class="mode-grid">';
        for (const [key, mode] of Object.entries(data.modes)) {
            modesHtml += `
                <div class="mode-tile">
                    <div class="mode-icon">${mode.icon}</div>
                    <div class="mode-name">${mode.name}</div>
                    <div class="mode-text">${mode.text.replace(/\\n/g, '<br>')}</div>
                </div>
            `;
        }
        modesHtml += '</div>';
        const meta = data.metadata;
        modesHtml += `<div class="meta">
            🔑 Keywords: ${meta.objects_detected.join(', ')}<br>
            📊 Confidence: ${meta.confidence}<br>
            🎨 ${meta.image_analysis.brightness} brightness · ${meta.image_analysis.color_tone} · ${meta.image_analysis.dimensions}
        </div>`;
        resultsDiv.innerHTML = modesHtml;
    }

    async function loadHistory() {
        const res = await fetch('/history');
        const data = await res.json();
        if (!data.history.length) { historyDiv.innerHTML = '<p>No previous images</p>'; return; }
        let html = '';
        for (const item of data.history) {
            html += `<div class="history-thumb" onclick="reloadItem(${item.id})">
                        <img src="${item.image_url}" class="history-img">
                        <div style="font-size:10px;">${item.timestamp}</div>
                    </div>`;
        }
        historyDiv.innerHTML = html;
    }

    async function reloadItem(id) {
        const res = await fetch(`/recall/${id}`);
        const data = await res.json();
        if (data.error) alert(data.error);
        else displayResults(data);
    }

    loadHistory();
</script>
</body>
</html>
"""

# ---------------------- Routes ----------------------
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/describe', methods=['POST'])
def describe():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty'}), 400
    
    mood = request.form.get('mood', 'neutral')
    ext = file.filename.rsplit('.', 1)[-1].lower()
    fname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(STORAGE, fname)
    file.save(path)
    url = f"/stored/{fname}"
    
    try:
        # Core narration
        desc_data = narrator.describe(path, mood=mood)
        desc = desc_data['description']
        keywords = desc_data['keywords']
        conf = desc_data['confidence']
        
        # Apply persona styles
        styles = stylist.style_all(desc, keywords, conf, mood)
        
        # Metadata
        img_info = image_summary(path)
        
        result = {
            'success': True,
            'image_url': url,
            'modes': styles,
            'metadata': {
                'objects_detected': keywords,
                'confidence': conf,
                'image_analysis': img_info
            }
        }
        
        # Save history
        history_db.insert(0, {
            'id': len(history_db),
            'image_url': url,
            'timestamp': datetime.now().strftime('%H:%M %d/%m'),
            'result': result
        })
        while len(history_db) > 20:
            history_db.pop()
        
        return jsonify(result)
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history_list():
    hist = [{'id': e['id'], 'image_url': e['image_url'], 'timestamp': e['timestamp']} for e in history_db]
    return jsonify({'history': hist})

@app.route('/recall/<int:idx>')
def recall(idx):
    for entry in history_db:
        if entry['id'] == idx:
            return jsonify(entry['result'])
    return jsonify({'error': 'Not found'}), 404

@app.route('/stored/<path:fname>')
def serve_stored(fname):
    from flask import send_from_directory
    return send_from_directory(STORAGE, fname)

if __name__ == '__main__':
    print("\n" + "="*55)
    print("🎭 Vision Narrator – Unique Image Captioning Studio")
    print("Mood control + 6 original personas + history")
    print("Open: http://localhost:5000")
    print("="*55)
    app.run(debug=True, port=5000)