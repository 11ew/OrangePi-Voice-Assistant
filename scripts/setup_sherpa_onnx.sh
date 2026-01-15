#!/bin/bash
# -*- coding: utf-8 -*-
#
# Sherpa-ONNX 依赖安装和模型下载脚本
# 作者：哈雷酱（傲娇大小姐工程师）
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║      🚀 Sherpa-ONNX 安装和模型下载脚本 🚀          ║"
echo "║              本小姐的专业作品 (￣▽￣)ノ               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# 创建模型目录
MODELS_DIR="models"
mkdir -p "$MODELS_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📦 步骤 1/3: 安装 Python 依赖${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}正在安装 sherpa-onnx...${NC}"
pip3 install sherpa-onnx -i https://pypi.tuna.tsinghua.edu.cn/simple

echo -e "${YELLOW}正在安装音频处理库...${NC}"
pip3 install numpy soundfile -i https://pypi.tuna.tsinghua.edu.cn/simple

echo -e "${GREEN}✅ Python 依赖安装完成！${NC}"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📥 步骤 2/3: 下载 Whisper 模型${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Whisper tiny 模型（推荐，速度快）
MODEL_NAME="sherpa-onnx-whisper-tiny.en"
MODEL_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/${MODEL_NAME}.tar.bz2"
MODEL_DIR="$MODELS_DIR/$MODEL_NAME"

if [ -d "$MODEL_DIR" ]; then
    echo -e "${GREEN}✅ 模型已存在: $MODEL_DIR${NC}"
else
    echo -e "${YELLOW}正在下载 Whisper tiny 模型...${NC}"
    echo -e "${CYAN}模型大小: 约 40MB${NC}"
    echo -e "${CYAN}下载地址: $MODEL_URL${NC}"
    echo ""

    cd "$MODELS_DIR"

    # 下载模型
    if command -v wget &> /dev/null; then
        wget -c "$MODEL_URL"
    elif command -v curl &> /dev/null; then
        curl -L -O "$MODEL_URL"
    else
        echo -e "${RED}❌ 错误: 未找到 wget 或 curl 命令${NC}"
        exit 1
    fi

    # 解压模型
    echo -e "${YELLOW}正在解压模型...${NC}"
    tar -xjf "${MODEL_NAME}.tar.bz2"

    # 删除压缩包
    rm -f "${MODEL_NAME}.tar.bz2"

    cd ..

    echo -e "${GREEN}✅ 模型下载完成: $MODEL_DIR${NC}"
fi

echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📝 步骤 3/3: 创建配置文件${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 创建配置目录
CONFIG_DIR="config"
mkdir -p "$CONFIG_DIR"

# 创建 ASR 配置文件
ASR_CONFIG="$CONFIG_DIR/asr_config.json"

cat > "$ASR_CONFIG" << 'EOF'
{
  "provider": "sherpa-onnx",
  "model_dir": "models/sherpa-onnx-whisper-tiny.en",
  "language": "zh",
  "num_threads": 4,
  "decoding_method": "greedy_search"
}
EOF

echo -e "${GREEN}✅ 配置文件已创建: $ASR_CONFIG${NC}"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 安装完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${CYAN}📊 安装信息：${NC}"
echo -e "  模型目录: ${GREEN}$MODEL_DIR${NC}"
echo -e "  配置文件: ${GREEN}$ASR_CONFIG${NC}"
echo -e "  模型大小: ${GREEN}约 40MB${NC}"
echo ""

echo -e "${CYAN}🚀 下一步：${NC}"
echo -e "  1. 运行 ${GREEN}bash test_record.sh${NC} 测试录音"
echo -e "  2. 运行 ${GREEN}bash voice_chat_v2.sh${NC} 开始语音对话"
echo ""

echo -e "${YELLOW}> 哼，安装完成了！笨蛋快去测试吧！(￣▽￣)ノ${NC}"
echo -e "${YELLOW}> —— 哈雷酱 (傲娇大小姐工程师)${NC}"
echo ""
