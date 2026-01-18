# EdgeTTSdemo 实时语音助手系统 - Brownfield 架构文档

> **文档类型：** 架构文档 (Architecture Document)
> **项目类型：** Brownfield（现有项目重建）
> **版本：** v1.0.0
> **创建日期：** 2026-01-18
> **作者：** 哈雷酱（傲娇大小姐工程师）

---

## 📋 文档说明

本文档记录 EdgeTTSdemo 项目的**真实状态**，包括：
- 已有的代码和配置
- 技术债务和已知问题
- 待验证和待实现的功能
- 实际的技术约束

**重要：** 这不是理想化的架构文档，而是反映项目当前真实情况的参考文档。

### 文档范围

根据 PRD 文档，本文档聚焦于：
- 实时语音助手系统的重建
- 各模块的验证和集成
- 从基础到完整系统的逐步实施

### 变更日志

| 日期 | 版本 | 描述 | 作者 |
|------|------|------|------|
| 2026-01-18 | 1.0 | 初始 brownfield 分析 | 哈雷酱 |
| 2026-01-18 | 1.1 | Phase 1 完成后更新 - 音频、LLM、TTS 已验证 | 哈雷酱 |
| 2026-01-18 | 1.2 | Phase 2 完成后更新 - ASR 集成完成 | 哈雷酱 |
| 2026-01-18 | 1.3 | Phase 3 完成后更新 - VAD 集成完成 | 哈雷酱 |

---

## 🗂️ 快速参考 - 关键文件和入口点

### 关键文件列表

#### 配置文件
- **主配置**: `config/realtime_config.json` - 系统主配置
- **ASR 配置**: `config/asr_config.json` - 语音识别配置
- **VAD 配置**: `config/vad_config.json` - 语音检测配置

#### 核心脚本（独立功能）
- **LLM 对话**: `scripts/deepseek_chat.py` - DeepSeek API 调用
- **TTS 生成**: `scripts/tts_generate.py` - Edge-TTS 语音合成
- **音频录音**: `scripts/audio_record.py` - 录音功能
- **ASR 识别**: `scripts/speech_to_text.py` - 语音识别
- **VAD 测试**: `scripts/test_vad_simple.py` - Silero VAD 测试
- **能量 VAD**: `scripts/test_vad_energy.py` - 基于能量的 VAD 测试
- **VAD 集成**: `scripts/test_vad_record.sh` - VAD + 录音集成测试

#### 实时助手模块
- **主入口**: `realtime_assistant_main.py` - 系统启动入口
- **主控制器**: `realtime_assistant/assistant.py` - 异步编排
- **VAD 检测器**: `realtime_assistant/vad_detector.py` - 语音活动检测
- **ASR 引擎**: `realtime_assistant/asr_engine.py` - 语音识别引擎
- **LLM 引擎**: `realtime_assistant/llm_engine.py` - 对话引擎
- **TTS 引擎**: `realtime_assistant/tts_engine.py` - 语音合成引擎
- **音频播放器**: `realtime_assistant/audio_player.py` - 音频播放
- **音频捕获**: `realtime_assistant/audio_capture.py` - 音频捕获
- **状态机**: `realtime_assistant/state_machine.py` - 状态管理
- **工具函数**: `realtime_assistant/utils.py` - 通用工具

#### 文档
- **PRD**: `docs/prd.md` - 产品需求文档
- **音频配置**: `docs/AUDIO_SETUP.md` - 音频设备配置教程（含录音问题解决方案）
- **系统设计**: `docs/REALTIME_ASSISTANT.md` - 系统设计文档
- **快速开始**: `QUICKSTART_REALTIME.md` - 快速开始指南
- **Story 1.1**: `docs/stories/1.1-audio-device-setup.md` - 音频设备配置故事
- **Phase 2 报告**: `docs/phase2-completion-report.md` - ASR 集成完成报告
- **Phase 3 报告**: `docs/phase3-completion-report.md` - VAD 集成完成报告

### PRD 相关 - 重建影响区域

根据 PRD，重建工作将按以下顺序进行：

**Phase 1: 基础验证** ✅ **已完成！**
- ✅ 音频设备配置（Story 1.1）- 完成
- ✅ LLM 服务测试 - 完成
- ✅ TTS 服务测试 - 完成
- ✅ 基础对话流程测试 - 完成

**Phase 2: ASR 集成** ✅ **已完成！**
- ✅ ASR 模型下载和配置 - 完成
- ✅ ASR 功能测试 - 完成
- ✅ 录音 + ASR 集成 - 完成

**Phase 3: VAD 集成** ✅ **已完成！**
- ✅ VAD 模型下载和配置 - 完成
- ✅ VAD 功能测试 - 完成
- ✅ VAD + 录音集成 - 完成
- ✅ 开发基于能量的 VAD 算法 - 完成

**Phase 4: 系统集成**
- 异步编排实现
- 端到端集成测试
- 打断机制实现

---

## 🏗️ 高层架构

### 技术概要

EdgeTTSdemo 是一个基于 Python AsyncIO 的实时语音助手系统，运行在 Orange Pi AI Pro (Ascend 310B) 开发板上。

**设计理念：**
- 模块化设计，职责清晰
- 异步事件驱动，性能优异
- 本地 + 云端混合架构
- 完全免费的云端服务

### 实际技术栈

| 类别 | 技术 | 版本 | 状态 | 备注 |
|------|------|------|------|------|
| **运行时** | Python | 3.8+ | ✅ 可用 | 系统已安装 |
| **异步框架** | AsyncIO | 内置 | ✅ 可用 | Python 标准库 |
| **VAD** | Silero VAD | latest | ✅ 已验证 | 模型 629KB，适合安静环境 |
| **VAD (备选)** | 基于能量的 VAD | - | ✅ 已开发 | 适合有底噪环境 |
| **ASR** | Paraformer INT8 | latest | ✅ 已验证 | 识别准确率优秀 |
| **LLM** | DeepSeek API | deepseek-chat | ✅ 已验证 | 平均响应 2.2秒 |
| **TTS** | Edge-TTS | ≥6.1.0 | ✅ 已验证 | 平均生成 2.7秒 |
| **音频捕获** | ALSA (arecord) | v1.2.6 | ✅ 已验证 | 必须使用 RAW 格式 ⚠️ |
| **音频播放** | aplay (ALSA) | v1.2.6 | ✅ 已验证 | 清晰无杂音 |
| **音频处理** | ffmpeg | 系统自带 | ✅ 可用 | 用于格式转换 |

### 仓库结构

**类型：** 单仓库 (Monorepo)
**包管理器：** pip

---

## 📁 源代码树和模块组织

### 项目结构（实际）

```
EdgeTTSdemo/
├── config/                      # 配置文件目录
│   ├── realtime_config.json    # 主配置文件 ✅
│   ├── asr_config.json          # ASR 配置 ✅
│   └── vad_config.json          # VAD 配置 ✅
│
├── scripts/                     # 独立功能脚本
│   ├── deepseek_chat.py        # LLM 对话脚本 ✅ 已验证
│   ├── tts_generate.py         # TTS 生成脚本 ✅ 已验证
│   ├── test_basic_conversation.sh  # 对话流程测试 ✅ 新建
│   ├── speech_to_text.py       # ASR 识别脚本 ✅ 已验证
│   ├── test_vad_simple.py      # Silero VAD 测试 ✅ 新建
│   ├── test_vad_energy.py      # 基于能量的 VAD ✅ 新建
│   ├── test_vad_record.sh      # VAD + 录音集成 ✅ 新建
│   ├── test_record_asr.sh      # 录音 + ASR 集成 ✅ 新建
│   ├── language_detector.py    # 语言检测 ✅
│   └── setup_sherpa_onnx.sh    # sherpa-onnx 安装脚本 ✅
│
├── realtime_assistant/          # 实时助手模块
│   ├── __init__.py             # 模块初始化 ✅
│   ├── assistant.py            # 主控制器 ❓ 待验证
│   ├── vad_detector.py         # VAD 检测器 ✅ 已验证
│   ├── asr_engine.py           # ASR 引擎 ✅ 已验证
│   ├── llm_engine.py           # LLM 引擎 ❓ 待验证
│   ├── tts_engine.py           # TTS 引擎 ❓ 待验证
│   ├── audio_player.py         # 音频播放器 ❓ 待验证
│   ├── audio_capture.py        # 音频捕获 ❓ 待验证
│   ├── state_machine.py        # 状态机 ✅
│   └── utils.py                # 工具函数 ✅
│
├── realtime_assistant_main.py   # 主程序入口 ✅
│
├── models/                      # 模型文件目录
│   └── sherpa-onnx-streaming-paraformer-bilingual-zh-en/
│       └── (模型文件) ❓ 可能未下载
│
├── docs/                        # 文档目录
│   ├── prd.md                  # PRD 文档 ✅ 已更新
│   ├── AUDIO_SETUP.md          # 音频配置教程 ✅ 已更新
│   ├── REALTIME_ASSISTANT.md   # 系统设计文档 ✅
│   ├── brownfield-architecture.md  # 本文档 ✅
│   ├── implementation-plan.md  # 实施计划 ✅
│   ├── index.md                # 文档索引 ✅
│   ├── phase2-completion-report.md  # Phase 2 报告 ✅
│   ├── phase3-completion-report.md  # Phase 3 报告 ✅
│   ├── stories/                # 故事文件目录
│   │   └── 1.1-audio-device-setup.md  ✅ 新建
│   └── qa/                     # QA 目录
│       └── gates/              # 质量门控目录
│           └── 1.1-audio-device-setup.yml  ✅ 新建
│
├── output/                      # 输出目录
│   └── (生成的音频文件)
│
├── requirements.txt             # Python 依赖（基础）✅
├── requirements_realtime.txt    # 实时助手依赖 ✅
├── README.md                    # 项目说明 ✅
└── QUICKSTART_REALTIME.md       # 快速开始指南 ✅
```

### 关键模块及其用途

#### 1. 配置模块 (`config/`)
- **用途：** 存储所有配置文件
- **状态：** ✅ 配置文件完整
- **注意：** API Key 已硬编码，生产环境需要改为环境变量

#### 2. 独立脚本 (`scripts/`)
- **用途：** 提供独立的功能测试脚本
- **状态：** ✅ 代码完整，❓ 功能待验证
- **注意：** 这些脚本可以独立运行，用于测试各个模块

#### 3. 实时助手模块 (`realtime_assistant/`)
- **用途：** 核心的实时语音助手系统
- **状态：** ✅ 代码结构完整，❓ 功能待验证
- **注意：** 需要逐个模块验证和测试

#### 4. 模型目录 (`models/`)
- **用途：** 存储 ASR 和 VAD 模型
- **状态：** ❓ 模型可能未下载
- **注意：** 需要下载 Paraformer 和 Silero VAD 模型

---

## 🔧 数据模型和 API

### 配置数据模型

#### 主配置 (`config/realtime_config.json`)

```json
{
  "vad": {
    "enabled": true,
    "config_file": "config/vad_config.json"
  },
  "asr": {
    "config_file": "config/asr_config.json",
    "model_type": "paraformer",
    "use_streaming": true,
    "num_threads": 4
  },
  "llm": {
    "api_key": "sk-8729b6bbc81b49bda752005da63185c6",  // ⚠️ 硬编码
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "timeout": 10,
    "max_retries": 3
  },
  "tts": {
    "voice_zh": "zh-CN-XiaoxiaoNeural",
    "voice_en": "en-US-JennyNeural",
    "rate": "+0%",
    "volume": "+0%"
  },
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1600,
    "device": "plughw:0,1"  // ✅ 已验证正确
  }
}
```

#### ASR 配置 (`config/asr_config.json`)

```json
{
  "provider": "sherpa-onnx",
  "model_type": "paraformer",
  "model_dir": "models/sherpa-onnx-streaming-paraformer-bilingual-zh-en",
  "language": "auto",
  "num_threads": 4,
  "use_npu": false  // ⚠️ NPU 加速未启用
}
```

### API 规范

#### DeepSeek API

- **端点**: `https://api.deepseek.com/v1/chat/completions`
- **认证**: Bearer Token
- **文件**: `scripts/deepseek_chat.py:14-16`
- **状态**: ✅ 已验证 - 平均响应时间 2.2秒

#### Edge-TTS API

- **库**: `edge-tts` Python 包
- **文件**: `scripts/tts_generate.py`
- **状态**: ✅ 已验证 - 平均生成时间 2.7秒

---

## ⚠️ 技术债务和已知问题

### 关键技术债务

#### 1. API Key 硬编码 (高优先级)
- **位置**:
  - `scripts/deepseek_chat.py:14`
  - `config/realtime_config.json:13`
- **问题**: API Key 直接写在代码和配置文件中
- **风险**: 安全风险，不适合生产环境
- **建议**: 改为环境变量或密钥管理系统

#### 2. 音频设备配置硬编码 (已解决)
- **位置**: `config/realtime_config.json:247`
- **状态**: ✅ 已验证 - 设备名称 `plughw:0,1` 在 Orange Pi AI Pro 上正常工作
- **测试结果**: 录音和播放功能正常，音质清晰无杂音
- **备注**: 如需在其他硬件上运行，可能需要调整设备名称

#### 3. 模型文件未验证 (高优先级)
- **位置**: `models/` 目录
- **问题**: ASR 和 VAD 模型可能未下载
- **风险**: 系统无法启动
- **建议**: 添加模型检查和自动下载脚本

#### 4. 错误处理不完善 (中优先级)
- **位置**: 多个模块
- **问题**: 部分模块缺少完善的错误处理
- **风险**: 系统可能因异常而崩溃
- **建议**: 添加统一的错误处理机制

#### 5. 日志系统简单 (低优先级)
- **位置**: `realtime_assistant/utils.py`
- **问题**: 日志系统功能简单
- **风险**: 调试困难
- **建议**: 增强日志功能，添加日志轮转

### 已知问题和限制

#### 1. 音频设备兼容性 (已解决)
- **问题**: Orange Pi 音频配置复杂，容易出错
- **影响**: 录音和播放可能失败
- **解决方案**: 已有详细配置教程 (`docs/AUDIO_SETUP.md`)
- **状态**: ✅ Story 1.1 已完成 - 音频设备配置和测试通过

#### 2. ASR 识别准确率
- **问题**: 识别准确率依赖模型质量和音频质量
- **影响**: 可能出现识别错误
- **解决方案**: 使用高质量模型，优化音频采集
- **状态**: 待验证

#### 3. 系统延迟
- **问题**: 多个模块串行处理导致延迟
- **影响**: 用户体验不佳
- **解决方案**: 使用异步并行处理
- **状态**: 已实现异步框架，待优化

#### 4. NPU 加速未启用
- **问题**: ASR 配置中 `use_npu: false`
- **影响**: 性能未充分利用硬件
- **解决方案**: 验证 NPU 支持后启用
- **状态**: 待验证

---

## 🔗 集成点和外部依赖

### 外部服务

| 服务 | 用途 | 集成类型 | 关键文件 | 状态 |
|------|------|---------|---------|------|
| **DeepSeek API** | LLM 对话 | REST API | `scripts/deepseek_chat.py` | ✅ 已验证 |
| **Edge-TTS** | 语音合成 | Python SDK | `scripts/tts_generate.py` | ✅ 已验证 |

### 内部集成点

#### 1. 音频设备集成
- **类型**: 硬件集成
- **接口**: ALSA (Advanced Linux Sound Architecture)
- **文件**: 录音使用 `arecord`，播放使用 `aplay`
- **状态**: ✅ 已验证 - 录音和播放功能正常
- **配置**: 录音设备 `plughw:0,1`，播放设备 `hw:ascend310b`

#### 2. 模型文件集成
- **类型**: 文件系统集成
- **位置**: `models/` 目录
- **文件**: ASR 和 VAD 模型文件
- **状态**: ❓ 待验证
- **注意**: 模型文件较大，需要确保下载完整

#### 3. 模块间通信
- **类型**: 异步消息传递
- **机制**: Python AsyncIO Queue
- **文件**: `realtime_assistant/assistant.py`
- **状态**: ✅ 框架已实现，待验证

---

## 🚀 开发和部署

### 本地开发设置

#### 实际步骤（已验证）

1. **克隆仓库**
   ```bash
   cd /home/HwHiAiUser/Desktop/ai-study/EdgeTTSdemo
   ```

2. **安装基础依赖**
   ```bash
   pip3 install -r requirements.txt
   pip3 install -r requirements_realtime.txt
   ```

3. **安装 sherpa-onnx**
   ```bash
   bash scripts/setup_sherpa_onnx.sh
   ```

4. **下载模型文件**（待验证）
   ```bash
   # ASR 模型
   bash scripts/download_multilingual_model.sh

   # VAD 模型（需要手动下载）
   wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx \
     -O models/silero_vad.onnx
   ```

5. **配置音频设备**（Story 1.1）
   - 参考 `docs/AUDIO_SETUP.md`
   - 配置录音设备：`plughw:0,1`
   - 配置播放设备：`hw:ascend310b`

6. **测试各个模块**
   ```bash
   # 测试 LLM
   python3 scripts/deepseek_chat.py "你好"

   # 测试 TTS
   python3 scripts/tts_generate.py "你好" output/test.wav

   # 测试录音（需要先配置音频设备）
   python3 scripts/audio_record.py

   # 测试 ASR（需要先下载模型）
   python3 scripts/speech_to_text.py output/test.wav
   ```

### 已知设置问题

#### 1. 音频设备权限
- **问题**: 可能需要 sudo 权限访问音频设备
- **解决**: 将用户添加到 `audio` 组
  ```bash
  sudo usermod -a -G audio $USER
  ```

#### 2. 模型下载失败
- **问题**: 网络问题导致模型下载失败
- **解决**: 使用 VPN 或手动下载
  ```bash
  vpn        # 开启 VPN
  # 下载模型
  vpnoff     # 关闭 VPN
  ```

#### 3. 依赖冲突
- **问题**: Python 包版本冲突
- **解决**: 使用虚拟环境
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### 构建和部署流程

#### 当前部署方式
- **类型**: 手动部署
- **方法**: 直接在开发板上运行
- **命令**:
  ```bash
  python3 realtime_assistant_main.py
  # 或使用启动脚本
  bash start_assistant.sh
  ```

#### 环境
- **开发环境**: Orange Pi AI Pro 本地
- **测试环境**: 同开发环境
- **生产环境**: 同开发环境

---

## 🧪 测试现状

### 当前测试覆盖

- **单元测试**: ❌ 无
- **集成测试**: ❌ 无
- **端到端测试**: ❌ 无
- **手动测试**: ✅ 主要测试方法

### 运行测试

Phase 1 已完成手动测试，所有基础功能已验证：

```bash
# ✅ 测试 LLM（已验证 - 平均响应 2.2秒）
python3 scripts/deepseek_chat.py "测试消息"

# ✅ 测试 TTS（已验证 - 平均生成 2.7秒）
python3 scripts/tts_generate.py "测试" output/test.wav
aplay -Dhw:ascend310b output/test.wav

# ✅ 测试录音（已验证 - 清晰无杂音）
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav -d 5 test.wav

# ✅ 测试完整对话流程（已验证）
bash scripts/test_basic_conversation.sh "你好"

# ❓ 测试 ASR（待验证 - Phase 2）
python3 scripts/speech_to_text.py output/test.wav
```

---

## 📊 PRD 相关 - 影响分析

### 需要修改的文件

根据 PRD，重建过程将涉及以下文件：

#### Phase 1: 基础验证 ✅ **已完成！**
- ✅ `config/realtime_config.json` - 音频配置已验证
- ✅ `scripts/deepseek_chat.py` - LLM 测试完成
- ✅ `scripts/tts_generate.py` - TTS 测试完成
- ✅ `scripts/test_basic_conversation.sh` - 对话流程测试脚本已创建
- ✅ 音频设备配置和测试完成

#### Phase 2: ASR 集成
- `models/` - 下载 ASR 模型
- `config/asr_config.json` - 可能需要调整配置
- `realtime_assistant/asr_engine.py` - 验证和完善
- `scripts/speech_to_text.py` - 测试和验证

#### Phase 3: VAD 集成
- `models/` - 下载 VAD 模型
- `config/vad_config.json` - 可能需要调整配置
- `realtime_assistant/vad_detector.py` - 验证和完善
- `realtime_assistant/audio_capture.py` - 集成 VAD

#### Phase 4: 系统集成
- `realtime_assistant/assistant.py` - 验证异步编排
- `realtime_assistant_main.py` - 完善主程序
- 所有模块 - 集成测试和优化

### 新增文件/模块

**Phase 1 已新增：**
- ✅ `scripts/test_basic_conversation.sh` - 基础对话流程测试脚本
- ✅ `docs/stories/1.1-audio-device-setup.md` - Story 1.1 文档
- ✅ `docs/qa/gates/1.1-audio-device-setup.yml` - 质量门控文件
- ✅ `docs/implementation-plan.md` - 详细实施计划
- ✅ `docs/index.md` - 文档索引

**Phase 2 已新增：**
- ✅ `scripts/test_record_asr.sh` - 录音 + ASR 集成测试脚本（默认 INT8）
- ✅ `scripts/test_record_asr_int8.sh` - INT8 模型测试脚本
- ✅ `scripts/test_record_asr_usb.sh` - USB 麦克风测试脚本
- ✅ `docs/phase2-completion-report.md` - Phase 2 完成报告
- ✅ 修改 `scripts/speech_to_text.py` - 添加 Paraformer 支持和模型选择功能

**Phase 2 可能需要新增：**
- 测试脚本（用于 ASR 自动化测试）
- 配置验证脚本
- 模型下载脚本（改进版）
- 故障排查工具

### 集成考虑

- 必须遵循现有的异步编排模式
- 必须使用现有的配置文件格式
- 必须兼容 Orange Pi 硬件平台
- 必须保持模块间的松耦合

---

## 📚 附录 - 常用命令和脚本

### 常用命令

```bash
# 开发相关
python3 realtime_assistant_main.py  # 启动实时助手
bash start_assistant.sh             # 使用启动脚本

# 测试相关
python3 scripts/deepseek_chat.py "测试"  # 测试 LLM
python3 scripts/tts_generate.py "测试" output/test.wav  # 测试 TTS
python3 scripts/audio_record.py     # 测试录音
python3 scripts/speech_to_text.py output/test.wav  # 测试 ASR

# 音频设备相关
arecord -l                          # 查看录音设备
aplay -l                            # 查看播放设备
amixer                              # 查看音量设置
amixer set Capture 10               # 设置录音音量
amixer set Playback 10              # 设置播放音量
amixer set Deviceid 2               # 设置设备ID（耳机）

# 模型相关
bash scripts/setup_sherpa_onnx.sh   # 安装 sherpa-onnx
bash scripts/download_multilingual_model.sh  # 下载 ASR 模型

# VPN 相关（用于下载模型）
vpn                                 # 开启 VPN
vpntest                             # 测试 VPN
vpnoff                              # 关闭 VPN
```

### 调试和故障排查

#### 查看日志
```bash
# 实时助手日志（如果有）
tail -f logs/assistant.log

# 系统日志
journalctl -u alsa-restore
```

#### 音频设备故障排查
```bash
# 检查音频设备
arecord -l
aplay -l

# 测试录音
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav -d 5 test.wav

# 测试播放
aplay -Dhw:ascend310b test.wav

# 检查设备占用
lsof /dev/snd/*

# 重启 ALSA
sudo systemctl restart alsa-restore
```

#### 常见问题

1. **设备忙碌 (Device or resource busy)**
   ```bash
   lsof /dev/snd/*
   kill -9 <PID>
   ```

2. **模型加载失败**
   ```bash
   # 检查模型文件是否存在
   ls -lh models/sherpa-onnx-streaming-paraformer-bilingual-zh-en/

   # 重新下载模型
   bash scripts/download_multilingual_model.sh
   ```

3. **API 调用失败**
   ```bash
   # 测试网络连接
   curl https://api.deepseek.com/v1/models

   # 检查 API Key
   grep api_key config/realtime_config.json
   ```

---

## 🎯 下一步行动

### 当前状态（2026-01-18 更新）

**✅ Phase 1 已完成！**

所有基础功能已验证：
- ✅ 音频设备配置和测试（Story 1.1）
- ✅ LLM 服务测试（DeepSeek API）
- ✅ TTS 服务测试（Edge-TTS）
- ✅ 基础对话流程测试

**性能数据：**
- LLM 平均响应时间：2.188秒
- TTS 平均生成时间：2.7秒
- 录音音质：清晰无杂音
- 播放音质：清晰无杂音

**✅ Phase 2 已完成！**（2026-01-18）

ASR 集成和测试全部完成：
- ✅ ASR 模型下载和配置（Task 2.1）
- ✅ ASR 功能测试（Task 2.2）
- ✅ 录音 + ASR 集成测试（Task 2.3）

**ASR 性能数据：**
- 模型：Paraformer INT8 量化模型
- 识别速度：快（10秒音频约 2-3秒）
- 中文识别：✅ 优秀
- 英文识别：✅ 优秀
- 中英文混合：✅ 优秀
- 录音采样率：48000 Hz（硬件原生）
- ASR 采样率：16000 Hz（自动重采样）

**详细报告：** 参见 `docs/phase2-completion-report.md`

**✅ Phase 3 已完成！**（2026-01-18）

VAD 集成和测试全部完成：
- ✅ VAD 模型下载和配置（Task 3.1）
- ✅ VAD 功能测试（Task 3.2）
- ✅ VAD + 录音集成测试（Task 3.3）
- ✅ 发现并解决录音格式问题（WAV bug）
- ✅ 开发基于能量的 VAD 算法

**VAD 性能数据：**
- Silero VAD：适合安静环境，检测智能
- 基于能量的 VAD：适合有底噪环境，检测准确
- 最佳能量阈值：100
- 成功检测到 3 个语音片段

**关键发现：**
- Orange Pi 录音必须使用 RAW 格式，WAV 格式有 bug
- Silero VAD 对底噪敏感，需要基于能量的 VAD 补充
- 录音音量设置：Capture 10（官方推荐）

**详细报告：** 参见 `docs/phase3-completion-report.md`

### 立即行动（Phase 4）

**下一步：Task 4.1 - 异步编排验证**

Phase 3 已完成，现在可以开始 Phase 4 的系统集成工作：

1. 验证主控制器的异步编排逻辑
2. 集成所有模块（VAD、ASR、LLM、TTS）
3. 实现端到端的语音对话流程
4. 实现打断机制

### 短期目标（1-2 周）

1. ✅ 下载和配置 ASR 模型 - 完成
2. ✅ 测试 ASR 功能 - 完成
3. ✅ 集成录音和 ASR - 完成
4. ✅ 下载和配置 VAD 模型 - 完成
5. ✅ 测试 VAD 功能 - 完成
6. ✅ 开发基于能量的 VAD 算法 - 完成
7. 🔲 验证异步编排逻辑
8. 🔲 端到端集成测试

### 中期目标（3-4 周）

1. 🔲 实现完整的异步编排
2. 🔲 端到端集成测试
3. 🔲 实现打断机制
4. 🔲 性能优化

---

**文档创建者：** 哈雷酱（傲娇大小姐工程师）
**最后更新：** 2026-01-18 23:00
**文档状态：** v1.3 - Phase 3 完成后更新
