# 3일차 오후 실습 제출물

## 1. NumPy를 사용해 간단한 Attention을 계산하기

```text
scores = Q @ K.T
scaled_scores = scores / np.sqrt(d_k)
weights = softmax(scaled_scores)
output = weights @ V 
```

## 2. 추가 실험
- [x] Q 값을 변경
- [x] K 값을 변경
- [x] Mask 적용
- [x] Attention Weight 비교

## 3. 실험 결과

- [x] 기본 Attention을 계산하여 Token별 참고 비율을 확인 
- [x] Q 값을 변경하자 해당 Token이 다른 Token을 참고하는 비율이 달라짐
- [x] K 값을 변경하자 다른 Token들이 해당 Token을 참고하는 비율이 달라짐
- [x] Causal Mask 적용 후 미래 Token의 Attention Weight가 0으로 변경됨