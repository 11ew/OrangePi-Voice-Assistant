#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge-TTS 文字转语音脚本
作者: 幽浮喵 (猫娘工程师)
功能: 将文本转换为单声道 WAV 音频文件，适配 3.5mm 接口播放
"""

import asyncio
import edge_tts
import sys
import os
from pathlib import Path

# 默认配置
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"  # 中文女声（晓晓）
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


async def text_to_speech(text, output_file, voice=DEFAULT_VOICE,
                         rate=DEFAULT_RATE, volume=DEFAULT_VOLUME,
                         pitch=DEFAULT_PITCH):
    """
    将文本转换为语音文件

    参数:
        text: 要转换的文本
        output_file: 输出文件路径
        voice: 语音类型
        rate: 语速
        volume: 音量
        pitch: 音调
    """
    print(f"🎤 开始生成语音喵～")
    print(f"📝 文本内容: {text}")
    print(f"🔊 使用语音: {voice}")
    print(f"⚡ 语速: {rate}, 音量: {volume}, 音调: {pitch}")

    # 创建 TTS 对象
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)

    # 生成音频文件
    await communicate.save(output_file)

    print(f"✅ 语音文件已生成: {output_file}")

    # 显示文件信息
    file_size = os.path.getsize(output_file)
    print(f"📦 文件大小: {file_size / 1024:.2f} KB")


async def convert_to_mono_wav(input_file, output_file):
    """
    将音频转换为单声道 WAV 格式（适配 3.5mm 接口）

    注意: 需要系统安装 ffmpeg
    """
    print(f"\n🔄 转换为单声道 WAV 格式喵～")

    # 使用 ffmpeg 转换
    # -ac 1: 单声道
    # -ar 48000: 采样率 48kHz
    # -sample_fmt s16: 16-bit PCM
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-ac", "1",           # 单声道
        "-ar", "48000",       # 48kHz 采样率
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
        print(f"✅ 转换成功: {output_file}")
        file_size = os.path.getsize(output_file)
        print(f"📦 文件大小: {file_size / 1024:.2f} KB")
    else:
        print(f"❌ 转换失败: {stderr.decode()}")
        sys.exit(1)


async def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("❌ 用法错误喵～")
        print(f"用法: {sys.argv[0]} <文本内容> [输出文件] [语音类型] [语速] [音量] [音调]")
        print(f"\n可用语音类型:")
        for key, value in CHINESE_VOICES.items():
            print(f"  {key}: {value}")
        print(f"\n参数说明:")
        print(f"  语速: -50% 到 +50% (如: +25%)")
        print(f"  音量: -50% 到 +50% (如: +10%)")
        print(f"  音调: -100Hz 到 +100Hz (如: +50Hz)")
        print(f"\n示例:")
        print(f"  {sys.argv[0]} '你好，世界' output.wav xiaoxiao")
        print(f"  {sys.argv[0]} '你好，世界' output.wav xiaoxiao +25% +10% +50Hz")
        sys.exit(1)

    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/tts_output.wav"
    voice_key = sys.argv[3] if len(sys.argv) > 3 else "xiaoxiao"
    rate = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_RATE
    volume = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_VOLUME
    pitch = sys.argv[6] if len(sys.argv) > 6 else DEFAULT_PITCH

    # 获取语音类型
    voice = CHINESE_VOICES.get(voice_key, DEFAULT_VOICE)

    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 生成临时 MP3 文件
    temp_file = output_file.replace(".wav", "_temp.mp3")

    try:
        # 第一步: 生成 MP3
        await text_to_speech(text, temp_file, voice, rate, volume, pitch)

        # 第二步: 转换为单声道 WAV
        await convert_to_mono_wav(temp_file, output_file)

        # 删除临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"🗑️  已删除临时文件: {temp_file}")

        print(f"\n🎉 全部完成喵～可以播放啦！")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
