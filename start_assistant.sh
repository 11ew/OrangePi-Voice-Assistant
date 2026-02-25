#!/bin/bash
# 实时语音助手启动脚本
# 作者：哈雷酱（傲娇大小姐工程师）
# 功能：检查环境并启动实时语音助手系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查函数
check_failed=0

check_python_deps() {
    print_header "检查 Python 依赖包"
    local deps=("aiohttp" "edge-tts" "sherpa_onnx" "sounddevice" "numpy")
    for dep in "${deps[@]}"; do
        # 特殊处理 sherpa_onnx 的显示名称
        local display_name="$dep"
        if [ "$dep" = "sherpa_onnx" ]; then
            display_name="sherpa-onnx"
        fi

        if pip list 2>/dev/null | grep -q "^$dep "; then
            local version=$(pip list 2>/dev/null | grep "^$dep " | awk '{print $2}')
            print_success "$display_name ($version)"
        else
            print_error "$display_name 未安装"
            check_failed=1
        fi
    done
    echo ""
}

check_system_commands() {
    print_header "检查系统命令"
    local commands=("ffmpeg" "aplay" "arecord")
    for cmd in "${commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            print_success "$cmd"
        else
            print_error "$cmd 未找到"
            check_failed=1
        fi
    done
    echo ""
}

check_config_files() {
    print_header "检查配置文件"
    local configs=("config/realtime_config.json" "config/asr_config.json" "config/vad_config.json")
    for config in "${configs[@]}"; do
        if [ -f "$config" ]; then
            print_success "$config"
        else
            print_error "$config 不存在"
            check_failed=1
        fi
    done
    echo ""
}

check_model_files() {
    print_header "检查模型文件"
    if [ -f "models/silero_vad.onnx" ]; then
        local size=$(du -h "models/silero_vad.onnx" | cut -f1)
        print_success "VAD 模型 (${size})"
    else
        print_error "VAD 模型不存在"
        check_failed=1
    fi
    if [ -d "models/sherpa-onnx-streaming-paraformer-bilingual-zh-en" ]; then
        local count=$(ls -1 "models/sherpa-onnx-streaming-paraformer-bilingual-zh-en" | wc -l)
        print_success "ASR 模型目录 (${count} 个文件)"
    else
        print_error "ASR 模型目录不存在"
        check_failed=1
    fi
    echo ""
}

check_audio_devices() {
    print_header "检查音频设备"
    if arecord -l 2>/dev/null | grep -q "card 0"; then
        print_success "录音设备可用"
    else
        print_warning "录音设备可能不可用"
    fi
    if aplay -l 2>/dev/null | grep -q "ascend310b"; then
        print_success "播放设备可用"
    else
        print_warning "播放设备可能不可用"
    fi
    local occupied=$(lsof /dev/snd/* 2>/dev/null | wc -l)
    if [ "$occupied" -gt 0 ]; then
        print_warning "音频设备被占用 ($occupied 个进程)"
    else
        print_success "音频设备未被占用"
    fi
    echo ""
}

# 主函数
main() {
    clear
    print_header "🎙️  实时语音助手启动检查"
    echo ""
    check_python_deps
    check_system_commands
    check_config_files
    check_model_files
    check_audio_devices
    
    if [ $check_failed -eq 1 ]; then
        print_header "❌ 环境检查失败"
        print_error "请修复上述问题后再启动系统"
        echo ""
        exit 1
    fi
    
    print_header "✅ 环境检查通过"
    echo ""
    print_info "准备启动实时语音助手系统..."
    echo ""
    read -p "是否立即启动？(y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        print_header "🚀 启动实时语音助手"
        echo ""
        print_info "按 Ctrl+C 停止系统"
        echo ""
        sleep 2
        python3 realtime_assistant_main.py
    else
        echo ""
        print_info "已取消启动"
        echo ""
    fi
}

main
