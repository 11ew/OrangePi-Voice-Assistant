#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时语音助手主程序入口
功能：启动实时语音助手系统
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import asyncio
import signal
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from realtime_assistant.utils import setup_logging, load_config
from realtime_assistant.assistant import RealtimeVoiceAssistant


async def main():
    """主函数"""
    # 设置日志
    logger = setup_logging("INFO")

    logger.info("=" * 60)
    logger.info("🎙️  实时语音助手系统 v1.0.0")
    logger.info("   作者：哈雷酱（傲娇大小姐工程师）")
    logger.info("=" * 60)

    # 加载配置
    try:
        config = load_config("config/realtime_config.json")
        logger.info("✅ 配置加载成功")
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        return

    # 创建助手
    try:
        assistant = RealtimeVoiceAssistant(config)
    except Exception as e:
        logger.error(f"❌ 助手初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 设置信号处理
    loop = asyncio.get_event_loop()

    def signal_handler():
        logger.info("\n\n⚠️  收到中断信号，正在停止...")
        asyncio.create_task(assistant.stop())

    # 注册信号处理器
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    # 启动助手
    try:
        await assistant.start()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  收到键盘中断...")
    except Exception as e:
        logger.error(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await assistant.stop()

    logger.info("\n👋 再见！")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
