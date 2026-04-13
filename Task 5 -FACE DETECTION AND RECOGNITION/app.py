# face_vision_app.py
# ============================================================
# FaceVision – Real‑time Face Detection & Recognition
# Author: [Your Name]
# Task 5: Face detection + recognition using DNN detector
#         and LBP + KNN recognizer (custom implementation)
# Features: Web UI, image upload, webcam, enroll new faces
# ============================================================

import os
import cv2
import numpy as np
import pickle
import base64
from flask import Flask, render_template_string, request, jsonify, Response
from skimage.feature import local_binary_pattern
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize

# ---------------------- Configuration ----------------------
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
UPLOAD_FOLDER = 'temp_faces'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Recognition parameters
LBP_RADIUS = 1
LBP_N_POINTS = 8 * LBP_RADIUS
LBP_METHOD = 'uniform'
KNN_NEIGHBORS = 3
RECOGNITION_THRESHOLD = 0.6   # 60% confidence required

# Paths
MODEL_PATH = 'face_model.pkl'
LABEL_MAP_PATH = 'label_map.pkl'

# ---------------------- DNN Face Detector (more accurate than Haar) ----------------------
class ModernFaceDetector:
    """Uses OpenCV's DNN module with a pre-trained Caffe model."""
    
    def __init__(self):
        # Download model files if not present
        prototxt = "deploy.prototxt"
        caffemodel = "res10_300x300_ssd_iter_140000.caffemodel"
        
        if not os.path.exists(prototxt) or not os.path.exists(caffemodel):
            print("[Detector] Downloading face detection model...")
            import urllib.request
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
                prototxt
            )
            urllib.request.urlretrieve(
                "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel",
                caffemodel
            )
        
        self.net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
        print("[Detector] DNN face detector ready.")
    
    def detect(self, image, conf_threshold=0.5):
        """Return list of (x, y, w, h) face boxes."""
        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123], False, False)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x, y, x2, y2) = box.astype("int")
                x, y = max(0, x), max(0, y)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x and y2 > y:
                    faces.append((x, y, x2 - x, y2 - y))
        return faces


# ---------------------- LBP + KNN Recognizer (your custom logic) ----------------------
class TextureRecognizer:
    def __init__(self):
        self.knn = None
        self.label_map = {}   # id -> name
        self.trained = False
    
    def _extract_features(self, face_img):
        """LBP histogram normalized."""
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
        gray = cv2.equalizeHist(gray)
        resized = cv2.resize(gray, (100, 100))
        lbp = local_binary_pattern(resized, LBP_N_POINTS, LBP_RADIUS, method=LBP_METHOD)
        n_bins = LBP_N_POINTS + 2
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins))
        return normalize(hist.reshape(1, -1), norm='l2').ravel()
    
    def train(self, face_samples, labels):
        if not face_samples:
            raise ValueError("No training samples")
        features = np.array([self._extract_features(f) for f in face_samples])
        k = min(KNN_NEIGHBORS, len(face_samples))
        self.knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
        self.knn.fit(features, labels)
        self.trained = True
    
    def predict(self, face_img):
        if not self.trained:
            return "Unknown", 0.0
        feat = self._extract_features(face_img).reshape(1, -1)
        proba = self.knn.predict_proba(feat)[0]
        best_idx = np.argmax(proba)
        confidence = proba[best_idx]
        if confidence < RECOGNITION_THRESHOLD:
            return "Unknown", confidence
        label_id = self.knn.classes_[best_idx]
        name = self.label_map.get(label_id, f"Person-{label_id}")
        return name, confidence
    
    def save(self):
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump({'knn': self.knn, 'label_map': self.label_map}, f)
    
    def load(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                data = pickle.load(f)
                self.knn = data['knn']
                self.label_map = data['label_map']
                self.trained = True
            return True
        return False
    
    def set_label_map(self, label_map):
        self.label_map = label_map


# ---------------------- Training Helper ----------------------
def collect_training_faces(detector):
    """Scan data/known_faces/ folder and return (face_samples, labels, label_map)."""
    data_dir = "data/known_faces"
    if not os.path.exists(data_dir):
        return [], [], {}
    
    face_samples = []
    labels = []
    label_map = {}
    label_id = 0
    
    for person_name in os.listdir(data_dir):
        person_path = os.path.join(data_dir, person_name)
        if not os.path.isdir(person_path):
            continue
        label_map[label_id] = person_name
        for img_file in os.listdir(person_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(person_path, img_file)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                faces = detector.detect(img)
                if faces:
                    x, y, w, h = faces[0]  # take largest face
                    face_roi = img[y:y+h, x:x+w]
                    face_samples.append(face_roi)
                    labels.append(label_id)
        label_id += 1
    return face_samples, labels, label_map


# ---------------------- Flask Web UI ----------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FaceVision | Detect & Recognize</title>
    <style>
        *{box-sizing:border-box;}
        body{font-family:'Segoe UI',sans-serif; background:#0f172a; color:#f1f5f9; margin:0; padding:20px;}
        .container{max-width:1200px; margin:0 auto;}
        h1{color:#f59e0b;}
        .grid{display:grid; grid-template-columns:1fr 1fr; gap:24px;}
        .card{background:#1e293b; border-radius:24px; padding:20px; box-shadow:0 8px 20px rgba(0,0,0,0.3);}
        .card h2{margin-top:0;}
        button, .btn{background:#f59e0b; border:none; padding:10px 20px; border-radius:40px; cursor:pointer; font-weight:bold; margin:5px;}
        .btn-secondary{background:#475569;}
        input, select{width:100%; padding:10px; border-radius:12px; border:1px solid #475569; background:#0f172a; color:white; margin-bottom:12px;}
        video, canvas, img{width:100%; border-radius:20px; background:#000;}
        .result-box{background:#0f172a; border-radius:16px; padding:12px; margin-top:12px;}
        .face-badge{display:inline-block; background:#f59e0b; color:#0f172a; padding:4px 12px; border-radius:40px; margin:4px;}
        .status{font-size:0.9rem; opacity:0.8;}
        @media (max-width:800px){.grid{grid-template-columns:1fr;}}
    </style>
</head>
<body>
<div class="container">
    <h1>👤 FaceVision</h1>
    <p>DNN face detection + LBP/KNN recognition | Upload image or use webcam</p>
    <div class="grid">
        <!-- Left: Controls & Upload -->
        <div class="card">
            <h2>📸 Image Upload</h2>
            <input type="file" id="imageInput" accept="image/*">
            <button id="uploadBtn">Detect & Recognize</button>
            <div id="uploadPreview"></div>
            <div id="uploadResult"></div>
            <hr>
            <h2>🎥 Webcam</h2>
            <button id="startCam">Start Webcam</button>
            <button id="stopCam" class="btn-secondary">Stop</button>
            <video id="webcam" autoplay playsinline style="display:none;"></video>
            <canvas id="canvas" style="display:none;"></canvas>
            <div id="webcamResult"></div>
        </div>
        <!-- Right: Training & Enroll -->
        <div class="card">
            <h2>🧠 Training</h2>
            <p>Place photos in <code>data/known_faces/PersonName/</code> folder</p>
            <button id="trainBtn">Train Model</button>
            <div id="trainStatus"></div>
            <hr>
            <h2>📝 Enroll New Face</h2>
            <p>Take a photo from webcam, enter name, and add to training set.</p>
            <button id="captureBtn" disabled>Capture Face</button>
            <input type="text" id="newName" placeholder="Enter person's name">
            <button id="enrollBtn" disabled>Enroll & Retrain</button>
            <div id="enrollStatus"></div>
        </div>
    </div>
</div>

<script>
    // DOM elements
    const imgInput = document.getElementById('imageInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadResult = document.getElementById('uploadResult');
    const startCam = document.getElementById('startCam');
    const stopCam = document.getElementById('stopCam');
    const webcamVideo = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const webcamResult = document.getElementById('webcamResult');
    const trainBtn = document.getElementById('trainBtn');
    const trainStatus = document.getElementById('trainStatus');
    const captureBtn = document.getElementById('captureBtn');
    const newNameInput = document.getElementById('newName');
    const enrollBtn = document.getElementById('enrollBtn');
    let stream = null;
    let capturedFace = null;

    // Upload image
    uploadBtn.onclick = async () => {
        const file = imgInput.files[0];
        if (!file) { alert('Select an image'); return; }
        const formData = new FormData();
        formData.append('image', file);
        uploadPreview.innerHTML = '<p>Processing...</p>';
        const res = await fetch('/detect_image', { method: 'POST', body: formData });
        const data = await res.json();
        uploadPreview.innerHTML = `<img src="data:image/jpeg;base64,${data.annotated}" style="max-width:100%; border-radius:20px;">`;
        let facesHtml = '<div class="result-box"><strong>Results:</strong><br>';
        data.faces.forEach(f => {
            facesHtml += `<span class="face-badge">${f.name} (${(f.confidence*100).toFixed(0)}%)</span> `;
        });
        facesHtml += `<div class="status">Total faces: ${data.total_faces} | Recognized: ${data.recognised_count}</div></div>`;
        uploadResult.innerHTML = facesHtml;
    };

    // Webcam
    startCam.onclick = async () => {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        webcamVideo.srcObject = stream;
        webcamVideo.style.display = 'block';
        captureBtn.disabled = false;
        startWebcamDetection();
    };
    stopCam.onclick = () => {
        if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
        webcamVideo.style.display = 'none';
        captureBtn.disabled = true;
        if (detectInterval) clearInterval(detectInterval);
    };
    let detectInterval = null;
    function startWebcamDetection() {
        if (detectInterval) clearInterval(detectInterval);
        detectInterval = setInterval(async () => {
            if (!webcamVideo.videoWidth) return;
            canvas.width = webcamVideo.videoWidth;
            canvas.height = webcamVideo.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
            const dataURL = canvas.toDataURL('image/jpeg');
            const blob = await (await fetch(dataURL)).blob();
            const formData = new FormData();
            formData.append('image', blob);
            const res = await fetch('/detect_image', { method: 'POST', body: formData });
            const data = await res.json();
            webcamResult.innerHTML = `<img src="data:image/jpeg;base64,${data.annotated}" style="max-width:100%; border-radius:20px;">`;
        }, 500);
    }

    // Capture face for enrollment
    captureBtn.onclick = () => {
        if (!webcamVideo.videoWidth) return;
        const ctx = canvas.getContext('2d');
        canvas.width = webcamVideo.videoWidth;
        canvas.height = webcamVideo.videoHeight;
        ctx.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
        // Send to backend to extract largest face
        const dataURL = canvas.toDataURL('image/jpeg');
        fetch('/extract_face', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({image: dataURL}) })
        .then(res => res.json())
        .then(data => {
            if (data.face_base64) {
                capturedFace = data.face_base64;
                enrollBtn.disabled = false;
                document.getElementById('enrollStatus').innerHTML = '<span style="color:#4ade80;">✅ Face captured. Enter name and enroll.</span>';
            } else {
                document.getElementById('enrollStatus').innerHTML = '<span style="color:#f87171;">No face detected. Position your face clearly.</span>';
            }
        });
    };

    enrollBtn.onclick = async () => {
        const name = newNameInput.value.trim();
        if (!name || !capturedFace) { alert('Capture a face and enter name'); return; }
        const res = await fetch('/enroll', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name: name, face: capturedFace}) });
        const data = await res.json();
        if (data.success) {
            document.getElementById('enrollStatus').innerHTML = '<span style="color:#4ade80;">✅ Enrolled! Retrain model.</span>';
            capturedFace = null;
            enrollBtn.disabled = true;
        } else {
            document.getElementById('enrollStatus').innerHTML = '<span style="color:#f87171;">Enrollment failed.</span>';
        }
    };

    trainBtn.onclick = async () => {
        trainStatus.innerHTML = 'Training...';
        const res = await fetch('/train', { method: 'POST' });
        const data = await res.json();
        if (data.success) trainStatus.innerHTML = '<span style="color:#4ade80;">✅ Model trained successfully!</span>';
        else trainStatus.innerHTML = '<span style="color:#f87171;">Training failed. Add face images to data/known_faces/</span>';
    };
</script>
</body>
</html>
"""

# ---------------------- Flask Routes ----------------------
detector = ModernFaceDetector()
recognizer = TextureRecognizer()
recognizer.load()

def annotate_image(image, faces, recognitions):
    out = image.copy()
    for (x, y, w, h), (name, conf) in zip(faces, recognitions):
        color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
        cv2.rectangle(out, (x, y), (x+w, y+h), color, 2)
        label = f"{name} ({conf:.0%})"
        cv2.putText(out, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return out

def encode_image(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/detect_image', methods=['POST'])
def detect_image():
    file = request.files['image']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    faces = detector.detect(img)
    results = []
    for (x,y,w,h) in faces:
        face_roi = img[y:y+h, x:x+w]
        name, conf = recognizer.predict(face_roi)
        results.append((name, conf))
    annotated = annotate_image(img, faces, results)
    annotated_b64 = encode_image(annotated)
    return jsonify({
        'annotated': annotated_b64,
        'faces': [{'name': n, 'confidence': c} for n,c in results],
        'total_faces': len(faces),
        'recognised_count': sum(1 for n,_ in results if n != 'Unknown')
    })

@app.route('/train', methods=['POST'])
def train_model():
    faces_samples, labels, label_map = collect_training_faces(detector)
    if not faces_samples:
        return jsonify({'success': False, 'error': 'No training data'})
    recognizer.train(faces_samples, labels)
    recognizer.set_label_map(label_map)
    recognizer.save()
    return jsonify({'success': True})

@app.route('/enroll', methods=['POST'])
def enroll():
    data = request.json or {}
    name = (data.get('name') or '').strip()
    face_value = data.get('face')

    if not name or not face_value:
        return jsonify({'success': False, 'error': 'Name and face are required'}), 400

    # Accept both data URL format and raw base64 strings.
    face_b64 = face_value.split(',', 1)[1] if ',' in face_value else face_value

    try:
        face_bytes = base64.b64decode(face_b64)
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid face image data'}), 400

    nparr = np.frombuffer(face_bytes, np.uint8)
    face_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if face_img is None:
        return jsonify({'success': False, 'error': 'Unable to decode face image'}), 400

    # Save to data/known_faces/name/
    save_dir = f"data/known_faces/{name}"
    os.makedirs(save_dir, exist_ok=True)
    import uuid
    filename = f"{uuid.uuid4().hex}.jpg"
    cv2.imwrite(os.path.join(save_dir, filename), face_img)
    return jsonify({'success': True})

@app.route('/extract_face', methods=['POST'])
def extract_face():
    data = request.json
    img_b64 = data['image'].split(',')[1]
    img_bytes = base64.b64decode(img_b64)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    faces = detector.detect(img)
    if not faces:
        return jsonify({'face_base64': None})
    x,y,w,h = faces[0]
    face_roi = img[y:y+h, x:x+w]
    _, buffer = cv2.imencode('.jpg', face_roi)
    return jsonify({'face_base64': base64.b64encode(buffer).decode('utf-8')})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("👤 FaceVision – DNN + LBP/KNN Recognition")
    print("Open: http://localhost:5000")
    print("="*50)
    app.run(debug=True, port=5000)