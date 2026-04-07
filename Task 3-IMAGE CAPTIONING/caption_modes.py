"""
caption_modes.py
Real Image Captioning using BLIP (Vision Transformer + Transformer Decoder)
Satisfies: pre-trained vision model (CNN equivalent) + sequence generation (Transformer)
"""

import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from typing import Dict, List
import numpy as np


class RealImageCaptioning:
    """
    BLIP-based caption generator.
    - Vision Transformer (ViT) acts as the "CNN" feature extractor.
    - Transformer decoder acts as the "RNN/Transformer" caption generator.
    """
    
    def __init__(self):
        # Load pre-trained model (downloads once, ~1.5GB)
        # processor handles image preprocessing and tokenization
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
    def generate_caption(self, image_path: str, max_length: int = 50) -> Dict:
        """
        Generate a caption from an image.
        Steps:
        1. Load and convert image to RGB.
        2. Processor converts image to tensor (vision transformer input).
        3. Model generates token IDs using beam search.
        4. Decode tokens to text.
        5. Extract keywords and compute confidence.
        """
        image = Image.open(image_path).convert('RGB')
        
        # Vision part: extract features (equivalent to CNN)
        inputs = self.processor(image, return_tensors="pt").to(self.device)
        
        # Language part: generate caption (Transformer decoder)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,               # beam search for better quality
                temperature=0.7,           # slight randomness
                repetition_penalty=1.2
            )
        
        caption = self.processor.decode(outputs[0], skip_special_tokens=True)
        
        # Keyword extraction (simple NLP post-processing)
        stopwords = {'a', 'an', 'the', 'of', 'with', 'to', 'and', 'in', 'on', 'at', 'is', 'are'}
        words = caption.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 3][:5]
        
        # Confidence heuristic: based on caption length and keyword variety
        confidence = min(0.6 + (len(keywords) / 20) + (len(caption) / 200), 0.95)
        
        return {
            'caption': caption,
            'keywords': keywords,
            'confidence': round(confidence, 2)
        }


class MultiModeFormatter:
    """Transforms one base caption into multiple stylistic outputs (NLP register adaptation)."""
    
    @staticmethod
    def format_all(base_caption: str, keywords: List[str], confidence: float) -> Dict[str, Dict]:
        """Apply six different style templates to the same base caption."""
        modes = {
            'tweet': {
                'icon': '🐦',
                'name': 'Twitter/X Post',
                'template': lambda c, k: f"📸 {c.capitalize()} {' '.join(['#'+kw for kw in k[:3]])}"
            },
            'news_headline': {
                'icon': '📰',
                'name': 'News Headline',
                'template': lambda c, k: f"BREAKING: {c.upper()} – Visual Analysis Reveals {', '.join(k[:3])}"
            },
            'poetic': {
                'icon': '📝',
                'name': 'Poetic Prose',
                'template': lambda c, k: f"In frames of light, a story grows,\n{c.capitalize()},\nWhere {k[0] if k else 'beauty'} softly shows."
            },
            'alt_text': {
                'icon': '♿',
                'name': 'Accessibility Alt-Text',
                'template': lambda c, k: f"Image description: {c}. Key elements: {', '.join(k[:4])}."
            },
            'forensic': {
                'icon': '🔍',
                'name': 'Forensic Report',
                'template': lambda c, k: f"🔍 FORENSIC ANALYSIS: Visual evidence indicates {c.lower()}. Confidence: {confidence:.0%}. Tags: {', '.join(k[:4])}"
            },
            'haiku': {
                'icon': '🌸',
                'name': 'Haiku',
                'template': lambda c, k: f"{c.split('.')[0][:30]}...\n{k[0] if k else 'Silence'} breathes deep —\nA moment caught in time."
            }
        }
        
        results = {}
        for mode_key, mode_info in modes.items():
            try:
                text = mode_info['template'](base_caption, keywords)
                results[mode_key] = {
                    'text': text,
                    'description': mode_info['name'],
                    'icon': mode_info['icon'],
                    'keywords': keywords,
                    'confidence': confidence
                }
            except Exception:
                results[mode_key] = {
                    'text': f"Error formatting {mode_key}",
                    'description': mode_info['name'],
                    'icon': mode_info['icon'],
                    'keywords': [],
                    'confidence': 0.5
                }
        return results


def simple_image_analysis(image_path: str) -> Dict:
    """Extract brightness and color profile for metadata (UI only, not part of captioning)."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    brightness = arr.mean() / 255
    r_mean, g_mean, b_mean = arr.mean(axis=(0,1))
    color_temp = 'warm' if r_mean > g_mean and r_mean > b_mean else 'cool'
    return {
        'brightness': round(brightness, 2),
        'color_profile': color_temp,
        'size': f"{img.width}×{img.height}"
    }