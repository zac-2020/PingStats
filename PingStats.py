# -*- coding: utf-8 -*-
# @Time     : 2024/11/15 10:48
# @Author   : Zac
# @Email    : zac_2020@qq.com
# @Software : PyCharm
# @File     : PingTools.py
# @Board    : None
# @version  : PingTools v1.0
from xml.etree.ElementTree import VERSION

import ping3
import argparse
# https://rich.pythonlang.cn/en/stable/traceback.html
from rich.console import Console
from rich.table import Table
from rich.live import Live
import time


class PingData:
    def __init__(self, max_list: int = 1000):
        """
        统计 ping 数据
        :param max_list: 数据列表最大长度，用于限制统计范围 0 的话就不保存datalist
        """
        self.delay: float = 0.0  # 当前延迟
        self.data: list = []  # 存储延迟数据
        self.max_list = max_list  # 最大记录数
        self.total_sum = 0

    def append(self, delay: float):
        """
        添加新的延迟数据，并更新统计
        :param delay: 本次 ping 的延迟时间，0 表示超时
        """
        self.delay = delay
        self.total_sum += delay
        self.data.append(delay)
        # 限制 data 长度
        if len(self.data) > self.max_list:
            removed = self.data.pop(0)
            self.total_sum -= removed

    @property
    def delay_max(self):
        return max(self.data)

    @property
    def delay_min(self):
        return min(self.data)

    @property
    def success_count(self):
        return self.count - self.error_count

    @property
    def error_count(self):
        return self.data.count(-1)

    @property
    def jitter(self):
        if len(self.data) < 2:
            return 0
        return self.delay_max - self.delay_min

    @property
    def delay_avg(self):
        # 错误是-1  有多少错误就补多少
        return (self.sum + self.error_count) / self.success_count if self.success_count > 0 else 0

    @property
    def packet_loss_rate(self):
        return (self.error_count / self.count) * 100 if self.count > 0 else 0

    @property
    def count(self):
        return len(self.data)

    @property
    def sum(self):
        # return sum(self.data)  # 每次调用 sum 都会重新计算数据总和，数据量较大时性能可能较差
        return self.total_sum

    def __str__(self):
        """提供一个简洁的统计信息字符串"""
        return (
            f"Count: {self.count}, Errors: {self.error_count}, "
            f"Loss Rate: {self.packet_loss_rate:.2f}%, "
            f"Avg: {self.delay_avg:.2f}ms, Min: {self.delay_min:.2f}ms, "
            f"Max: {self.delay_max:.2f}ms"
        )


class PingStats:
    def __init__(self, host, timeout_s: int = 4, ttl=None, size: int = 32, max_count: int = 100, valid_count: int = 100,
                 interval_ms: float = 1000, forever: bool = False):
        """
        执行 ping 操作并统计数据
        """
        self.size = max(min(size, 1472), 8)
        self.host = host
        self.timeout_s = timeout_s
        self.ttl = ttl
        self.max_count = 0 if forever else max_count
        self.count = 0  # 计数器
        self.interval_ms = max(interval_ms, 100)  # 最低 100 毫秒 若用户将 interval_ms 设置为极小值，会导致循环过快，增加 CPU 占用。

        self.near_10_ping_data = PingData(max_list=10)
        self.near_50_ping_data = PingData(max_list=50)
        self.near_n_ping_data = PingData(max_list=valid_count)
        self.near_1000_ping_data = PingData(max_list=1000)

    def start(self):
        console = Console()
        with Live(self.create_rich_table(), console=console, auto_refresh=True) as live:
            while self.count < self.max_count or self.max_count == 0:
                try:
                    if self.interval_ms > 0 and self.count > 0:
                        time.sleep(self.interval_ms / 1000)
                    self.count += 1
                    ping3.EXCEPTIONS = False
                    delay = ping3.ping(self.host, timeout=self.timeout_s, unit='ms', ttl=self.ttl, size=self.size)
                    if delay is False:
                        delay = -1
                        err_msg = "error"
                    elif delay is None:
                        delay = -1
                        err_msg = "timeout"
                    self.near_n_ping_data.append(delay)
                    self.near_1000_ping_data.append(delay)
                    self.near_10_ping_data.append(delay)
                    self.near_50_ping_data.append(delay)
                    console.log(
                        f"PingStats {VERSION} 来自({self.host})的回复：字节={self.size} 时间={err_msg if delay == -1 else delay} ms ")
                    live.update(self.create_rich_table())
                except KeyboardInterrupt:
                    console.log("bye.")
                    exit(0)

    def create_rich_table(self):
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(self.count * self.interval_ms / 1000))
        table = Table(
            title=f"PingStats {VERSION}"
            # f"来自({self.host})的回复：字节={self.size} 时间={self.near_10_ping_data.delay:.2f}ms"
                  f" 运行时间: {elapsed_time}"
                  f""
        )
        table.add_column(f"当前：{self.near_10_ping_data.delay:.2f}ms", justify="center", style="cyan", no_wrap=True)
        table.add_column("平均延迟", justify="center", style="cyan", no_wrap=True)
        table.add_column("丢包(错误数/总数)）", justify="center", style="cyan", no_wrap=True)
        table.add_column("最大抖动（最大延迟/最小延迟）", justify="center", style="cyan", no_wrap=True)

        self.add_table_row(table, f"近({self.near_10_ping_data.count})次Ping", self.near_10_ping_data)
        self.add_table_row(table, f"近({self.near_50_ping_data.count})次Ping", self.near_50_ping_data)
        self.add_table_row(table, f"近({self.near_n_ping_data.count})次Ping", self.near_n_ping_data)
        self.add_table_row(table, f"近({self.near_1000_ping_data.count})次Ping", self.near_1000_ping_data)
        return table

    @staticmethod
    def add_table_row(table, label, stats: PingData):
        loss_rate_color = "red" if stats.packet_loss_rate > 10 else "green"
        table.add_row(
            label,
            # f"{stats.packet_loss_rate:.2f}%({stats.error_count}/{stats.count})",
            f"{stats.delay_avg:.2f}ms" if stats.count > 0 else "None",
            f"[{loss_rate_color}]{stats.packet_loss_rate:.2f}%({stats.error_count}/{stats.count})[/]",
            f"{stats.jitter:.2f}ms({stats.delay_max:.2f}-{stats.delay_min:.2f})"
            if stats.count > 0
            else "None",
        )


if __name__ == '__main__':
    VERSION = "v1.0.1"
    parser = argparse.ArgumentParser(description=f"PingStats Tool {VERSION}")

    # 通用目标地址
    parser.add_argument('host', type=str, help='目标主机地址')

    parser.add_argument('-t', action='store_true', help='Ping 指定的主机，直到停止（适用于 Windows -t 参数）')
    parser.add_argument('-n', '--count', type=int, default=100, help='发送的回显请求数（默认 100 次）')
    parser.add_argument('-l', '--size', type=int, default=56, help='发送缓冲区大小（默认 56 字节）')
    parser.add_argument('-i', '--ttl', type=int, default=None, help='生存时间 TTL（默认不设置）')
    parser.add_argument('-w', '--timeout_s', type=int, default=4, help='等待每次回复的超时时间（秒，默认 4 秒）')
    parser.add_argument('-d', '--interval_ms', type=float, default=1000, help='Ping 间隔时间（毫秒，默认 1000 毫秒）')
    parser.add_argument('-v', '--valid_count', type=int, default=100, help='最近 N 次统计数据的数量（默认 100）')

    args = parser.parse_args()

    # 永久 Ping (-t 参数处理)
    forever = args.t

    # 创建 PingStats 实例并运行
    ping_instance = PingStats(
        host=args.host,
        timeout_s=args.timeout_s,
        ttl=args.ttl,
        size=args.size,
        max_count=0 if forever else args.count,
        valid_count=args.valid_count,
        interval_ms=args.interval_ms,
    )
    ping_instance.start()
