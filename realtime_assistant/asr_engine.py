#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR 引擎模块
功能：封装 Sherpa-ONNX 语音识别，提供异步接口
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import os
import asyncio
import logging
import numpy as np
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

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


class ASREngine:
    """ASR 语音识别引擎"""

    def __init__(self, config: dict):
        """
        初始化 ASR 引擎

        参数:
            config: ASR 配置字典
        """
        # 延迟导入 sherpa-onnx
        _import_sherpa_onnx()

        self.logger = logging.getLogger("realtime_assistant.asr")
        self.config = config

        # 加载 ASR 配置
        asr_config_file = config.get("config_file", "config/asr_config.json")
        self.asr_config = self._load_asr_config(asr_config_file)

        # 创建识别器
        self.recognizer = self._create_recognizer()

        # 线程池（用于异步处理 CPU 密集型任务）
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.logger.info("✅ ASR 引擎初始化完成")

    def _load_asr_config(self, config_file: str) -> dict:
        """加载 ASR 配置文件"""
        import json

        project_root = Path(__file__).parent.parent
        config_path = project_root / config_file

        if not config_path.exists():
            raise FileNotFoundError(f"ASR 配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_recognizer(self):
        """创建识别器"""
        project_root = Path(__file__).parent.parent
        model_dir = project_root / self.asr_config["model_dir"]

        if not model_dir.exists():
            raise FileNotFoundError(f"模型目录不存在: {model_dir}")

        self.logger.info(f"📦 加载 ASR 模型: {model_dir}")

        model_type = self.asr_config.get("model_type", "whisper")

        if model_type == "sense-voice" or "sense-voice" in str(model_dir):
            return self._create_sensevoice_recognizer(model_dir)
        elif model_type == "paraformer" or "paraformer" in str(model_dir):
            return self._create_paraformer_recognizer(model_dir)
        else:
            return self._create_whisper_recognizer(model_dir)

    def _create_sensevoice_recognizer(self, model_dir: Path):
        """创建 SenseVoice 识别器"""
        self.logger.info("🎯 使用 SenseVoice 模型")

        model_file = str(model_dir / "model.onnx")
        tokens_file = str(model_dir / "tokens.txt")

        use_npu = self.asr_config.get("use_npu", False)
        provider = "cann" if use_npu else "cpu"

        if use_npu:
            self.logger.info("⚡ 启用 NPU 加速")
        else:
            self.logger.info("💻 使用 CPU 推理")

        recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=model_file,
            tokens=tokens_file,
            num_threads=self.asr_config.get("num_threads", 4),
            provider=provider,
            debug=False,
        )

        self.logger.info("✅ SenseVoice 模型加载完成")
        return recognizer

    def _create_paraformer_recognizer(self, model_dir: Path):
        """创建 Paraformer 流式识别器"""
        self.logger.info("🎯 使用 Paraformer 流式模型")

        # 检查是否使用 INT8 量化模型
        encoder_file = "encoder.int8.onnx" if (model_dir / "encoder.int8.onnx").exists() else "encoder.onnx"
        decoder_file = "decoder.int8.onnx" if (model_dir / "decoder.int8.onnx").exists() else "decoder.onnx"

        if "int8" in encoder_file:
            self.logger.info("⚡ 使用 INT8 量化模型")

        recognizer = sherpa_onnx.OnlineRecognizer.from_paraformer(
            encoder=str(model_dir / encoder_file),
            decoder=str(model_dir / decoder_file),
            tokens=str(model_dir / "tokens.txt"),
            num_threads=self.asr_config.get("num_threads", 4),
            sample_rate=16000,
            feature_dim=80,
            decoding_method=self.asr_config.get("decoding_method", "greedy_search"),
            debug=False,
        )

        self.logger.info("✅ Paraformer 模型加载完成")
        return recognizer

    def _create_whisper_recognizer(self, model_dir: Path):
        """创建 Whisper 识别器"""
        self.logger.info("🎯 使用 Whisper 模型")

        # 根据模型目录确定文件名
        if "tiny.en" in str(model_dir):
            encoder_file = "tiny.en-encoder.onnx"
            decoder_file = "tiny.en-decoder.onnx"
            tokens_file = "tiny.en-tokens.txt"
            language = "en"
        elif "base" in str(model_dir):
            encoder_file = "base-encoder.int8.onnx"
            decoder_file = "base-decoder.int8.onnx"
            tokens_file = "base-tokens.txt"
            language = self.asr_config.get("language", "")
        else:
            encoder_file = "tiny-encoder.onnx"
            decoder_file = "tiny-decoder.onnx"
            tokens_file = "tiny-tokens.txt"
            language = self.asr_config.get("language", "")

        recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=str(model_dir / encoder_file),
            decoder=str(model_dir / decoder_file),
            tokens=str(model_dir / tokens_file),
            language=language,
            task="transcribe",
            num_threads=self.asr_config.get("num_threads", 4),
            decoding_method=self.asr_config.get("decoding_method", "greedy_search"),
            debug=False,
        )

        self.logger.info("✅ Whisper 模型加载完成")
        return recognizer

    def _transcribe_sync(self, audio_data: np.ndarray) -> str:
        """
        同步识别（在线程池中执行）

        参数:
            audio_data: 音频数据数组

        返回:
            识别结果文本
        """
        # 确保是 float32 类型
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # 判断是流式还是离线识别器
        if isinstance(self.recognizer, sherpa_onnx.OnlineRecognizer):
            # 流式识别
            stream = self.recognizer.create_stream()
            stream.accept_waveform(16000, audio_data)

            # 解码
            while self.recognizer.is_ready(stream):
                self.recognizer.decode_stream(stream)

            # get_result() 直接返回字符串
            text = self.recognizer.get_result(stream).strip()
        else:
            # 离线识别
            stream = self.recognizer.create_stream()
            stream.accept_waveform(16000, audio_data)

            self.recognizer.decode_stream(stream)
            result = stream.result
            # result 是对象，有 text 属性
            text = result.text.strip()

        return text

    async def transcribe_async(self, audio_data: np.ndarray) -> str:
        """
        异步识别音频

        参数:
            audio_data: 音频数据数组

        返回:
            识别结果文本
        """
        loop = asyncio.get_event_loop()

        # 在线程池中执行同步识别
        text = await loop.run_in_executor(
            self.executor,
            self._transcribe_sync,
            audio_data
        )

        if text:
            self.logger.info(f"🎤 识别结果: {text}")
        else:
            self.logger.warning("⚠️  识别结果为空")

        return text

    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        同步识别音频

        参数:
            audio_data: 音频数据数组

        返回:
            识别结果文本
        """
        return self._transcribe_sync(audio_data)

    def get_stats(self) -> dict:
        """
        获取统计信息

        返回:
            统计信息字典
        """
        return {
            "model_type": self.asr_config.get("model_type", "whisper"),
            "model_dir": self.asr_config["model_dir"],
            "num_threads": self.asr_config.get("num_threads", 4),
            "use_npu": self.asr_config.get("use_npu", False),
        }

    def __del__(self):
        """析构函数"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
