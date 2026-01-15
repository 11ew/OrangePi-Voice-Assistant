#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sherpa-ONNX 语音识别模块
功能：使用 Sherpa-ONNX 进行本地语音识别
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import os
import json
from pathlib import Path

try:
    import sherpa_onnx
except ImportError:
    print("❌ 错误: 未安装 sherpa-onnx", file=sys.stderr)
    print("请运行: bash scripts/setup_sherpa_onnx.sh", file=sys.stderr)
    sys.exit(1)


def load_config(config_file="config/asr_config.json"):
    """
    加载配置文件

    参数:
        config_file: 配置文件路径

    返回:
        配置字典
    """
    config_path = Path(__file__).parent.parent / config_file

    if not config_path.exists():
        print(f"⚠️  配置文件不存在: {config_path}", file=sys.stderr)
        print("使用默认配置", file=sys.stderr)
        return {
            "provider": "sherpa-onnx",
            "model_dir": "models/sherpa-onnx-whisper-tiny.en",
            "language": "zh",
            "num_threads": 4,
            "decoding_method": "greedy_search"
        }

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_recognizer(config):
    """
    创建 Sherpa-ONNX 识别器

    参数:
        config: 配置字典

    返回:
        识别器对象
    """
    model_dir = Path(__file__).parent.parent / config["model_dir"]

    if not model_dir.exists():
        print(f"❌ 错误: 模型目录不存在: {model_dir}", file=sys.stderr)
        print("请运行: bash scripts/setup_sherpa_onnx.sh", file=sys.stderr)
        sys.exit(1)

    print(f"📦 加载模型: {model_dir}", file=sys.stderr)

    # 根据模型目录确定文件名前缀
    if "tiny.en" in str(model_dir):
        # 英文专用模型
        encoder_file = "tiny.en-encoder.onnx"
        decoder_file = "tiny.en-decoder.onnx"
        tokens_file = "tiny.en-tokens.txt"
        language = "en"  # 英文模型强制使用英文
    elif "base" in str(model_dir):
        # Base 多语言模型（使用 int8 量化版本，速度更快）
        encoder_file = "base-encoder.int8.onnx"
        decoder_file = "base-decoder.int8.onnx"
        tokens_file = "base-tokens.txt"
        # 使用空字符串让 Whisper 自动检测语言
        language = config.get("language", "")  # 空字符串表示自动检测
    else:
        # Tiny 多语言模型（默认）
        encoder_file = "tiny-encoder.onnx"
        decoder_file = "tiny-decoder.onnx"
        tokens_file = "tiny-tokens.txt"
        # 使用空字符串让 Whisper 自动检测语言
        language = config.get("language", "")  # 空字符串表示自动检测

    if language:
        print(f"🌐 识别语言: {language}", file=sys.stderr)
    else:
        print(f"🌐 识别语言: 自动检测", file=sys.stderr)

    # 使用 from_whisper 类方法创建识别器
    recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=str(model_dir / encoder_file),
        decoder=str(model_dir / decoder_file),
        tokens=str(model_dir / tokens_file),
        language=language,
        task="transcribe",
        num_threads=config.get("num_threads", 4),
        decoding_method=config.get("decoding_method", "greedy_search"),
        debug=False,
    )

    print(f"✅ 模型加载完成", file=sys.stderr)

    return recognizer


def transcribe_audio(audio_file, config=None):
    """
    识别音频文件

    参数:
        audio_file: 音频文件路径
        config: 配置字典（可选）

    返回:
        识别的文本
    """
    # 加载配置
    if config is None:
        config = load_config()

    # 检查音频文件
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"❌ 错误: 音频文件不存在: {audio_path}", file=sys.stderr)
        return None

    print(f"🎤 开始识别: {audio_path}", file=sys.stderr)

    # 创建识别器
    recognizer = create_recognizer(config)

    # 读取音频
    try:
        import soundfile as sf
        audio_data, sample_rate = sf.read(str(audio_path), dtype='float32')

        # 如果是立体声，转换为单声道
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]

        print(f"📊 音频信息: 采样率={sample_rate}Hz, 时长={len(audio_data)/sample_rate:.2f}秒", file=sys.stderr)

    except Exception as e:
        print(f"❌ 读取音频失败: {e}", file=sys.stderr)
        return None

    # 创建音频流
    stream = recognizer.create_stream()

    # 接受音频数据
    stream.accept_waveform(sample_rate, audio_data)

    # 执行识别
    recognizer.decode_stream(stream)

    # 获取结果
    result = stream.result.text

    if result:
        print(f"✅ 识别结果: {result}", file=sys.stderr)
        return result
    else:
        print(f"⚠️  未识别到语音", file=sys.stderr)
        return ""


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 speech_to_text.py <音频文件>", file=sys.stderr)
        print("示例: python3 speech_to_text.py output/recordings/test.wav", file=sys.stderr)
        sys.exit(1)

    audio_file = sys.argv[1]

    # 识别音频
    result = transcribe_audio(audio_file)

    if result:
        # 输出结果（只输出纯文本，方便后续处理）
        print(result)
        sys.exit(0)
    else:
        print("识别失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
