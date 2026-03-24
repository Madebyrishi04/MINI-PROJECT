import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path
from typing import Union, List, Dict

import torch
import torch.nn.functional as F
from transformers import DistilBertTokenizerFast

warnings.filterwarnings("ignore")

CHECKPOINT_DIR = Path("/content/drive/MyDrive/FakeNews_Model/checkpoints")
MODEL_NAME     = "distilbert-base-uncased"
MAX_LEN        = 256
CONFIDENCE_THRESHOLD = 0.70

LABEL_MAP = {0: "REAL", 1: "FAKE"}
COLOR_MAP  = {"FAKE": "#e74c3c", "REAL": "#2ecc71", "UNCERTAIN": "#f39c12"}


class FakeNewsPredictor:

    def __init__(
        self,
        checkpoint_path: str = None,
        model_name: str = MODEL_NAME,
        max_len: int = MAX_LEN,
        device: str = None,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
    ):
        self.model_name  = model_name
        self.max_len     = max_len
        self.threshold   = confidence_threshold

        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[*] Using device: {self.device}")

        self.tokenizer = DistilBertTokenizerFast.from_pretrained(model_name)

        import sys; sys.path.insert(0, ".")
        from model_arch import DistilBertFakeNewsClassifier

        self.model = DistilBertFakeNewsClassifier(model_name=model_name).to(self.device)

        if checkpoint_path is None:
            checkpoint_path = str(CHECKPOINT_DIR / "best_model.pt")

        self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        self.model.eval()

    def _tokenize(self, text: str):
        return self.tokenizer(
            str(text),
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

    @torch.no_grad()
    def predict(self, text: str):
        enc = self._tokenize(text)

        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)

        out = self.model(input_ids, attention_mask)
        probs = F.softmax(out["logits"], dim=-1).squeeze()

        real_prob = probs[0].item()
        fake_prob = probs[1].item()

        confidence = max(fake_prob, real_prob)
        label = LABEL_MAP[int(probs.argmax())]

        verdict = label if confidence >= self.threshold else "UNCERTAIN"

        return {
            "label": label,
            "verdict": verdict,
            "confidence": round(confidence, 4),
            "fake_prob": round(fake_prob, 4),
            "real_prob": round(real_prob, 4),
        }


# MAIN
if __name__ == "__main__":
    predictor = FakeNewsPredictor()

    text = "BREAKING: Hillary Clinton completely destroyed 30,000 classified emails to hide her crimes"
    result = predictor.predict(text)

    print("\nPrediction:")
    print(result)