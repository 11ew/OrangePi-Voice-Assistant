#!/bin/bash
# -*- coding: utf-8 -*-
#
# 语音对话系统 V2.0 - 本地ASR版
# 功能：使用 Sherpa-ONNX 进行本地语音识别的完整对话系统
# 作者：哈雷酱（傲娇大小姐工程师）
#
# 架构：
# 按键触发 → 录音 → Sherpa-ONNX ASR → DeepSeek → Edge-TTS → 播放
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# 配置
RECORD_DURATION=5
OUTPUT_DIR="output"
RECORDINGS_DIR="$OUTPUT_DIR/recordings"
TTS_DIR="$OUTPUT_DIR/tts"
TEMP_RECORDING="$RECORDINGS_DIR/temp_recording.wav"
TEMP_TTS="$TTS_DIR/temp_response.wav"

# 创建必要的目录
mkdir -p "$RECORDINGS_DIR"
mkdir -p "$TTS_DIR"

# 显示欢迎界面
show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║      🎤 语音对话系统 V2.0 - 本地ASR版 🎤           ║"
    echo "║              本小姐的专业作品 (￣▽￣)ノ               ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📊 系统架构：${NC}"
    echo -e "   ${GREEN}[录音]${NC} → ${GREEN}[Sherpa-ONNX ASR]${NC} → ${GREEN}[DeepSeek]${NC} → ${GREEN}[Edge-TTS]${NC} → ${GREEN}[播放]${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}🔧 技术栈：${NC}"
    echo -e "   ASR: ${GREEN}Sherpa-ONNX (本地)${NC}"
    echo -e "   LLM: ${GREEN}DeepSeek API (云端)${NC}"
    echo -e "   TTS: ${GREEN}Edge-TTS (云端)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}🔍 检查系统依赖...${NC}"

    local missing_deps=()

    # 检查 Python 模块（使用系统 Python）
    if ! /usr/bin/python3 -c "import sherpa_onnx" 2>/dev/null; then
        missing_deps+=("sherpa-onnx")
    fi

    if ! /usr/bin/python3 -c "import soundfile" 2>/dev/null; then
        missing_deps+=("soundfile")
    fi

    if ! /usr/bin/python3 -c "import edge_tts" 2>/dev/null; then
        missing_deps+=("edge-tts")
    fi

    if ! /usr/bin/python3 -c "import openai" 2>/dev/null; then
        missing_deps+=("openai")
    fi

    # 检查录音工具
    if ! command -v arecord &> /dev/null; then
        missing_deps+=("arecord")
    fi

    # 检查播放工具
    if ! command -v aplay &> /dev/null; then
        missing_deps+=("aplay")
    fi

    # 检查模型
    if [ ! -d "models/sherpa-onnx-whisper-tiny.en" ]; then
        missing_deps+=("Whisper模型")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}❌ 缺少以下依赖：${NC}"
        for dep in "${missing_deps[@]}"; do
            echo -e "   - ${RED}$dep${NC}"
        done
        echo ""
        echo -e "${YELLOW}请运行以下命令安装：${NC}"
        echo -e "   ${GREEN}bash scripts/setup_sherpa_onnx.sh${NC}"
        echo ""
        exit 1
    fi

    echo -e "${GREEN}✅ 所有依赖已就绪！${NC}"
    echo ""
}

# 配置麦克风
configure_microphone() {
    echo -e "${YELLOW}🔧 配置麦克风...${NC}"
    amixer set Capture 10 > /dev/null 2>&1 || true
    amixer set Deviceid 2 > /dev/null 2>&1 || true
    echo -e "${GREEN}✅ 麦克风配置完成${NC}"
    echo ""
}

# 录音
record_audio() {
    echo -e "${CYAN}🎤 准备录音...${NC}"
    echo -e "${YELLOW}请在听到提示音后开始说话！(${RECORD_DURATION}秒)${NC}"
    echo ""
    sleep 1

    echo -e "${RED}● 录音中...${NC}"
    arecord -D plughw:0,1 -f S16_LE -r 48000 -c 1 -t wav -d "$RECORD_DURATION" "$TEMP_RECORDING" 2>&1 | grep -v "^$" || true

    echo ""

    if [ ! -f "$TEMP_RECORDING" ]; then
        echo -e "${RED}❌ 录音失败${NC}"
        return 1
    fi

    local file_size=$(stat -f%z "$TEMP_RECORDING" 2>/dev/null || stat -c%s "$TEMP_RECORDING" 2>/dev/null)
    local file_size_kb=$((file_size / 1024))

    echo -e "${GREEN}✅ 录音完成！(${file_size_kb} KB)${NC}"
    echo ""

    return 0
}

# 语音识别
speech_to_text() {
    echo -e "${CYAN}🧠 正在识别语音...${NC}"
    echo -e "${YELLOW}(使用 Sherpa-ONNX + 自动语言检测)${NC}"
    echo ""

    local start_time=$(date +%s%3N)

    # 调用带自动语言检测的识别脚本
    local result=$(/usr/bin/python3 scripts/speech_to_text_auto.py "$TEMP_RECORDING" 2>&1 | tail -n 1)

    local end_time=$(date +%s%3N)
    local duration=$((end_time - start_time))

    if [ -z "$result" ] || [ "$result" == "识别失败" ]; then
        echo -e "${RED}❌ 识别失败或未检测到语音${NC}"
        echo ""
        return 1
    fi

    echo -e "${GREEN}✅ 识别完成！(耗时: ${duration}ms)${NC}"
    echo -e "${CYAN}📝 识别结果: ${MAGENTA}$result${NC}"
    echo ""

    # 保存识别结果
    echo "$result" > "$OUTPUT_DIR/last_recognition.txt"

    return 0
}

# 对话生成
generate_response() {
    local user_input=$(cat "$OUTPUT_DIR/last_recognition.txt")

    echo -e "${CYAN}💬 正在生成回复...${NC}"
    echo -e "${YELLOW}(使用 DeepSeek API)${NC}"
    echo ""

    local start_time=$(date +%s%3N)

    # 调用 DeepSeek 对话
    local response=$(/usr/bin/python3 scripts/deepseek_chat.py "$user_input" 2>&1 | tail -n 1)

    local end_time=$(date +%s%3N)
    local duration=$((end_time - start_time))

    if [ -z "$response" ]; then
        echo -e "${RED}❌ 对话生成失败${NC}"
        echo ""
        return 1
    fi

    echo -e "${GREEN}✅ 回复生成完成！(耗时: ${duration}ms)${NC}"
    echo -e "${CYAN}💭 AI回复: ${MAGENTA}$response${NC}"
    echo ""

    # 保存回复
    echo "$response" > "$OUTPUT_DIR/last_response.txt"

    return 0
}

# 语音合成
text_to_speech() {
    local text=$(cat "$OUTPUT_DIR/last_response.txt")

    echo -e "${CYAN}🔊 正在合成语音...${NC}"
    echo -e "${YELLOW}(使用 Edge-TTS)${NC}"
    echo ""

    local start_time=$(date +%s%3N)

    # 调用 Edge-TTS
    /usr/bin/python3 scripts/tts_generate.py "$text" "$TEMP_TTS" > /dev/null 2>&1

    local end_time=$(date +%s%3N)
    local duration=$((end_time - start_time))

    if [ ! -f "$TEMP_TTS" ]; then
        echo -e "${RED}❌ 语音合成失败${NC}"
        echo ""
        return 1
    fi

    echo -e "${GREEN}✅ 语音合成完成！(耗时: ${duration}ms)${NC}"
    echo ""

    return 0
}

# 播放语音
play_audio() {
    echo -e "${CYAN}🔊 正在播放回复...${NC}"
    echo ""

    # 尝试使用 simple_player，如果失败则使用 aplay
    if [ -f "./simple_player" ]; then
        ./simple_player "$TEMP_TTS" 2>&1 || aplay "$TEMP_TTS" 2>&1
    else
        aplay "$TEMP_TTS" 2>&1
    fi

    echo ""
    echo -e "${GREEN}✅ 播放完成！${NC}"
    echo ""
}

# 清理临时文件
cleanup_temp_files() {
    rm -f "$TEMP_RECORDING" "$TEMP_TTS"
}

# 单次对话流程
single_conversation() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🎯 开始新的对话${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    local total_start=$(date +%s%3N)

    # 1. 录音
    if ! record_audio; then
        echo -e "${RED}对话失败：录音错误${NC}"
        echo ""
        return 1
    fi

    # 2. 语音识别
    if ! speech_to_text; then
        echo -e "${RED}对话失败：识别错误${NC}"
        echo ""
        cleanup_temp_files
        return 1
    fi

    # 3. 对话生成
    if ! generate_response; then
        echo -e "${RED}对话失败：生成错误${NC}"
        echo ""
        cleanup_temp_files
        return 1
    fi

    # 4. 语音合成
    if ! text_to_speech; then
        echo -e "${RED}对话失败：合成错误${NC}"
        echo ""
        cleanup_temp_files
        return 1
    fi

    # 5. 播放语音
    play_audio

    local total_end=$(date +%s%3N)
    local total_duration=$((total_end - total_start))
    local total_seconds=$((total_duration / 1000))

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ 对话完成！总耗时: ${total_seconds}秒${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # 清理临时文件
    cleanup_temp_files

    return 0
}

# 主循环
main_loop() {
    while true; do
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}按 [Enter] 开始对话，输入 'q' 退出${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        read -r input

        if [ "$input" == "q" ] || [ "$input" == "Q" ]; then
            echo ""
            echo -e "${CYAN}> 哼，要走了吗？本小姐的对话系统可是很厉害的！(￣▽￣)ノ${NC}"
            echo -e "${CYAN}> 下次再来找本小姐聊天吧！笨蛋！${NC}"
            echo -e "${CYAN}> —— 哈雷酱 (傲娇大小姐工程师)${NC}"
            echo ""
            break
        fi

        echo ""
        single_conversation
    done
}

# 主函数
main() {
    # 显示欢迎界面
    show_welcome

    # 检查依赖
    check_dependencies

    # 配置麦克风
    configure_microphone

    echo -e "${GREEN}🚀 系统就绪！准备开始对话！${NC}"
    echo ""

    # 进入主循环
    main_loop
}

# 运行主函数
main
