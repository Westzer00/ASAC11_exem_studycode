import numpy as np

np.set_printoptions(precision=3, suppress=True)


# Softmax: 점수를 비율로 변환
def softmax(x):
    exp_x = np.exp(x)
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)


# 실습용 Q, K, V
Q = np.array([
    [1.0, 0.0],
    [0.0, 1.0],
    [1.0, 1.0]
])

K = np.array([
    [1.0, 0.0],
    [0.0, 1.0],
    [1.0, 1.0]
])

V = np.array([
    [1.0, 0.0],
    [0.0, 1.0],
    [1.0, 1.0]
])

d_k = 2


# 1. 기본 Attention

scores = Q @ K.T
scaled_scores = scores / np.sqrt(d_k)
weights = softmax(scaled_scores)
output = weights @ V

print("1. 기본 Attention Weight")
print(weights)

print("\nAttention Output")
print(output)


# 2. Q 값 변경

Q_changed = Q.copy()
Q_changed[2] = [2.0, 0.0]

q_scores = Q_changed @ K.T
q_scaled_scores = q_scores / np.sqrt(d_k)
q_weights = softmax(q_scaled_scores)

print("\n2. Q 변경 후 Weight")
print(q_weights)


# 3. K 값 변경

K_changed = K.copy()
K_changed[1] = [2.0, 0.0]

k_scores = Q @ K_changed.T
k_scaled_scores = k_scores / np.sqrt(d_k)
k_weights = softmax(k_scaled_scores)

print("\n3. K 변경 후 Weight")
print(k_weights)


# 4. Causal Mask 적용

mask = np.array([
    [0, -1e9, -1e9],
    [0,     0, -1e9],
    [0,     0,     0]
])

masked_scores = scaled_scores + mask
mask_weights = softmax(masked_scores)

print("\n4. Mask 적용 후 Weight")
print(mask_weights)