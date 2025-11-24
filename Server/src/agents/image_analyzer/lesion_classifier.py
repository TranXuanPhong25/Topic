from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Optional, Dict, Any, List

from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

MODEL_ID = "suinleelab/monet"
BASE_DIR = Path(__file__).resolve().parent
CANDIDATES_FILE = BASE_DIR / "candidates.txt"


class _LesionClassifierSingleton:
    _instance: Optional["LesionClassifier"] = None

    @classmethod
    def get_instance(cls) -> "LesionClassifier":
        if cls._instance is None:
            cls._instance = LesionClassifier()
        return cls._instance

class LesionClassifier:
    def __init__(self) -> None:
        self.processor = CLIPProcessor.from_pretrained(MODEL_ID)
        self.model = CLIPModel.from_pretrained(MODEL_ID).eval()

        self.candidate_texts: List[str] = self._load_candidates_from_txt()

    def _load_candidates_from_txt(self) -> List[str]:
        path = Path(CANDIDATES_FILE)
        if not path.is_file():
            print(f"[LesionClassifier] Candidates file not found: {path}")
            return []

        lines: List[str] = []
        with path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue  # cho phép comment
                lines.append(line)
        print(f"[LesionClassifier] Loaded {len(lines)} candidate diagnoses from {path}")
        return lines

    def _decode_base64_image(self, image_data: str) -> Image.Image:
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return image

    def classify_image(self, image: Image.Image, top_k: int = 5) -> Dict[str, Any]:
        inputs = self.processor(
            
            text=self.candidate_texts,
            images=image,
            return_tensors="pt",
            padding=True,
        )
        with torch.no_grad():
            out = self.model(**inputs)
            sims = out.logits_per_image[0]          # [num_labels]
            probs = torch.softmax(sims, dim=-1)
            topk = torch.topk(probs, k=min(top_k, probs.shape[-1]))
            indices = topk.indices.tolist()
            scores = topk.values.tolist()

        def extract_label(text: str) -> str:
            # Lấy phần trước dấu ":" làm tên bệnh để hiển thị
            if ":" in text:
                return text.split(":", 1)[0].strip()
            return text.strip()

        top_predictions: List[Dict[str, Any]] = []
        for i, s in zip(indices, scores):
            full_text = self.candidate_texts[i]
            label = extract_label(full_text)
            top_predictions.append(
                {
                    "label": label,         # tên bệnh (có thể gồm cả tên Việt)
                    "full_text": full_text, # cả câu mô tả dùng cho CLIP
                    "score": float(s),
                    "index": i,
                }
            )

        print(f"[LesionClassifier] Top prediction: {top_predictions[0]['label']} (score: {top_predictions[0]['score']:.4f})")
        return {
            "top_label": top_predictions[0]["label"],
            "top_score": top_predictions[0]["score"],
            "top_k": top_predictions,
            "model": MODEL_ID,
        }

    def classify_base64(self, image_b64: str, top_k: int = 5) -> Dict[str, Any]:
        image = self._decode_base64_image(image_b64)
        return self.classify_image(image, top_k=top_k)


def get_lesion_classifier() -> LesionClassifier:
    return _LesionClassifierSingleton.get_instance()
