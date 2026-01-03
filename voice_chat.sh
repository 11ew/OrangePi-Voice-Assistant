#!/bin/bash
# -*- coding: utf-8 -*-
#
# DeepSeek 语音对话系统
# 功能：文字输入 → DeepSeek 对话 → TTS 语音输出
# 作者：哈雷酱（傲娇大小姐工程师）
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
OUTPUT_DIR="output"
VOICE="xiaoxiao"  # 默认语音：晓晓（温柔女声）
RATE="+0%"        # 默认语速
VOLUME="+0%"      # 默认音量
PITCH="+0Hz"      # 默认音调

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 显示欢迎界面
show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║      🤖 DeepSeek 语音对话系统 🎤                    ║"
    echo "║              本小姐的智能作品 (￣▽￣)ノ               ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# 显示当前配置
show_config() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📋 当前语音配置：${NC}"

    case $VOICE in
        xiaoxiao) echo -e "   🔊 语音: ${GREEN}晓晓 - 女声(温柔)${NC}" ;;
        xiaoyi)   echo -e "   🔊 语音: ${GREEN}晓伊 - 女声(活泼)${NC}" ;;
        yunjian)  echo -e "   🔊 语音: ${GREEN}云健 - 男声(沉稳)${NC}" ;;
        yunxi)    echo -e "   🔊 语音: ${GREEN}云希 - 男声(年轻)${NC}" ;;
        xiaoxuan) echo -e "   🔊 语音: ${GREEN}晓萱 - 女声(甜美)${NC}" ;;
        yunyang)  echo -e "   🔊 语音: ${GREEN}云扬 - 男声(热情)${NC}" ;;
    esac

    echo -e "   ⚡ 语速: ${GREEN}${RATE}${NC}"
    echo -e "   🔈 音量: ${GREEN}${VOLUME}${NC}"
    echo -e "   🎵 音调: ${GREEN}${PITCH}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 与 DeepSeek 对话并播放语音
chat_and_speak() {
    local user_input="$1"

    echo -e "${YELLOW}👤 你说: ${NC}${user_input}"
    echo ""

    # 调用 DeepSeek API
    echo -e "${CYAN}🤖 DeepSeek 正在思考...${NC}"
    local response=$(python3 scripts/deepseek_chat.py "$user_input" 2>/dev/null)

    if [ $? -ne 0 ] || [ -z "$response" ]; then
        echo -e "${RED}❌ DeepSeek 调用失败！${NC}"
        return 1
    fi

    # 显示 DeepSeek 的回复
    echo -e "${GREEN}🤖 DeepSeek: ${NC}"
    echo "$response"
    echo ""

    # 生成语音文件
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local audio_file="${OUTPUT_DIR}/chat_${timestamp}.wav"

    echo -e "${CYAN}🎤 正在生成语音...${NC}"
    python3 scripts/tts_generate.py "$response" "$audio_file" "$VOICE" "$RATE" "$VOLUME" "$PITCH" 2>&1 | grep -v "^$"

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 语音生成失败！${NC}"
        return 1
    fi

    # 播放语音
    echo -e "${CYAN}🔊 正在播放语音...${NC}"
    ./simple_player "$audio_file"

    echo ""
    echo -e "${GREEN}✅ 对话完成！${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 切换语音
change_voice() {
    echo ""
    echo -e "${CYAN}🔊 选择语音类型：${NC}"
    echo ""
    echo "  1) 晓晓 - 女声(温柔) ⭐推荐"
    echo "  2) 晓伊 - 女声(活泼)"
    echo "  3) 云健 - 男声(沉稳)"
    echo "  4) 云希 - 男声(年轻)"
    echo "  5) 晓萱 - 女声(甜美)"
    echo "  6) 云扬 - 男声(热情)"
    echo ""
    read -p "请选择 (1-6): " choice

    case $choice in
        1) VOICE="xiaoxiao" ;;
        2) VOICE="xiaoyi" ;;
        3) VOICE="yunjian" ;;
        4) VOICE="yunxi" ;;
        5) VOICE="xiaoxuan" ;;
        6) VOICE="yunyang" ;;
        *) echo -e "${RED}无效选择！${NC}"; return ;;
    esac

    echo -e "${GREEN}✅ 语音已切换！${NC}"
}

# 调整语速
change_rate() {
    echo ""
    echo -e "${CYAN}⚡ 调整语速：${NC}"
    echo ""
    echo "  1) 很慢 (-50%)"
    echo "  2) 较慢 (-25%)"
    echo "  3) 正常 (0%)"
    echo "  4) 较快 (+25%)"
    echo "  5) 很快 (+50%)"
    echo "  6) 自定义"
    echo ""
    read -p "请选择 (1-6): " choice

    case $choice in
        1) RATE="-50%" ;;
        2) RATE="-25%" ;;
        3) RATE="+0%" ;;
        4) RATE="+25%" ;;
        5) RATE="+50%" ;;
        6)
            read -p "请输入语速 (如: +20% 或 -30%): " RATE
            ;;
        *) echo -e "${RED}无效选择！${NC}"; return ;;
    esac

    echo -e "${GREEN}✅ 语速已调整！${NC}"
}

# 主菜单
show_menu() {
    echo -e "${CYAN}📌 主菜单：${NC}"
    echo ""
    echo "  1) 💬 开始对话"
    echo "  2) 🔊 切换语音类型"
    echo "  3) ⚡ 调整语速"
    echo "  4) 🔄 重置配置"
    echo "  5) ❌ 退出程序"
    echo ""
}

# 重置配置
reset_config() {
    VOICE="xiaoxiao"
    RATE="+0%"
    VOLUME="+0%"
    PITCH="+0Hz"
    echo -e "${GREEN}✅ 配置已重置为默认值！${NC}"
}

# 主循环
main() {
    show_welcome

    # 检查依赖
    if [ ! -f "simple_player" ]; then
        echo -e "${RED}❌ 错误: 找不到 simple_player，请先运行 make 编译！${NC}"
        exit 1
    fi

    if [ ! -f "scripts/deepseek_chat.py" ]; then
        echo -e "${RED}❌ 错误: 找不到 deepseek_chat.py！${NC}"
        exit 1
    fi

    if [ ! -f "scripts/tts_generate.py" ]; then
        echo -e "${RED}❌ 错误: 找不到 tts_generate.py！${NC}"
        exit 1
    fi

    while true; do
        show_config
        show_menu

        read -p "请选择操作 (1-5): " choice

        case $choice in
            1)
                echo ""
                read -p "💬 请输入你的问题: " user_input
                if [ -n "$user_input" ]; then
                    echo ""
                    chat_and_speak "$user_input"
                else
                    echo -e "${RED}❌ 输入不能为空！${NC}"
                fi
                ;;
            2)
                change_voice
                ;;
            3)
                change_rate
                ;;
            4)
                reset_config
                ;;
            5)
                echo ""
                echo -e "${CYAN}👋 再见！本小姐期待下次为你服务～ (￣▽￣)ノ${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 无效选择，请重新输入！${NC}"
                ;;
        esac

        echo ""
        read -p "按回车键继续..."
        clear
        show_welcome
    done
}

# 运行主程序
main
