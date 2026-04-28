import function as func

# 模数 p
p = 1000000007
print(f'模数 p: {p}')

# 输入参与方 id 以及秘密 s
uid = int(input('请输入参与方 id (1/2/3): '))
s = int(input(f'请输入用户{uid}的秘密值 s: '))

# 秘密份额横坐标为 1, 2, 3
shares_x = [1, 2, 3]

# 构造一次多项式 f(x) = s + r*x mod p (t=1, 即 (2,3) 门限)
print(f'\n用户{uid}的秘密值的多项式及秘密份额：')
f = func.get_polynomial(s, 1, p, str(uid))
for j in range(3):
    share_y = func.count_polynomial(f, shares_x[j], p)
    print(f'  ({shares_x[j]}, {share_y})')
    with open(f'user_{uid}_{j+1}.txt', 'w') as fout:
        fout.write(str(share_y))
