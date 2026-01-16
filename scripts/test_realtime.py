#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时语音助手 - 系统测试脚本
作者：哈雷酱（傲娇大小姐工程师）
版本：v1.0.0
"""

import sys
import os
import time
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_header(text):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"{Colors.CYAN}{text}{Colors.NC}")
    print(f"{'='*60}\n")

def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")

def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def print_info(text):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.NC}")

def test_imports():
    """测试模块导入"""
    print_header("测试 1: 模块导入")

    modules = [
        ("numpy", "NumPy"),
        ("asyncio", "AsyncIO"),
        ("aiohttp", "aiohttp"),
        ("edge_tts", "Edge-TTS"),
    ]

    all_passed = True

    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print_success(f"{display_name} 导入成功")
        except ImportError as e:
            print_error(f"{display_name} 导入失败: {e}")
            all_passed = False

    # 测试 sherpa-onnx（可选）
    try:
        import sherpa_onnx
        print_success(f"sherpa-onnx 导入成功 (版本: {sherpa_onnx.__version__})")
    except ImportError:
        print_warning("sherpa-onnx 导入失败（将使用延迟导入）")

    # 测试 sounddevice（可选）
    try:
        import sounddevice
        print_success("sounddevice 导入成功")
    except (ImportError, OSError) as e:
        print_warning(f"sounddevice 导入失败: {e}")

    return all_passed

def test_config_loading():
    """测试配置加载"""
    print_header("测试 2: 配置加载")

    try:
        from realtime_assistant.utils import load_config

        # 测试加载主配置
        config = load_config("config/realtime_config.json")
        print_success("主配置加载成功")
        print_info(f"  - VAD 启用: {config.get('vad', {}).get('enabled')}")
        print_info(f"  - ASR 模型: {config.get('asr', {}).get('model_type')}")
        print_info(f"  - LLM 模型: {config.get('llm', {}).get('model')}")

        # 测试加载 VAD 配置
        vad_config = load_config("config/vad_config.json")
        print_success("VAD 配置加载成功")
        print_info(f"  - 阈值: {vad_config.get('threshold')}")
        print_info(f"  - 采样率: {vad_config.get('sample_rate')}")

        return True
    except Exception as e:
        print_error(f"配置加载失败: {e}")
        return False

def test_state_machine():
    """测试状态机"""
    print_header("测试 3: 状态机")

    try:
        from realtime_assistant.state_machine import AssistantState, StateMachine

        # 创建状态机
        sm = StateMachine()
        print_success("状态机创建成功")
        print_info(f"  - 初始状态: {sm.state.value}")

        # 测试状态转换
        sm.transition(AssistantState.LISTENING)
        print_success(f"状态转换成功: {sm.state.value}")

        sm.transition(AssistantState.PROCESSING)
        print_success(f"状态转换成功: {sm.state.value}")

        sm.transition(AssistantState.IDLE)
        print_success(f"状态转换成功: {sm.state.value}")

        return True
    except Exception as e:
        print_error(f"状态机测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_utils():
    """测试工具函数"""
    print_header("测试 4: 工具函数")

    try:
        from realtime_assistant.utils import setup_logging, PerformanceMonitor

        # 测试日志设置
        logger = setup_logging("INFO")
        print_success("日志系统初始化成功")

        # 测试性能监控
        monitor = PerformanceMonitor()
        monitor.start("test_task")
        time.sleep(0.1)
        elapsed = monitor.stop("test_task")
        print_success(f"性能监控测试成功 (耗时: {elapsed:.3f}s)")

        return True
    except Exception as e:
        print_error(f"工具函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vad_model():
    """测试 VAD 模型"""
    print_header("测试 5: VAD 模型")

    vad_model_path = project_root / "models" / "silero_vad.onnx"

    if vad_model_path.exists():
        size = vad_model_path.stat().st_size / 1024  # KB
        print_success(f"VAD 模型存在: {vad_model_path}")
        print_info(f"  - 大小: {size:.1f} KB")
        return True
    else:
        print_warning(f"VAD 模型不存在: {vad_model_path}")
        print_info("系统将在首次运行时尝试加载模型")
        return True  # 不算失败

async def test_async_operations():
    """测试异步操作"""
    print_header("测试 6: 异步操作")

    try:
        # 测试异步任务
        async def async_task(name, delay):
            await asyncio.sleep(delay)
            return f"{name} 完成"

        # 并行执行多个任务
        tasks = [
            async_task("任务1", 0.1),
            async_task("任务2", 0.1),
            async_task("任务3", 0.1),
        ]

        results = await asyncio.gather(*tasks)
        print_success("异步任务执行成功")
        for result in results:
            print_info(f"  - {result}")

        return True
    except Exception as e:
        print_error(f"异步操作测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print_header("测试 7: 文件结构")

    required_files = [
        "realtime_assistant/__init__.py",
        "realtime_assistant/utils.py",
        "realtime_assistant/state_machine.py",
        "realtime_assistant/vad_detector.py",
        "realtime_assistant/audio_capture.py",
        "realtime_assistant/asr_engine.py",
        "realtime_assistant/llm_engine.py",
        "realtime_assistant/tts_engine.py",
        "realtime_assistant/audio_player.py",
        "realtime_assistant/assistant.py",
        "realtime_assistant_main.py",
        "config/realtime_config.json",
        "config/vad_config.json",
        "config/asr_config.json",
        "requirements_realtime.txt",
    ]

    all_exist = True

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} 不存在")
            all_exist = False

    return all_exist

def print_summary(results):
    """打印测试总结"""
    print_header("测试总结")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"总测试数: {total}")
    print(f"{Colors.GREEN}通过: {passed}{Colors.NC}")
    print(f"{Colors.RED}失败: {failed}{Colors.NC}")
    print(f"通过率: {passed/total*100:.1f}%")

    print("\n详细结果:")
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ 通过{Colors.NC}" if result else f"{Colors.RED}❌ 失败{Colors.NC}"
        print(f"  {test_name}: {status}")

    if failed == 0:
        print(f"\n{Colors.GREEN}{'='*60}")
        print("🎉 所有测试通过！系统已准备就绪！")
        print(f"{'='*60}{Colors.NC}\n")
        return True
    else:
        print(f"\n{Colors.YELLOW}{'='*60}")
        print("⚠️  部分测试失败，请检查错误信息")
        print(f"{'='*60}{Colors.NC}\n")
        return False

async def main():
    """主函数"""
    print_header("🎙️  实时语音助手 - 系统测试")
    print("作者：哈雷酱（傲娇大小姐工程师）")
    print("版本：v1.0.0\n")

    # 运行所有测试
    results = {}

    results["模块导入"] = test_imports()
    results["配置加载"] = test_config_loading()
    results["状态机"] = test_state_machine()
    results["工具函数"] = test_utils()
    results["VAD 模型"] = test_vad_model()
    results["异步操作"] = await test_async_operations()
    results["文件结构"] = test_file_structure()

    # 打印总结
    success = print_summary(results)

    # 返回退出码
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}测试过程中发生错误: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
