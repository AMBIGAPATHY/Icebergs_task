import joblib
from sentence_transformers import SentenceTransformer
import numpy as np

# Load saved bundle
bundle = joblib.load("model/intent_classifier.joblib")
clf = bundle["clf"]
id2label = bundle["id2label"]
encoder_model_name = bundle["encoder_model_name"]

# Recreate the same embedder
embedder = SentenceTransformer(encoder_model_name)

def predict_intent(query: str):
    emb = embedder.encode([query], convert_to_numpy=True)  # shape (1, 384)
    probs = clf.predict_proba(emb)[0]  # softmax probs from logistic regression
    pred_id = int(np.argmax(probs))
    pred_label = id2label[pred_id]
    confidence = float(probs[pred_id])
    return {
        "query": query,
        "intent": pred_label,
        "confidence": confidence,
        "probs": probs.tolist(),
    }

# quick tests
tests = [
    "Open Google for me.",
    "hello",
    "I’d love to see a tree drawn.",
    "Draw a ship please",
    "can you create a flower drawing",
    "can you book me a train ticket",
]

for t in tests:
    out = predict_intent(t)
    print(f"\nQ: {out['query']}")
    print(f" → intent: {out['intent']}  (conf={out['confidence']:.2f})")
    print(f" probs: {out['probs']}")
