# Makefile for Edge-TTS Demo
# Author: 哈雷酱(本小姐)
# Date: 2026-01-03

# 编译器和标志
CC = gcc
CFLAGS = -Wall -O2 -I./src
LDFLAGS = -lasound

# 源文件和目标文件
SRC_DIR = src
SOURCES = $(SRC_DIR)/simple_player.c $(SRC_DIR)/audio_utils.c
TARGET = simple_player

# 默认目标
all: $(TARGET)
	@echo "✅ 编译完成！"
	@echo "📝 使用方法: ./$(TARGET) <WAV文件>"
	@echo "📝 示例: ./$(TARGET) output/hello.wav"

# 编译目标
$(TARGET): $(SOURCES)
	@echo "🔨 正在编译 $(TARGET)..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)

# 清理
clean:
	@echo "🗑️  清理编译文件..."
	rm -f $(TARGET)
	@echo "✅ 清理完成！"

# 测试
test: $(TARGET)
	@echo "🧪 运行测试..."
	@if [ -f output/test.wav ]; then \
		./$(TARGET) output/test.wav; \
	else \
		echo "❌ 测试文件不存在，请先运行: python3 scripts/tts_generate.py '测试' output/test.wav"; \
	fi

# 安装依赖
install-deps:
	@echo "📦 安装系统依赖..."
	sudo apt update
	sudo apt install -y python3 python3-pip ffmpeg alsa-utils libasound2-dev gcc make
	pip3 install edge-tts
	@echo "✅ 依赖安装完成！"

# 帮助
help:
	@echo "Edge-TTS Demo Makefile"
	@echo ""
	@echo "可用目标:"
	@echo "  make              - 编译程序"
	@echo "  make clean        - 清理编译文件"
	@echo "  make test         - 运行测试"
	@echo "  make install-deps - 安装依赖"
	@echo "  make help         - 显示此帮助"

.PHONY: all clean test install-deps help
