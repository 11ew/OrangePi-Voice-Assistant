#!/bin/bash
# -*- coding: utf-8 -*-
#
# 下载多语言 Whisper 模型
# 支持：中文、英文混合识别
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
MODEL_NAME="sherpa-onnx-whisper-tiny"
MODEL_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-tiny.tar.bz2"
MODEL_DIR="models/sherpa-onnx-whisper-tiny"
TEMP_FILE="/tmp/${MODEL_NAME}.tar.bz2"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║     📦 下载多语言 Whisper 模型 (中英文)              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# 检查是否已经下载
if [ -d "$MODEL_DIR" ]; then
    echo -e "${YELLOW}⚠️  模型目录已存在: $MODEL_DIR${NC}"
    echo -e "${YELLOW}是否重新下载？(y/N)${NC}"
    read -r response
    if [ ! "$response" = "y" ] && [ ! "$response" = "Y" ]; then
        echo -e "${GREEN}✅ 保留现有模型${NC}"
        exit 0
    fi
    echo -e "${YELLOW}🗑️  删除旧模型...${NC}"
    rm -rf "$MODEL_DIR"
fi

# 创建模型目录
mkdir -p models

echo -e "${CYAN}📥 开始下载...${NC}"
echo -e "${BLUE}URL: $MODEL_URL${NC}"
echo ""

# 下载模型
if command -v wget &> /dev/null; then
    wget -O "$TEMP_FILE" "$MODEL_URL"
elif command -v curl &> /dev/null; then
    curl -L -o "$TEMP_FILE" "$MODEL_URL"
else
    echo -e "${RED}❌ 错误: 需要 wget 或 curl${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}📦 解压模型...${NC}"
echo ""

# 解压模型
cd models
tar xjf "$TEMP_FILE"

# 清理临时文件
rm -f "$TEMP_FILE"

echo ""
echo -e "${GREEN}✅ 模型下载完成！${NC}"
echo ""

# 显示模型信息
echo -e "${CYAN}📊 模型信息:${NC}"
echo -e "   目录: ${GREEN}$MODEL_DIR${NC}"
du -sh "$MODEL_DIR" | sed 's/^/   大小: /'
echo ""

# 列出文件
echo -e "${CYAN}📁 模型文件:${NC}"
ls -lh "$MODEL_DIR" | tail -n +2 | awk '{print "   " $9 " (" $5 ")"}'
echo ""

echo -e "${GREEN}🎉 现在可以使用中英文混合识别了！${NC}"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo -e "   - 中文识别: language = zh"
echo -e "   - 英文识别: language = en"
echo -e "   - 中英文混合: language = zh (Whisper 会自动检测)"
echo ""
