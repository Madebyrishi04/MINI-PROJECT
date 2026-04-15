import re
import os
import pickle
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple

import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from transformers import DistilBertTokenizerFast
from collections import Counter

warnings.filterwarnings("ignore")

# CONFIG

DATA_DIR      = Path("data")
PROC_DIR      = Path("processed")
PROC_DIR.mkdir(exist_ok=True)

MODEL_NAME    = "distilbert-base-uncased"
MAX_LEN       = 256
BATCH_SIZE    = 32
TEST_SIZE     = 0.15
VAL_SIZE      = 0.15
RANDOM_SEED   = 42
USE_TITLE_ONLY = False

torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# TEXT CLEANING

def clean_text(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return ""
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\(Reuters\)\s*-?\s*", "", text)
    text = re.sub(r"([!?.,'\"]{2,})", lambda m: m.group(0)[0], text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()

def build_input_text(row: pd.Series, use_title_only: bool = False) -> str:
    title = clean_text(str(row.get("title", "") or ""))
    body  = clean_text(str(row.get("text",  "") or ""))

    if use_title_only or not body:
        return title if title else body
    if not title:
        return body[:512]

    return f"{title} [SEP] {body[:800]}"

# LOADING THE DATASET (ONLY FOR WELFAKE)

def load_dataset() -> pd.DataFrame:
    path = DATA_DIR / "WELFake" / "WELFake_Dataset.csv"
    if not path.exists():
        raise FileNotFoundError("WELFake_Dataset.csv not found.")
    return pd.read_csv(path)

# PREPROCESSING

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    print(f"[*] Raw dataset size: {len(df)}")

    df = df.dropna(subset=["label"]).copy()

    df["input_text"] = df.apply(lambda r: build_input_text(r), axis=1)

    df = df[df["input_text"].str.strip() != ""].copy()

    df["label"] = df["label"].astype(int)

    before = len(df)
    df = df.drop_duplicates(subset=["input_text"]).reset_index(drop=True)
    print(f"[*] Dropped {before - len(df)} duplicates")

    df = df[df["input_text"].str.len() >= 5].reset_index(drop=True)

    print(f"[*] Clean dataset size : {len(df)}")
    print(f"[*] Label distribution :\n{df['label'].value_counts()}")

    return df[["input_text", "label"]]

# SPLIT

def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_val, test = train_test_split(
        df, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=df["label"]
    )

    rel_val = VAL_SIZE / (1 - TEST_SIZE)

    train, val = train_test_split(
        train_val, test_size=rel_val, random_state=RANDOM_SEED, stratify=train_val["label"]
    )

    print(f"\n[*] Split sizes → Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)

# DATASET CLASS

class FakeNewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=MAX_LEN):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]),
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }

# SAMPLER
def build_weighted_sampler(labels):
    class_counts = Counter(labels)
    weights = [1.0 / class_counts[lbl] for lbl in labels]
    return WeightedRandomSampler(weights=weights, num_samples=len(labels), replacement=True)

# DATALOADERS

def build_dataloaders(train_df, val_df, test_df, tokenizer):
    train_ds = FakeNewsDataset(train_df["input_text"].tolist(), train_df["label"].tolist(), tokenizer)
    val_ds   = FakeNewsDataset(val_df["input_text"].tolist(), val_df["label"].tolist(), tokenizer)
    test_ds  = FakeNewsDataset(test_df["input_text"].tolist(), test_df["label"].tolist(), tokenizer)

    sampler = build_weighted_sampler(train_df["label"].tolist())

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler)
    val_loader   = DataLoader(val_ds, batch_size=BATCH_SIZE)
    test_loader  = DataLoader(test_ds, batch_size=BATCH_SIZE)

    return train_loader, val_loader, test_loader

# CLASS WEIGHTS
def get_class_weights(labels):
    classes = np.unique(labels)
    weights = compute_class_weight("balanced", classes=classes, y=labels)
    return torch.tensor(weights, dtype=torch.float)

# SAVE

def save_splits(train_df, val_df, test_df):
    train_df.to_csv(PROC_DIR / "train.csv", index=False)
    val_df.to_csv(PROC_DIR / "val.csv", index=False)
    test_df.to_csv(PROC_DIR / "test.csv", index=False)

# MAIN
if __name__ == "__main__":
    df = load_dataset()

    df = preprocess(df)

    train_df, val_df, test_df = split_data(df)

    save_splits(train_df, val_df, test_df)

    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

    train_loader, val_loader, test_loader = build_dataloaders(
        train_df, val_df, test_df, tokenizer
    )

    class_weights = get_class_weights(train_df["label"].tolist())

    tokenizer.save_pretrained("tokenizer_saved")

    print("\n[✓] Preprocessing complete (WELFake only)")