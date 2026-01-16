#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频捕获模块
功能：实时捕获麦克风音频，提供异步音频流
作者：哈雷酱（傲娇大小姐工程师）
"""

import asyncio
import numpy as np
import logging
from typing import Optional
import queue

# 延迟导入 sounddevice（避免启动时的导入错误）
sd = None

def _import_sounddevice():
    """延迟导入 sounddevice"""
    global sd
    if sd is not None:
        return sd

    try:
        import sounddevice as _sd
        sd = _sd
        return sd
    except ImportError:
        raise ImportError("未安装 sounddevice，请运行: pip install sounddevice")
    except OSError as e:
        raise OSError(f"PortAudio 库未找到，请安装: sudo apt-get install portaudio19-dev\n错误详情: {e}")


class AudioCapture:
    """音频捕获器"""

    def __init__(self, config: dict):
        """
        初始化音频捕获器

        参数:
            config: 音频配置字典
        """
        self.logger = logging.getLogger("realtime_assistant.audio_capture")
        self.config = config

        self.sample_rate = config.get("sample_rate", 16000)
        self.channels = config.get("channels", 1)
        self.chunk_size = config.get("chunk_size", 1600)  # 100ms @ 16kHz
        self.device = config.get("device", "default")

        # 音频队列
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_running = False

        self.logger.info("🎙️  音频捕获器初始化完成")
        self.logger.info(f"   - 采样率: {self.sample_rate} Hz")
        self.logger.info(f"   - 声道数: {self.channels}")
        self.logger.info(f"   - 块大小: {self.chunk_size} 样本")

    def _audio_callback(self, indata, frames, time_info, status):
        """
        音频回调函数

        参数:
            indata: 输入音频数据
            frames: 帧数
            time_info: 时间信息
            status: 状态
        """
        if status:
            self.logger.warning(f"⚠️  音频状态: {status}")

        # 将音频数据放入队列
        audio_data = indata.copy().flatten()
        self.audio_queue.put(audio_data)

    def start(self):
        """启动音频捕获"""
        # 延迟导入 sounddevice
        _import_sounddevice()

        if self.is_running:
            self.logger.warning("⚠️  音频捕获已在运行")
            return

        self.logger.info("🎙️  启动音频捕获...")

        # 创建音频流
        self.stream = sd.InputStream(
            device=self.device if self.device != "default" else None,
            channels=self.channels,
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            dtype=np.float32,
            callback=self._audio_callback
        )

        self.stream.start()
        self.is_running = True

        self.logger.info("✅ 音频捕获已启动")

    def stop(self):
        """停止音频捕获"""
        if not self.is_running:
            return

        self.logger.info("🛑 停止音频捕获...")

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.is_running = False

        # 清空队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        self.logger.info("✅ 音频捕获已停止")

    async def read_async(self) -> Optional[np.ndarray]:
        """
        异步读取音频数据

        返回:
            音频数据数组，如果没有则返回 None
        """
        if not self.is_running:
            return None

        # 使用 asyncio 的方式从队列读取
        loop = asyncio.get_event_loop()
        try:
            # 在线程池中执行阻塞的 queue.get
            audio_data = await loop.run_in_executor(
                None,
                self.audio_queue.get,
                True,  # block
                0.1    # timeout
            )
            return audio_data
        except queue.Empty:
            return None

    def read(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """
        同步读取音频数据

        参数:
            timeout: 超时时间（秒）

        返回:
            音频数据数组，如果没有则返回 None
        """
        if not self.is_running:
            return None

        try:
            audio_data = self.audio_queue.get(timeout=timeout)
            return audio_data
        except queue.Empty:
            return None

    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.audio_queue.qsize()

    def clear_queue(self):
        """清空队列"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


async def audio_stream_generator(capture: AudioCapture):
    """
    音频流生成器

    参数:
        capture: 音频捕获器

    生成:
        音频数据数组
    """
    logger = logging.getLogger("realtime_assistant.audio_capture")

    while capture.is_running:
        audio_data = await capture.read_async()
        if audio_data is not None:
            yield audio_data
        else:
            # 短暂休眠，避免 CPU 占用过高
            await asyncio.sleep(0.01)
