# 双语语音对话系统说明

## 系统概述

本小姐实现了一个智能的双语语音对话系统！(￣▽￣)ノ

**核心特性：**
- 🎤 **自动语言检测**：说中文识别中文，说英文识别英文
- 💬 **智能回复**：中文输入→中文回复，英文输入→英文回复
- 🔊 **匹配语音**：中文回复用中文语音，英文回复用英文语音

## 技术架构

```
录音 (48kHz)
    ↓
双语言识别 (speech_to_text_auto.py)
    ├─ 中文识别 (language=zh)
    └─ 英文识别 (language=en)
    ↓
智能选择最佳结果
    ↓
语言检测 (detect_language)
    ↓
DeepSeek 对话生成 (deepseek_chat.py)
    ├─ 中文输入 → 中文系统提示词 → 中文回复
    └─ 英文输入 → 英文系统提示词 → 英文回复
    ↓
自动语言检测 TTS (tts_generate.py)
    ├─ 中文文本 → zh-CN-XiaoxiaoNeural
    └─ 英文文本 → en-US-JennyNeural
    ↓
播放语音
```

## 核心组件

### 1. 双语言识别 (`speech_to_text_auto.py`)

**策略：**
1. 用当前配置的语言识别一次
2. 用另一种语言再识别一次
3. 对比两次结果，选择更合理的

**判断标准：**
- 文本合理性（不是乱码）
- 语言匹配度
- 文本长度

**示例：**
```bash
# 中文输入："一加一等于几"
# 结果1 (zh): "1+1等一集"  ✅ 合理
# 结果2 (en): "我特可能I do"  ❌ 乱码
# 选择：结果1

# 英文输入："what can I do"
# 结果1 (zh): "我特可能I do"  ❌ 乱码
# 结果2 (en): "what can I do"  ✅ 合理
# 选择：结果2
```

### 2. 智能对话生成 (`deepseek_chat.py`)

**语言检测：**
- 统计中文字符和英文字母比例
- 阈值：40%
- 中文比例 > 40% → 中文
- 英文比例 > 40% → 英文
- 其他 → 混合（默认中文）

**系统提示词：**

**中文：**
```
你是一个友好的语音助手。请遵循以下规则：
1. 回复要简洁自然，像朋友聊天一样，不要太官方
2. 如果用户的问题包含明显的语音识别错误（错别字），请根据上下文推测真实意图
3. 回复控制在 50 字以内，适合语音播报
4. 可以使用适当的语气词，让对话更生动
```

**英文：**
```
You are a friendly voice assistant. Please follow these rules:
1. Reply in a casual, natural way like a friend, not too formal
2. If the user's question contains obvious speech recognition errors, guess the intent from context
3. Keep replies under 50 words, suitable for voice playback
4. Use appropriate tone to make the conversation lively
```

### 3. 自动语音合成 (`tts_generate.py`)

**支持的语音：**

**中文语音：**
- `xiaoxiao` - zh-CN-XiaoxiaoNeural（女声-晓晓，温柔）
- `xiaoyi` - zh-CN-XiaoyiNeural（女声-晓伊，活泼）
- `yunjian` - zh-CN-YunjianNeural（男声-云健，沉稳）
- `yunxi` - zh-CN-YunxiNeural（男声-云希，年轻）
- `xiaoxuan` - zh-CN-XiaoxuanNeural（女声-晓萱，甜美）
- `yunyang` - zh-CN-YunyangNeural（男声-云扬，热情）

**英文语音：**
- `jenny` - en-US-JennyNeural（女声-Jenny，友好）
- `aria` - en-US-AriaNeural（女声-Aria，自然）
- `guy` - en-US-GuyNeural（男声-Guy，专业）
- `davis` - en-US-DavisNeural（男声-Davis，沉稳）
- `jane` - en-US-JaneNeural（女声-Jane，温柔）
- `jason` - en-US-JasonNeural（男声-Jason，活力）

**自动检测：**
- 不指定语音类型时，自动检测文本语言
- 中文文本 → 使用中文语音（默认：晓晓）
- 英文文本 → 使用英文语音（默认：Jenny）
- 混合文本 → 使用中文语音

## 使用方法

### 启动系统

```bash
bash voice_chat_v2.sh
```

### 测试组件

**测试语音识别：**
```bash
# 录制音频
arecord -D plughw:0,1 -f S16_LE -r 48000 -c 1 -t wav -d 5 test.wav

# 自动语言检测识别
/usr/bin/python3 scripts/speech_to_text_auto.py test.wav
```

**测试对话生成：**
```bash
# 中文
/usr/bin/python3 scripts/deepseek_chat.py "你好，今天天气怎么样？"

# 英文
/usr/bin/python3 scripts/deepseek_chat.py "Hello, how are you?"
```

**测试语音合成：**
```bash
# 自动检测（中文）
/usr/bin/python3 scripts/tts_generate.py "你好，世界" output/test_zh.wav

# 自动检测（英文）
/usr/bin/python3 scripts/tts_generate.py "Hello, world" output/test_en.wav

# 指定语音
/usr/bin/python3 scripts/tts_generate.py "你好" output/test.wav xiaoyi
/usr/bin/python3 scripts/tts_generate.py "Hello" output/test.wav jenny
```

## 配置文件

### ASR 配置 (`config/asr_config.json`)

```json
{
  "provider": "sherpa-onnx",
  "model_dir": "models/sherpa-onnx-whisper-tiny",
  "language": "zh",
  "num_threads": 4,
  "decoding_method": "greedy_search"
}
```

**说明：**
- `language` 设置为 `zh` 或 `en` 作为首选语言
- `speech_to_text_auto.py` 会自动尝试两种语言

## 工作流程示例

### 中文对话

```
用户说话："你好，今天天气怎么样？"
    ↓
录音：48kHz WAV 文件
    ↓
识别：
  - 尝试1 (zh): "你好，今天天气怎么样？" ✅
  - 尝试2 (en): "ni hao jin tian tian qi zen me yang" ❌
  - 选择：结果1
    ↓
语言检测：中文 (chinese_ratio = 100%)
    ↓
DeepSeek：使用中文系统提示词
  回复："今天天气不错哦，阳光明媚，温度适中，适合出门走走呢！"
    ↓
TTS：检测到中文，使用 zh-CN-XiaoxiaoNeural
    ↓
播放：中文女声
```

### 英文对话

```
用户说话："Hello, how are you?"
    ↓
录音：48kHz WAV 文件
    ↓
识别：
  - 尝试1 (zh): "我特可能I do" ❌
  - 尝试2 (en): "Hello, how are you?" ✅
  - 选择：结果2
    ↓
语言检测：英文 (english_ratio = 100%)
    ↓
DeepSeek：使用英文系统提示词
  回复："Hey there! I'm doing great, thanks for asking. How about you?"
    ↓
TTS：检测到英文，使用 en-US-JennyNeural
    ↓
播放：英文女声
```

## 技术细节

### 语言检测算法

```python
def detect_language(text):
    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

    # 统计英文字母
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    # 计算比例
    total_chars = chinese_chars + english_chars
    chinese_ratio = chinese_chars / total_chars
    english_ratio = english_chars / total_chars

    # 判断（阈值 40%）
    if chinese_ratio > 0.4:
        return 'zh'
    elif english_ratio > 0.4:
        return 'en'
    else:
        return 'mixed'
```

### 识别结果合理性判断

```python
def is_sensible_text(text, language='auto'):
    # 检查是否为空
    if not text or len(text.strip()) == 0:
        return False

    # 检查是否全是特殊字符
    if re.match(r'^[^a-zA-Z\u4e00-\u9fff0-9]+$', text):
        return False

    # 检查是否重复字符过多（乱码特征）
    if len(set(text)) < len(text) * 0.3 and len(text) > 5:
        return False

    return True
```

## 性能优化

### 采样率设置

- **录音采样率**：48000 Hz（硬件原生）
- **Whisper 要求**：16000 Hz
- **自动重采样**：Sherpa-ONNX 内部自动处理

**为什么使用 48000 Hz？**
- Orange Pi 官方测试脚本使用 48000 Hz
- 直接使用 16000 Hz 会导致识别失败
- Sherpa-ONNX 会自动从 48000 Hz 重采样到 16000 Hz

### 双重识别策略

**优点：**
- 提高识别准确率
- 自动选择最佳结果
- 适应中英文混合场景

**缺点：**
- 识别时间增加约 2 倍
- 计算资源消耗增加

**优化建议：**
- 如果确定只使用一种语言，可以直接使用 `speech_to_text.py`
- 对于性能敏感场景，可以考虑缓存识别结果

## 故障排除

### 问题1：识别结果全是括号 "((((("

**原因**：采样率设置错误
**解决**：确保使用 48000 Hz 采样率

### 问题2：英文识别成中文拼音

**原因**：模型语言设置为中文
**解决**：使用 `speech_to_text_auto.py` 进行双语言识别

### 问题3：TTS 语音不匹配

**原因**：未启用自动语言检测
**解决**：不指定语音类型参数，让系统自动检测

### 问题4：DeepSeek 回复语言不对

**原因**：语言检测阈值问题
**解决**：检查文本中中英文字符比例，调整阈值

## 未来改进

- [ ] 支持更多语言（日语、韩语等）
- [ ] 优化识别速度（单次识别 + 后验证）
- [ ] 添加语音情感检测
- [ ] 支持多轮对话上下文
- [ ] 添加唤醒词功能
- [ ] 支持自定义语音风格

---

**作者**：哈雷酱（傲娇大小姐工程师）
**版本**：V2.0
**日期**：2026-01-15

哼，这个双语系统可是本小姐精心设计的！(￣▽￣)ノ
