import json
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# JSON 파일 읽기
with open("documents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

menus = list(data.keys())
documents = list(data.values())

# 문장을 띄어쓰기 기준으로 나누기 => 단어의 벡터화를 진행 !! 
print("1. 문서별 단어 리스트")

for menu, document in data.items():
    print(menu, ":", document.split())

# DTM 만들기 
count_vectorizer = CountVectorizer(analyzer=str.split)
dtm = count_vectorizer.fit_transform(documents)

dtm_table = pd.DataFrame(
    dtm.toarray(),
    index=menus,
    columns=count_vectorizer.get_feature_names_out()
)

print("\n2. DTM")
print(dtm_table)

# TF-IDF 만들기
tfidf_vectorizer = TfidfVectorizer(analyzer=str.split)
tfidf = tfidf_vectorizer.fit_transform(documents)

tfidf_table = pd.DataFrame(
    tfidf.toarray(),
    index=menus,
    columns=tfidf_vectorizer.get_feature_names_out()
)

print("\n3. TF-IDF")
print(tfidf_table.round(3))

# 검색어 입력
query = input("\n먹고 싶은 메뉴를 입력하세요: ")
query_words = query.split()

print("\n4. 입력 단어 중요도")

for word in query_words:

    if word in tfidf_vectorizer.vocabulary_:
        word_index = tfidf_vectorizer.vocabulary_[word]
        idf = tfidf_vectorizer.idf_[word_index]

        print(f"{word}의 IDF: {idf:.3f}")

    else:
        print(f"{word}: 문서에 없는 단어")

# 입력 문장과 각 메뉴의 유사도 계산
query_vector = tfidf_vectorizer.transform([query])
scores = cosine_similarity(query_vector, tfidf)[0]

result = pd.DataFrame({
    "메뉴": menus,
    "유사도": scores
}).sort_values("유사도", ascending=False)

print("\n5. 검색 결과")
print(result.head(3).to_string(index=False))