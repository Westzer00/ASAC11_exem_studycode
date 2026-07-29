import json

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


with open("documents.json", encoding="utf-8") as f:
    documents = json.load(f)

titles = [doc["title"] for doc in documents]
texts = [doc["title"] + " " + doc["content"] for doc in documents]

questions = [
    ("같은 단어", "비밀번호 재설정 방법"),
    ("같은 의미, 다른 단어", "로그인 암호를 새로 바꾸고 싶어"),
    ("오류 코드·제품명", "E101 오류 해결 방법"),
    ("유사 단어, 다른 의미", "자바 여행하기 좋은 시기"),
]


# TF-IDF
tfidf = TfidfVectorizer()
tfidf_docs = tfidf.fit_transform(texts)

# BM25
bm25 = BM25Okapi([text.split() for text in texts])

# Embedding
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
document_vectors = model.encode(texts, normalize_embeddings=True)


def top1(scores):
    index = int(np.argmax(scores))
    return titles[index]


results = []

for question_type, query in questions:
    tfidf_scores = cosine_similarity(
        tfidf.transform([query]),
        tfidf_docs,
    )[0]

    bm25_scores = bm25.get_scores(query.split())

    query_vector = model.encode(query, normalize_embeddings=True)
    embedding_scores = document_vectors @ query_vector

    results.append({
        "질문 유형": question_type,
        "질문": query,
        "TF-IDF": top1(tfidf_scores),
        "BM25": top1(bm25_scores),
        "Embedding": top1(embedding_scores),
    })


df = pd.DataFrame(results)

print(df.to_string(index=False))
df.to_csv("results.csv", index=False, encoding="utf-8-sig")

print("\nresults.csv 저장 완료")