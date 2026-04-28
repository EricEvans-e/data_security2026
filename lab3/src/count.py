p = 1000000007

# 输入参与方 id
uid = int(input('请输入参与方 id (1/2/3): '))

# 读取属于自己的份额 user_{1,2,3}_{id}.txt
data = []
for i in range(1, 4):
    with open(f'user_{i}_{uid}.txt', 'r') as f:
        data.append(int(f.read()))

# 计算三个秘密份额的和 (模 p)
d = sum(data) % p
print(f'x={uid} 求得的秘密份额和为: {d}')

# 保存到 d_{id}.txt
with open(f'd_{uid}.txt', 'w') as f:
    f.write(str(d))
