#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR 识别测试脚本
功能：录音 5 秒，然后进行语音识别
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import os
import time
import subprocess
import numpy as np
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 延迟导入项目模块
from realtime_assistant.asr_engine import ASREngine
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_asr")


def record_audio(duration: int = 5) -> np.ndarray:
    """
    录音指定时长

    参数:
        duration: 录音时长（秒）

    返回:
        音频数据数组（16000 Hz, float32）
    """
    logger.info("=" * 60)
    logger.info(f"🎤 开始录音（{duration} 秒）")
    logger.info("=" * 60)

    # 设置音频参数
    logger.info("📋 设置音频参数...")
    subprocess.run(['amixer', 'set', 'Capture', '10'],
                   check=False, capture_output=True)
    subprocess.run(['amixer', 'set', 'Deviceid', '2'],
                   check=False, capture_output=True)
    logger.info("✅ 音频参数设置完成")

    # 倒计时
    logger.info("")
    logger.info("⚠️  请对着麦克风清晰地说话...")
    logger.info(f"   （录音将在 3 秒后开始）")
    logger.info("")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    logger.info("")
    logger.info(f"🔴 开始录音！（{duration} 秒）")
    logger.info("")

    # 临时文件
    pcm_file = "test_asr_temp.pcm"

    # 录音（48000 Hz RAW 格式）
    cmd = [
        'arecord',
        '-D', 'plughw:0,1',
        '-f', 'S16_LE',
        '-r', '48000',
        '-c', '1',
        '-t', 'raw',
        '-d', str(duration),
        pcm_file
    ]

    subprocess.run(cmd, check=True)

    logger.info("")
    logger.info("✅ 录音完成！")
    logger.info("")

    # 读取 PCM 数据
    with open(pcm_file, 'rb') as f:
        audio_bytes = f.read()

    # 转换为 numpy 数组
    audio_data = np.frombuffer(audio_bytes, dtype=np.int16)

    # 转换为 float32，范围 [-1.0, 1.0]
    audio_data = audio_data.astype(np.float32) / 32768.0

    # 降采样：48000 Hz -> 16000 Hz（每 3 个样本取 1 个）
    audio_data = audio_data[::3]

    # 删除临时文件
    os.remove(pcm_file)

    logger.info(f"📊 音频信息:")
    logger.info(f"   - 原始采样率: 48000 Hz")
    logger.info(f"   - 目标采样率: 16000 Hz")
    logger.info(f"   - 样本数: {len(audio_data)}")
    logger.info(f"   - 时长: {len(audio_data) / 16000:.2f} 秒")
    logger.info(f"   - 最大值: {np.max(np.abs(audio_data)):.4f}")
    logger.info(f"   - 平均值: {np.mean(np.abs(audio_data)):.4f}")
    logger.info("")

    return audio_data


def test_asr():
    """测试 ASR 识别"""
    logger.info("=" * 60)
    logger.info("🎯 ASR 识别测试")
    logger.info("=" * 60)
    logger.info("")

    # 加载 ASR 配置
    config_file = project_root / "config" / "asr_config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        asr_config = json.load(f)

    # 创建 ASR 引擎
    logger.info("📦 初始化 ASR 引擎...")
    asr_engine = ASREngine({"config_file": "config/asr_config.json"})
    logger.info("")

    # 录音
    audio_data = record_audio(duration=5)

    # 识别
    logger.info("=" * 60)
    logger.info("🎯 开始语音识别...")
    logger.info("=" * 60)
    logger.info("")

    start_time = time.time()
    text = asr_engine.transcribe(audio_data)
    elapsed = time.time() - start_time

    logger.info("")
    logger.info("=" * 60)
    logger.info("📝 识别结果")
    logger.info("=" * 60)
    logger.info("")

    if text:
        logger.info(f"✅ 识别成功！")
        logger.info(f"   文本: {text}")
        logger.info(f"   耗时: {elapsed:.2f} 秒")
    else:
        logger.info(f"❌ 识别失败（结果为空）")
        logger.info(f"   耗时: {elapsed:.2f} 秒")

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ 测试完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        test_asr()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⚠️  用户中断")
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
