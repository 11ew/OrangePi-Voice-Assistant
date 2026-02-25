# 🧪 测试脚本使用指南

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **版本：** 1.0.0
> **日期：** 2026-02-26

---

## 📋 概述

本目录包含所有经过验证的测试脚本，用于验证 EdgeTTSdemo 项目的各个功能模块。

所有脚本都经过实际测试，可以作为范本使用。

---

## 📁 测试脚本列表

### 1. 音频设备测试 - `test_audio_48k.sh`

**功能：** 完整的音频设备测试（录音 + 播放）

**用途：**
- ✅ 验证音频设备配置
- ✅ 测试录音功能（48000 Hz RAW 格式）
- ✅ 测试播放功能
- ✅ 检查音频质量

**使用方法：**
```bash
cd /home/HwHiAiUser/Desktop/ai-study/EdgeTTSdemo
./tests/test_audio_48k.sh
```

**测试流程：**
1. 设置音频参数（Capture=10, Deviceid=2, Playback=10）
2. 录音 5 秒（48000 Hz RAW 格式）
3. 转换为 WAV 格式
4. 验证音频质量
5. 播放录音

**预期结果：**
- ✅ 录音正常，无错误
- ✅ 音频最大值 > 1000
- ✅ 播放清晰，能听到自己的声音

**详细文档：** [音频测试脚本使用指南](../docs/audio-test-script-guide.md)

---

### 2. ASR 识别测试 - `test_asr_recognition.py`

**功能：** ASR 语音识别测试（录音 + 识别）

**用途：**
- ✅ 验证 ASR 识别准确率
- ✅ 测试 48000 Hz → 16000 Hz 降采样
- ✅ 检查识别速度
- ✅ 验证录音质量

**使用方法：**
```bash
cd /home/HwHiAiUser/Desktop/ai-study/EdgeTTSdemo
python3 tests/test_asr_recognition.py
```

**测试流程：**
1. 初始化 ASR 引擎（Paraformer 模型）
2. 设置音频参数（Capture=10, Deviceid=2）
3. 录音 5 秒（48000 Hz RAW 格式）
4. 自动降采样到 16000 Hz
5. 调用 ASR 引擎识别
6. 显示识别结果和耗时

**预期结果：**
- ✅ 识别准确率 > 90%
- ✅ 识别速度 2-3 秒
- ✅ 音频质量正常

**详细文档：** [ASR 识别测试脚本使用指南](../docs/asr-test-script-guide.md)

---

### 3. 音频播放测试 - `test_playback.py`

**功能：** TTS 语音合成和播放测试

**用途：**
- ✅ 验证 TTS 生成功能
- ✅ 测试 AudioPlayer 播放器
- ✅ 检查播放设备配置
- ✅ 验证音频采样率匹配

**使用方法：**
```bash
cd /home/HwHiAiUser/Desktop/ai-study/EdgeTTSdemo
python3 tests/test_playback.py
```

**测试流程：**
1. 初始化 TTS 引擎（Edge-TTS）
2. 生成测试语音（"你好，我是哈雷酱，这是播放测试"）
3. 检查音频文件（48000 Hz WAV 格式）
4. 设置音频参数（Deviceid=2, Playback=10）
5. 使用 AudioPlayer 播放音频
6. 等待播放完成

**预期结果：**
- ✅ TTS 生成成功
- ✅ 播放声音清晰
- ✅ 速度正常（不快不慢）
- ✅ 音量合适

**详细文档：** [音频播放测试脚本使用指南](../docs/playback-test-script-guide.md)

---

## 🎯 测试顺序建议

### 首次配置系统

按以下顺序测试，确保每个模块都正常工作：

```bash
# 1. 测试音频设备（最基础）
./tests/test_audio_48k.sh

# 2. 测试 ASR 识别（依赖录音）
python3 tests/test_asr_recognition.py

# 3. 测试播放功能（依赖 TTS）
python3 tests/test_playback.py

# 4. 运行完整系统
python3 realtime_assistant_main.py
```

### 调试特定问题

**录音问题：**
```bash
./tests/test_audio_48k.sh
```

**识别问题：**
```bash
python3 tests/test_asr_recognition.py
```

**播放问题：**
```bash
python3 tests/test_playback.py
```

---

## 🔬 技术要点

### 采样率配置

**关键发现：** Orange Pi AI Pro 硬件原生采样率是 **48000 Hz**

| 模块 | 录音采样率 | 处理采样率 | 播放采样率 |
|-----|----------|----------|----------|
| **音频设备** | 48000 Hz | - | 48000 Hz |
| **ASR 识别** | 48000 Hz | 16000 Hz（降采样） | - |
| **TTS 播放** | - | - | 48000 Hz |

**为什么这样设计？**
1. **录音使用 48000 Hz** - 硬件原生采样率，音质最佳
2. **ASR 降采样到 16000 Hz** - Paraformer 模型需要
3. **播放使用 48000 Hz** - 避免速度异常

### 音频设备参数

**必须设置的参数：**
```bash
amixer set Capture 10    # 录音音量（值越小信号越强）
amixer set Deviceid 2    # 设备 ID（2 = 耳机/麦克风）
amixer set Playback 10   # 播放音量
```

**播放设备：**
```bash
aplay -Dhw:ascend310b audio.wav
```

---

## 🐛 常见问题

### 问题 1：录音无声或音量低

**解决方案：**
```bash
# 降低 Capture 值（增强信号）
amixer set Capture 5
# 或者
amixer set Capture 1
```

### 问题 2：识别准确率低

**可能原因：**
- 录音质量差
- 环境噪音大
- 说话不清晰

**解决方案：**
- 在安静环境测试
- 靠近麦克风说话
- 调整 Capture 音量

### 问题 3：播放无声音

**解决方案：**
```bash
# 检查耳机连接
# 设置播放参数
amixer set Playback 10
amixer set Deviceid 2

# 测试官方音频
aplay -Dhw:ascend310b /opt/opi_test/audio/tianlu.wav
```

### 问题 4：播放速度异常

**可能原因：**
- 采样率不匹配

**解决方案：**
- 确保 TTS 生成 48000 Hz 音频
- 确保播放器使用正确的设备

---

## 📚 相关文档

### 详细使用指南

- [音频测试脚本使用指南](../docs/audio-test-script-guide.md)
- [ASR 识别测试脚本使用指南](../docs/asr-test-script-guide.md)
- [音频播放测试脚本使用指南](../docs/playback-test-script-guide.md)

### 问题修复报告

- [录音采样率问题修复报告](../docs/audio-capture-sample-rate-fix.md)
- [播放采样率问题修复报告](../docs/playback-sample-rate-fix.md)

### 配置指南

- [音频配置完全指南](../docs/AUDIO_SETUP.md)
- [项目开发路线图](../ROADMAP.md)

---

## 🎓 最佳实践

### 测试前准备

1. **确保耳机已插入** - 3.5mm 接口
2. **选择安静环境** - 减少背景噪音
3. **检查设备占用** - 确保音频设备未被占用
4. **准备测试内容** - 想好要说的话

### 测试建议

1. **首次测试** - 使用默认参数
2. **音量调整** - 根据实际效果调整
3. **多次测试** - 至少测试 2-3 次
4. **记录结果** - 记录最佳配置

### 集成前验证

在运行实时语音助手前，务必：

1. ✅ 运行所有测试脚本
2. ✅ 确认所有功能正常
3. ✅ 记录最佳配置参数
4. ✅ 验证端到端流程

---

## 📊 修复历史

### 2026-02-26 修复记录

#### 1. 录音采样率问题 ✅

**问题：** 使用 16000 Hz 录音导致失真
**修复：** 改为 48000 Hz 录音 + 降采样到 16000 Hz
**效果：** 识别准确率提升 9 倍（< 10% → > 90%）

#### 2. 播放设备问题 ✅

**问题：** 未指定播放设备，无声音
**修复：** 使用 `-Dhw:ascend310b` 指定设备
**效果：** 能听到声音

#### 3. 播放采样率问题 ✅

**问题：** TTS 生成 16000 Hz，播放快 3 倍
**修复：** 改为生成 48000 Hz 音频
**效果：** 播放速度正常

---

**创建者：** 哈雷酱（傲娇大小姐工程师）
**创建日期：** 2026-02-26
**状态：** 已验证，可用于生产

---

**哼，笨蛋！这些测试脚本都是本小姐精心设计的，一定要好好使用啊！(￣▽￣)ノ**

**所有脚本都经过实际验证，可以放心作为范本参考！( ` ω´ )**
