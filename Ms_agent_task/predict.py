# predict.py
import os
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# --------------------------
# Paths / model load
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# your model lives in model/intent_classifier.joblib
MODEL_PATH = os.path.join(BASE_DIR, "model", "intent_classifier.joblib")

# load the saved bundle
_bundle = joblib.load(MODEL_PATH)

# expected keys from your training script:
#   "clf", "id2label", "encoder_model_name"
_clf = _bundle.get("clf", None)
_id2label = _bundle.get("id2label", {})
_encoder_model_name = _bundle.get(
    "encoder_model_name",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# recreate the same sentence transformer encoder
_embedder = SentenceTransformer(_encoder_model_name)

# --------------------------
# Known drawable shapes + aliases
# --------------------------
KNOWN_SHAPES = {
    "tree",
    "house",
    "windmill",
    "train",
    "star",
    "flower",
}

# sometimes classifier may output variations / synonyms.
ALIAS_MAP = {
    "home": "house",
    "building": "house",
    "wind mill": "windmill",
    "wind-mill": "windmill",
    "locomotive": "train",
    "train engine": "train",
    "flowers": "flower",
    "flower plant": "flower",
    "five pointed star": "star",
    "5-pointed star": "star",
    "star shape": "star",
}


def _predict_intent_label(text: str) -> str:
    """
    Use the sentence-transformer encoder + sklearn classifier
    to return the raw string label predicted by the model.
    This matches your uploaded inference script. :contentReference[oaicite:4]{index=4}
    """
    if _clf is None:
        # model not loaded, safest fallback
        return "unknown"

    # 1) embed the query (shape -> (1, 384) by default for MiniLM)
    emb = _embedder.encode([text], convert_to_numpy=True)

    # 2) classifier forward
    # clf.predict_proba(...) -> softmax probs over classes
    probs = _clf.predict_proba(emb)[0]
    pred_id = int(np.argmax(probs))
    raw_label = _id2label.get(pred_id, "unknown")

    return str(raw_label)


def _normalize_label(raw_label: str) -> str:
    """
    Take raw model label (like 'Flower', 'train', 'Wind Mill Intent')
    and normalize into our draw keys.
    """
    if raw_label is None:
        return "unknown"

    lbl = raw_label.strip().lower()

    # direct match first
    if lbl in KNOWN_SHAPES:
        return lbl

    # alias map second
    if lbl in ALIAS_MAP:
        mapped = ALIAS_MAP[lbl]
        if mapped in KNOWN_SHAPES:
            return mapped

    # substring fallback: if model returns 'draw_flower' or 'flower_intent'
    for shape in KNOWN_SHAPES:
        if shape in lbl:
            return shape

    return "unknown"


def classify_text(user_text: str) -> str:
    """
    Public function used by app.py.
    1. Predict raw intent label (like "flower" / "draw_flower" / "greeting")
    2. Normalize to our drawable set.
    3. Return final label or "unknown".
    """
    raw_label = _predict_intent_label(user_text)
    final_label = _normalize_label(raw_label)
    return final_label


# Optional helper if you ever want debug info in console
def debug_predict(user_text: str):
    raw_label = _predict_intent_label(user_text)
    mapped = _normalize_label(raw_label)
    return {
        "input": user_text,
        "raw_label": raw_label,
        "mapped_label": mapped,
    }


if __name__ == "__main__":
    # quick manual test when running `python predict.py`
    tests = [
        "draw a flower",
        "can you make a house",
        "please show me a windmill",
        "draw me a dragon",
        "i want a train drawing",
        "can you draw a star for me",
        "hello",
    ]
    for t in tests:
        info = debug_predict(t)
        print(info)
