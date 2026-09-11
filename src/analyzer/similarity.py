from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calc_similarity(text_a: str, text_b: str) -> float:
    if not text_a or not text_b:
        return 0.0
    try:
        vec = TfidfVectorizer().fit_transform([text_a, text_b])
        score = cosine_similarity(vec[0], vec[1])[0][0]
        return round(score * 100, 1)
    except Exception:
        return 0.0
