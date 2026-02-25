# 更新日志

> **项目：** EdgeTTSdemo 实时语音助手系统
> **维护者：** 哈雷酱（傲娇大小姐工程师）

---

## [Unreleased]

### Phase 4: 系统集成（进行中）

**目标：**
- 异步编排验证
- 端到端集成测试
- 打断机制实现

---

## [2026-01-19] - RNNoise 降噪研究

### 🔬 技术研究

#### Added
- ✅ RNNoise C 库编译和安装
- ✅ Python 封装模块 `realtime_assistant/rnnoise_denoiser.py`
- ✅ 测试脚本 `scripts/test_rnnoise.py`
- ✅ 完整测试报告 `docs/rnnoise-integration-report.md`
- ✅ 状态说明文档 `docs/rnnoise-status.md`
- ✅ 功能说明 `README_RNNOISE.md`

#### Tested
- ✅ RNNoise 降噪功能验证
- ✅ 降噪效果测试（信号衰减 51.5%）
- ✅ VAD 检测效果测试（降噪后失效）

#### Decided
- ⏸️ **暂时搁置 RNNoise 方案**
  - 原因：当前录音设备信号强度不足
  - 决定：等待设备升级后重新评估
  - 保留：代码和库保留供未来使用

#### Documentation
- ✅ 更新文档索引 `docs/index.md`
- ✅ 添加 RNNoise 相关文档
- ✅ 记录测试结果和决策理由

---

## [2026-01-18] - Phase 3 完成

### ✅ Phase 3: VAD 集成

#### Added
- ✅ Silero VAD 模型集成
- ✅ VAD 检测器模块 `realtime_assistant/vad_detector.py`
- ✅ 基于能量的 VAD 算法 `scripts/test_vad_energy.py`
- ✅ VAD 测试脚本 `scripts/test_vad_simple.py`
- ✅ VAD + 录音集成测试 `scripts/test_vad_record.sh`

#### Fixed
- ✅ 发现并解决 Orange Pi WAV 格式录音 bug
  - 问题：使用 `-t wav` 录音音量极低
  - 解决：使用 RAW 格式录音 + ffmpeg 转换
- ✅ Silero VAD 底噪敏感问题
  - 问题：无法在有底噪环境下分割语音
  - 解决：开发基于能量的 VAD 算法

#### Tested
- ✅ Silero VAD 功能测试
- ✅ 基于能量的 VAD 测试（成功分割 3 个语音片段）
- ✅ VAD + 录音集成测试

#### Documentation
- ✅ Phase 3 完成报告 `docs/phase3-completion-report.md`
- ✅ 更新音频配置文档 `docs/AUDIO_SETUP.md`
- ✅ 更新 PRD 文档 `docs/prd.md`
- ✅ 更新架构文档 `docs/brownfield-architecture.md`

---

## [2026-01-18] - Phase 2 完成

### ✅ Phase 2: ASR 集成

#### Added
- ✅ Paraformer INT8 模型集成
- ✅ ASR 引擎模块 `realtime_assistant/asr_engine.py`
- ✅ 语音识别脚本 `scripts/speech_to_text.py`
- ✅ 录音 + ASR 集成测试脚本

#### Fixed
- ✅ 录音采样率配置问题
  - 硬件原生支持：48000 Hz
  - ASR 要求：16000 Hz
  - 解决：自动重采样

#### Tested
- ✅ 中文识别：优秀
- ✅ 英文识别：优秀
- ✅ 中英文混合识别：优秀
- ✅ 识别速度：2-3秒（INT8 模型）

#### Documentation
- ✅ Phase 2 完成报告 `docs/phase2-completion-report.md`
- ✅ 更新 PRD 文档
- ✅ 更新架构文档

---

## [2026-01-18] - Phase 1 完成

### ✅ Phase 1: 基础验证

#### Added
- ✅ 音频设备配置和测试
- ✅ LLM 服务测试（DeepSeek API）
- ✅ TTS 服务测试（Edge-TTS）
- ✅ 基础对话流程测试脚本

#### Tested
- ✅ 录音设备：`plughw:0,1`（48kHz）
- ✅ 播放设备：`hw:ascend310b`（耳机输出）
- ✅ LLM 响应时间：平均 2.188秒
- ✅ TTS 生成时间：平均 2.7秒

#### Documentation
- ✅ Story 1.1 文档 `docs/stories/1.1-audio-device-setup.md`
- ✅ 音频配置完全指南 `docs/AUDIO_SETUP.md`
- ✅ PRD 文档 `docs/prd.md`
- ✅ 架构文档 `docs/brownfield-architecture.md`
- ✅ 实施计划 `docs/implementation-plan.md`

---

## [2026-01-03] - 初始版本

### Added
- ✅ 基础 TTS 功能（Edge-TTS）
- ✅ 简单音频播放器（使用 aplay）
- ✅ 交互式 TTS 工具
- ✅ 项目基础文档

---

## 版本说明

### 版本号规则

- **Phase X 完成** - 主要阶段完成
- **日期标记** - 功能更新和修复

### 状态标记

- ✅ 已完成
- 🔲 待开始
- ⏸️ 暂时搁置
- ❌ 已取消

---

**维护者：** 哈雷酱（傲娇大小姐工程师）
**最后更新：** 2026-01-19

---

**哼，本小姐的更新日志可是非常详细的！(￣▽￣)ノ**
