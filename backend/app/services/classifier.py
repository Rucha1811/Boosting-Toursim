"""
Community issue classification.

Trained-on-the-fly sklearn pipeline (TF-IDF + linear classifier) over the
platform's own labeled seed reports. A keyword rule fallback guarantees a
sensible classification even before training data is available, so the feature
never fails at demo time. The model is trivially replaceable.
"""

import logging
import re
from typing import List, Tuple

logger = logging.getLogger("virsa.classifier")

CATEGORIES = ["traffic", "parking", "waste", "infrastructure", "safety", "overcrowding", "other"]

RULE_MAP = [
    (["accident", "jam", "signal", "traffic", "vehicle", "congestion", "road", "two-wheeler", "lorry", "truck", "bus"], "traffic"),
    (["parking", "park", "no-parking", "no parking", "tow"], "parking"),
    (["garbage", "waste", "litter", "rubbish", "dump", "bin full", "overflowing", "trash", "dirty", "hygiene"], "waste"),
    (["road work", "pothole", "drain", "manhole", "broken", "lighting", "street light", "footpath", "tile", "leak", "clogged", "water"], "infrastructure"),
    (["safety", "threat", "harass", "unsafe", "dark", "scary", "suspicious", "minor"], "safety"),
    (["crowd", "overcrowd", "rush", "too many people", "jam packed", "mela", "festival crowd", "queue"], "overcrowding"),
]

def _rule_classify(text: str) -> Tuple[str, float]:
    t = text.lower()
    best, conf = "other", 0.0
    for words, cat in RULE_MAP:
        if any(w in t for w in words):
            conf = max(conf, 0.82)
            best = cat
    return best, conf


_loaded = False
_sklearn = None
_clf = None
_vec = None
_labels = None


def _load_sklearn():
    global _loaded, _sklearn, _clf, _vec, _labels
    if _loaded:
        return True
    _loaded = True
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import SGDClassifier
        from sklearn.pipeline import Pipeline

        _sklearn = "ok"
    except Exception as exc:  # pragma: no cover
        logger.warning("sklearn unavailable (%s); using rule classifier", exc)
        return False
    return True


def train(samples: List[Tuple[str, str]]):
    """samples: (text, category) pairs collected from labeled platform reports."""
    if not _load_sklearn() or not samples:
        return
    global _clf, _vec
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import SGDClassifier
        from sklearn.pipeline import Pipeline

        texts = [t for t, _ in samples]
        y = [c for _, c in samples]
        _vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", lowercase=True)
        _clf = SGDClassifier(loss="modified_huber", max_iter=200, random_state=42)
        X = _vec.fit_transform(texts)
        _clf.fit(X, y)
        logger.info("report classifier trained on %d labeled reports", len(samples))
    except Exception as exc:
        logger.warning("failed to fit classifier: %s", exc)
        _clf = None


def classify(text: str) -> Tuple[str, float]:
    rule_cat, rule_conf = _rule_classify(text)
    if _clf is not None and _vec is not None:
        try:
            X = _vec.transform([text])
            cat = _clf.predict(X)[0]
            conf = float(max(_clf.predict_proba(X)[0]))
            # Merge signals: prefer model label when confident, otherwise rule.
            if conf >= 0.5:
                return str(cat), round(conf, 3)
        except Exception:
            pass
    return rule_cat, rule_conf