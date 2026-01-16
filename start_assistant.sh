#!/bin/bash
# 实时语音助手启动脚本
# 作者：哈雷酱（傲娇大小姐工程师）

set -e

echo "🎙️ 实时语音助手系统 - 启动脚本"
echo "============================================================"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  警告：不建议使用 root 用户运行"
    echo ""
fi

# 1. 初始化音频设备
echo "🔧 初始化音频设备..."
echo "   - 设置录音音量..."
sudo amixer set Capture 10 > /dev/null 2>&1 || echo "   ⚠️  无法设置 Capture 音量"

echo "   - 设置设备 ID 为耳机 MIC..."
sudo amixer set Deviceid 2 > /dev/null 2>&1 || echo "   ⚠️  无法设置 Deviceid"

echo "   - 设置播放音量..."
sudo amixer set Playback 10 > /dev/null 2>&1 || echo "   ⚠️  无法设置 Playback 音量"

echo "✅ 音频设备初始化完成"
echo ""

# 2. 检查依赖
echo "📦 检查依赖..."
python3 -c "import sounddevice, sherpa_onnx, aiohttp, edge_tts, numpy, soundfile" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 所有依赖已安装"
else
    echo "❌ 缺少依赖，请运行: pip install -r requirements_realtime.txt"
    exit 1
fi
echo ""

# 3. 检查模型文件
echo "🎯 检查模型文件..."
if [ -f "models/silero_vad.onnx" ]; then
    echo "✅ VAD 模型存在"
else
    echo "❌ VAD 模型不存在: models/silero_vad.onnx"
    exit 1
fi

if [ -d "models/sherpa-onnx-streaming-paraformer-bilingual-zh-en" ]; then
    echo "✅ ASR 模型存在"
else
    echo "❌ ASR 模型不存在: models/sherpa-onnx-streaming-paraformer-bilingual-zh-en"
    exit 1
fi
echo ""

# 4. 显示音频设备信息
echo "🎤 音频设备信息:"
python3 -c "import sounddevice as sd; print(sd.query_devices())" 2>/dev/null || echo "⚠️  无法获取音频设备信息"
echo ""

# 5. 启动实时语音助手
echo "🚀 启动实时语音助手..."
echo "============================================================"
echo ""
echo "💡 提示："
echo "   - 请确保已插入带 MIC 的耳机到 3.5mm 接口"
echo "   - 按 Ctrl+C 可以优雅退出系统"
echo "   - 系统会自动监听你的语音，无需按键"
echo ""
echo "============================================================"
echo ""

# 运行主程序
python3 realtime_assistant_main.py

echo ""
echo "✅ 实时语音助手已退出"
