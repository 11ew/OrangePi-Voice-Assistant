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

        # 硬件采样率（Orange Pi 原生 48000 Hz）
        self.hardware_sample_rate = 48000
        # 目标采样率（ASR 需要 16000 Hz）
        self.target_sample_rate = config.get("sample_rate", 16000)
        self.channels = config.get("channels", 1)
        # 块大小基于硬件采样率（100ms @ 48kHz = 4800 样本）
        self.chunk_size = int(self.hardware_sample_rate * 0.1)
        self.device = config.get("device", "plughw:0,1")

        # 降采样比例
        self.downsample_ratio = self.hardware_sample_rate // self.target_sample_rate

        # 音频队列
        self.audio_queue = queue.Queue()
        self.process = None
        self.reader_thread = None
        self.is_running = False

        self.logger.info("🎙️  音频捕获器初始化完成（arecord 方式）")
        self.logger.info(f"   - 硬件采样率: {self.hardware_sample_rate} Hz")
        self.logger.info(f"   - 目标采样率: {self.target_sample_rate} Hz")
        self.logger.info(f"   - 降采样比例: {self.downsample_ratio}:1")
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

        # 设置 stdout 为非阻塞模式（避免阻塞导致进程崩溃）
        import fcntl
        import os
        try:
            fd = self.process.stdout.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            self.logger.debug("✅ 设置 stdout 为非阻塞模式")
        except Exception as e:
            self.logger.warning(f"⚠️  设置非阻塞模式失败: {e}")

        consecutive_empty_reads = 0  # 连续空读次数
        max_empty_reads = 10  # 最大连续空读次数

        try:
            while self.is_running:
                try:
                    # 从 arecord 的 stdout 读取数据（非阻塞）
                    chunk = self.process.stdout.read(bytes_per_chunk)

                    if not chunk:
                        consecutive_empty_reads += 1

                        # 检查进程是否还活着
                        if self.process.poll() is not None:
                            # 进程已退出
                            self.logger.warning("⚠️  arecord 进程已退出，尝试重启...")
                            if self.is_running:
                                self._restart_arecord()
                                consecutive_empty_reads = 0
                                continue
                            else:
                                break

                        # 如果连续多次空读，可能是管道问题
                        if consecutive_empty_reads >= max_empty_reads:
                            self.logger.warning(f"⚠️  连续 {max_empty_reads} 次空读，检查进程状态...")
                            if not self._check_process_health():
                                self._restart_arecord()
                                consecutive_empty_reads = 0
                                continue

                        # 短暂休眠，避免 CPU 占用过高
                        import time
                        time.sleep(0.01)
                        continue

                    # 成功读取数据，重置计数器
                    consecutive_empty_reads = 0

                except BlockingIOError:
                    # 非阻塞模式下，没有数据可读
                    import time
                    time.sleep(0.01)
                    continue

                # 转换为 numpy 数组
                audio_data = np.frombuffer(chunk, dtype=np.int16)

                # 如果是双声道，转换为单声道（取平均）
                if self.channels == 2:
                    audio_data = audio_data.reshape(-1, 2)
                    audio_data = np.mean(audio_data, axis=1).astype(np.int16)

                # 转换为 float32，范围 [-1.0, 1.0]
                audio_data = audio_data.astype(np.float32) / 32768.0

                # 降采样：从 48000 Hz 到 16000 Hz（每 3 个样本取 1 个）
                if self.downsample_ratio > 1:
                    audio_data = audio_data[::self.downsample_ratio]

                # 放入队列
                self.audio_queue.put(audio_data)

        except Exception as e:
            if self.is_running:
                self.logger.error(f"❌ 读取线程错误: {e}")
                import traceback
                traceback.print_exc()

        self.logger.debug("读取线程结束")

    def _check_process_health(self) -> bool:
        """
        检查 arecord 进程健康状态

        返回:
            True 表示健康，False 表示需要重启
        """
        if not self.process:
            return False

        # 检查进程是否还在运行
        if self.process.poll() is not None:
            return False

        # 检查 stdout 是否还可用
        try:
            if self.process.stdout.closed:
                return False
        except:
            return False

        return True

    def _restart_arecord(self):
        """重启 arecord 进程"""
        try:
            # 终止旧进程
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=1.0)
                except:
                    pass

            # 启动新进程
            cmd = [
                'arecord',
                '-D', self.device,
                '-f', 'S16_LE',
                '-r', str(self.hardware_sample_rate),
                '-c', str(self.channels),
                '-t', 'raw'
            ]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=self.chunk_size * 2 * self.channels * 10  # 增大缓冲区 10 倍
            )

            self.logger.info("✅ arecord 进程已重启")

        except Exception as e:
            self.logger.error(f"❌ 重启 arecord 失败: {e}")
            self.is_running = False

    def start(self):
        """启动音频捕获"""
        if self.is_running:
            self.logger.warning("⚠️  音频捕获已在运行")
            return

        self.logger.info("🎙️  启动音频捕获...")

        try:
            # 设置音频设备参数（参考官方脚本）
            import subprocess as sp

            # 设置 Deviceid（指定使用耳机/麦克风）
            try:
                sp.run(['amixer', 'set', 'Deviceid', '2'],
                       check=False, capture_output=True)
                self.logger.debug("✅ 设置 Deviceid = 2")
            except Exception as e:
                self.logger.warning(f"⚠️  设置 Deviceid 失败: {e}")

            # 设置 Capture 音量
            try:
                sp.run(['amixer', 'set', 'Capture', '10'],
                       check=False, capture_output=True)
                self.logger.debug("✅ 设置 Capture = 10")
            except Exception as e:
                self.logger.warning(f"⚠️  设置 Capture 音量失败: {e}")

            # 启动 arecord 进程
            # -D: 设备
            # -f: 格式 (S16_LE = signed 16-bit little-endian)
            # -r: 采样率（使用硬件原生 48000 Hz）
            # -c: 声道数
            # -t: 类型 (raw = 原始 PCM 数据)
            cmd = [
                'arecord',
                '-D', self.device,
                '-f', 'S16_LE',
                '-r', str(self.hardware_sample_rate),
                '-c', str(self.channels),
                '-t', 'raw'
            ]

            self.logger.debug(f"启动命令: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=self.chunk_size * 2 * self.channels * 10  # 增大缓冲区 10 倍
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
