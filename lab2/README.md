# Lab2: zkSNARK 零知识证明实验

本实验按教材第四章 `zkSNARK / 算术电路 / R1CS / setup-prove-verify` 的主线实现命题证明：

```text
x^3 + x + 5 = Out
```

在默认演示中，公开输入为 `Out = 35`，证明者的私密见证为 `x = 3`。证明者需要在不泄露 `x` 的前提下，让验证者相信自己知道一个满足约束的解。

## 目录结构

```text
lab2/
├─ zk_lab/            # libsnark 证明代码
├─ scripts/           # PowerShell 入口与 WSL 脚本
├─ results/           # 证明密钥、验证密钥、证明文件与日志
├─ report/            # LaTeX 报告
├─ src/               # 报告截图说明
├─ tests/             # 轻量级数学一致性测试
├─ requirements.txt
└─ README.md
```

## 实现说明

- WSL 独立工作目录固定为 `~/workspace/data-security-lab2/`。
- 如果 WSL 中使用 Python，只通过 `conda` 环境 `datasec-lab2-zk` 运行。
- `lab2` 仓库内只保留课程提交需要的源码、脚本、结果和报告，不把整个 `libsnark` 源码树纳入仓库。
- WSL 当前会把 `HOME` 暴露成异常值，脚本会统一改写为 `/home/eric`，避免路径混乱。

## 代码逻辑

证明电路把命题拆成如下 R1CS 约束：

1. `x * x = x_square`
2. `x_square * x = x_cube`
3. `(x_cube + x) * 1 = sum_with_x`
4. `(sum_with_x + 5) * 1 = expr_out`
5. `expr_out * 1 = out`

其中：

- 公有输入：`out`
- 私有输入：`x`, `x_square`, `x_cube`, `sum_with_x`, `expr_out`

## PowerShell 入口

建议从 `实验/lab2/` 目录执行：

```powershell
.\scripts\setup_wsl_env.ps1
.\scripts\build_lab2.ps1
.\scripts\run_demo.ps1 -X 3 -Out 35
.\scripts\run_negative_cases.ps1
.\scripts\build_report.ps1
```

可选参数：

- `-Distro Ubuntu-22.04`
- `-WorkspaceRoot /home/eric/workspace/data-security-lab2`
- `-SudoPassword 122333` 用于自动化安装依赖；若不提供，脚本会改用交互式 `sudo`

## WSL 工作区布局

WSL 侧脚本会维护以下目录：

```text
~/workspace/data-security-lab2/
├─ env/
├─ libsnark-src/
├─ build/
├─ artifacts/
└─ logs/
```

## 验证目标

- 正确样例：`x=3, out=35`，验证结果应为 `1`
- 错误 witness：`x=4, out=35`，证明阶段应失败
- 错误公开输入：对 `x=3, out=35` 生成的证明，用 `out=36` 验证，应输出 `0`

## 报告生成

在 `report/` 下使用：

```powershell
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

`build_report.ps1` 会自动执行这四步。
