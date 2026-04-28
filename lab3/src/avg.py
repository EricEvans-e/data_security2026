import function as func

p = 1000000007

# 任选两个参与方的局部和份额进行重构，例如 d2, d3
x_used = [2, 3]
d_values = []
for i in x_used:
    with open(f'd_{i}.txt', 'r') as f:
        d_values.append(int(f.read()))

# 拉格朗日插值重构总和 S
S = func.restructure_polynomial(x_used, d_values, 2, p)
print(f'重构总和 S = a + b + c = {S}')

# 直接除法求平均值
avg_direct = S / 3.0
print(f'平均值（直接除法）: {avg_direct}')

# 模逆元方式求平均值（有限域内）
inv3 = func.quickpower(3, p - 2, p)
avg_mod = (S * inv3) % p
print(f'3 在模{p}下的逆元: {inv3}')
print(f'平均值（模逆元运算）: {avg_mod}')
