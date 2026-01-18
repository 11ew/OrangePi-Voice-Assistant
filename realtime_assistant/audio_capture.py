#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频捕获模块
功能：实时捕获麦克风音频，提供异步音频流
作者：哈雷酱（傲娇大小姐工程师）
实现方式：使用 arecord 持续录音 + 管道读取（稳定可靠）
"""

import asyncio
import numpy as np
import logging
from typing import Optional
import queue
import subprocess
import threading


class AudioCapture:
    """音频捕获器（使用 arecord 方式）"""

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
        self.device = config.get("device", "plughw:0,1")  # 默认使用 plughw:0,1

        # 音频队列
        self.audio_queue = queue.Queue()
        self.process = None
        self.reader_thread = None
        self.is_running = False

        self.logger.info("🎙️  音频捕获器初始化完成（arecord 方式）")
        self.logger.info(f"   - 采样率: {self.sample_rate} Hz")
        self.logger.info(f"   - 声道数: {self.channels}")
        self.logger.info(f"   - 块大小: {self.chunk_size} 样本")
        self.logger.info(f"   - 设备: {self.device}")

    def _read_loop(self):
        """
        持续读取音频数据的线程函数
        """
        # 计算每次读取的字节数
        # int16 = 2 bytes per sample
        bytes_per_chunk = self.chunk_size * 2 * self.channels

        self.logger.debug(f"读取线程启动，每次读取 {bytes_per_chunk} 字节")

        try:
            while self.is_running:
                # 从 arecord 的 stdout 读取数据
                chunk = self.process.stdout.read(bytes_per_chunk)

                if not chunk:
                    # 如果读取到空数据，说明进程结束了
                    self.logger.warning("⚠️  arecord 进程意外结束")
                    break

                # 转换为 numpy 数组
                audio_data = np.frombuffer(chunk, dtype=np.int16)

                # 如果是双声道，转换为单声道（取平均）
                if self.channels == 2:
                    audio_data = audio_data.reshape(-1, 2)
                    audio_data = np.mean(audio_data, axis=1).astype(np.int16)

                # 转换为 float32，范围 [-1.0, 1.0]
                audio_data = audio_data.astype(np.float32) / 32768.0

                # 放入队列
                self.audio_queue.put(audio_data)

        except Exception as e:
            if self.is_running:
                self.logger.error(f"❌ 读取线程错误: {e}")
                import traceback
                traceback.print_exc()

        self.logger.debug("读取线程结束")

    def start(self):
        """启动音频捕获"""
        if self.is_running:
            self.logger.warning("⚠️  音频捕获已在运行")
            return

        self.logger.info("🎙️  启动音频捕获...")

        try:
            # 启动 arecord 进程
            # -D: 设备
            # -f: 格式 (S16_LE = signed 16-bit little-endian)
            # -r: 采样率
            # -c: 声道数
            # -t: 类型 (raw = 原始 PCM 数据)
            cmd = [
                'arecord',
                '-D', self.device,
                '-f', 'S16_LE',
                '-r', str(self.sample_rate),
                '-c', str(self.channels),
                '-t', 'raw'
            ]

            self.logger.debug(f"启动命令: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=self.chunk_size * 2 * self.channels
            )

            # 启动读取线程
            self.is_running = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()

            self.logger.info("✅ 音频捕获已启动")

        except Exception as e:
            self.logger.error(f"❌ 启动音频捕获失败: {e}")
            self.is_running = False
            if self.process:
                self.process.terminate()
                self.process = None
            raise

    def stop(self):
        """停止音频捕获"""
        if not self.is_running:
            return

        self.logger.info("🛑 停止音频捕获...")

        # 设置停止标志
        self.is_running = False

        # 终止 arecord 进程
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.logger.warning("⚠️  arecord 进程未响应，强制终止")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                self.logger.error(f"❌ 终止进程时出错: {e}")

            self.process = None

        # 等待读取线程结束
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2.0)
            if self.reader_thread.is_alive():
                self.logger.warning("⚠️  读取线程未能正常结束")

        self.reader_thread = None

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
