#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时语音助手主控制器
功能：异步编排所有模块，管理整个对话流程
作者：哈雷酱（傲娇大小姐工程师）
"""

import asyncio
import logging
from typing import Optional
import signal

from .vad_detector import VADDetector
from .audio_capture import AudioCapture
from .asr_engine import ASREngine
from .llm_engine import LLMEngine
from .tts_engine import TTSEngine
from .audio_player import AudioPlayer
from .state_machine import StateMachine, AssistantState
from .utils import PerformanceMonitor


class RealtimeVoiceAssistant:
    """实时语音助手主控制器"""

    def __init__(self, config: dict):
        """
        初始化实时语音助手

        参数:
            config: 配置字典
        """
        self.logger = logging.getLogger("realtime_assistant")
        self.config = config

        # 初始化各个模块
        self.logger.info("=" * 60)
        self.logger.info("🎙️  初始化实时语音助手...")
        self.logger.info("=" * 60)

        # VAD 检测器
        if config["vad"]["enabled"]:
            from .utils import load_config
            vad_config = load_config(config["vad"]["config_file"])
            self.vad = VADDetector(vad_config)
        else:
            self.vad = None

        # 音频捕获器
        self.audio_capture = AudioCapture(config["audio"])

        # ASR 引擎
        self.asr = ASREngine(config["asr"])

        # LLM 引擎
        self.llm = LLMEngine(config["llm"])

        # TTS 引擎
        self.tts = TTSEngine(config["tts"])

        # 音频播放器
        self.player = AudioPlayer()

        # 状态机
        self.state_machine = StateMachine()

        # 性能监控器
        self.monitor = PerformanceMonitor(self.logger)

        # 处理队列
        self.processing_queue = asyncio.Queue()

        # 运行状态
        self.is_running = False

        # 统计信息
        self.stats = {
            "total_segments": 0,
            "total_conversations": 0,
            "total_errors": 0
        }

        self.logger.info("=" * 60)
        self.logger.info("✅ 实时语音助手初始化完成")
        self.logger.info("=" * 60)

    async def _warmup_connections(self):
        """预热连接（并行优化）"""
        self.logger.info("🔥 预热连接中...")
        try:
            # 预热 LLM 连接
            await self.llm.warmup()
            self.logger.debug("✅ LLM 连接预热完成")
        except Exception as e:
            self.logger.warning(f"⚠️  连接预热失败: {e}")

    async def start(self):
        """启动语音助手"""
        if self.is_running:
            self.logger.warning("⚠️  语音助手已在运行")
            return

        self.is_running = True
        self.logger.info("\n🚀 启动实时语音助手...\n")

        # 预热连接（并行优化）
        await self._warmup_connections()

        # 启动音频捕获
        self.audio_capture.start()

        # 启动音频播放器
        await self.player.start()

        # 状态转换到监听
        self.state_machine.transition(AssistantState.LISTENING)

        # 启动各个异步任务
        tasks = [
            asyncio.create_task(self._vad_detection_loop(), name="vad_loop"),
            asyncio.create_task(self._processing_loop(), name="processing_loop"),
        ]

        self.logger.info("🎤 开始监听... (按 Ctrl+C 停止)\n")

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self.logger.info("\n⏹️  任务已取消")

    async def stop(self):
        """停止语音助手"""
        if not self.is_running:
            return

        self.logger.info("\n🛑 停止实时语音助手...")

        self.is_running = False

        # 停止音频捕获
        self.audio_capture.stop()

        # 停止音频播放器
        await self.player.stop()

        # 关闭 LLM 会话
        await self.llm.close()

        # 状态转换到空闲
        self.state_machine.transition(AssistantState.IDLE)

        # 输出统计信息
        self._print_stats()

        self.logger.info("✅ 实时语音助手已停止")

    async def _vad_detection_loop(self):
        """VAD 检测循环（优化版：边说边识别）"""
        self.logger.info("🎧 VAD 检测循环已启动")

        speech_buffer = []
        is_speaking = False
        silence_duration = 0
        last_recognition_time = 0
        speech_start_time = 0

        while self.is_running:
            try:
                # 读取音频数据
                audio_data = await self.audio_capture.read_async()
                if audio_data is None:
                    await asyncio.sleep(0.01)
                    continue

                # 接受音频数据
                if self.vad:
                    self.vad.accept_waveform(audio_data)

                    # 检查是否有语音活动
                    if self.vad.is_speech_detected():
                        if not is_speaking:
                            # 开始说话
                            is_speaking = True
                            speech_buffer = []
                            speech_start_time = asyncio.get_event_loop().time()
                            last_recognition_time = speech_start_time
                            self.logger.info("\n🎤 开始说话...")

                        # 累积语音数据
                        speech_buffer.append(audio_data)
                        silence_duration = 0

                        # 边说边识别：每累积 1 秒音频就开始一次识别
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_recognition_time >= 1.0 and len(speech_buffer) > 0:
                            # 提前识别（不等待完整片段）
                            segment = np.concatenate(speech_buffer)
                            duration = len(segment) / self.vad.sample_rate

                            self.logger.debug(f"⚡ 提前识别（累积 {duration:.1f}s）")

                            # 异步处理（不阻塞录音）
                            asyncio.create_task(self._process_partial_segment(segment.copy()))

                            last_recognition_time = current_time
                    else:
                        # 静音
                        if is_speaking:
                            silence_duration += len(audio_data) / self.vad.sample_rate

                            # 静音超过阈值，结束说话
                            if silence_duration > 0.5:
                                is_speaking = False

                                # 最终识别
                                if len(speech_buffer) > 0:
                                    segment = np.concatenate(speech_buffer)
                                    duration = len(segment) / self.vad.sample_rate

                                    self.stats["total_segments"] += 1
                                    self.logger.info(f"🛑 说话结束（时长: {duration:.2f}s）")

                                    # 放入处理队列（最终识别）
                                    await self.processing_queue.put(segment)

                                speech_buffer = []
                                silence_duration = 0

            except Exception as e:
                self.logger.error(f"❌ VAD 检测错误: {e}")
                self.stats["total_errors"] += 1

        self.logger.info("🛑 VAD 检测循环已停止")

    async def _process_partial_segment(self, segment):
        """
        处理部分语音片段（提前识别）

        参数:
            segment: 部分语音片段数组
        """
        try:
            # 只做识别，不做后续处理
            text = await self.asr.transcribe_async(segment)

            if text:
                self.logger.debug(f"⚡ 部分识别: {text}")
                # 可以在这里显示给用户，但不触发 LLM

        except Exception as e:
            self.logger.debug(f"⚠️  部分识别失败: {e}")

    async def _processing_loop(self):
        """主处理循环"""
        self.logger.info("⚙️  主处理循环已启动")

        while self.is_running:
            try:
                # 获取语音片段
                segment = await asyncio.wait_for(
                    self.processing_queue.get(),
                    timeout=0.5
                )

                # 处理语音片段
                await self._process_segment(segment)

            except asyncio.TimeoutError:
                # 队列为空，继续等待
                continue
            except Exception as e:
                self.logger.error(f"❌ 处理错误: {e}")
                self.stats["total_errors"] += 1

        self.logger.info("🛑 主处理循环已停止")

    async def _process_segment(self, segment):
        """
        处理语音片段

        参数:
            segment: 语音片段数组
        """
        self.state_machine.transition(AssistantState.PROCESSING)
        self.stats["total_conversations"] += 1

        try:
            # 1. ASR 识别
            self.logger.info("🎯 步骤 1/3: 语音识别...")
            self.monitor.start_timer("asr")

            user_text = await self.asr.transcribe_async(segment)

            asr_time = self.monitor.stop_timer("asr")

            if not user_text:
                self.logger.warning("⚠️  识别结果为空，跳过处理")
                self.state_machine.transition(AssistantState.LISTENING)
                return

            self.logger.info(f"👤 用户: {user_text}")

            # 2. LLM 对话（流式处理）
            self.logger.info("🎯 步骤 2/3: 生成回复（流式）...")
            self.monitor.start_timer("llm")

            # 使用流式 API
            full_response = ""
            sentence_buffer = ""
            word_count = 0  # 字数计数器

            async for chunk in self.llm.chat_stream_async(user_text, use_history=False):
                full_response += chunk
                sentence_buffer += chunk
                word_count += len(chunk)

                # 更激进的分割策略：
                # 1. 遇到句子结束符立即分割
                # 2. 或者累积超过 8 个字也分割（更早开始 TTS）
                should_split = (
                    any(punct in sentence_buffer for punct in ['。', '！', '？', '.', '!', '?']) or
                    word_count >= 8
                )

                if should_split:
                    # 找到句子，立即开始 TTS
                    sentences = self._extract_sentences(sentence_buffer)
                    for sentence in sentences[:-1]:  # 处理完整的句子
                        if sentence.strip():
                            # 并行处理：边生成边合成
                            asyncio.create_task(self._synthesize_and_play(sentence))

                    # 保留未完成的句子
                    sentence_buffer = sentences[-1] if sentences else ""
                    word_count = len(sentence_buffer)

            llm_time = self.monitor.stop_timer("llm")

            # 处理剩余的文本
            if sentence_buffer.strip():
                await self._synthesize_and_play(sentence_buffer)

            self.logger.info(f"🤖 助手: {full_response}")

            # 输出性能统计
            self.logger.info(f"\n📊 性能统计:")
            self.logger.info(f"   - ASR: {asr_time:.2f}s")
            self.logger.info(f"   - LLM (流式): {llm_time:.2f}s")
            self.logger.info(f"   - 总计: {asr_time + llm_time:.2f}s\n")

            # 状态转换回监听
            self.state_machine.transition(AssistantState.LISTENING)

        except Exception as e:
            self.logger.error(f"❌ 处理异常: {e}")
            self.stats["total_errors"] += 1
            self.state_machine.transition(AssistantState.ERROR)
            await asyncio.sleep(1)
            self.state_machine.transition(AssistantState.LISTENING)

    def _extract_sentences(self, text: str) -> list:
        """
        提取句子

        参数:
            text: 文本

        返回:
            句子列表
        """
        import re
        sentences = re.split(r'([。！？\.!?]+)', text)

        result = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else '')
            if sentence.strip():
                result.append(sentence)

        # 最后一个片段（可能不完整）
        if len(sentences) % 2 == 1:
            result.append(sentences[-1])

        return result if result else [text]

    async def _synthesize_and_play(self, text: str):
        """
        合成并播放（流式处理辅助函数）

        参数:
            text: 文本
        """
        try:
            # TTS 合成
            audio_file = await self.tts.synthesize_async(text)

            # 播放
            self.state_machine.transition(AssistantState.SPEAKING)
            await self.player.play_async(audio_file)

            # 等待播放完成
            while self.player.is_playing:
                await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"❌ 合成播放失败: {e}")

    def _print_stats(self):
        """输出统计信息"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 会话统计:")
        self.logger.info(f"   - 检测到的语音片段: {self.stats['total_segments']}")
        self.logger.info(f"   - 完成的对话轮次: {self.stats['total_conversations']}")
        self.logger.info(f"   - 发生的错误次数: {self.stats['total_errors']}")
        self.logger.info("=" * 60)

    def get_stats(self) -> dict:
        """
        获取统计信息

        返回:
            统计信息字典
        """
        return {
            **self.stats,
            "state": self.state_machine.get_state().value,
            "vad": self.vad.get_stats() if self.vad else None,
            "asr": self.asr.get_stats(),
            "llm": self.llm.get_stats(),
            "tts": self.tts.get_stats(),
            "player": self.player.get_stats(),
        }
