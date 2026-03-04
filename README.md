# 香橙派语音助手 (OrangePi Voice Assistant)

基于 Orange Pi AI Pro (Ascend 310B) 的实时语音助手系统。说话即可对话，支持中文语音交互。

## 它能做什么

对着麦克风说话，助手会：
1. **听** — 自动检测你在说话（VAD），录下语音
2. **懂** — 把语音转成文字（ASR 离线识别）
3. **想** — 调用大模型生成回复（DeepSeek）
4. **说** — 把回复转成语音播放出来（Edge-TTS）

整个流程延迟约 1-2 秒（首字），支持流式处理，边生成边播报。

## 技术栈

| 模块 | 技术方案 | 说明 |
|------|---------|------|
| 语音活动检测 (VAD) | Silero VAD + sherpa-onnx | 自动分割语音片段 |
| 语音识别 (ASR) | Paraformer INT8 + sherpa-onnx | 离线中文识别，准确率 >90% |
| 大语言模型 (LLM) | DeepSeek API | 流式输出，需联网 |
| 语音合成 (TTS) | Edge-TTS | 微软引擎，多种中文音色 |
| 音频采集 | arecord (ALSA) | 48kHz 采集，软件降采样到 16kHz |
| 音频播放 | aplay | 3.5mm 耳机输出 |

## 硬件要求

- **开发板**：Orange Pi AI Pro (Ascend 310B)
- **系统**：Ubuntu 22.04 (ARM64)
- **Python**：3.9+
- **内存**：8GB+
- **外设**：3.5mm 耳机/麦克风

## 快速开始

### 1. 安装依赖

```bash
# 系统依赖
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg alsa-utils

# Python 依赖
pip3 install edge-tts numpy aiohttp
```

### 2. 准备模型

需要以下模型文件放在 `models/` 目录：

- **Paraformer INT8** — ASR 语音识别模型
- **silero_vad.onnx** — VAD 语音活动检测模型

同时需要编译安装 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)（用于 ASR 和 VAD 推理）。

### 3. 配置

编辑 `config/realtime_config.json`，填入你的 DeepSeek API Key：

```json
{
  "llm": {
    "api_key": "你的 DeepSeek API Key",
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
  }
}
```

### 4. 配置音频设备

```bash
# 设置录音音量（注意：Orange Pi 音量值越小信号越强）
amixer set Capture 5
amixer set Deviceid 2

# 测试录音
arecord -D plughw:0,1 -f S16_LE -r 48000 -c 1 -d 3 test.wav

# 测试播放
aplay -D hw:ascend310b test.wav
```

### 5. 启动

```bash
python3 realtime_assistant_main.py
```

启动后对着麦克风说话即可开始对话。按 `Ctrl+C` 停止。

## 项目结构

```
├── realtime_assistant_main.py    # 主程序入口
├── realtime_assistant/           # 核心模块
│   ├── assistant.py              # 主控制器（异步编排）
│   ├── audio_capture.py          # 音频采集（arecord + 降采样）
│   ├── vad_detector.py           # VAD 语音活动检测
│   ├── asr_engine.py             # ASR 语音识别
│   ├── llm_engine.py             # LLM 对话（DeepSeek，流式）
│   ├── tts_engine.py             # TTS 语音合成（Edge-TTS，流式）
│   ├── audio_player.py           # 音频播放
│   └── state_machine.py          # 状态机
├── config/                       # 配置文件
│   ├── realtime_config.json      # 主配置
│   ├── asr_config.json           # ASR 配置
│   └── vad_config.json           # VAD 配置
├── models/                       # 模型文件（需自行下载）
├── scripts/                      # 辅助脚本
├── tests/                        # 测试脚本
└── docs/                         # 开发文档
```

## 工作流程

```
麦克风 ──→ 音频采集(48kHz) ──→ 降采样(16kHz) ──→ VAD检测
                                                      │
              耳机 ←── 音频播放 ←── TTS合成 ←── LLM对话 ←── ASR识别
              (流式播放)          (分句合成)   (流式输出)
```

## 配置说明

主配置文件 `config/realtime_config.json`：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `llm.api_key` | DeepSeek API 密钥 | 需自行填入 |
| `llm.max_tokens` | 回复最大 token 数 | 50 |
| `llm.system_prompt` | 助手人设提示词 | 可自定义 |
| `tts.voice_zh` | 中文语音音色 | `zh-CN-XiaoyiNeural` |
| `tts.rate` | 语速 | `+25%` |
| `audio.device` | 录音设备 | `plughw:0,1` |

可用的中文语音：晓晓、晓伊、云健、云希、晓萱、云扬。

## 已知问题

- Orange Pi 音频驱动存在**音量反向特性**：音量值越小，录音信号越强。建议录音音量设为 1-5。
- LLM 调用需要联网（DeepSeek API），其余模块均离线运行。

## License

MIT

## 作者

11ew
