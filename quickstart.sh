#!/bin/bash
# quickstart.sh - Edge-TTS快速开始脚本
# Author: 哈雷酱(本小姐)
# Date: 2026-01-03

set -e  # 遇到错误立即退出

echo "╔════════════════════════════════════════════════════╗"
echo "║   🎤 Edge-TTS 快速开始脚本 🎤                     ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# 1. 检查依赖
echo "📋 步骤 1/5: 检查依赖..."
echo ""

check_command() {
    if command -v "$1" &> /dev/null; then
        echo "  ✅ $1 已安装"
        return 0
    else
        echo "  ❌ $1 未安装"
        return 1
    fi
}

all_deps_ok=true

check_command python3 || all_deps_ok=false
check_command gcc || all_deps_ok=false
check_command ffmpeg || all_deps_ok=false
check_command aplay || all_deps_ok=false

if [ "$all_deps_ok" = false ]; then
    echo ""
    echo "❌ 缺少必要依赖！"
    echo "💡 运行以下命令安装："
    echo "   make install-deps"
    exit 1
fi

echo ""
echo "✅ 所有依赖已就绪！"
echo ""

# 2. 编译C程序
echo "📋 步骤 2/5: 编译C程序..."
echo ""
make clean > /dev/null 2>&1 || true
make
echo ""

# 3. 生成测试音频
echo "📋 步骤 3/5: 生成测试音频..."
echo ""
python3 scripts/tts_generate.py "你好，欢迎使用Edge TTS文字转语音系统！这是本小姐精心打造的教学项目哦！" output/hello.wav
echo ""

# 4. 播放测试音频
echo "📋 步骤 4/5: 播放测试音频..."
echo ""
./simple_player output/hello.wav
echo ""

# 5. 显示使用说明
echo "📋 步骤 5/5: 使用说明"
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   🎉 快速开始完成！                               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "📝 接下来你可以："
echo ""
echo "1️⃣  生成自定义语音："
echo "   python3 scripts/tts_generate.py '你的文本' output/custom.wav"
echo ""
echo "2️⃣  播放音频文件："
echo "   ./simple_player output/custom.wav"
echo ""
echo "3️⃣  查看详细教程："
echo "   cat docs/tutorial.md"
echo ""
echo "4️⃣  尝试不同的语音："
echo "   python3 scripts/tts_generate.py '测试' output/test.wav xiaoxiao"
echo "   python3 scripts/tts_generate.py '测试' output/test.wav yunxi"
echo ""
echo "💡 提示：查看 README.md 了解更多信息"
echo ""
