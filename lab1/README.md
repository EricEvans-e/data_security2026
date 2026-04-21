# Lab1: Paillier 隐私信息获取实验

本实验在 `localhost` 上实现单服务器、半诚实模型下的 `1-out-of-m` PIR。项目同时包含：

- 基础实验：服务器保存明文消息，客户端使用 Paillier 构造加密 one-hot 查询并解密目标消息。
- 扩展实验：客户端保存 AES-256 密钥，服务器保存 AES-GCM 密文，通过同一套 PIR 逻辑取回目标密文并在客户端解密。
- 对比实验：输出消息规模、密钥长度、基础版与扩展版开销的统计结果。
- 正式报告：`report/main.tex`。

## 目录结构

```text
lab1/
├─ pir_lab/            # 核心实现
├─ scripts/            # 运行入口与 benchmark
├─ tests/              # 自动化测试
├─ results/            # benchmark 与演示日志
├─ report/             # LaTeX 报告
├─ requirements.txt
└─ README.md
```

## 环境准备

推荐环境：

- Python 3.12
- XeLaTeX

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## 基础实验运行

终端 1 启动服务器：

```powershell
python scripts/run_server.py --mode basic --host 127.0.0.1 --port 9101 --count 16
```

终端 2 发起查询：

```powershell
python scripts/run_client.py --mode basic --host 127.0.0.1 --port 9101 --dataset-size 16 --key-size 2048 --index 5
```

客户端会输出：

- 目标下标
- 请求/响应字节数
- 密钥生成、查询构造、网络传输、解密耗时
- 解密得到的目标消息

## 扩展实验运行

先由客户端生成并保存 AES 密钥：

```powershell
python scripts/init_aes_key.py demo_aes.key
```

终端 1 启动扩展版服务器：

```powershell
python scripts/run_server.py --mode aes --host 127.0.0.1 --port 9102 --count 16 --key-file demo_aes.key
```

终端 2 发起扩展查询：

```powershell
python scripts/run_client.py --mode aes --host 127.0.0.1 --port 9102 --dataset-size 16 --key-size 2048 --index 5 --key-file demo_aes.key
```

说明：

- 扩展实验内部使用 `AES-GCM`，服务端实际存储的是 `nonce|tag|ciphertext`。
- 服务端在处理请求时会检查 AES 密文编码后的整数是否不超过 Paillier 的 `max_int`。这比“严格小于 `n`”更强，是 `phe` 库安全编码的实际约束。

## 对比实验

运行 benchmark：

```powershell
python scripts/benchmark.py
```

输出文件：

- `results/benchmark_results.json`
- `results/benchmark_tables.md`

当前已生成的三组实验：

- 消息规模：`m = 8, 16, 32, 64`
- 密钥长度：`1024, 2048, 3072`
- 模式对比：`basic` vs `aes`

## 自动化测试

```powershell
python -m pytest -q
```

测试覆盖：

- 消息编码/解码
- Paillier 选择向量与聚合
- 基础版 TCP 查询
- 扩展版 TCP 查询
- 下标异常处理

## 报告生成

在 `report/` 目录执行：

```powershell
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

## 结果文件

实现过程中已生成以下可直接引用的结果：

- `results/basic_server.out.log`
- `results/basic_client.log`
- `results/aes_server.out.log`
- `results/aes_client.log`
- `results/benchmark_results.json`

这些文件已经和报告中的截图位、实验数据表相对应。
