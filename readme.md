
# **PingStats Tool 使用说明**

## **简介**
`PingStats Tool` 是一个基于 Python 的高级 Ping 工具，支持统计延迟、丢包率、抖动等网络性能指标，兼容 Windows 和 Linux 环境。程序能够通过命令行接收参数，适配 Windows 的常见 Ping 参数，支持实时展示统计信息。

---

## **功能特点**
- **支持持续 Ping**：通过 `-t` 参数实现无限次 Ping。
- **多种统计信息**：
  - 平均延迟、丢包率、最大抖动等。
  - 支持统计最近 10 次、50 次、用户自定义的 N 次以及最多 1000 次 Ping 的数据。
- **跨平台支持**：兼容 Windows 和 Linux 系统。
- **动态更新输出**：使用 Rich 库动态刷新统计信息表格。
- **参数灵活**：支持调整超时时间、TTL、数据包大小、Ping 次数等。

---

## **使用方法**

### **命令格式**
```bash
python script.py <host> [options]
```

### **必选参数**
- **`host`**：目标主机地址（可以是域名或 IP 地址）。

### **可选参数**
| 参数                    | 类型      | 默认值    | 描述                                                                                  |
|-------------------------|-----------|-----------|---------------------------------------------------------------------------------------|
| `-t`                     | flag      | `False`   | 持续 Ping，直到手动停止（Ctrl+C）。                                                  |
| `-n <count>`             | 整数      | `100`     | 发送的回显请求数。设置为 0 时表示不限次数。                                           |
| `-l <size>`              | 整数      | `56`      | 发送缓冲区大小（字节）。默认 56，范围 8-1472。                                       |
| `-i <ttl>`               | 整数      | 未设置    | 设置生存时间（TTL）。                                                                |
| `-w <timeout>`           | 整数      | `4`       | 每次 Ping 的超时时间（秒）。                                                         |
| `--valid_count <N>`      | 整数      | `100`     | 统计最近 N 次的延迟和丢包数据。                                                     |
| `-delay <interval_ms>`   | 浮点数    | `1000`    | 两次 Ping 的间隔时间（毫秒）。最低为 10 毫秒。                                       |
| `--help`                 | N/A       | N/A       | 显示帮助信息。                                                                       |

---

## **使用示例**

### **基础示例**
Ping `8.8.8.8`，发送 10 个数据包：
```bash
python script.py 8.8.8.8 -n 10
```

### **持续 Ping**
持续 Ping `www.example.com`，直到手动停止：
```bash
python script.py www.example.com -t
```

### **自定义统计范围**
统计最近 200 次的延迟信息：
```bash
python script.py 192.168.1.1 -n 200 --valid_count 200
```

### **调整超时与数据包大小**
使用 64 字节的数据包，超时时间设置为 2 秒：
```bash
python script.py 192.168.1.1 -l 64 -w 2
```

### **设置 TTL**
发送 TTL 为 128 的 Ping 请求：
```bash
python script.py 8.8.8.8 -i 128
```

### **快速连续 Ping**
每隔 50 毫秒发送一次 Ping：
```bash
python script.py 192.168.1.1 -delay 50
```

---

## **实时统计信息**
运行时会动态更新以下表格信息：

| **统计项**       | **平均延迟**       | **丢包率（错误数/总数）** | **最大抖动（最大延迟/最小延迟）** |
|------------------|--------------------|---------------------------|------------------------------------|
| 最近 10 次 Ping  | 平均延迟（毫秒）  | 丢包率和统计数            | 最大延迟 - 最小延迟（毫秒）       |
| 最近 50 次 Ping  | 平均延迟（毫秒）  | 丢包率和统计数            | 最大延迟 - 最小延迟（毫秒）       |
| 最近 N 次 Ping   | 平均延迟（毫秒）  | 丢包率和统计数            | 最大延迟 - 最小延迟（毫秒）       |
| 最近 1000 次 Ping| 平均延迟（毫秒）  | 丢包率和统计数            | 最大延迟 - 最小延迟（毫秒）       |

---

## **许可证**
本项目遵循 MIT 开源许可证，详见 LICENSE 文件。
```