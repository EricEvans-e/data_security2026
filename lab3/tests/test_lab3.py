"""
Lab3 自动化测试脚本

测试流程：模拟三人分别输入私有数据，通过 Shamir (2,3) 秘密共享
完成隐私求和与平均值计算，验证正确性、门限恢复一致性及隐私性。
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import function as func

P = 1000000007
SHARES_X = [1, 2, 3]


def run_full_flow(secrets):
    """运行完整流程：份额生成 → 局部求和 → 重构平均，返回中间产物"""
    n = len(secrets)

    # ---- 阶段1: 每个用户生成多项式并分发份额 ----
    all_shares = {}  # all_shares[user_id][point_idx] = share_value
    for uid, s in enumerate(secrets, start=1):
        f = func.get_polynomial(s, 1, P, str(uid))
        for j, x in enumerate(SHARES_X, start=1):
            share_y = func.count_polynomial(f, x, P)
            all_shares[(uid, j)] = share_y

    # ---- 阶段2: 每个计算方求局部和 ----
    d = {}
    for receiver in range(1, n + 1):
        total = 0
        for sender in range(1, n + 1):
            total = (total + all_shares[(sender, receiver)]) % P
        d[receiver] = total

    # ---- 阶段3: 拉格朗日插值重构 ----
    # 用 d1, d2 重构
    S12 = func.restructure_polynomial([1, 2], [d[1], d[2]], 2, P)
    # 用 d1, d3 重构
    S13 = func.restructure_polynomial([1, 3], [d[1], d[3]], 2, P)
    # 用 d2, d3 重构
    S23 = func.restructure_polynomial([2, 3], [d[2], d[3]], 2, P)

    avg_direct = S12 / 3.0

    return {
        'all_shares': all_shares,
        'd': d,
        'S12': S12,
        'S13': S13,
        'S23': S23,
        'avg_direct': avg_direct,
    }


def test_basic_correctness():
    """基础正确性：3+6+9=18, avg=6.0"""
    print('=' * 60)
    print('测试1: 基础正确性 (3, 6, 9)')
    print('=' * 60)
    result = run_full_flow([3, 6, 9])
    expected_sum = 18
    expected_avg = 6.0

    assert result['S12'] == expected_sum, f'S12={result["S12"]}, expected={expected_sum}'
    assert result['S13'] == expected_sum
    assert result['S23'] == expected_sum
    assert abs(result['avg_direct'] - expected_avg) < 1e-9

    print(f'  d1={result["d"][1]}, d2={result["d"][2]}, d3={result["d"][3]}')
    print(f'  S (via d1,d2) = {result["S12"]}')
    print(f'  S (via d1,d3) = {result["S13"]}')
    print(f'  S (via d2,d3) = {result["S23"]}')
    print(f'  avg = {result["avg_direct"]}')
    print('  PASS\n')


def test_threshold_consistency():
    """门限一致性：任意2份份额恢复结果应相同"""
    print('=' * 60)
    print('测试2: 门限恢复一致性 (100, 200, 300)')
    print('=' * 60)
    result = run_full_flow([100, 200, 300])

    assert result['S12'] == result['S13'] == result['S23'] == 600
    print(f'  S12={result["S12"]}, S13={result["S13"]}, S23={result["S23"]}')
    print('  三者一致，PASS\n')


def test_non_divisible():
    """非整除测试：1+2+2=5, avg≈1.666..."""
    print('=' * 60)
    print('测试3: 非整除情况 (1, 2, 2)')
    print('=' * 60)
    result = run_full_flow([1, 2, 2])

    assert result['S12'] == 5
    assert abs(result['avg_direct'] - 5 / 3.0) < 1e-9
    print(f'  S = {result["S12"]}, avg = {result["avg_direct"]}')
    print(f'  期望: 5/3 ≈ {5/3}')
    print('  PASS\n')


def test_randomness():
    """随机性验证：同一输入两次运行，份额不同但重构一致"""
    print('=' * 60)
    print('测试4: 随机性验证 (分别运行两次)')
    print('=' * 60)
    r1 = run_full_flow([42, 17, 99])
    r2 = run_full_flow([42, 17, 99])

    # 份额应不同（多项式随机系数不同）
    shares_differ = False
    for k in r1['all_shares']:
        if r1['all_shares'][k] != r2['all_shares'][k]:
            shares_differ = True
            break
    assert shares_differ, '两次运行的份额应不同'

    # 但重构结果相同
    assert r1['S12'] == r2['S12'] == 158
    print(f'  第一次 S={r1["S12"]}, d={r1["d"]}')
    print(f'  第二次 S={r2["S12"]}, d={r2["d"]}')
    print('  份额不同但重构结果相同，PASS\n')


def test_privacy_intuition():
    """隐私直观验证：单个份额文件不暴露原始秘密"""
    print('=' * 60)
    print('测试5: 隐私性直观验证')
    print('=' * 60)
    result = run_full_flow([12345, 67890, 11111])

    # 取 user_1_1.txt (用户1分给计算方1的份额)
    share = result['all_shares'][(1, 1)]
    print(f'  用户1的秘密=12345, 其发给计算方1的份额={share}')
    print(f'  份额在模P下呈现为随机数，无法直接推断原始值')

    # 进一步：验证份额本身不直接等于秘密值
    assert share != 12345, '份额不应等于秘密值本身'
    print('  份额 ≠ 秘密值，满足直观隐私要求')
    print('  PASS\n')


def test_large_values():
    """较大值测试"""
    print('=' * 60)
    print('测试6: 较大值 (1000000, 2000000, 3000000)')
    print('=' * 60)
    result = run_full_flow([1000000, 2000000, 3000000])

    assert result['S12'] == 6000000
    assert abs(result['avg_direct'] - 2000000.0) < 1e-9
    print(f'  S = {result["S12"]}, avg = {result["avg_direct"]}')
    print('  PASS\n')


if __name__ == '__main__':
    test_basic_correctness()
    test_threshold_consistency()
    test_non_divisible()
    test_randomness()
    test_privacy_intuition()
    test_large_values()
    print('=' * 60)
    print('全部 6 项测试通过!')
    print('=' * 60)
