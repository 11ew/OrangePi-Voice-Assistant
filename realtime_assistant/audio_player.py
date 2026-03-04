#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频播放器模块
功能：异步音频播放，支持队列和打断机制
作者：哈雷酱（傲娇大小姐工程师）
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional


class AudioPlayer:
    """音频播放器"""

    def __init__(self):
        """初始化音频播放器"""
        self.logger = logging.getLogger("realtime_assistant.player")

        # 播放队列
        self.play_queue = asyncio.Queue()

        # 当前播放进程
        self.current_process: Optional[asyncio.subprocess.Process] = None

        # 播放状态
        self.is_playing = False
        self.is_running = False

        self.logger.info("✅ 音频播放器初始化完成")

    async def play_async(self, audio_file: str):
        """
        异步播放音频（添加到队列）

        参数:
            audio_file: 音频文件路径
        """
        if not Path(audio_file).exists():
            self.logger.error(f"❌ 音频文件不存在: {audio_file}")
            return

        await self.play_queue.put(audio_file)
        self.logger.debug(f"📥 音频已加入队列: {audio_file}")

    async def _play_worker(self):
        """播放工作循环"""
        self.logger.info("🎵 播放工作线程已启动")

        while self.is_running:
            try:
                # 从队列获取音频文件
                audio_file = await asyncio.wait_for(
                    self.play_queue.get(),
                    timeout=0.5
                )

                # 播放音频
                await self._play_file(audio_file)

            except asyncio.TimeoutError:
                # 队列为空，继续等待
                continue
            except Exception as e:
                self.logger.error(f"❌ 播放错误: {e}")

        self.logger.info("🛑 播放工作线程已停止")

    async def _play_file(self, audio_file: str):
        """
        播放单个音频文件

        参数:
            audio_file: 音频文件路径
        """
        self.is_playing = True
        self.logger.info(f"🔊 播放音频: {audio_file}")

        try:
            # 使用 aplay 播放（指定 Orange Pi 播放设备）
            self.current_process = await asyncio.create_subprocess_exec(
                "aplay",
                "-Dhw:ascend310b",  # Orange Pi 播放设备
                "-q",  # 安静模式
                audio_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # 等待播放完成
            await self.current_process.wait()

            if self.current_process.returncode == 0:
                self.logger.info("✅ 播放完成")
            else:
                stderr = await self.current_process.stderr.read()
                self.logger.error(f"❌ 播放失败: {stderr.decode()}")

        except Exception as e:
            self.logger.error(f"❌ 播放异常: {e}")
        finally:
            self.is_playing = False
            self.current_process = None

    async def interrupt(self):
        """打断当前播放"""
        if self.current_process and self.is_playing:
            self.logger.info("⏹️  打断播放")

            try:
                self.current_process.terminate()
                await asyncio.wait_for(self.current_process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                self.current_process.kill()
                await self.current_process.wait()

            self.is_playing = False
            self.current_process = None

        # 清空队列
        while not self.play_queue.empty():
            try:
                self.play_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        self.logger.info("✅ 播放已打断，队列已清空")

    async def start(self):
        """启动播放器"""
        if self.is_running:
            return

        self.is_running = True
        self.logger.info("🔊 音频播放器已启动")

        # 设置音频设备参数（并行优化：提前设置）
        import subprocess as sp
        try:
            sp.run(['amixer', 'set', 'Deviceid', '2'], check=False, capture_output=True)
            sp.run(['amixer', 'set', 'Playback', '10'], check=False, capture_output=True)
            self.logger.debug("✅ 音频设备参数已设置")
        except Exception as e:
            self.logger.warning(f"⚠️  设置音频参数失败: {e}")

        # 启动播放工作线程
        asyncio.create_task(self._play_worker())

    async def stop(self):
        """停止播放器"""
        if not self.is_running:
            return

        self.logger.info("🛑 停止播放器...")

        # 打断当前播放
        await self.interrupt()

        # 停止工作线程
        self.is_running = False

        self.logger.info("✅ 播放器已停止")

    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.play_queue.qsize()

    def get_stats(self) -> dict:
        """
        获取统计信息

        返回:
            统计信息字典
        """
        return {
            "is_playing": self.is_playing,
            "is_running": self.is_running,
            "queue_size": self.play_queue.qsize()
        }
