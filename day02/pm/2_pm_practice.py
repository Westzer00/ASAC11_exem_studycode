import numpy as np
import matplotlib.pyplot as plt


# 영어 문장과 한국어 문장을 Token으로 나누기
english_tokens = ["I", "love", "machine", "learning"]
korean_tokens = ["나는", "머신러닝을", "좋아한다"]


# 행: 한국어 Token
# 열: 영어 Token
attention_weights = np.array([
    [0.90, 0.05, 0.03, 0.02],  # 나는
    [0.02, 0.03, 0.45, 0.50],  # 머신러닝을
    [0.03, 0.90, 0.04, 0.03],  # 좋아한다
])


# Attention Weight 출력
print("Attention Weight")
print(attention_weights)

print("\n각 한국어 Token이 가장 많이 참고한 영어 Token")

for row_index, korean_token in enumerate(korean_tokens):
    # 현재 행에서 가장 큰 값의 열 번호 찾기
    max_index = np.argmax(attention_weights[row_index])

    english_token = english_tokens[max_index]
    weight = attention_weights[row_index, max_index]

    print(f"{korean_token} → {english_token}: {weight:.2f}")