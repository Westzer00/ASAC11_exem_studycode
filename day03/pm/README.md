## Transformer 구조도

## NumPy를 사용해 간단한 Attention을 계산합니다.
scores = Q @ K.T
scaled_scores = scores / np.sqrt(d_k)
weights = softmax(scaled_scores)
output = weights @ V 
## 추가 실험
- [x] 2nd checkbox

- [ ] Q 값을 변경
- [ ] K 값을 변경
- [ ] Mask 적용
- [ ] Attention Weight 비교
