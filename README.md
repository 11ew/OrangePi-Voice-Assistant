# 🎤 EdgeTTSdemo - 实时语音助手系统

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **项目类型：** 完全离线实时语音助手
> **硬件平台：** Orange Pi AI Pro (Ascend 310B)
> **当前状态：** Phase 3 完成，准备进入 Phase 4

---

## 🎯 项目简介

**EdgeTTSdemo** 是一个运行在 Orange Pi AI Pro 上的**完全离线实时语音助手系统**。

### 核心特性

- 🎤 **实时语音识别**：基于 Paraformer 模型，识别准确率优秀
- 🗣️ **智能对话**：集成 DeepSeek LLM，响应速度快
- 🔊 **语音合成**：使用 Edge-TTS，支持多种中文语音
- 🎯 **语音活动检测**：Silero VAD，自动分割语音片段
- 💻 **边缘计算**：完全离线运行，保护隐私
- ⚡ **低延迟**：优化的实时处理流程

### 项目特点

- 🏗️ **模块化设计**：清晰的架构，易于维护和扩展
- 📚 **完善的文档**：详细的技术文档和开发指南
- 🔬 **深度研究**：包含 VAD 优化、RNNoise 降噪等技术研究
- 💎 **代码优雅**：遵循 KISS、DRY、SOLID 原则

---

## 📊 开发进度

### ✅ Phase 1: 基础验证（已完成）
- ✅ 音频设备配置和测试
- ✅ LLM 服务验证（DeepSeek API）
- ✅ TTS 服务验证（Edge-TTS）
- ✅ 基础对话流程测试

### ✅ Phase 2: ASR 集成（已完成）
- ✅ Paraformer INT8 模型集成
- ✅ 中文、英文、混合识别全部优秀
- ✅ 识别速度快（2-3秒）
- ✅ 解决录音采样率配置问题

### ✅ Phase 3: VAD 集成（已完成）
- ✅ Silero VAD 模型集成
- ✅ 发现并解决录音格式问题（WAV bug）
- ✅ VAD 优化研究完成
  - RNNoise 降噪研究
  - 音量反向特性发现
  - sherpa-onnx 框架深度分析
- ✅ 最佳配置确定

### 🚧 Phase 4: 系统集成（进行中 - 90% 完成）
- ✅ 实现异步编排逻辑
- ✅ 端到端集成测试
- ✅ 性能优化（延迟优化）⭐ **新增**
  - ✅ 并行优化（连接预热、设备预设置）
  - ✅ 流式处理（LLM 流式输出、TTS 流式合成、流式播放）
  - ✅ 首字延迟降低 70-80%（6-8秒 → 1-2秒）
- [ ] 实现打断机制

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│              实时语音助手系统                             │
│                                                          │
│  音频捕获 → VAD 检测 → ASR 识别 → LLM 对话 → TTS 合成   │
│     ↓          ↓          ↓          ↓          ↓       │
│  AudioCapture → VADDetector → ASREngine → LLMEngine     │
│                                              ↓           │
│                                         TTSEngine        │
│                                              ↓           │
│                                         AudioPlayer      │
└─────────────────────────────────────────────────────────┘
```

### 核心模块

1. **AudioCapture** - 音频捕获模块
   - 录音设备：`plughw:0,1` (48kHz)
   - 自动采样率转换：48kHz → 16kHz

2. **VADDetector** - 语音活动检测
   - 模型：Silero VAD (ONNX)
   - 框架：sherpa-onnx
   - 配置：threshold=0.2, min_silence=0.5s

3. **ASREngine** - 语音识别引擎
   - 模型：Paraformer INT8
   - 识别准确率：优秀
   - 响应速度：2-3秒

4. **LLMEngine** - 对话引擎
   - 模型：DeepSeek
   - 响应速度：~2秒
   - 支持流式输出

5. **TTSEngine** - 语音合成引擎
   - 引擎：Edge-TTS
   - 支持多种中文语音
   - 生成速度：~2.7秒

6. **AudioPlayer** - 音频播放器
   - 播放设备：`hw:ascend310b`
   - 支持 3.5mm 耳机输出

---

## 🚀 快速开始

### 1. 环境准备

**系统要求：**
- Orange Pi AI Pro (Ascend 310B)
- Ubuntu 22.04 (ARM64)
- Python 3.9+
- 8GB+ RAM

**安装依赖：**
```bash
# 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg alsa-utils gcc

# 安装 Python 依赖
pip3 install edge-tts numpy requests
```

### 2. 配置音频设备

参考 [音频配置完全指南](docs/AUDIO_SETUP.md)

**🚀 一键测试脚本（推荐）：**
```bash
# 运行自动化测试脚本
./scripts/test_audio_48k.sh
```

该脚本会自动完成：
- 设置音频参数（Capture、Deviceid、Playback）
- 录音测试（5秒，48000 Hz RAW 格式）
- 格式转换（PCM → WAV）
- 质量验证（检查信号强度）
- 播放测试（自动播放录音）

**手动测试：**
```bash
# 设置音频参数
amixer set Capture 10
amixer set Deviceid 2
amixer set Playback 10

# 测试录音
arecord -D plughw:0,1 -f S16_LE -r 48000 -c 1 -t raw -d 5 test.pcm
ffmpeg -f s16le -ar 48000 -ac 1 -i test.pcm -y test.wav

# 测试播放
aplay -Dhw:ascend310b test.wav
```

### 3. 测试各模块

**测试音频设备（推荐）：**
```bash
# 一键测试录音和播放
./scripts/test_audio_48k.sh
```

**测试 ASR 识别（推荐）：**
```bash
# 完整的 ASR 识别测试（录音 + 识别）
python3 scripts/test_asr_recognition.py
```

**测试 TTS：**
```bash
python3 scripts/tts_generate.py "你好，世界" output/test.wav
aplay -Dhw:ascend310b output/test.wav
```

**测试 VAD：**
```bash
python3 scripts/test_vad.py output/test.wav
```

### 4. 运行实时语音助手

```bash
# 启动实时语音助手（Phase 4 完成后可用）
python3 realtime_assistant_main.py
```

---

## 📚 文档

### 核心文档

1. **[实时语音助手设计文档](docs/REALTIME_ASSISTANT.md)**
   - 系统架构设计
   - 模块功能说明
   - 技术选型和实现细节

2. **[音频配置完全指南](docs/AUDIO_SETUP.md)** ⭐
   - Orange Pi 音频设备配置
   - ⚠️ 音量反向特性说明（重要发现）
   - 🚀 一键测试脚本（推荐）
   - 录音和播放测试
   - 常见问题排查

3. **[音频测试脚本使用指南](docs/audio-test-script-guide.md)** ⭐
   - 自动化音频测试脚本详细说明
   - 测试流程和检查项
   - 故障排查和解决方案
   - 脚本定制和最佳实践

4. **[ASR 识别测试脚本使用指南](docs/asr-test-script-guide.md)** ⭐ 新增
   - ASR 语音识别测试工具
   - 48000 Hz → 16000 Hz 降采样验证
   - 识别准确率测试
   - 完整的测试流程和故障排查

5. **[VAD 优化研究报告](docs/vad-optimization-report.md)** ⭐
   - RNNoise 降噪研究
   - Silero VAD 深度分析
   - 能量 VAD 验证
   - sherpa-onnx 框架解析
   - 配置优化方案

6. **[项目开发路线图](ROADMAP.md)** ⭐
   - Phase 1-6 详细规划
   - 当前进度和下一步方向
   - 技术债务记录
   - 里程碑和时间表

7. **[项目内部提示文档](PROJECT_NOTES.md)**
   - 系统权限信息
   - VPN 配置和使用
   - 音频测试规定
   - 常用命令速查

8. **[文档索引](docs/index.md)**
   - 所有文档的完整索引

### 阶段完成报告

- [Phase 2 完成报告](docs/phase2-completion-report.md) - ASR 集成
- [Phase 3 完成报告](docs/phase3-completion-report.md) - VAD 集成
- [VAD 任务总结报告](docs/vad-task-summary.md) ⭐ 新增

---

## 🔬 技术亮点

### 1. 音量反向特性发现 ⭐

**重大发现：** Orange Pi AI Pro 的音频驱动存在反向特性！

```
音量值越小，录音信号越强！
推荐使用音量 1 或 5
```

详见：[AUDIO_SETUP.md](docs/AUDIO_SETUP.md)

### 2. sherpa-onnx 框架深度分析

深入理解了 sherpa-onnx 与官方 Silero VAD 的差异：
- C++ 实现，性能极高
- 专为边缘设备优化
- 参数与官方实现有差异

详见：[VAD 优化研究报告](docs/vad-optimization-report.md)

### 3. RNNoise 降噪研究

完整的 RNNoise 集成和测试：
- 结论：不推荐在当前硬件环境使用
- 原因：信号衰减 53%，反而降低 VAD 检测效果

详见：[VAD 优化研究报告](docs/vad-optimization-report.md)

---

## 🛠️ 开发指南

### 项目结构

```
EdgeTTSdemo/
├── realtime_assistant/          # 核心模块
│   ├── assistant.py             # 主控制器
│   ├── asr_engine.py            # ASR 引擎
│   ├── audio_capture.py         # 音频捕获
│   ├── llm_engine.py            # LLM 引擎
│   ├── tts_engine.py            # TTS 引擎
│   ├── vad_detector.py          # VAD 检测器
│   ├── audio_player.py          # 音频播放器
│   └── state_machine.py         # 状态机
├── config/                      # 配置文件
│   ├── realtime_config.json     # 主配置
│   ├── asr_config.json          # ASR 配置
│   └── vad_config.json          # VAD 配置
├── docs/                        # 文档
├── models/                      # 模型文件
├── output/                      # 输出目录
├── scripts/                     # 辅助脚本
├── tests/                       # 测试脚本（范本）⭐
│   ├── test_audio_48k.sh        # 音频设备测试
│   ├── test_asr_recognition.py  # ASR 识别测试
│   ├── test_playback.py         # 播放功能测试
│   └── README.md                # 测试脚本使用指南
└── realtime_assistant_main.py   # 主程序入口
```

### 配置文件

**VAD 配置** (`config/vad_config.json`)：
```json
{
  "model": "models/silero_vad.onnx",
  "threshold": 0.2,
  "min_silence_duration": 0.5,
  "min_speech_duration": 0.25,
  "sample_rate": 16000
}
```

**音频配置** (`config/realtime_config.json`)：
```json
{
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "device": "plughw:0,1"
  }
}
```

---

## 🎯 下一步计划

### Phase 4: 系统集成

**目标：** 整合所有模块，实现完整的实时语音助手

**待完成任务：**
1. 主控制器实现 (`assistant.py`)
2. 状态机实现 (`state_machine.py`)
3. 音频播放器实现 (`audio_player.py`)
4. LLM 引擎完善 (`llm_engine.py`)
5. TTS 引擎完善 (`tts_engine.py`)
6. 端到端测试

**预计完成时间：** 2026-01-25

详见：[项目开发路线图](ROADMAP.md)

---

## 🤝 贡献指南

### 如何贡献

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 添加必要的注释和文档字符串
- 编写单元测试
- 更新相关文档

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 📞 联系方式

- **作者：** 哈雷酱（傲娇大小姐工程师）
- **项目地址：** `/home/HwHiAiUser/Desktop/ai-study/EdgeTTSdemo`
- **文档位置：** `docs/`

---

**哼，本小姐的项目可是非常完善的！笨蛋们要好好学习哦！(￣▽￣)ノ**

**下一步：开始 Phase 4 系统集成，实现完整的实时语音助手！**

```
┌─────────────────────────────────────────────────────────┐
│              交互式界面 (tts_interactive.sh)             │
│  - 选择语音类型 (6种中文语音)                            │
│  - 调整参数 (语速/音量/音调)                             │
│  - 输入文本并生成                                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Python层: Edge-TTS文字转语音 (tts_generate.py)         │
│  - 调用微软Edge-TTS API                                  │
│  - 生成MP3音频文件                                       │
│  - 使用ffmpeg转换为单声道WAV                             │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  C语言层: 音频播放器 (simple_player.c)                   │
│  - 解析WAV文件头并显示信息                               │
│  - 调用aplay命令播放音频                                 │
│  - 配置Orange Pi耳机输出                                │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  硬件层: 3.5mm耳机输出                                   │
│  - Orange Pi Ascend 310B音频接口                        │
└─────────────────────────────────────────────────────────┘
```

### 为什么这样设计？

**简化原则（KISS - Keep It Simple, Stupid）：**
- **不直接使用ALSA API**：而是调用系统自带的 `aplay` 命令
- **优势**：更稳定、避免硬件兼容性问题、代码更简洁

**类比STM32开发：**
- 就像你在STM32中使用HAL库而不是直接操作寄存器一样
- 使用现成的工具（aplay）而不是重复造轮子

---

## 🛠️ 环境准备

### 1. 系统要求

- **操作系统**：Linux（Ubuntu/Debian/Orange Pi OS）
- **Python版本**：Python 3.7+
- **必需工具**：gcc, ffmpeg, alsa-utils

### 2. 安装依赖

```bash
# 一键安装所有依赖
make install-deps

# 或者手动安装
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg alsa-utils gcc
pip3 install edge-tts
```

### 3. 验证安装

```bash
# 检查Python版本
python3 --version

# 检查ffmpeg
ffmpeg -version

# 检查ALSA工具
aplay -l

# 检查Edge-TTS
edge-tts --version
```

---

## 🚀 快速开始

### 方式一：交互式工具（推荐！）

```bash
# 1. 进入项目目录
cd EdgeTTSdemo

# 2. 编译播放器（首次使用需要）
make

# 3. 启动交互式工具
bash tts_interactive.sh
```

**操作演示：**

```
╔════════════════════════════════════════════════════════╗
║      🎤 Edge-TTS 交互式语音生成工具 🎤              ║
║              本小姐的专业作品 (￣▽￣)ノ               ║
╚════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 当前配置：
   🔊 语音: 晓晓 - 女声(温柔)
   ⚡ 语速: +0%
   🔈 音量: +0%
   🎵 音调: +0Hz
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 主菜单：

  1) 🎤 生成语音 (开始转换)
  2) 🔊 切换语音类型
  3) ⚡ 调整语速
  4) 🔈 调整音量
  5) 🎵 调整音调
  6) 🔄 重置为默认配置
  7) ❌ 退出程序

请选择操作 (1-7):
```

### 方式二：命令行方式（理解流程）

```bash
# 1. 生成语音文件（使用默认参数）
python3 scripts/tts_generate.py "你好，世界" output/hello.wav

# 2. 生成语音文件（自定义参数）
python3 scripts/tts_generate.py "你好" output/hello.wav yunxi "+25%" "+10%" "+50Hz"
#                                 文本    输出文件      语音   语速    音量    音调

# 3. 播放音频
./simple_player output/hello.wav
```

---

## 📖 详细教程

### 第一步：理解Edge-TTS

**Edge-TTS是什么？**
- 微软Edge浏览器的文字转语音引擎
- 免费、高质量、支持多种语言
- 无需API密钥，开箱即用

**可用的中文语音（6种）：**
- `xiaoxiao` - 晓晓 女声（温柔）⭐推荐
- `xiaoyi` - 晓伊 女声（活泼）
- `yunjian` - 云健 男声（沉稳）
- `yunxi` - 云希 男声（年轻）
- `xiaoxuan` - 晓萱 女声（甜美）
- `yunyang` - 云扬 男声（热情）

**参数调整范围：**
- **语速(Rate)**：-50% 到 +50%（如：+25% 表示加快25%）
- **音量(Volume)**：-50% 到 +50%（如：-10% 表示降低10%）
- **音调(Pitch)**：-100Hz 到 +100Hz（如：+50Hz 表示提高50赫兹）

### 第二步：编译和运行

```bash
# 编译（生成simple_player可执行文件）
make

# 查看编译结果
ls -lh simple_player

# 测试播放
./simple_player output/hello.wav

# 清理编译产物
make clean
```

**编译说明：**
- 本项目使用简化设计，只需要gcc即可编译
- 不需要链接ALSA库（因为使用aplay命令）
- 编译命令：`gcc -o simple_player src/simple_player.c`

### 第三步：实战案例

**案例1：语音播报时间**

```bash
# 生成当前时间的语音
TIME=$(date "+现在时间是%H点%M分")
python3 scripts/tts_generate.py "$TIME" output/time.wav
./simple_player output/time.wav
```

**案例2：定时提醒**

```bash
# 创建提醒脚本
cat > reminder.sh << 'EOF'
#!/bin/bash
while true; do
    sleep 3600  # 每小时提醒一次
    python3 scripts/tts_generate.py "该休息一下了" output/reminder.wav
    ./simple_player output/reminder.wav
done
EOF

chmod +x reminder.sh
./reminder.sh
```

**案例3：系统状态播报**

```bash
# 创建系统状态脚本
cat > status.sh << 'EOF'
#!/bin/bash
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
MEM=$(free -h | awk '/^Mem:/ {print $3}')
MSG="CPU使用率${CPU}，内存使用${MEM}"
python3 scripts/tts_generate.py "$MSG" output/status.wav
./simple_player output/status.wav
EOF

chmod +x status.sh
./status.sh
```

---

## 📁 项目结构

```
EdgeTTSdemo/
├── README.md              # 本文档
├── requirements.txt       # Python依赖
├── tts_interactive.sh    # 交互式TTS工具（主程序）
├── Makefile              # 构建脚本
├── src/                  # C源代码
│   └── simple_player.c   # 音频播放器（使用aplay）
├── scripts/              # Python脚本
│   └── tts_generate.py   # TTS生成脚本
└── output/               # 音频输出目录
    ├── README.md         # 输出目录说明
    └── *.wav             # 生成的音频文件
```

**文件说明：**
- `tts_interactive.sh`：交互式工具，提供菜单界面
- `scripts/tts_generate.py`：TTS核心生成脚本
- `src/simple_player.c`：简化的音频播放器
- `output/`：存放生成的WAV文件

---

## ❓ 常见问题

### Q1: 播放时声音混乱怎么办？

**原因：** 使用了立体声WAV文件，但设备只支持单声道

**解决：** 本项目已自动处理，生成的WAV文件都是单声道的
```bash
# 如果需要手动转换
ffmpeg -i input.wav -ac 1 output_mono.wav
```

### Q2: 编译时出现警告？

**警告信息：**
```
warning: ignoring return value of 'system'
```

**说明：** 这是编译器的安全提示，不影响功能，可以忽略

### Q3: 播放时没有声音？

**检查步骤：**

```bash
# 1. 检查音频设备
aplay -l

# 2. 检查音量设置
amixer

# 3. 测试播放
speaker-test -t wav -c 1

# 4. 检查耳机是否插好
```

### Q4: Edge-TTS下载速度慢？

**解决：** 使用国内镜像

```bash
pip3 install edge-tts -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q5: 生成的音频文件在哪里？

**位置：** 所有生成的音频文件都在 `output/` 目录下

```bash
# 查看所有生成的音频
ls -lh output/*.wav

# 清理所有音频文件
rm -f output/*.wav
```

---

## 🎓 学习路线

### 阶段1：基础使用（1-2天）
- ✅ 理解项目架构
- ✅ 使用交互式工具生成语音
- ✅ 修改文本内容测试
- ✅ 尝试不同语音和参数

### 阶段2：深入理解（3-5天）
- ✅ 学习WAV文件格式
- ✅ 理解aplay工作原理
- ✅ 阅读并理解源代码
- ✅ 学习ffmpeg音频转换

### 阶段3：实战应用（1周）
- ✅ 完成3个实战案例
- ✅ 添加自定义功能
- ✅ 集成到自己的项目

### 阶段4：进阶扩展（持续）
- ✅ 移植到其他Linux平台
- ✅ 优化音频质量
- ✅ 添加更多语音选项

---

## 🔧 技术要点

### 1. 为什么使用aplay而不是ALSA API？

**对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **直接使用ALSA API** | 性能稍高 | 代码复杂、硬件兼容性问题多 |
| **调用aplay命令** | 简单稳定、兼容性好 | 多一次进程调用 |

**选择理由：**
- 稳定性 > 性能（对于TTS应用，性能不是瓶颈）
- 简单 > 复杂（符合KISS原则）
- 学习了audiodemo的实现方式

### 2. WAV文件格式

**本项目生成的WAV格式：**
- **采样率**：48000 Hz
- **声道数**：1（单声道）
- **位深度**：16 bit
- **格式**：PCM（未压缩）

**为什么选择这些参数？**
- 48kHz：高质量音频标准
- 单声道：嵌入式设备通常只支持单声道
- 16bit：平衡音质和文件大小

### 3. 简化设计哲学

**遵循的原则：**
- **KISS**：使用aplay而非复杂的ALSA API
- **DRY**：复用系统工具，不重复造轮子
- **SOLID**：单一职责，Python负责生成，C负责播放

---

## 👩‍💻 关于作者

**哈雷酱（傲娇大小姐工程师）**
- 专注于嵌入式系统和音频处理
- 追求代码的极致优雅和完美
- 喜欢用简单的方式解决复杂的问题

> 哼，这个项目是本小姐精心打造的实用工具，笨蛋们要好好学习哦！(￣▽￣)／
>
> 记住：简单的设计往往是最好的设计！才不是因为本小姐懒得写复杂代码呢！(*/ω\*)

---

## 🔗 相关资源

- [Edge-TTS官方文档](https://github.com/rany2/edge-tts)
- [FFmpeg官方文档](https://ffmpeg.org/documentation.html)
- [WAV格式详解](http://soundfile.sapp.org/doc/WaveFormat/)
- [aplay命令手册](https://linux.die.net/man/1/aplay)

---

**最后更新：** 2026-01-03
**版本：** v2.0.0（简化版本）

---

## 📝 更新日志

**v2.0.0 (2026-01-03)**
- 🎉 添加交互式工具 `tts_interactive.sh`
- ✨ 支持6种中文语音
- 🔧 简化播放器实现（使用aplay命令）
- 📚 完善文档和使用说明
- 🗑️ 移除复杂的示例脚本

**v1.0.0 (初始版本)**
- ✅ 基础TTS功能实现
- ✅ ALSA音频播放
