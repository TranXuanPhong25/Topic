from __future__ import annotations

import base64
import io
from typing import Optional, Dict, Any, List

from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

HF_REPO = "Jayanth2002/dinov2-base-finetuned-SkinDisease"


class _LesionClassifierSingleton:
    _instance: Optional["LesionClassifier"] = None

    @classmethod
    def get_instance(cls) -> "LesionClassifier":
        if cls._instance is None:
            cls._instance = LesionClassifier()
        return cls._instance


class LesionClassifier:
    def __init__(self) -> None:
        self.processor = AutoImageProcessor.from_pretrained(HF_REPO)
        self.model = AutoModelForImageClassification.from_pretrained(HF_REPO).eval()
        # Prefer labels from config if available
        self.id2label = getattr(self.model.config, "id2label", None)

    def _decode_base64_image(self, image_data: str) -> Image.Image:
        # Strip data URL prefix if present
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return image

    def classify_image(self, image: Image.Image, top_k: int = 5) -> Dict[str, Any]:
        with torch.no_grad():
            enc = self.processor(image, return_tensors="pt")
            logits = self.model(**enc).logits
            probs = torch.softmax(logits, dim=-1).squeeze(0)
            topk = torch.topk(probs, k=min(top_k, probs.shape[-1]))
            indices = topk.indices.tolist()
            scores = topk.values.tolist()

        def idx_to_label(i: int) -> str:
            if self.id2label and i in self.id2label:
                return self.id2label[i]
            # Fallback to string index if labels missing
            return str(i)

        top_predictions: List[Dict[str, Any]] = [
            {"label": idx_to_label(i), "score": float(s)} for i, s in zip(indices, scores)
        ]
        print(top_predictions)
        return {
            "top_label": top_predictions[0]["label"],
            "top_score": top_predictions[0]["score"],
            "top_k": top_predictions,
            "model": HF_REPO,
        }

    def classify_base64(self, image_b64: str, top_k: int = 5) -> Dict[str, Any]:
        image = self._decode_base64_image(image_b64)
        return self.classify_image(image, top_k=top_k)


def get_lesion_classifier() -> LesionClassifier:
    return _LesionClassifierSingleton.get_instance()
