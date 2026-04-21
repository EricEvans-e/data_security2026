# Benchmark Tables
## Dataset Scale
| count | key_size | avg_total_ms | avg_request_bytes | avg_response_bytes |
| --- | --- | --- | --- | --- |
| 8 | 2048 | 1845.71 | 10811.33 | 1363 |
| 16 | 2048 | 2699.26 | 20920.67 | 1364 |
| 32 | 2048 | 4678.05 | 41142.67 | 1364 |
| 64 | 2048 | 8769.53 | 81588 | 1363.67 |

## Key Size Scale
| count | key_size | avg_total_ms | avg_request_bytes | avg_response_bytes |
| --- | --- | --- | --- | --- |
| 16 | 1024 | 454.14 | 10748.33 | 747.33 |
| 16 | 2048 | 2590.74 | 20921.67 | 1363.67 |
| 16 | 3072 | 9100.2 | 31090.67 | 1979.67 |

## Mode Compare
| mode | count | key_size | avg_total_ms | avg_request_bytes | avg_response_bytes |
| --- | --- | --- | --- | --- | --- |
| basic | 16 | 2048 | 2622.82 | 20923 | 1363.33 |
| aes | 16 | 2048 | 2418.77 | 20917.33 | 1372 |
