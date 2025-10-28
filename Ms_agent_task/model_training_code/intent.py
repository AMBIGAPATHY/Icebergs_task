import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib  # pip install joblib if you don't have it
from sentence_transformers import SentenceTransformer
import numpy as np

# -------------------------------------------------
# 1. Load and prep dataset
# -------------------------------------------------

df = pd.read_csv("data/training_dataset/intent.csv", encoding="cp1252")
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df = df.rename(columns={"Text": "text", "Category": "category"})

# Label encoding
label2id = {label: idx for idx, label in enumerate(sorted(df["category"].unique()))}
id2label = {v: k for k, v in label2id.items()}

df["label_id"] = df["category"].map(label2id)

print("Label map:", label2id)
print(df.head())

# Train/val split
train_df, val_df = train_test_split(
    df,
    test_size=0.2,
    stratify=df["label_id"],
    random_state=42
)

X_train_text = train_df["text"].tolist()
y_train = train_df["label_id"].tolist()

X_val_text = val_df["text"].tolist()
y_val = val_df["label_id"].tolist()

# -------------------------------------------------
# 2. Load sentence-transformer and create embeddings
# -------------------------------------------------

# This downloads a pretrained encoder from HF the first time.
# This part still works fine in 5.1.2.
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# turn sentences -> dense vectors
X_train_emb = embedder.encode(X_train_text, convert_to_numpy=True, show_progress_bar=True)
X_val_emb   = embedder.encode(X_val_text,   convert_to_numpy=True, show_progress_bar=True)

print("Embedding shape:", X_train_emb.shape)  # (num_samples, 384)

# -------------------------------------------------
# 3. Train a classifier on top of embeddings
# -------------------------------------------------

# We'll use multinomial logistic regression (softmax)
clf = LogisticRegression(
    max_iter=1000,
    multi_class="multinomial",
    solver="lbfgs",
)

clf.fit(X_train_emb, y_train)

# -------------------------------------------------
# 4. Evaluate
# -------------------------------------------------

y_val_pred = clf.predict(X_val_emb)
acc = accuracy_score(y_val, y_val_pred)
print(f"\nValidation accuracy: {acc:.4f}\n")

print("Detailed report:")
print(classification_report(
    y_val,
    y_val_pred,
    target_names=[id2label[i] for i in sorted(id2label.keys())]
))

# -------------------------------------------------
# 5. Save the model pieces for later inference
# -------------------------------------------------
# We'll save:
# - the sklearn classifier
# - the label maps
# - and we assume you'll load the same sentence-transformer model name at inference.

joblib.dump(
    {
        "clf": clf,
        "label2id": label2id,
        "id2label": id2label,
        "encoder_model_name": "sentence-transformers/all-MiniLM-L6-v2",
    },
    "intent_classifier.joblib"
)

print("\n✔ Saved classifier to intent_classifier.joblib")
print("✔ Remember: you still need the same SentenceTransformer at inference time.")
