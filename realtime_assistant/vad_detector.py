#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VAD 检测器模块
功能：使用 Silero VAD 进行语音活动检测，自动分割语音片段
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import os
import numpy as np
import logging
from typing import Optional, Generator
from pathlib import Path

# 延迟导入 sherpa-onnx（避免启动时的导入错误）
sherpa_onnx = None

def _import_sherpa_onnx():
    """延迟导入 sherpa-onnx"""
    global sherpa_onnx
    if sherpa_onnx is not None:
        return sherpa_onnx

    # 添加 sherpa-onnx 到 Python 路径
    sherpa_path = '/home/HwHiAiUser/Desktop/ai-study/EdgeTTSdemo/sherpa-onnx/build/lib.linux-aarch64-cpython-39'
    if os.path.exists(sherpa_path) and sherpa_path not in sys.path:
        sys.path.insert(0, sherpa_path)

    try:
        import sherpa_onnx as _sherpa
        sherpa_onnx = _sherpa
        return sherpa_onnx
    except ImportError as e:
        raise ImportError(f"未安装 sherpa-onnx，请运行: bash scripts/setup_sherpa_onnx.sh\n错误详情: {e}")


class VADDetector:
    """VAD 语音活动检测器"""

    def __init__(self, config: dict):
        """
        初始化 VAD 检测器

        参数:
            config: VAD 配置字典
        """
        # 延迟导入 sherpa-onnx
        _import_sherpa_onnx()

        self.logger = logging.getLogger("realtime_assistant.vad")
        self.config = config

        # 获取项目根目录
        project_root = Path(__file__).parent.parent
        model_path = project_root / config["model"]

        if not model_path.exists():
            raise FileNotFoundError(f"VAD 模型不存在: {model_path}")

        self.logger.info(f"📦 加载 VAD 模型: {model_path}")

        # 创建 VAD 配置
        vad_config = sherpa_onnx.VadModelConfig()
        vad_config.silero_vad.model = str(model_path)
        vad_config.silero_vad.threshold = config.get("threshold", 0.5)
        vad_config.silero_vad.min_silence_duration = config.get("min_silence_duration", 0.5)
        vad_config.silero_vad.min_speech_duration = config.get("min_speech_duration", 0.25)
        vad_config.silero_vad.window_size = config.get("window_size", 512)
        vad_config.sample_rate = config.get("sample_rate", 16000)

        # 创建 VAD 检测器
        self.vad = sherpa_onnx.VoiceActivityDetector(
            vad_config,
            buffer_size_in_seconds=config.get("buffer_size_seconds", 30)
        )

        self.sample_rate = config.get("sample_rate", 16000)
        self.energy_threshold = config.get("energy_threshold", 0.01)

        self.logger.info("✅ VAD 检测器初始化完成")
        self.logger.info(f"   - 阈值: {config.get('threshold', 0.5)}")
        self.logger.info(f"   - 最小静音: {config.get('min_silence_duration', 0.5)}s")
        self.logger.info(f"   - 最小语音: {config.get('min_speech_duration', 0.25)}s")

    def accept_waveform(self, samples: np.ndarray):
        """
        接受音频波形数据

        参数:
            samples: 音频样本数组 (float32, [-1, 1])
        """
        # 确保是 float32 类型
        if samples.dtype != np.float32:
            samples = samples.astype(np.float32)

        # 接受波形
        self.vad.accept_waveform(samples)

    def is_speech_detected(self) -> bool:
        """
        检查是否检测到语音

        返回:
            是否检测到语音
        """
        return not self.vad.empty()

    def get_speech_segment(self) -> Optional[np.ndarray]:
        """
        获取一个语音片段

        返回:
            语音片段数组，如果没有则返回 None
        """
        if self.vad.empty():
            return None

        # 获取语音片段
        segment = self.vad.front
        samples = segment.samples

        # 弹出已处理的片段
        self.vad.pop()

        # 转换为 numpy array（sherpa-onnx 返回的是 list）
        if isinstance(samples, list):
            samples = np.array(samples, dtype=np.float32)
        elif not isinstance(samples, np.ndarray):
            # 如果既不是 list 也不是 ndarray，尝试转换
            samples = np.array(samples, dtype=np.float32)

        # 验证语音片段
        if not self._is_valid_speech(samples):
            self.logger.debug("❌ 语音片段验证失败（能量过低或时长过短）")
            return None

        duration = len(samples) / self.sample_rate
        self.logger.debug(f"✅ 获取语音片段: {duration:.2f}s, {len(samples)} 样本")

        return samples

    def _is_valid_speech(self, samples: np.ndarray) -> bool:
        """
        验证是否为有效语音

        参数:
            samples: 音频样本数组

        返回:
            是否为有效语音
        """
        # 1. 检查时长
        duration = len(samples) / self.sample_rate
        min_duration = self.config.get("min_speech_duration", 0.25)
        if duration < min_duration:
            return False

        # 2. 检查能量
        energy = np.mean(np.abs(samples))
        if energy < self.energy_threshold:
            return False

        return True

    def reset(self):
        """重置 VAD 检测器"""
        # sherpa-onnx 的 VAD 不需要显式重置
        self.logger.debug("🔄 VAD 检测器已重置")

    def get_stats(self) -> dict:
        """
        获取统计信息

        返回:
            统计信息字典
        """
        return {
            "sample_rate": self.sample_rate,
            "threshold": self.config.get("threshold", 0.5),
            "energy_threshold": self.energy_threshold,
            "is_empty": self.vad.empty()
        }


def process_audio_stream(
    vad: VADDetector,
    audio_stream: Generator[np.ndarray, None, None]
) -> Generator[np.ndarray, None, None]:
    """
    处理音频流，生成语音片段

    参数:
        vad: VAD 检测器
        audio_stream: 音频流生成器

    生成:
        语音片段数组
    """
    logger = logging.getLogger("realtime_assistant.vad")

    for audio_chunk in audio_stream:
        # 接受音频块
        vad.accept_waveform(audio_chunk)

        # 检查是否有语音片段
        while vad.is_speech_detected():
            segment = vad.get_speech_segment()
            if segment is not None:
                logger.info(f"🎤 检测到语音片段: {len(segment) / vad.sample_rate:.2f}s")
                yield segment
