import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import DistilBertModel, DistilBertConfig, DistilBertPreTrainedModel
from typing import Optional, Tuple

MODEL_NAME     = "distilbert-base-uncased"
NUM_LABELS     = 2
DROPOUT_RATE   = 0.3
HIDDEN_DIM     = 256
LABEL_SMOOTHING = 0.1


class DistilBertFakeNewsClassifier(nn.Module):

    def __init__(
        self,
        model_name:   str = MODEL_NAME,
        num_labels:   int = NUM_LABELS,
        dropout_rate: float = DROPOUT_RATE,
        hidden_dim:   int = HIDDEN_DIM,
        freeze_layers: int = 2,
    ):
        super().__init__()
        self.num_labels = num_labels

        self.distilbert = DistilBertModel.from_pretrained(model_name)

        if freeze_layers > 0:
            self._freeze_bottom_layers(freeze_layers)

        hidden_size = self.distilbert.config.hidden_size

        self.classifier = nn.Sequential(
            nn.LayerNorm(hidden_size),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, num_labels),
        )

        self._init_weights()

    def _freeze_bottom_layers(self, n: int):

        for param in self.distilbert.embeddings.parameters():
            param.requires_grad = False

        for i, layer in enumerate(self.distilbert.transformer.layer):
            if i < n:
                for param in layer.parameters():
                    param.requires_grad = False

    def _init_weights(self):
        for module in self.classifier.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(
        self,
        input_ids:      torch.Tensor,
        attention_mask: torch.Tensor,
        labels:         Optional[torch.Tensor] = None,
    ) -> dict:

        outputs = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

        cls_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(cls_output)

        result = {"logits": logits}

        if labels is not None:
            loss_fn = LabelSmoothingCrossEntropy(
                smoothing=LABEL_SMOOTHING,
                num_classes=self.num_labels
            )
            result["loss"] = loss_fn(logits, labels)

        return result

    def get_attention_weights(self, input_ids, attention_mask):

        outputs = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_attentions=True,
        )
        return outputs.attentions

    def count_parameters(self):
        total     = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        frozen    = total - trainable
        return {"total": total, "trainable": trainable, "frozen": frozen}


class LabelSmoothingCrossEntropy(nn.Module):

    def __init__(self, smoothing: float = 0.1, num_classes: int = 2):
        super().__init__()
        self.smoothing   = smoothing
        self.num_classes = num_classes

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        log_probs = F.log_softmax(logits, dim=-1)

        with torch.no_grad():
            smooth_targets = torch.full_like(log_probs, self.smoothing / (self.num_classes - 1))
            smooth_targets.scatter_(1, targets.unsqueeze(1), 1.0 - self.smoothing)

        loss = -(smooth_targets * log_probs).sum(dim=-1).mean()
        return loss


class WeightedCrossEntropyLoss(nn.Module):

    def __init__(self, class_weights: torch.Tensor):
        super().__init__()
        self.ce = nn.CrossEntropyLoss(weight=class_weights)

    def forward(self, logits, labels):
        return self.ce(logits, labels)


def get_llrd_optimizer_groups(
    model,
    base_lr: float = 2e-5,
    lr_decay: float = 0.95,
    weight_decay: float = 0.01,
):

    no_decay = ["bias", "LayerNorm.weight"]
    groups   = []

    groups.append({
        "params": [p for n, p in model.classifier.named_parameters() if p.requires_grad],
        "lr": base_lr,
        "weight_decay": weight_decay,
    })

    num_layers = len(model.distilbert.transformer.layer)

    for layer_idx in reversed(range(num_layers)):
        layer = model.distilbert.transformer.layer[layer_idx]
        lr    = base_lr * (lr_decay ** (num_layers - layer_idx))

        groups.append({
            "params": [p for n, p in layer.named_parameters()
                       if p.requires_grad and not any(nd in n for nd in no_decay)],
            "lr": lr,
            "weight_decay": weight_decay,
        })

        groups.append({
            "params": [p for n, p in layer.named_parameters()
                       if p.requires_grad and any(nd in n for nd in no_decay)],
            "lr": lr,
            "weight_decay": 0.0,
        })

    return [g for g in groups if g["params"]]