#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS 引擎模块
功能：封装 Edge-TTS，提供异步语音合成接口
作者：哈雷酱（傲娇大小姐工程师）
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict
import time

try:
    import edge_tts
except ImportError:
    raise ImportError("未安装 edge-tts，请运行: pip install edge-tts")


class TTSEngine:
    """TTS 语音合成引擎"""

    def __init__(self, config: dict):
        """
        初始化 TTS 引擎

        参数:
            config: TTS 配置字典
        """
        self.logger = logging.getLogger("realtime_assistant.tts")
        self.config = config

        self.voice_zh = config.get("voice_zh", "zh-CN-XiaoxiaoNeural")
        self.voice_en = config.get("voice_en", "en-US-JennyNeural")
        self.rate = config.get("rate", "+0%")
        self.volume = config.get("volume", "+0%")
        self.pitch = config.get("pitch", "+0Hz")
        self.cache_enabled = config.get("cache_enabled", True)

        # 缓存
        self.cache: Dict[str, str] = {}

        # 输出目录
        self.output_dir = Path("output/tts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ TTS 引擎初始化完成")
        self.logger.info(f"   - 中文语音: {self.voice_zh}")
        self.logger.info(f"   - 英文语音: {self.voice_en}")
        self.logger.info(f"   - 缓存: {'启用' if self.cache_enabled else '禁用'}")

    def _detect_language(self, text: str) -> str:
        """
        检测文本语言

        参数:
            text: 文本

        返回:
            语言代码 ('zh' 或 'en')
        """
        # 简单的语言检测：统计中文字符比例
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len(text)

        if total_chars == 0:
            return 'zh'

        chinese_ratio = chinese_chars / total_chars

        # 如果中文字符超过 30%，认为是中文
        return 'zh' if chinese_ratio > 0.3 else 'en'

    def _get_voice(self, text: str) -> str:
        """
        根据文本获取语音

        参数:
            text: 文本

        返回:
            语音名称
        """
        language = self._detect_language(text)
        return self.voice_zh if language == 'zh' else self.voice_en

    async def synthesize_async(self, text: str, output_file: Optional[str] = None) -> str:
        """
        异步合成语音

        参数:
            text: 要合成的文本
            output_file: 输出文件路径（可选）

        返回:
            输出文件路径
        """
        # 检查缓存
        cache_key = f"{text}_{self._get_voice(text)}"
        if self.cache_enabled and cache_key in self.cache:
            cached_file = self.cache[cache_key]
            if Path(cached_file).exists():
                self.logger.info(f"📦 使用缓存: {cached_file}")
                return cached_file

        # 生成输出文件名
        if output_file is None:
            timestamp = int(time.time() * 1000)
            output_file = str(self.output_dir / f"tts_{timestamp}.mp3")

        # 选择语音
        voice = self._get_voice(text)

        self.logger.info(f"🎵 合成语音: {text[:30]}...")
        self.logger.info(f"   - 语音: {voice}")

        # 调用 Edge-TTS
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch
        )

        await communicate.save(output_file)

        # 转换为单声道 WAV（可选）
        wav_file = output_file.replace('.mp3', '.wav')
        await self._convert_to_wav(output_file, wav_file)

        # 更新缓存
        if self.cache_enabled:
            self.cache[cache_key] = wav_file

        self.logger.info(f"✅ 语音合成完成: {wav_file}")
        return wav_file

    async def _convert_to_wav(self, input_file: str, output_file: str):
        """
        转换为单声道 WAV

        参数:
            input_file: 输入文件（MP3）
            output_file: 输出文件（WAV）
        """
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ar", "48000",      # 采样率 48kHz（Orange Pi 硬件原生采样率）
            "-ac", "1",          # 单声道
            "-y",                # 覆盖输出文件
            output_file
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            self.logger.error(f"❌ 音频转换失败: {stderr.decode()}")
        else:
            self.logger.debug(f"✅ 音频转换完成: {output_file}")

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.logger.info("🗑️  TTS 缓存已清空")

    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)

    def get_stats(self) -> dict:
        """
        获取统计信息

        返回:
            统计信息字典
        """
        return {
            "voice_zh": self.voice_zh,
            "voice_en": self.voice_en,
            "cache_enabled": self.cache_enabled,
            "cache_size": len(self.cache)
        }
