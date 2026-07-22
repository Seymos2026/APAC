import os

import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

_vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib"))
_model = joblib.load(os.path.join(MODEL_DIR, "classifier.joblib"))


def top_keywords(abstract, n=8):
    vec = _vectorizer.transform([abstract])
    row = vec.tocoo()
    if row.nnz == 0:
        return []
    terms = np.array(_vectorizer.get_feature_names_out())[row.col]
    weights = row.data
    order = np.argsort(weights)[::-1][:n]
    return [terms[i] for i in order]


def classify_abstract(abstract):
    vec = _vectorizer.transform([abstract])
    label = _model.predict(vec)[0]
    probs = _model.predict_proba(vec)[0]
    classes = _model.classes_
    probabilities = sorted(
        [{"label": c, "probability": float(p)} for c, p in zip(classes, probs)],
        key=lambda x: x["probability"],
        reverse=True,
    )
    return {
        "label": label,
        "confidence": float(max(probs)),
        "probabilities": probabilities,
        "keywords": top_keywords(abstract),
    }
