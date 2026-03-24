import os
import json
import time
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from copy import deepcopy

import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.swa_utils import AveragedModel, SWALR
from transformers import (
    DistilBertTokenizerFast,
    get_cosine_schedule_with_warmup,
)
from sklearn.metrics import f1_score, accuracy_score, classification_report

warnings.filterwarnings("ignore")

# ImportING local modules using importlib to handle files with numbers in their names
import os
import sys
import importlib.util

def load_local_module(module_name, file_name):
    # Support both script execution and Jupyter interactive environments
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    file_path = os.path.join(base_dir, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find {file_path}. Ensure it exists in the same directory.")

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

model_arch = load_local_module("model_arch", "3_model.py")
# TryING the most likely preprocessing files based on browser downloads
try:
    preprocessing = load_local_module("preprocessing", "2_preprocessing (1).py")
except FileNotFoundError:
    try:
        preprocessing = load_local_module("preprocessing", "2_preprocessing.py")
    except FileNotFoundError:
        preprocessing = load_local_module("preprocessing", "preprocessing.py")

# ExtractING variables from THE model_arch
DistilBertFakeNewsClassifier = model_arch.DistilBertFakeNewsClassifier
get_llrd_optimizer_groups = model_arch.get_llrd_optimizer_groups
DROPOUT_RATE = model_arch.DROPOUT_RATE
HIDDEN_DIM = model_arch.HIDDEN_DIM
LABEL_SMOOTHING = model_arch.LABEL_SMOOTHING

# ExtractING variables from preprocessing
load_dataset = preprocessing.load_dataset
preprocess = preprocessing.preprocess
split_data = preprocessing.split_data
build_dataloaders = preprocessing.build_dataloaders
get_class_weights = preprocessing.get_class_weights
DATA_DIR = preprocessing.DATA_DIR
PROC_DIR = preprocessing.PROC_DIR
BATCH_SIZE = preprocessing.BATCH_SIZE
MAX_LEN = preprocessing.MAX_LEN

EPOCHS          = 10
LEARNING_RATE   = 2e-5
WEIGHT_DECAY    = 0.01
WARMUP_RATIO    = 0.06       # 6% of total steps for warmup
GRAD_CLIP       = 1.0
PATIENCE        = 3          # Early stopping patience (on val F1)
MIN_DELTA       = 0.001      # Minimum improvement to count
SWA_START_EPOCH = 7          # Start SWA from this epoch
SWA_LR          = 1e-5
FREEZE_LAYERS   = 2
MODEL_NAME      = "distilbert-base-uncased"
CHECKPOINT_DIR  = Path("checkpoints")
CHECKPOINT_DIR.mkdir(exist_ok=True)
LOGS_DIR        = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
RANDOM_SEED     = 42

torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# EARLY STOPPING

class EarlyStopping:
    def __init__(self, patience: int = 3, min_delta: float = 0.001, mode: str = "max"):
        self.patience   = patience
        self.min_delta  = min_delta
        self.mode       = mode
        self.best_score = None
        self.counter    = 0
        self.stopped    = False

    def step(self, score: float) -> bool:
        """Returns True if training should stop."""
        if self.best_score is None:
            self.best_score = score
            return False

        improved = (score > self.best_score + self.min_delta) if self.mode == "max" \
                   else (score < self.best_score - self.min_delta)

        if improved:
            self.best_score = score
            self.counter    = 0
        else:
            self.counter += 1
            print(f"    [EarlyStopping] No improvement for {self.counter}/{self.patience} epochs")
            if self.counter >= self.patience:
                self.stopped = True
                return True
        return False



# METRICS

def compute_metrics(preds: list, labels: list) -> dict:
    return {
        "accuracy" : accuracy_score(labels, preds),
        "f1"       : f1_score(labels, preds, average="macro"),
        "f1_fake"  : f1_score(labels, preds, pos_label=0, average="binary"),
        "f1_real"  : f1_score(labels, preds, pos_label=1, average="binary"),
    }

# TRAINING ONE EPOCH

def train_epoch(
    model, loader, optimizer, scheduler, scaler, device, epoch
) -> dict:
    model.train()
    total_loss = 0.0
    all_preds, all_labels = [], []

    for step, batch in enumerate(loader):
        input_ids      = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels         = batch["labels"].to(device)

        optimizer.zero_grad()

        # Mixed precision forward
        with autocast(enabled=(device.type == "cuda")):
            out  = model(input_ids, attention_mask, labels)
            loss = out["loss"]

        # Backward + gradient clipping
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()

        total_loss += loss.item()
        preds = out["logits"].argmax(dim=-1).cpu().tolist()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().tolist())

        if (step + 1) % 50 == 0:
            lr = scheduler.get_last_lr()[0]
            print(f"    Step {step+1}/{len(loader)} | Loss: {loss.item():.4f} | LR: {lr:.2e}")

    metrics = compute_metrics(all_preds, all_labels)
    metrics["loss"] = total_loss / len(loader)
    return metrics

# EVALUATING
@torch.no_grad()
def evaluate(model, loader, device) -> dict:
    model.eval()
    total_loss = 0.0
    all_preds, all_labels = [], []

    for batch in loader:
        input_ids      = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels         = batch["labels"].to(device)

        with autocast(enabled=(device.type == "cuda")):
            out = model(input_ids, attention_mask, labels)

        total_loss += out["loss"].item()
        preds = out["logits"].argmax(dim=-1).cpu().tolist()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().tolist())

    metrics = compute_metrics(all_preds, all_labels)
    metrics["loss"] = total_loss / len(loader)
    return metrics, all_preds, all_labels

# TRAINING LOOP
def train(
    model, train_loader, val_loader, device,
    epochs=EPOCHS, use_swa=True
):
    # ── Optimizer (LLRD) ──
    param_groups = get_llrd_optimizer_groups(model, base_lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    optimizer    = AdamW(param_groups, eps=1e-8)

    # ── Scheduler: warmup + cosine decay ──
    total_steps  = len(train_loader) * epochs
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler    = get_cosine_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    print(f"\n[*] Scheduler: cosine warmup ({warmup_steps} steps) → decay ({total_steps} total)")

    # ── Mixed precision ──
    scaler = GradScaler(enabled=(device.type == "cuda"))

    # ── SWA model ──
    swa_model    = AveragedModel(model) if use_swa else None
    swa_scheduler = SWALR(optimizer, swa_lr=SWA_LR) if use_swa else None

    # ── Early stopping ──
    early_stop   = EarlyStopping(patience=PATIENCE, min_delta=MIN_DELTA, mode="max")
    best_val_f1  = 0.0
    best_model_state = None

    history = {"train_loss": [], "val_loss": [], "train_f1": [], "val_f1": [],
               "train_acc": [], "val_acc": []}

    print(f"\n{'='*60}")
    print(f"  TRAINING — {epochs} epochs | Device: {device}")
    print(f"{'='*60}\n")

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        print(f"\n── Epoch {epoch}/{epochs} ──")

        # ── SWA phase ──
        if use_swa and epoch >= SWA_START_EPOCH:
            print("    [SWA mode active]")
            swa_scheduler.step()
        else:
            # ── Train ──
            train_metrics = train_epoch(model, train_loader, optimizer, scheduler, scaler, device, epoch)

        # ── Validate ──
        val_metrics, val_preds, val_labels = evaluate(model, val_loader, device)

        # ── SWA update ──
        if use_swa and epoch >= SWA_START_EPOCH:
            swa_model.update_parameters(model)

        # ── Log ──
        elapsed = time.time() - t0
        print(f"\n  Train → Loss: {train_metrics['loss']:.4f} | F1: {train_metrics['f1']:.4f} | Acc: {train_metrics['accuracy']:.4f}")
        print(f"  Val   → Loss: {val_metrics['loss']:.4f}   | F1: {val_metrics['f1']:.4f} | Acc: {val_metrics['accuracy']:.4f}")
        print(f"  Epoch time: {elapsed:.1f}s")

        history["train_loss"].append(train_metrics["loss"])
        history["val_loss"].append(val_metrics["loss"])
        history["train_f1"].append(train_metrics["f1"])
        history["val_f1"].append(val_metrics["f1"])
        history["train_acc"].append(train_metrics["accuracy"])
        history["val_acc"].append(val_metrics["accuracy"])

        # ── Save best model ──
        if val_metrics["f1"] > best_val_f1:
            best_val_f1 = val_metrics["f1"]
            best_model_state = deepcopy(model.state_dict())
            torch.save(best_model_state, CHECKPOINT_DIR / "best_model.pt")
            print(f"  ✓ New best model saved (val F1 = {best_val_f1:.4f})")

        # ── Overfitting guard ──
        gap = train_metrics["f1"] - val_metrics["f1"]
        if gap > 0.10:
            print(f"   Overfitting warning: train/val F1 gap = {gap:.4f}")

        # ── Early stopping ──
        if early_stop.step(val_metrics["f1"]):
            print(f"\n  [!] Early stopping triggered at epoch {epoch}")
            break

    # ── SWA batch norm update ──
    if use_swa and swa_model is not None:
        print("\n[*] Updating SWA batch norm statistics...")
        torch.optim.swa_utils.update_bn(train_loader, swa_model, device=device)
        torch.save(swa_model.state_dict(), CHECKPOINT_DIR / "swa_model.pt")
        print("    ✓ SWA model saved")

    # ── Save history ──
    with open(LOGS_DIR / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"\n[✓] Training complete | Best val F1: {best_val_f1:.4f}")
    return history, best_model_state

# PLOTTING TRAINING CURVES
def plot_training_curves(history: dict):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Training Curves — DistilBERT Fake News Classifier", fontweight="bold")

    epochs = range(1, len(history["train_loss"]) + 1)

    # Loss
    axes[0].plot(epochs, history["train_loss"], "b-o", label="Train Loss", markersize=4)
    axes[0].plot(epochs, history["val_loss"],   "r-o", label="Val Loss",   markersize=4)
    axes[0].set_title("Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # F1
    axes[1].plot(epochs, history["train_f1"], "b-o", label="Train F1", markersize=4)
    axes[1].plot(epochs, history["val_f1"],   "r-o", label="Val F1",   markersize=4)
    axes[1].set_title("Macro F1 Score")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("F1")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(LOGS_DIR / "training_curves.png", dpi=150)
    plt.show()
    print(f"[✓] Training curves saved to {LOGS_DIR}/training_curves.png")

# MAIN
if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Device: {device}")

    # ── LoadING THE data ──
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

    if (PROC_DIR / "train.csv").exists():
        train_df = pd.read_csv(PROC_DIR / "train.csv")
        val_df   = pd.read_csv(PROC_DIR / "val.csv")
        test_df  = pd.read_csv(PROC_DIR / "test.csv")
    else:

        print("[!] Preprocessed CSVs not found. Attempting to load ISOT dataset instead.")
        df = load_dataset("isot")
        df = preprocess(df)
        train_df, val_df, test_df = split_data(df)

    train_loader, val_loader, test_loader = build_dataloaders(
        train_df, val_df, test_df, tokenizer, batch_size=BATCH_SIZE
    )

    # ── BuildING model ──
    model = DistilBertFakeNewsClassifier(
        model_name    = MODEL_NAME,
        dropout_rate  = DROPOUT_RATE,
        hidden_dim    = HIDDEN_DIM,
        freeze_layers = FREEZE_LAYERS,
    ).to(device)

    # ── TrainING ──
    history, best_state = train(model, train_loader, val_loader, device, epochs=EPOCHS)

    # ── PlotTING ──
    plot_training_curves(history)

    # ── FinalLY testING evaluation ──
    print("\n[*] Loading best model for final test evaluation...")
    model.load_state_dict(torch.load(CHECKPOINT_DIR / "best_model.pt", map_location=device))
    test_metrics, test_preds, test_labels = evaluate(model, test_loader, device)

    print(f"\n{'='*55}")
    print(f"  FINAL TEST RESULTS")
    print(f"{'='*55}")
    for k, v in test_metrics.items():
        if k != "loss":
            print(f"  {k:15s}: {v:.4f}")
    print(f"\n{classification_report(test_labels, test_preds, target_names=['FAKE','REAL'])}")
    print("\n[✓] Script 4 complete. Proceed to 5_evaluate.py")