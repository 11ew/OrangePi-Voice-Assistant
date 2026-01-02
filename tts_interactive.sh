#!/bin/bash
# 交互式TTS工具 - 简单易用的文字转语音
# Author: 哈雷酱(本小姐)
# Usage: bash tts_interactive.sh

clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║      🎤 Edge-TTS 交互式语音生成工具 🎤              ║"
echo "║              本小姐的专业作品 (￣▽￣)ノ               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 默认配置
VOICE="xiaoxiao"
RATE="+0%"
VOLUME="+0%"
PITCH="+0Hz"
OUTPUT_DIR="output"

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 语音列表
declare -A VOICE_NAMES=(
    ["xiaoxiao"]="晓晓 - 女声(温柔)"
    ["xiaoyi"]="晓伊 - 女声(活泼)"
    ["yunjian"]="云健 - 男声(沉稳)"
    ["yunxi"]="云希 - 男声(年轻)"
    ["xiaoxuan"]="晓萱 - 女声(甜美)"
    ["yunyang"]="云扬 - 男声(热情)"
)

# 显示当前配置
show_config() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 当前配置："
    echo "   🔊 语音: ${VOICE_NAMES[$VOICE]}"
    echo "   ⚡ 语速: $RATE"
    echo "   🔈 音量: $VOLUME"
    echo "   🎵 音调: $PITCH"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# 选择语音
select_voice() {
    echo ""
    echo "╔═══════════════════════════════════╗"
    echo "║       🎤 选择语音类型 🎤         ║"
    echo "╚═══════════════════════════════════╝"
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
        *) echo "❌ 无效选择，保持原配置"; return ;;
    esac

    echo "✅ 已切换到: ${VOICE_NAMES[$VOICE]}"
}

# 调整语速
adjust_rate() {
    echo ""
    echo "╔═══════════════════════════════════╗"
    echo "║       ⚡ 调整语速 ⚡             ║"
    echo "╚═══════════════════════════════════╝"
    echo ""
    echo "  1) 很慢 (-50%)"
    echo "  2) 较慢 (-25%)"
    echo "  3) 正常 (0%)   ⭐默认"
    echo "  4) 较快 (+25%)"
    echo "  5) 很快 (+50%)"
    echo "  6) 自定义..."
    echo ""
    read -p "请选择 (1-6): " choice

    case $choice in
        1) RATE="-50%" ;;
        2) RATE="-25%" ;;
        3) RATE="+0%" ;;
        4) RATE="+25%" ;;
        5) RATE="+50%" ;;
        6)
            read -p "请输入语速 (如: +30% 或 -20%): " custom_rate
            RATE="$custom_rate"
            ;;
        *) echo "❌ 无效选择，保持原配置"; return ;;
    esac

    echo "✅ 语速已设置为: $RATE"
}

# 调整音量
adjust_volume() {
    echo ""
    echo "╔═══════════════════════════════════╗"
    echo "║       🔈 调整音量 🔈             ║"
    echo "╚═══════════════════════════════════╝"
    echo ""
    echo "  1) 很小 (-50%)"
    echo "  2) 较小 (-25%)"
    echo "  3) 正常 (0%)   ⭐默认"
    echo "  4) 较大 (+25%)"
    echo "  5) 很大 (+50%)"
    echo "  6) 自定义..."
    echo ""
    read -p "请选择 (1-6): " choice

    case $choice in
        1) VOLUME="-50%" ;;
        2) VOLUME="-25%" ;;
        3) VOLUME="+0%" ;;
        4) VOLUME="+25%" ;;
        5) VOLUME="+50%" ;;
        6)
            read -p "请输入音量 (如: +30% 或 -20%): " custom_volume
            VOLUME="$custom_volume"
            ;;
        *) echo "❌ 无效选择，保持原配置"; return ;;
    esac

    echo "✅ 音量已设置为: $VOLUME"
}

# 调整音调
adjust_pitch() {
    echo ""
    echo "╔═══════════════════════════════════╗"
    echo "║       🎵 调整音调 🎵             ║"
    echo "╚═══════════════════════════════════╝"
    echo ""
    echo "  1) 很低 (-100Hz)"
    echo "  2) 较低 (-50Hz)"
    echo "  3) 正常 (0Hz)   ⭐默认"
    echo "  4) 较高 (+50Hz)"
    echo "  5) 很高 (+100Hz)"
    echo "  6) 自定义..."
    echo ""
    read -p "请选择 (1-6): " choice

    case $choice in
        1) PITCH="-100Hz" ;;
        2) PITCH="-50Hz" ;;
        3) PITCH="+0Hz" ;;
        4) PITCH="+50Hz" ;;
        5) PITCH="+100Hz" ;;
        6)
            read -p "请输入音调 (如: +30Hz 或 -20Hz): " custom_pitch
            PITCH="$custom_pitch"
            ;;
        *) echo "❌ 无效选择，保持原配置"; return ;;
    esac

    echo "✅ 音调已设置为: $PITCH"
}

# 生成语音
generate_speech() {
    echo ""
    echo "╔═══════════════════════════════════╗"
    echo "║       📝 输入文本生成语音 📝     ║"
    echo "╚═══════════════════════════════════╝"
    echo ""
    echo "💡 提示: 输入 'q' 返回主菜单"
    echo ""
    read -p "请输入要转换的文字: " text

    if [ "$text" = "q" ] || [ -z "$text" ]; then
        echo "❌ 已取消"
        return
    fi

    # 生成文件名 (使用时间戳)
    timestamp=$(date +"%Y%m%d_%H%M%S")
    output_file="${OUTPUT_DIR}/tts_${timestamp}.wav"

    echo ""
    echo "🎤 开始生成语音..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 调用TTS生成脚本
    python3 scripts/tts_generate.py "$text" "$output_file" "$VOICE" "$RATE" "$VOLUME" "$PITCH"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 语音生成成功！"
        echo "📁 文件: $output_file"
        echo ""
        read -p "是否立即播放？(y/n): " play_choice

        if [ "$play_choice" = "y" ] || [ "$play_choice" = "Y" ]; then
            echo ""
            echo "🎵 正在播放..."
            ./simple_player "$output_file"
            echo ""
            echo "✅ 播放完成！"
        fi
    else
        echo "❌ 语音生成失败！"
    fi

    echo ""
    read -p "按回车键继续..."
}

# 主菜单
main_menu() {
    while true; do
        clear
        echo "╔════════════════════════════════════════════════════════╗"
        echo "║      🎤 Edge-TTS 交互式语音生成工具 🎤              ║"
        echo "║              本小姐的专业作品 (￣▽￣)ノ               ║"
        echo "╚════════════════════════════════════════════════════════╝"

        show_config

        echo "📌 主菜单："
        echo ""
        echo "  1) 🎤 生成语音 (开始转换)"
        echo "  2) 🔊 切换语音类型"
        echo "  3) ⚡ 调整语速"
        echo "  4) 🔈 调整音量"
        echo "  5) 🎵 调整音调"
        echo "  6) 🔄 重置为默认配置"
        echo "  7) ❌ 退出程序"
        echo ""
        read -p "请选择操作 (1-7): " choice

        case $choice in
            1) generate_speech ;;
            2) select_voice ;;
            3) adjust_rate ;;
            4) adjust_volume ;;
            5) adjust_pitch ;;
            6)
                VOICE="xiaoxiao"
                RATE="+0%"
                VOLUME="+0%"
                PITCH="+0Hz"
                echo "✅ 已重置为默认配置"
                sleep 1
                ;;
            7)
                echo ""
                echo "👋 再见，笨蛋！记得常来找本小姐哦～ (*/ω\*)"
                echo ""
                exit 0
                ;;
            *)
                echo "❌ 无效选择，请重新输入"
                sleep 1
                ;;
        esac
    done
}

# 启动程序
main_menu
