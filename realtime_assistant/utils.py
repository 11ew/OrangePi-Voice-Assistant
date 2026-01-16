#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
功能：提供日志配置、配置加载、文件管理、性能监控等工具函数
作者：哈雷酱（傲娇大小姐工程师）
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
import sys


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    配置日志系统

    参数:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    返回:
        配置好的 logger 对象
    """
    logger = logging.getLogger("realtime_assistant")
    logger.setLevel(getattr(logging, log_level.upper()))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # 使用彩色格式化器
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def load_config(config_file: str) -> Dict[str, Any]:
    """
    加载配置文件

    参数:
        config_file: 配置文件路径（相对于项目根目录）

    返回:
        配置字典
    """
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    config_path = project_root / config_file

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config


def ensure_dir(directory: str) -> Path:
    """
    确保目录存在，不存在则创建

    参数:
        directory: 目录路径

    返回:
        Path 对象
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化性能监控器

        参数:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("realtime_assistant")
        self.timers = {}
        self.counters = {}

    def start_timer(self, name: str):
        """开始计时"""
        self.timers[name] = time.time()

    def stop_timer(self, name: str) -> float:
        """
        停止计时并返回耗时

        参数:
            name: 计时器名称

        返回:
            耗时（秒）
        """
        if name not in self.timers:
            self.logger.warning(f"计时器 '{name}' 不存在")
            return 0.0

        elapsed = time.time() - self.timers[name]
        del self.timers[name]

        self.logger.debug(f"⏱️  {name}: {elapsed:.3f}s")
        return elapsed

    def increment_counter(self, name: str, value: int = 1):
        """增加计数器"""
        self.counters[name] = self.counters.get(name, 0) + value

    def get_counter(self, name: str) -> int:
        """获取计数器值"""
        return self.counters.get(name, 0)

    def reset_counter(self, name: str):
        """重置计数器"""
        self.counters[name] = 0

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "counters": self.counters.copy(),
            "active_timers": list(self.timers.keys())
        }

    def log_stats(self):
        """记录统计信息"""
        stats = self.get_stats()
        self.logger.info(f"📊 性能统计: {stats}")


def format_duration(seconds: float) -> str:
    """
    格式化时长

    参数:
        seconds: 秒数

    返回:
        格式化的时长字符串
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
