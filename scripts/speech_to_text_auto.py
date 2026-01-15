#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动语言检测的语音识别脚本（Whisper 自动检测版）
功能：使用 Whisper 的自动语言检测功能进行识别
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import os
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from speech_to_text import load_config, transcribe_audio


def transcribe_with_auto_language_detection(audio_file, config_file="config/asr_config.json"):
    """
    使用 Whisper 自动语言检测进行语音识别

    策略：
    1. 设置 language 为空字符串
    2. Whisper 自动检测语言并识别
    3. 返回识别结果

    参数:
        audio_file: 音频文件路径
        config_file: 配置文件路径

    返回:
        识别结果
    """
    # 加载配置
    config = load_config(config_file)

    print(f"🔄 启用 Whisper 自动语言检测...", file=sys.stderr)
    print("")

    # 设置为空字符串，让 Whisper 自动检测语言
    config["language"] = ""

    # 使用 Whisper 自动检测并识别
    print(f"📝 使用 Whisper 自动检测语言并识别...", file=sys.stderr)
    result = transcribe_audio(audio_file, config)
    print(f"   识别结果: {result}", file=sys.stderr)
    print("")

    print(f"✅ 最终结果: {result}", file=sys.stderr)
    print("")

    return result


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 speech_to_text_auto.py <音频文件>", file=sys.stderr)
        print("示例: python3 speech_to_text_auto.py output/recordings/test.wav", file=sys.stderr)
        sys.exit(1)

    audio_file = sys.argv[1]

    # 检查文件是否存在
    if not Path(audio_file).exists():
        print(f"❌ 错误: 音频文件不存在: {audio_file}", file=sys.stderr)
        sys.exit(1)

    # Whisper 自动语言检测识别
    result = transcribe_with_auto_language_detection(audio_file)

    if result:
        # 输出结果（只输出纯文本，方便后续处理）
        print(result)
        sys.exit(0)
    else:
        print("识别失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
