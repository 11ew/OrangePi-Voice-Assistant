#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频播放测试脚本
功能：测试 TTS 生成和播放功能
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import os
import asyncio
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 延迟导入项目模块
from realtime_assistant.tts_engine import TTSEngine
from realtime_assistant.audio_player import AudioPlayer
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_playback")


async def test_playback():
    """测试播放功能"""
    logger.info("=" * 60)
    logger.info("🔊 音频播放测试")
    logger.info("=" * 60)
    logger.info("")

    # 测试文本
    test_text = "你好，我是哈雷酱，这是播放测试"

    # 1. 初始化 TTS 引擎
    logger.info("📦 初始化 TTS 引擎...")
    config_file = project_root / "config" / "realtime_config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    tts_engine = TTSEngine(config.get("tts", {}))
    logger.info("")

    # 2. 生成语音
    logger.info("=" * 60)
    logger.info("🎵 生成语音...")
    logger.info("=" * 60)
    logger.info(f"   文本: {test_text}")
    logger.info("")

    audio_file = await tts_engine.synthesize_async(test_text)

    if not audio_file:
        logger.error("❌ 语音生成失败")
        return

    logger.info(f"✅ 语音生成完成: {audio_file}")
    logger.info("")

    # 3. 检查音频文件
    logger.info("=" * 60)
    logger.info("📊 检查音频文件...")
    logger.info("=" * 60)

    if not Path(audio_file).exists():
        logger.error(f"❌ 音频文件不存在: {audio_file}")
        return

    file_size = Path(audio_file).stat().st_size
    logger.info(f"   文件路径: {audio_file}")
    logger.info(f"   文件大小: {file_size / 1024:.2f} KB")
    logger.info("")

    # 4. 设置音频参数
    logger.info("=" * 60)
    logger.info("📋 设置音频参数...")
    logger.info("=" * 60)

    subprocess.run(['amixer', 'set', 'Deviceid', '2'],
                   check=False, capture_output=True)
    subprocess.run(['amixer', 'set', 'Playback', '10'],
                   check=False, capture_output=True)

    logger.info("✅ 音频参数设置完成")
    logger.info("   - Deviceid = 2")
    logger.info("   - Playback = 10")
    logger.info("")

    # 5. 测试播放（使用 AudioPlayer）
    logger.info("=" * 60)
    logger.info("🔊 测试播放（AudioPlayer）...")
    logger.info("=" * 60)
    logger.info("")

    logger.info("⚠️  请戴上耳机，准备听音频...")
    logger.info("   （播放将在 3 秒后开始）")
    logger.info("")

    for i in range(3, 0, -1):
        print(f"{i}...")
        await asyncio.sleep(1)

    logger.info("")
    logger.info("🔊 开始播放！")
    logger.info("")

    # 创建播放器
    player = AudioPlayer()
    await player.start()

    # 播放音频
    await player.play_async(audio_file)

    # 等待播放完成
    while player.is_playing or player.get_queue_size() > 0:
        await asyncio.sleep(0.1)

    await player.stop()

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ 播放测试完成")
    logger.info("=" * 60)
    logger.info("")

    # 6. 询问用户反馈
    logger.info("📝 请回答以下问题：")
    logger.info("")
    logger.info("   1. 你听到声音了吗？（是/否）")
    logger.info("   2. 声音清晰吗？（是/否）")
    logger.info("   3. 音量合适吗？（是/否）")
    logger.info("   4. 内容正确吗？（是/否）")
    logger.info("")


if __name__ == "__main__":
    try:
        asyncio.run(test_playback())
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⚠️  用户中断")
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
