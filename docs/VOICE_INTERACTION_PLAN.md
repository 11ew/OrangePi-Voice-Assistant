# 🎤 语音对话交互系统 - 流式输出方案

> **制定者：** 哈雷酱（傲娇大小姐工程师）
> **目标硬件：** 香橙派 AI Pro 8T (Ascend 310B)
> **制定日期：** 2026-01-03
> **更新日期：** 2026-01-03
> **最终目标：** 🚀 **流式语音对话系统**
> **状态：** 待用户确认 ⏳

---

## 📋 方案概述

将现有的**文字输入对话系统**升级为**流式语音交互系统**，实现：

```
用户语音输入 → 本地VAD检测 → 本地语音识别 → DeepSeek流式对话 → 流式TTS → 实时播放
```

**核心设计理念：**
- ✅ **本地处理**：VAD语音检测 + ASR语音识别（降低延迟）
- ✅ **云端流式**：DeepSeek流式对话 + 流式TTS（边生成边播放）
- ✅ **流式架构**：文字流式生成 → 句子分割 → 并行TTS → 边播边说
- ✅ **极致体验**：总延迟 < 3秒，首字延迟 < 1秒

---

## 🏗️ 技术架构

### 当前系统架构
```
┌─────────────────────────────────────────────────────────┐
│  文字输入 (键盘)                                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  DeepSeek API (对话生成) - 云端                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Edge-TTS (语音合成) - 云端                              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  aplay (音频播放 - 3.5mm耳机)                           │
└─────────────────────────────────────────────────────────┘
```

### 升级后架构（本地+云端混合）
```
┌─────────────────────────────────────────────────────────┐
│  🎤 语音输入 (麦克风/耳机)                               │
│  - arecord 录音                                          │
│  - 支持按键触发/连续监听                                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  🔍 VAD 语音活动检测 (本地) ⚡                           │
│  方案：Silero-VAD / WebRTC-VAD                           │
│  - 实时检测语音开始/结束                                 │
│  - 自动分割录音片段                                      │
│  - 延迟 < 100ms                                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  🧠 语音识别 ASR (本地) ⚡                                │
│  推荐方案：Whisper 本地部署                              │
│  - 使用 Whisper.cpp (C++优化版本)                        │
│  - 或 FunASR (阿里达摩院开源)                            │
│  - 延迟 < 2秒                                            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  💬 DeepSeek API (对话生成) - 云端 ☁️                    │
│  - 已有实现，无需修改                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  🔊 Edge-TTS (语音合成) - 云端 ☁️                        │
│  - 已有实现，无需修改                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  🎧 aplay (音频播放)                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 实施方案（本地优先策略）

### 阶段一：录音功能实现 ✨

**目标：** 实现稳定的录音功能

**技术细节：**
```bash
# 录音参数（参考官方脚本）
设备: plughw:0,1 (香橙派录音设备)
格式: S16_LE (16-bit PCM)
采样率: 16000 Hz (适配Whisper模型)
声道: 单声道 (mono)
时长: 可配置 (默认5秒，VAD模式下动态)
```

**实现内容：**
1. **创建录音脚本** `scripts/audio_record.py`
   - 封装 arecord 命令
   - 支持录音时长配置
   - 自动配置麦克风音量
   - 返回录音文件路径

2. **录音测试工具** `test_record.sh`
   - 快速测试录音功能
   - 录音后立即播放验证
   - 显示录音文件信息

**预期输出：**
- ✅ 能够录制清晰的音频
- ✅ 音频格式：WAV (16kHz, 16-bit, mono)
- ✅ 存储位置：`output/recordings/`

---

### 阶段二：VAD语音活动检测（本地）🔍

**目标：** 实时检测语音开始和结束，实现自然对话

**方案对比：**

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Silero-VAD** | 准确率高、轻量级、支持ONNX | 需要安装onnxruntime | ⭐⭐⭐⭐⭐ |
| **WebRTC-VAD** | 超轻量、C实现、延迟极低 | 准确率稍低 | ⭐⭐⭐⭐ |
| **pyaudio-vad** | 简单易用 | 依赖较多 | ⭐⭐⭐ |

**推荐方案：Silero-VAD（本地推理）**

**实现内容：**
1. **创建VAD检测脚本** `scripts/vad_detector.py`
   - 使用 Silero-VAD 模型（ONNX格式）
   - 实时音频流检测
   - 自动分割语音片段
   - 配置灵敏度参数

2. **VAD配置** `config/vad_config.json`
   ```json
   {
     "model": "silero_vad",
     "threshold": 0.5,
     "min_speech_duration_ms": 250,
     "min_silence_duration_ms": 500,
     "window_size_samples": 512
   }
   ```

**预期输出：**
- ✅ 实时检测语音开始（延迟 < 100ms）
- ✅ 准确检测语音结束
- ✅ 自动过滤环境噪音

---

### 阶段三：本地语音识别（ASR）🧠

**目标：** 将录音转换为文字（本地处理，降低延迟）

**方案对比：**

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Whisper.cpp** | C++优化、速度快、支持量化 | 需要编译 | ⭐⭐⭐⭐⭐ |
| **FunASR** | 阿里开源、中文优化、支持流式 | 模型较大 | ⭐⭐⭐⭐ |
| **Faster-Whisper** | Python实现、易用、支持GPU | 需要CTranslate2 | ⭐⭐⭐⭐⭐ |
| **Whisper API** | 准确率最高 | 需要网络、有延迟 | ⭐⭐⭐ |

**推荐方案：Faster-Whisper（本地推理）**

**为什么选择本地ASR？**
- ✅ **降低延迟**：本地推理 < 2秒，API调用 > 3秒
- ✅ **节省成本**：无API费用
- ✅ **隐私保护**：语音数据不上传
- ✅ **离线可用**：不依赖网络
- ✅ **香橙派算力足够**：Ascend 310B 可以运行 Whisper tiny/base 模型

**实现内容：**
1. **创建ASR脚本** `scripts/speech_to_text.py`
   - 使用 faster-whisper 库
   - 支持 tiny/base/small 模型
   - 输入：WAV音频文件
   - 输出：识别的文字内容
   - 错误处理和重试机制

2. **模型下载和配置** `scripts/download_models.sh`
   ```bash
   # 下载 Whisper tiny 模型（最快，39M）
   # 下载 Whisper base 模型（平衡，74M）
   # 下载 Whisper small 模型（准确，244M）
   ```

3. **配置管理** `config/asr_config.json`
   ```json
   {
     "provider": "faster-whisper",
     "model_size": "base",
     "device": "cpu",
     "compute_type": "int8",
     "language": "zh",
     "beam_size": 5
   }
   ```

**预期输出：**
- ✅ 准确识别中文语音（准确率 > 90%）
- ✅ 识别延迟 < 2秒（base模型）
- ✅ 支持多种口音
- ✅ 完全本地运行

---

### 阶段四：完整语音对话流程 🎭

**目标：** 整合所有模块，实现完整对话

**交互模式：**

#### 模式A：按键触发模式（推荐初期使用）
```
1. 用户按下"开始录音"按钮（或按回车键）
2. 系统录音 5 秒
3. 本地VAD检测有效语音片段
4. 本地Whisper进行语音识别
5. 调用 DeepSeek 对话（云端）
6. 调用 Edge-TTS 生成语音（云端）
7. 播放语音
8. 等待下一次按键
```

#### 模式B：连续对话模式（进阶，更自然）
```
1. 系统持续监听麦克风
2. VAD检测到语音活动
3. 自动开始录音
4. VAD检测到静音后停止
5. 本地Whisper识别
6. DeepSeek对话（云端）
7. Edge-TTS生成（云端）
8. 播放语音
9. 返回监听状态
```

**实现内容：**
1. **主程序** `voice_assistant.sh`
   - 整合录音、VAD、识别、对话、播放
   - 支持两种交互模式
   - 美化的交互界面
   - 配置管理

2. **Python控制器** `scripts/voice_controller.py`
   - 统一管理各个模块
   - 状态机控制流程
   - 日志记录
   - 性能监控

**预期输出：**
- ✅ 流畅的语音对话体验
- ✅ 总响应时间 < 8秒（VAD+ASR+对话+TTS+播放）
- ✅ 稳定运行不崩溃

---

### 阶段五：优化与增强 🚀

**目标：** 提升用户体验和系统稳定性

**优化内容：**

1. **性能优化**
   - 模型预加载（启动时加载Whisper模型）
   - 并行处理（识别完成后立即开始对话，同时准备TTS）
   - 音频缓冲优化
   - 减少云端API调用延迟

2. **交互优化**
   - 添加提示音（开始录音/结束录音/思考中）
   - 实时状态显示（监听中/录音中/识别中/思考中/播放中）
   - 语音打断功能（播放时可打断）
   - 音量可视化

3. **功能增强**
   - 支持多轮对话上下文
   - 语音指令识别（如"退出"、"重新说"、"清空历史"）
   - 对话历史记录和回放
   - 支持自定义唤醒词（可选）

4. **错误处理**
   - 网络断开重连
   - 云端API失败降级方案
   - 录音失败提示
   - 模型加载失败处理

---

## 📁 新增文件结构

```
EdgeTTSdemo/
├── scripts/
│   ├── audio_record.py          # 录音模块（新增）
│   ├── vad_detector.py          # VAD语音检测模块（新增）⚡本地
│   ├── speech_to_text.py        # 语音识别模块（新增）⚡本地
│   ├── voice_controller.py      # 语音对话控制器（新增）
│   ├── download_models.sh       # 模型下载脚本（新增）
│   ├── deepseek_chat.py         # DeepSeek对话（已有）☁️云端
│   └── tts_generate.py          # TTS生成（已有）☁️云端
│
├── config/
│   ├── vad_config.json          # VAD配置文件（新增）
│   └── asr_config.json          # ASR配置文件（新增）
│
├── models/                      # 本地模型目录（新增）
│   ├── silero_vad.onnx          # Silero VAD模型
│   └── whisper-base/            # Whisper base模型
│
├── voice_assistant.sh           # 语音助手主程序（新增）
├── test_record.sh               # 录音测试工具（新增）
│
├── output/
│   ├── recordings/              # 录音文件目录（新增）
│   └── *.wav                    # TTS输出（已有）
│
└── docs/
    └── VOICE_INTERACTION_PLAN.md # 本方案文档
```

---

## 🔧 依赖安装

### Python依赖（本地优先）
```bash
# VAD语音检测
pip3 install torch onnxruntime  # Silero-VAD依赖
pip3 install webrtcvad          # 备选方案

# 本地语音识别（推荐）
pip3 install faster-whisper     # Whisper本地推理（推荐）
pip3 install openai-whisper     # 官方Whisper（备选）

# 音频处理
pip3 install pydub              # 音频处理
pip3 install numpy              # 数值计算
pip3 install soundfile          # 音频文件读写

# 环境管理
pip3 install python-dotenv      # 环境变量管理

# 已有依赖
pip3 install edge-tts
pip3 install requests
```

### 系统依赖
```bash
# 已安装
sudo apt install alsa-utils ffmpeg

# 确认录音设备
arecord -l

# 测试录音
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -d 3 test.wav
aplay test.wav
```

---

## ⚙️ 配置说明

### 1. API密钥配置

创建 `.env` 文件：
```bash
# DeepSeek API（已有）
DEEPSEEK_API_KEY=sk-8729b6bbc81b49bda752005da63185c6

# OpenAI API（可选 - 仅在使用Whisper API时需要）
# OPENAI_API_KEY=your-openai-api-key-here
```

### 2. VAD配置

在 `config/vad_config.json` 中配置：
```json
{
  "model": "silero_vad",
  "model_path": "models/silero_vad.onnx",
  "threshold": 0.5,
  "min_speech_duration_ms": 250,
  "min_silence_duration_ms": 500,
  "window_size_samples": 512,
  "sample_rate": 16000
}
```

### 3. ASR配置

在 `config/asr_config.json` 中配置：
```json
{
  "provider": "faster-whisper",
  "model_size": "base",
  "model_path": "models/whisper-base",
  "device": "cpu",
  "compute_type": "int8",
  "language": "zh",
  "beam_size": 5,
  "vad_filter": true
}
```

### 4. 录音参数配置

```json
{
  "recording": {
    "device": "plughw:0,1",
    "format": "S16_LE",
    "rate": 16000,
    "channels": 1,
    "duration": 5
  }
}
```

---

## 📊 实施时间表

| 阶段 | 任务 | 预计工作量 | 优先级 |
|------|------|----------|--------|
| **阶段一** | 录音功能实现 | 简单 | 🔴 高 |
| **阶段二** | VAD语音检测（本地） | 中等 | 🔴 高 |
| **阶段三** | 本地语音识别（ASR） | 中等 | 🔴 高 |
| **阶段四** | 完整对话流程 | 复杂 | 🟡 中 |
| **阶段五** | 优化与增强 | 复杂 | 🟢 低 |

**建议实施顺序：**
1. 先完成**阶段一**，验证录音功能
2. 再完成**阶段三**（跳过VAD），使用按键触发模式测试ASR
3. 完成**阶段四**，实现基础对话功能
4. 最后完成**阶段二**，添加VAD实现连续对话
5. 根据需求选择性实施**阶段五**

---

## ✅ 验收标准

### 基础功能（必须）
- ✅ 能够录制清晰的音频
- ✅ 本地VAD准确检测语音开始/结束
- ✅ 本地语音识别准确率 > 90%
- ✅ 完整对话流程运行正常
- ✅ 语音输出清晰可听

### 性能指标（期望）
- ✅ 录音延迟 < 0.5秒
- ✅ VAD检测延迟 < 100ms
- ✅ 本地ASR识别 < 2秒
- ✅ 云端对话生成 < 5秒
- ✅ 云端TTS生成 < 2秒
- ✅ 总响应时间 < 10秒

### 稳定性（重要）
- ✅ 连续运行 1小时不崩溃
- ✅ 网络异常能够恢复
- ✅ 模型加载失败有提示
- ✅ 错误提示清晰友好

---

## 🎓 技术要点

### 1. 录音设备配置
```bash
# 设置麦克风音量
amixer set Capture 10

# 设置设备为耳机（带麦克风）
amixer set Deviceid 2

# 录音命令（16kHz适配Whisper）
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav -d 5 output.wav
```

### 2. Silero-VAD使用示例
```python
import torch
import torchaudio

# 加载模型
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=False,
                              onnx=True)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

# 读取音频
wav = read_audio('audio.wav', sampling_rate=16000)

# 检测语音片段
speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)
```

### 3. Faster-Whisper使用示例
```python
from faster_whisper import WhisperModel

# 加载模型（首次会自动下载）
model = WhisperModel("base", device="cpu", compute_type="int8")

# 识别音频
segments, info = model.transcribe("audio.wav", language="zh", beam_size=5)

# 获取结果
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

### 4. 流程控制（伪代码）
```python
def voice_chat_loop_with_vad():
    # 预加载模型
    vad_model = load_vad_model()
    whisper_model = load_whisper_model()

    while True:
        # 1. 持续监听（VAD模式）
        audio_stream = start_audio_stream()

        # 2. VAD检测语音活动
        if vad_model.detect_speech(audio_stream):
            print("检测到语音，开始录音...")

            # 3. 录音直到静音
            audio_data = record_until_silence(vad_model)

            # 4. 本地语音识别
            user_text = whisper_model.transcribe(audio_data)
            print(f"识别结果: {user_text}")

            # 5. 云端对话生成
            response_text = chat_with_deepseek(user_text)

            # 6. 云端语音合成
            tts_file = text_to_speech(response_text)

            # 7. 播放
            play_audio(tts_file)
```

---

## 🚨 风险与应对

### 风险1：录音质量差
**应对：**
- 调整麦克风增益
- 使用降噪算法
- 更换更好的麦克风

### 风险2：本地识别准确率低
**应对：**
- 使用更大的Whisper模型（small）
- 添加语音预处理（降噪、增强）
- 限制使用场景（安静环境）
- 备选方案：切换到云端API

### 风险3：响应时间长
**应对：**
- 使用更小的Whisper模型（tiny）
- 优化模型量化（int8）
- 并行处理（识别完立即开始对话）
- 预加载模型

### 风险4：模型占用内存大
**应对：**
- 使用量化模型（int8）
- 使用更小的模型（tiny/base）
- 监控内存使用
- 必要时使用云端API

### 风险5：VAD误检测
**应对：**
- 调整阈值参数
- 增加最小语音时长
- 使用更好的VAD模型
- 添加手动触发选项

---

## 💡 后续扩展方向

1. **唤醒词检测**
   - 使用 Porcupine 或 Snowboy
   - 实现"小助手"唤醒
   - 无需按键即可对话

2. **多语言支持**
   - 支持英文对话
   - 自动语言检测
   - 中英混合识别

3. **情感识别**
   - 识别用户情绪
   - 调整回复风格
   - 语音情感合成

4. **完全离线模式**
   - 本地部署对话模型（如 Llama）
   - 离线TTS引擎（如 piper-tts）
   - 完全不依赖网络

5. **智能家居控制**
   - 语音控制设备
   - 场景联动
   - 自定义指令

6. **性能优化**
   - 使用 Ascend 310B 加速推理
   - 模型量化和剪枝
   - 流式处理

---

## 📝 注意事项

1. **API密钥安全**
   - 不要提交到Git
   - 使用环境变量管理
   - 定期更换密钥

2. **隐私保护**
   - 录音文件定期清理
   - 不上传敏感信息
   - 本地处理优先

3. **资源管理**
   - 及时清理临时文件
   - 监控磁盘空间
   - 控制并发请求
   - 监控内存使用

4. **错误处理**
   - 所有API调用都要try-catch
   - 提供友好的错误提示
   - 记录详细日志
   - 模型加载失败降级

5. **模型管理**
   - 首次运行会下载模型
   - 模型文件较大（base模型约74MB）
   - 建议提前下载
   - 定期更新模型

---

## 🎉 总结

本方案采用**本地+云端混合**策略，充分利用香橙派AI Pro 8T的算力优势：

**核心优势：**
- ✅ **本地处理**：VAD + ASR 降低延迟，提升响应速度
- ✅ **云端处理**：DeepSeek + TTS 保证对话质量
- ✅ **复用现有代码**：DeepSeek + TTS 无需修改
- ✅ **成本优化**：本地ASR免费，无API费用
- ✅ **隐私保护**：语音数据本地处理
- ✅ **离线可用**：录音和识别不依赖网络
- ✅ **易于扩展**：模块化架构

**本小姐的建议：**
1. **先实现阶段一和阶段三**，使用按键触发模式验证基础功能
2. 确认本地ASR效果满意后，再实现**阶段四**的完整对话流程
3. **阶段二的VAD**可以后续添加，实现更自然的连续对话
4. **阶段五**根据实际需求选择性实施

**关键技术选型：**
- **VAD**：Silero-VAD（轻量级、准确率高）
- **ASR**：Faster-Whisper base模型（平衡速度和准确率）
- **对话**：DeepSeek API（已有，质量高）
- **TTS**：Edge-TTS（已有，免费）

---

> 哼，这个优化方案是本小姐根据你的硬件特点精心设计的！(￣▽￣)ノ
>
> **本地处理VAD和ASR，云端处理对话和TTS**，这样既能降低延迟，又能保证质量！
>
> 香橙派AI Pro 8T的Ascend 310B算力完全够用，运行Whisper base模型绰绰有余！
>
> 笨蛋快确认吧，本小姐已经迫不及待要开始实施了！( ` ω´ )
>
> —— 哈雷酱 (傲娇大小姐工程师)

**最后更新：** 2026-01-03
**版本：** v2.0 (本地+云端混合方案)
