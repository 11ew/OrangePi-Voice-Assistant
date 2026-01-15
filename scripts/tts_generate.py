#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge-TTS 文字转语音脚本（双语支持版）
作者: 哈雷酱（傲娇大小姐工程师）
功能: 将文本转换为单声道 WAV 音频文件，支持中英文自动检测
"""

import asyncio
import edge_tts
import sys
import os
import re
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from language_detector import detect_language, get_language_name

# 默认配置
DEFAULT_VOICE_ZH = "zh-CN-XiaoxiaoNeural"  # 中文女声（晓晓）
DEFAULT_VOICE_EN = "en-US-JennyNeural"     # 英文女声（Jenny）
DEFAULT_RATE = "+0%"  # 语速（-50% 到 +50%）
DEFAULT_VOLUME = "+0%"  # 音量（-50% 到 +50%）
DEFAULT_PITCH = "+0Hz"  # 音调

# 可用的中文语音列表
CHINESE_VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",  # 女声-晓晓（温柔）
    "xiaoyi": "zh-CN-XiaoyiNeural",      # 女声-晓伊（活泼）
    "yunjian": "zh-CN-YunjianNeural",    # 男声-云健（沉稳）
    "yunxi": "zh-CN-YunxiNeural",        # 男声-云希（年轻）
    "xiaoxuan": "zh-CN-XiaoxuanNeural",  # 女声-晓萱（甜美）
    "yunyang": "zh-CN-YunyangNeural",    # 男声-云扬（热情）
}

# 可用的英文语音列表
ENGLISH_VOICES = {
    "jenny": "en-US-JennyNeural",        # 女声-Jenny（友好）
    "aria": "en-US-AriaNeural",          # 女声-Aria（自然）
    "guy": "en-US-GuyNeural",            # 男声-Guy（专业）
    "davis": "en-US-DavisNeural",        # 男声-Davis（沉稳）
    "jane": "en-US-JaneNeural",          # 女声-Jane（温柔）
    "jason": "en-US-JasonNeural",        # 男声-Jason（活力）
}


async def text_to_speech(text, output_file, voice=None,
                         rate=DEFAULT_RATE, volume=DEFAULT_VOLUME,
                         pitch=DEFAULT_PITCH, auto_detect=True):
    """
    将文本转换为语音文件

    参数:
        text: 要转换的文本
        output_file: 输出文件路径
        voice: 语音类型（默认使用中文语音，可读中英文混合）
        rate: 语速
        volume: 音量
        pitch: 音调
        auto_detect: 保留参数（向后兼容）
    """
    # 使用默认中文语音（可以读中英文混合内容）
    if voice is None:
        voice = DEFAULT_VOICE_ZH

    print(f"🎤 开始生成语音～", file=sys.stderr)
    print(f"📝 文本内容: {text}", file=sys.stderr)
    print(f"🔊 使用语音: {voice}", file=sys.stderr)
    print(f"⚡ 语速: {rate}, 音量: {volume}, 音调: {pitch}", file=sys.stderr)

    # 创建 TTS 对象
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)

    # 生成音频文件
    await communicate.save(output_file)

    print(f"✅ 语音文件已生成: {output_file}", file=sys.stderr)

    # 显示文件信息
    file_size = os.path.getsize(output_file)
    print(f"📦 文件大小: {file_size / 1024:.2f} KB", file=sys.stderr)


async def convert_to_mono_wav(input_file, output_file):
    """
    将音频转换为单声道 WAV 格式（适配 3.5mm 接口）

    注意: 需要系统安装 ffmpeg
    """
    print(f"\n🔄 转换为单声道 WAV 格式～", file=sys.stderr)

    # 使用 ffmpeg 转换
    # -ac 1: 单声道
    # -ar 48000: 采样率 48kHz（硬件层面）
    # -b:a 128k: 比特率 128kbps
    # -sample_fmt s16: 16-bit PCM
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-ac", "1",           # 单声道
        "-ar", "48000",       # 48kHz 采样率（硬件层面）
        "-b:a", "128k",       # 128kbps 比特率
        "-sample_fmt", "s16", # 16-bit
        "-f", "wav",          # WAV 格式
        output_file
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"✅ 转换成功: {output_file}", file=sys.stderr)
        file_size = os.path.getsize(output_file)
        print(f"📦 文件大小: {file_size / 1024:.2f} KB", file=sys.stderr)
    else:
        print(f"❌ 转换失败: {stderr.decode()}", file=sys.stderr)
        sys.exit(1)


async def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("❌ 用法错误～", file=sys.stderr)
        print(f"用法: {sys.argv[0]} <文本内容> [输出文件] [语音类型] [语速] [音量] [音调]", file=sys.stderr)
        print(f"\n可用中文语音:", file=sys.stderr)
        for key, value in CHINESE_VOICES.items():
            print(f"  {key}: {value}", file=sys.stderr)
        print(f"\n可用英文语音:", file=sys.stderr)
        for key, value in ENGLISH_VOICES.items():
            print(f"  {key}: {value}", file=sys.stderr)
        print(f"\n参数说明:", file=sys.stderr)
        print(f"  语音类型: 留空则自动检测语言", file=sys.stderr)
        print(f"  语速: -50% 到 +50% (如: +25%)", file=sys.stderr)
        print(f"  音量: -50% 到 +50% (如: +10%)", file=sys.stderr)
        print(f"  音调: -100Hz 到 +100Hz (如: +50Hz)", file=sys.stderr)
        print(f"\n示例:", file=sys.stderr)
        print(f"  {sys.argv[0]} '你好，世界' output.wav", file=sys.stderr)
        print(f"  {sys.argv[0]} 'Hello, world' output.wav", file=sys.stderr)
        print(f"  {sys.argv[0]} '你好，世界' output.wav xiaoxiao +25% +10% +50Hz", file=sys.stderr)
        sys.exit(1)

    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/tts_output.wav"
    voice_key = sys.argv[3] if len(sys.argv) > 3 else None
    rate = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_RATE
    volume = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_VOLUME
    pitch = sys.argv[6] if len(sys.argv) > 6 else DEFAULT_PITCH

    # 获取语音类型
    voice = None
    if voice_key:
        # 先在中文语音中查找
        voice = CHINESE_VOICES.get(voice_key)
        # 如果没找到，再在英文语音中查找
        if not voice:
            voice = ENGLISH_VOICES.get(voice_key)
        # 如果还是没找到，直接使用输入的值（可能是完整的语音ID）
        if not voice:
            voice = voice_key

    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 生成临时 MP3 文件
    temp_file = output_file.replace(".wav", "_temp.mp3")

    try:
        # 第一步: 生成 MP3（自动检测语言）
        await text_to_speech(text, temp_file, voice, rate, volume, pitch, auto_detect=(voice is None))

        # 第二步: 转换为单声道 WAV
        await convert_to_mono_wav(temp_file, output_file)

        # 删除临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"🗑️  已删除临时文件: {temp_file}", file=sys.stderr)

        print(f"\n🎉 全部完成～可以播放啦！", file=sys.stderr)

    except Exception as e:
        print(f"❌ 发生错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
