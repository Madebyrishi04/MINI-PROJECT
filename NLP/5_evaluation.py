import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

import torch
import torch.nn.functional as F
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score,
    brier_score_loss,
)
from sklearn.calibration import calibration_curve
from transformers import DistilBertTokenizerFast

warnings.filterwarnings("ignore")

CHECKPOINT_DIR = Path("/content/drive/MyDrive/FakeNews_Model/checkpoints")
LOGS_DIR       = Path("logs")
FIGURES_DIR    = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)
MODEL_NAME     = "distilbert-base-uncased"

# GETTING PREDICTIONS

@torch.no_grad()
def get_predictions(model, loader, device):
    model.eval()
    all_labels, all_preds, all_probs = [], [], []

    for batch in loader:
        input_ids      = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels         = batch["labels"].to(device)

        out    = model(input_ids, attention_mask)
        probs  = F.softmax(out["logits"], dim=-1)
        preds  = out["logits"].argmax(dim=-1)

        all_labels.extend(labels.cpu().numpy())
        all_preds.extend(preds.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

    return np.array(all_labels), np.array(all_preds), np.array(all_probs)

# CONFUSION MATRIX
def plot_confusion_matrix(labels, preds):
    cm = confusion_matrix(labels, preds)

    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["FAKE","REAL"],
                yticklabels=["FAKE","REAL"])
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.savefig(FIGURES_DIR / "confusion_matrix.png")
    plt.show()

# ROC CURVE
def plot_roc(labels, probs):
    fpr, tpr, _ = roc_curve(labels, probs[:,1])
    auc = roc_auc_score(labels, probs[:,1])

    plt.plot(fpr, tpr, label=f"AUC={auc:.4f}")
    plt.plot([0,1],[0,1],'--')
    plt.legend()
    plt.title("ROC Curve")
    plt.savefig(FIGURES_DIR / "roc.png")
    plt.show()

# MAIN
if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # IMPORTING LOCAL FILES
   # from model_arch import DistilBertFakeNewsClassifier
    #from preprocessing import FakeNewsDataset, MAX_LEN, BATCH_SIZE

    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

    # LOADING TEST DATA (ONLY WELFAKE CSV)
    test_df = pd.read_csv("processed/test.csv")

    from torch.utils.data import DataLoader
    test_ds = FakeNewsDataset(
        test_df["input_text"].tolist(),
        test_df["label"].tolist(),
        tokenizer,
        MAX_LEN
    )

    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

    # LOADING MODEL
    model = DistilBertFakeNewsClassifier().to(device)
    model.load_state_dict(torch.load("checkpoints/best_model.pt", map_location=device))

    # PREDICTIONS
    labels, preds, probs = get_predictions(model, test_loader, device)

    # RESULTS
    print("\nCLASSIFICATION REPORT")
    print(classification_report(labels, preds))

    plot_confusion_matrix(labels, preds)
    plot_roc(labels, probs)

    print("\n[✓] Evaluation Complete")