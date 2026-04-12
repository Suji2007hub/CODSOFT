
# Vision Narrator – Image Captioning AI (CV + NLP)

---

## 📌 Overview

This project is an **Image Captioning AI system** that generates natural language descriptions for uploaded images.

It combines:
- **Computer Vision (Vision Transformer / BLIP model)**
- **Natural Language Processing (Transformer-based text generation)**

The system not only generates captions but also transforms them into multiple creative formats.

---

## 🎯 Features

- ✅ Image caption generation using pre-trained BLIP model
- ✅ Vision Transformer-based feature extraction
- ✅ Transformer decoder for text generation
- ✅ Multi-style caption generation:
  - Tweet style
  - News headline
  - Poetic description
  - Accessibility alt-text
  - Forensic report
  - Haiku format
- ✅ Keyword extraction from captions
- ✅ Confidence score estimation
- ✅ Image metadata analysis (brightness, color tone, size)
- ✅ Upload-based web interface using Flask
- ✅ History system for previously generated captions
- ✅ Single-file or minimal structured architecture

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.8+ |
| Deep Learning | PyTorch |
| Vision-Language | BLIP (Salesforce pretrained model) |
| NLP | HuggingFace Transformers |
| Web Framework | Flask |
| Image Processing | PIL, NumPy |

---

## 📁 Project Structure

```
task3/
└── caption_app.py   # Complete CV + NLP + Web Application
└── README.md        # Documentation
```

---

## ⚙️ Installation & Run

### 1. Install dependencies

```bash
pip install torch torchvision transformers flask pillow numpy
```

### 2. Run application

```bash
python caption_app.py
```

### 3. Open browser

```
http://localhost:5000
```

> First run may download the BLIP model (~1.5GB).

---

## 🧠 How It Works

The system works in 3 stages:

**1. Image Processing (Computer Vision)**
- Input image is processed using a Vision Transformer (BLIP model)
- Visual features are extracted

**2. Caption Generation (NLP)**
- Transformer decoder generates a base caption
- Example: `"a dog sitting on a sofa"`

**3. Post Processing**
- Extracts keywords from caption
- Computes confidence score
- Converts caption into multiple creative formats

---

## ✨ Unique Design Choices

- Single model pipeline (Vision + Language combined)
- Multi-style caption transformation (6 formats)
- Custom keyword extraction logic
- Confidence scoring heuristic
- Image metadata analysis (brightness + color tone)
- History tracking system for previous outputs
- Lightweight Flask API design

---

## 📝 Evaluation Checklist

| Requirement | Status |
|---|---|
| Combine Computer Vision + NLP | ✅ |
| Pre-trained image model (ViT/ResNet equiv.) | ✅ |
| Transformer-based caption generation | ✅ |
| Image-to-text output | ✅ |
| Clean structured implementation | ✅ |
| Web interface (Flask) | ✅ |
| Unique implementation | ✅ |

---

## 👨‍💻 Author & Submission

This project was completed as **Task 3** of the **CodeSoft Internship Program**.  
All code is original and written by me, **V S Sujithraa**.

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details


