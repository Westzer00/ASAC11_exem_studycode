# 3일차 오후 실습 제출물

## 1. NumPy를 사용해 간단한 Attention을 계산하기

```text
scores = Q @ K.T
scaled_scores = scores / np.sqrt(d_k)
weights = softmax(scaled_scores)
output = weights @ V 
```

## 2. 추가 실험
- [ ] Q 값을 변경
- [ ] K 값을 변경
- [ ] Mask 적용
- [ ] Attention Weight 비교
