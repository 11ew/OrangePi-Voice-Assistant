# EdgeTTSdemo项目结构说明

本小姐精心设计的项目结构，每个文件都有它的用途哦！(￣▽￣)ノ

## 📁 目录结构

```
EdgeTTSdemo/
│
├── README.md                 # 项目总览和快速开始指南
├── requirements.txt          # Python依赖列表
├── Makefile                  # C程序构建脚本
├── quickstart.sh            # 一键快速开始脚本
│
├── docs/                    # 📖 文档目录
│   ├── getting-started.md   # 新手入门指南（必读！）
│   └── tutorial.md          # 进阶教程（深入学习）
│
├── src/                     # 🔧 C源代码目录
│   ├── audio_utils.h        # ALSA音频工具头文件
│   ├── audio_utils.c        # ALSA音频工具实现
│   └── simple_player.c      # 简单音频播放器
│
├── scripts/                 # 🐍 Python脚本目录
│   └── tts_generate.py      # Edge-TTS文字转语音脚本
│
├── examples/                # 💡 实战案例目录
│   ├── README.md            # 案例集说明
│   ├── 01_voice_clock.sh    # 智能语音时钟
│   ├── 02_system_monitor.sh # 系统状态播报
│   ├── 03_timer_reminder.sh # 定时提醒助手
│   ├── 04_compare_voices.sh # 语音对比工具
│   ├── 05_batch_generate.sh # 批量语音生成
│   └── 06_temp_monitor.sh   # 温度监控报警
│
└── output/                  # 📦 输出目录（音频文件）
    └── (生成的WAV文件)
```

## 📝 文件说明

### 核心文件

#### README.md
- **作用：** 项目总览，快速开始指南
- **适合：** 所有用户
- **内容：** 项目简介、技术架构、环境准备、快速开始

#### requirements.txt
- **作用：** Python依赖包列表
- **内容：** `edge-tts` （目前只有这一个依赖）

#### Makefile
- **作用：** C程序构建脚本
- **命令：**
  - `make` - 编译程序
  - `make clean` - 清理编译文件
  - `make test` - 运行测试
  - `make install-deps` - 安装依赖

#### quickstart.sh
- **作用：** 一键快速开始脚本
- **功能：** 检查依赖、编译、生成测试音频、播放

---

### 文档目录 (docs/)

#### getting-started.md
- **目标人群：** 新手、初学者
- **内容：**
  - 5步学习路线
  - 环境准备详细步骤
  - 快速测试
  - 基础练习
  - 常见问题解答

#### tutorial.md
- **目标人群：** 有一定基础的学习者
- **内容：**
  - 从STM32到Linux的知识迁移
  - WAV文件格式详解
  - ALSA音频编程原理
  - Edge-TTS深入使用
  - 实战案例集
  - 性能优化技巧

---

### 源代码目录 (src/)

#### audio_utils.h
- **作用：** ALSA音频工具头文件
- **定义：**
  - WAV文件头结构体 (`wav_header_t`)
  - 音频配置结构体 (`audio_config_t`)
  - 函数声明

#### audio_utils.c
- **作用：** ALSA音频工具实现
- **功能：**
  - WAV文件头解析
  - ALSA设备初始化
  - 音频数据播放
  - 错误恢复机制

#### simple_player.c
- **作用：** 简单音频播放器主程序
- **流程：**
  1. 读取WAV文件头
  2. 初始化ALSA设备
  3. 播放音频数据
  4. 显示进度
  5. 清理资源

---

### Python脚本目录 (scripts/)

#### tts_generate.py
- **作用：** Edge-TTS文字转语音生成脚本
- **功能：**
  - 调用Edge-TTS API
  - 生成MP3音频
  - 转换为单声道WAV格式
  - 支持多种中文语音
  - 可调参数（语速、音量、音调）

**用法：**
```bash
python3 scripts/tts_generate.py "文本" 输出文件 [语音类型]
```

---

### 实战案例目录 (examples/)

所有案例都是可直接运行的Shell脚本，每个案例都有详细注释。

#### 01_voice_clock.sh
- **难度：** ⭐
- **功能：** 每小时语音播报时间
- **学习点：** 定时循环、时间获取

#### 02_system_monitor.sh
- **难度：** ⭐⭐
- **功能：** 定期播报系统状态（CPU、内存、温度）
- **学习点：** 系统信息获取、文本处理

#### 03_timer_reminder.sh
- **难度：** ⭐⭐
- **功能：** 定时提醒
- **学习点：** 数组使用、时间比对

#### 04_compare_voices.sh
- **难度：** ⭐
- **功能：** 对比不同语音效果
- **学习点：** 数组遍历、用户交互

#### 05_batch_generate.sh
- **难度：** ⭐⭐⭐
- **功能：** 批量生成语音
- **学习点：** 文件读取、批量处理

#### 06_temp_monitor.sh
- **难度：** ⭐⭐⭐
- **功能：** 温度监控报警
- **学习点：** 实时监控、状态机

---

### 输出目录 (output/)

- **作用：** 存放生成的音频文件
- **格式：** WAV（单声道、48kHz、16bit）
- **特点：** 可以安全删除，会自动重新生成

---

## 🎯 文件使用建议

### 新手路线

1. **第1天：** 阅读 `README.md` 和 `docs/getting-started.md`
2. **第2天：** 运行 `quickstart.sh` 和简单案例
3. **第3-7天：** 阅读 `docs/tutorial.md`，运行所有案例

### 进阶路线

1. **第1周：** 修改 `examples/` 中的案例
2. **第2周：** 研究 `src/` 中的C代码
3. **第3周：** 优化 `scripts/tts_generate.py`
4. **持续：** 集成到自己的项目

---

## 🔧 可修改的配置

### Python层配置
- `scripts/tts_generate.py` 第16-19行：默认语音参数
- `scripts/tts_generate.py` 第22-27行：可用语音列表

### C层配置
- `src/audio_utils.c` 第143行：音频设备名称
- `src/audio_utils.c` 第197-198行：音量设置
- `src/simple_player.c` 第26行：缓冲区大小

---

## 📊 文件依赖关系

```
quickstart.sh
    ├── Makefile
    │   └── src/*.c
    └── scripts/tts_generate.py

examples/*.sh
    ├── scripts/tts_generate.py
    └── simple_player (编译后的可执行文件)

simple_player
    ├── src/simple_player.c
    └── src/audio_utils.c + audio_utils.h
```

---

## 💡 本小姐的设计理念

1. **模块化：** 每个文件职责单一，易于理解和维护
2. **可复用：** `audio_utils.c/.h` 可以直接复用到其他项目
3. **渐进式：** 从简单到复杂，适合不同水平的学习者
4. **实践导向：** 提供大量可运行的示例

---

**版本：** v1.0
**更新日期：** 2026-01-03
**作者：** 哈雷酱（傲娇大小姐工程师）

> 哼，这个结构是本小姐精心设计的，简洁又优雅！(￣▽￣)ノ
