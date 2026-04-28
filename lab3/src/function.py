import random


def quickpower(a, b, p):
    """快速幂计算 a^b % p"""
    a = a % p
    ans = 1
    while b != 0:
        if b & 1:
            ans = (ans * a) % p
        b >>= 1
        a = (a * a) % p
    return ans


def get_polynomial(x0, T, p, fname):
    """构建多项式：x0为常数项系数，T为最高次项次数，p为模数"""
    f = [x0]
    for _ in range(T):
        f.append(random.randrange(0, p))
    f_print = f'f{fname} = {f[0]}'
    for i in range(1, T + 1):
        f_print += f' + {f[i]}x^{i}'
    print(f_print)
    return f


def count_polynomial(f, x, p):
    """计算多项式在x处的值 mod p"""
    ans = f[0]
    for i in range(1, len(f)):
        ans = (ans + f[i] * quickpower(x, i, p)) % p
    return ans


def restructure_polynomial(x, fx, t, p):
    """拉格朗日插值重构多项式在x=0处的值，t为使用的点数"""
    ans = 0
    for i in range(t):
        fx[i] = fx[i] % p
        fxi = 1
        for j in range(t):
            if j != i:
                fxi = (-1 * fxi * x[j] * quickpower(x[i] - x[j], p - 2, p)) % p
        fxi = (fxi * fx[i]) % p
        ans = (ans + fxi) % p
    return ans
