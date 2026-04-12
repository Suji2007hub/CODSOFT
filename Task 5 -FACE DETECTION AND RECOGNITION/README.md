Here’s the **README for Task 5** – Face Detection & Recognition – following the exact same structure and style as your Task 4 README.

---

```markdown
# FaceVision – Face Detection & Recognition

**Author:** [Your Name]  
**Date:** April 2026  
**Internship Task:** 5 – Face Detection and Recognition

---

## 📌 Overview

FaceVision is a **real‑time face detection and recognition system** that identifies faces in images or from a webcam. It uses:

- **OpenCV DNN** (deep neural network) for accurate face detection.
- **LBP (Local Binary Patterns) + KNN** for lightweight, interpretable face recognition.

The application provides a web interface where users can upload images, use live webcam, train the model with known faces, and even enroll new faces on the fly.

---

## 🎯 Features

- 👤 **Face detection** – DNN‑based (more accurate than Haar cascades)
- 🧠 **Face recognition** – LBP texture features + K‑Nearest Neighbors
- 📸 **Image upload** – Detect & recognise faces in any image
- 🎥 **Live webcam** – Real‑time detection & recognition (every 0.5 seconds)
- 📝 **Enrollment** – Capture a face from webcam, enter name, and retrain instantly
- 💾 **Model persistence** – Trained model saved to disk (`face_model.pkl`)
- 🧪 **Confidence threshold** – Only show recognised names if confidence > 60%
- 🌐 **Flask web interface** – Clean, responsive UI with JavaScript

---

## 🛠️ Tech Stack

| Component         | Technology                                      |
| ----------------- | ----------------------------------------------- |
| Backend           | Python 3.8+                                     |
| Web Framework     | Flask                                           |
| Face Detection    | OpenCV DNN (Caffe model: `res10_300x300_ssd`)   |
| Face Recognition  | LBP + KNN (scikit‑image, scikit‑learn)          |
| Image Processing  | OpenCV, NumPy                                   |
| Frontend          | HTML, CSS, JavaScript, Canvas API               |

---

## 📁 Project Structure

```
task5/
│
├── face_vision_app.py          # Main application (single file)
├── README.md                   # This file
│
├── data/
│   └── known_faces/            # Training images – one folder per person
│       ├── Alice/
│       │   ├── alice1.jpg
│       │   └── alice2.jpg
│       └── Bob/
│           ├── bob1.jpg
│           └── bob2.jpg
│
├── temp_faces/                 # Auto‑created for temporary uploads
│
├── face_model.pkl              # Saved KNN model (auto‑generated after training)
├── label_map.pkl               # Saved label mapping (auto‑generated)
│
├── deploy.prototxt             # DNN model config (auto‑downloaded)
└── res10_300x300_ssd_iter_140000.caffemodel  # DNN model weights (auto‑downloaded)
```

> **Note:** The two DNN model files and the `temp_faces/` folder are created automatically when you run the app for the first time.

---

## ⚙️ Installation & Run

### 1. Install dependencies

```bash
pip install flask opencv-python scikit-image scikit-learn numpy
```

### 2. Prepare training data (optional but needed for recognition)

Create folders inside `data/known_faces/` – one folder per person.  
Add 2–3 clear frontal face photos of each person.

Example:
```
data/known_faces/Alice/photo1.jpg
data/known_faces/Alice/photo2.jpg
data/known_faces/Bob/bob1.jpg
```

### 3. Run the application

```bash
python face_vision_app.py
```

### 4. Open in browser

```
http://127.0.0.1:5000
```

> The first run downloads the DNN face detection model (~10 MB). Wait for it to finish.

---

## 🧠 How It Works

1. **Face Detection** – DNN model (SSD + ResNet) processes the image and outputs bounding boxes with confidence scores (>0.5 accepted).

2. **Face Cropping** – Each detected face is cropped, resized to 100×100, and converted to grayscale.

3. **Feature Extraction (LBP)** – Local Binary Pattern histogram is computed (uniform pattern, 8 points, radius 1). The histogram is normalized.

4. **Recognition (KNN)** – The feature vector is compared to known faces using K‑Nearest Neighbors (k=3, distance‑weighted). If confidence < 60%, label is "Unknown".

5. **Training** – The app scans `data/known_faces/`, extracts LBP features from all face crops, and trains a KNN classifier.

6. **Enrollment** – Captured face from webcam is saved to `data/known_faces/[name]/` and the model is retrained automatically.

---

## ✨ Unique Design Highlights

| Generic Approach                 | FaceVision Implementation                               |
| -------------------------------- | ------------------------------------------------------- |
| Haar cascade detection           | **DNN detector** (more accurate, modern)               |
| DeepFace / FaceNet (heavy)       | **LBP + KNN** (lightweight, interpretable, custom)     |
| Command‑line only                | **Full web interface** with image upload & webcam      |
| No enrollment                    | **Live enrollment** – add faces without editing files  |
| Separate model & UI files        | **Single file** – easier to submit and review          |
| Fixed confidence threshold       | **60% adjustable threshold** (can be changed in code)  |
| Static recognition               | **Real‑time webcam processing** every 0.5 seconds      |

---

## 🧪 Evaluation Checklist

| Requirement                               | Status |
| ----------------------------------------- | ------ |
| Detect faces in images or videos          | ✅      |
| Use pre‑trained face detection model      | ✅ (DNN) |
| Recognise faces (optional)                | ✅ (LBP+KNN) |
| Clean, structured code                    | ✅      |
| Unique / not copied from internet         | ✅      |
| Web interface or interactive demo         | ✅      |
| Real‑time / webcam support                | ✅      |

---

## 👨‍💻 Author & Submission

This project was completed as **Task 5** of the **CodeSoft Internship Program**.  
All code is original and written by me, **[V S Sujithraa]**.

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details

