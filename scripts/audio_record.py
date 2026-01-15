#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
录音模块
功能：封装 arecord 命令，实现简单的录音功能
作者：哈雷酱（傲娇大小姐工程师）
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# 默认录音配置（适配 Whisper 模型）
DEFAULT_DEVICE = "plughw:0,1"  # 香橙派录音设备
DEFAULT_FORMAT = "S16_LE"      # 16-bit PCM
DEFAULT_RATE = 48000           # 48kHz 采样率（硬件层面，Sherpa-ONNX 会自动重采样到 16kHz）
DEFAULT_CHANNELS = 1           # 单声道
DEFAULT_DURATION = 5           # 默认录音时长（秒）


def setup_microphone(volume=10):
    """
    配置麦克风音量

    参数:
        volume: 音量大小 (0-100)
    """
    try:
        # 设置麦克风音量
        subprocess.run(
            ["amixer", "set", "Capture", str(volume)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )

        # 设置设备为耳机（带麦克风）
        subprocess.run(
            ["amixer", "set", "Deviceid", "2"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )

        print(f"✅ 麦克风音量已设置为: {volume}")
    except Exception as e:
        print(f"⚠️  麦克风配置失败: {e}")


def record_audio(output_file=None, duration=DEFAULT_DURATION,
                device=DEFAULT_DEVICE, rate=DEFAULT_RATE,
                channels=DEFAULT_CHANNELS, format_type=DEFAULT_FORMAT):
    """
    录制音频

    参数:
        output_file: 输出文件路径（如果为None，自动生成）
        duration: 录音时长（秒）
        device: 录音设备
        rate: 采样率
        channels: 声道数
        format_type: 音频格式

    返回:
        录音文件路径
    """
    # 如果没有指定输出文件，自动生成
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent / "output" / "recordings"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"recording_{timestamp}.wav"
    else:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎤 开始录音...")
    print(f"📝 录音时长: {duration} 秒")
    print(f"📁 输出文件: {output_file}")

    # 构建 arecord 命令
    cmd = [
        "arecord",
        "-D", device,           # 设备
        "-f", format_type,      # 格式
        "-r", str(rate),        # 采样率
        "-c", str(channels),    # 声道数
        "-t", "wav",            # 文件类型
        "-d", str(duration),    # 时长
        str(output_file)        # 输出文件
    ]

    try:
        # 执行录音命令
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        # 检查文件是否生成
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✅ 录音完成！")
            print(f"📦 文件大小: {file_size / 1024:.2f} KB")
            return str(output_file)
        else:
            print(f"❌ 录音失败：文件未生成")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ 录音失败: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return None


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 audio_record.py <输出文件> [录音时长]")
        print("示例: python3 audio_record.py output/test.wav 5")
        print("\n如果不指定输出文件，将自动生成文件名")
        sys.exit(1)

    # 解析参数
    output_file = sys.argv[1] if sys.argv[1] != "auto" else None
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_DURATION

    # 配置麦克风
    setup_microphone()

    # 录音
    result = record_audio(output_file, duration)

    if result:
        print(f"\n🎉 录音文件已保存: {result}")
        sys.exit(0)
    else:
        print(f"\n❌ 录音失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
