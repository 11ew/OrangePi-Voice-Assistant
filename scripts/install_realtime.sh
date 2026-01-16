#!/bin/bash
# 实时语音助手 - 一键安装脚本
# 作者：哈雷酱（傲娇大小姐工程师）
# 版本：v1.0.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
    echo ""
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_warning "请不要使用 root 用户运行此脚本"
        print_info "建议使用普通用户，脚本会在需要时提示输入 sudo 密码"
        exit 1
    fi
}

# 检查系统类型
check_system() {
    print_header "🔍 检查系统环境"

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        print_info "操作系统: $OS $VER"
    else
        print_error "无法识别操作系统"
        exit 1
    fi

    # 检查架构
    ARCH=$(uname -m)
    print_info "系统架构: $ARCH"

    # 检查 Python 版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_info "Python 版本: $PYTHON_VERSION"

        # 检查 Python 版本是否 >= 3.8
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
            print_error "Python 版本过低，需要 Python 3.8+"
            exit 1
        fi
    else
        print_error "未找到 Python 3"
        exit 1
    fi

    print_success "系统环境检查通过"
}

# 安装系统依赖
install_system_deps() {
    print_header "📦 安装系统依赖"

    print_info "更新包管理器..."
    sudo apt-get update -qq

    print_info "安装 PortAudio（音频捕获）..."
    sudo apt-get install -y portaudio19-dev

    print_info "安装 ALSA（音频系统）..."
    sudo apt-get install -y libasound2-dev

    print_info "安装 FFmpeg（音频转换）..."
    sudo apt-get install -y ffmpeg

    print_info "安装其他依赖..."
    sudo apt-get install -y build-essential python3-dev

    print_success "系统依赖安装完成"
}

# 安装 Python 依赖
install_python_deps() {
    print_header "🐍 安装 Python 依赖"

    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        print_info "安装 pip..."
        sudo apt-get install -y python3-pip
    fi

    # 升级 pip
    print_info "升级 pip..."
    pip3 install --upgrade pip -q

    # 安装基础依赖
    if [ -f "requirements.txt" ]; then
        print_info "安装基础依赖..."
        pip3 install -r requirements.txt -q
    fi

    # 安装实时助手依赖
    if [ -f "requirements_realtime.txt" ]; then
        print_info "安装实时助手依赖..."
        pip3 install -r requirements_realtime.txt -q
    fi

    # 安装 sherpa-onnx
    print_info "安装 sherpa-onnx..."
    pip3 install sherpa-onnx -q

    print_success "Python 依赖安装完成"
}

# 验证安装
verify_installation() {
    print_header "✅ 验证安装"

    # 验证 sherpa-onnx
    print_info "验证 sherpa-onnx..."
    if python3 -c "import sherpa_onnx; print('sherpa-onnx:', sherpa_onnx.__version__)" 2>/dev/null; then
        print_success "sherpa-onnx 安装成功"
    else
        print_warning "sherpa-onnx 导入失败，将使用延迟导入"
    fi

    # 验证 sounddevice
    print_info "验证 sounddevice..."
    if python3 -c "import sounddevice" 2>/dev/null; then
        print_success "sounddevice 安装成功"
    else
        print_error "sounddevice 安装失败"
        return 1
    fi

    # 验证 aiohttp
    print_info "验证 aiohttp..."
    if python3 -c "import aiohttp" 2>/dev/null; then
        print_success "aiohttp 安装成功"
    else
        print_error "aiohttp 安装失败"
        return 1
    fi

    # 验证 edge-tts
    print_info "验证 edge-tts..."
    if python3 -c "import edge_tts" 2>/dev/null; then
        print_success "edge-tts 安装成功"
    else
        print_error "edge-tts 安装失败"
        return 1
    fi

    print_success "所有依赖验证通过"
}

# 检查 VAD 模型
check_vad_model() {
    print_header "🎯 检查 VAD 模型"

    VAD_MODEL="models/silero_vad.onnx"

    if [ -f "$VAD_MODEL" ]; then
        VAD_SIZE=$(du -h "$VAD_MODEL" | cut -f1)
        print_success "VAD 模型已存在: $VAD_MODEL ($VAD_SIZE)"
    else
        print_warning "VAD 模型不存在: $VAD_MODEL"
        print_info "系统将在首次运行时尝试加载模型"
    fi
}

# 配置音频权限
configure_audio_permissions() {
    print_header "🔊 配置音频权限"

    # 检查用户是否在 audio 组
    if groups | grep -q audio; then
        print_success "用户已在 audio 组"
    else
        print_info "将用户添加到 audio 组..."
        sudo usermod -a -G audio $USER
        print_warning "需要重新登录或重启系统以使权限生效"
    fi
}

# 测试系统
test_system() {
    print_header "🧪 测试系统"

    print_info "测试主程序..."
    if python3 realtime_assistant_main.py --help &> /dev/null; then
        print_success "主程序可以正常启动"
    else
        print_error "主程序启动失败"
        print_info "请查看错误信息并手动排查"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    print_header "📖 使用说明"

    echo "安装完成！现在你可以："
    echo ""
    echo "1. 查看帮助信息："
    echo "   python3 realtime_assistant_main.py --help"
    echo ""
    echo "2. 启动实时语音助手："
    echo "   python3 realtime_assistant_main.py"
    echo ""
    echo "3. 查看快速开始指南："
    echo "   cat QUICKSTART_REALTIME.md"
    echo ""
    echo "4. 查看系统架构文档："
    echo "   cat docs/REALTIME_ASSISTANT.md"
    echo ""

    if ! groups | grep -q audio; then
        print_warning "重要提示："
        print_warning "你的用户已被添加到 audio 组，但需要重新登录才能生效"
        print_warning "请运行以下命令之一："
        print_warning "  - 重新登录: logout"
        print_warning "  - 重启系统: sudo reboot"
    fi
}

# 主函数
main() {
    print_header "🎙️  实时语音助手 - 一键安装脚本"
    echo "作者：哈雷酱（傲娇大小姐工程师）"
    echo "版本：v1.0.0"
    echo ""

    # 检查 root
    check_root

    # 检查系统
    check_system

    # 询问是否继续
    echo ""
    read -p "是否继续安装？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "安装已取消"
        exit 0
    fi

    # 安装系统依赖
    install_system_deps

    # 安装 Python 依赖
    install_python_deps

    # 验证安装
    verify_installation

    # 检查 VAD 模型
    check_vad_model

    # 配置音频权限
    configure_audio_permissions

    # 测试系统
    test_system

    # 显示使用说明
    show_usage

    print_header "🎉 安装完成！"
    print_success "实时语音助手已成功安装！"
}

# 运行主函数
main
