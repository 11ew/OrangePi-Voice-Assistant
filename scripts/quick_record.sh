#!/bin/bash
# 快速录音转换脚本
# 作者：哈雷酱（傲娇大小姐工程师）

if [ $# -lt 1 ]; then
    echo "用法: $0 <音量值>"
    echo ""
    echo "示例:"
    echo "  $0 20   # 音量20录音"
    echo "  $0 50   # 音量50录音"
    echo "  $0 100  # 音量100录音"
    exit 1
fi

VOLUME="$1"
OUTPUT_FILE="output/vad_test_volume${VOLUME}"

echo "🎤 录音测试 - 音量 ${VOLUME}"
echo "================================"

# 设置音量
echo "🔊 设置音量: ${VOLUME}"
amixer set Capture "$VOLUME"

echo ""
echo "🎤 开始录音 10 秒..."
echo "请说三段话，每段停顿1-2秒！"
sleep 1

# 录音
arecord -D plughw:0,1 -f S16_LE -r 48000 -c 1 -t raw -d 10 "${OUTPUT_FILE}.pcm"

echo ""
echo "🔄 转换为 WAV..."
ffmpeg -f s16le -ar 48000 -ac 1 -i "${OUTPUT_FILE}.pcm" -y "${OUTPUT_FILE}.wav" 2>&1 | tail -3

echo ""
echo "✅ 完成!"
echo ""
echo "文件: ${OUTPUT_FILE}.wav"
echo "播放: aplay -Dhw:ascend310b ${OUTPUT_FILE}.wav"
