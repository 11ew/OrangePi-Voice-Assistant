# EdgeTTSdemo 项目文档索引

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **更新日期：** 2026-02-26（性能优化完成）

---

## 📚 核心文档

### 项目规划

- **[PRD - 产品需求文档](prd.md)** ⭐
  - 项目背景和目标
  - 功能需求和验收标准
  - 实施路线图（Phase 1-5）
  - 当前状态：Phase 3 完成

- **[实施计划](implementation-plan.md)**
  - 详细的实施步骤
  - 任务分解和时间安排

### 架构设计

- **[Brownfield 架构文档](brownfield-architecture.md)** ⭐
  - 项目真实状态记录
  - 技术栈和模块组织
  - 技术债务和已知问题
  - 集成点和依赖关系

- **[系统设计文档](REALTIME_ASSISTANT.md)**
  - 实时语音助手系统设计
  - 异步编排架构
  - 数据流和状态机

### 配置指南

- **[音频配置完全指南](AUDIO_SETUP.md)** ⭐
  - Orange Pi 音频设备配置
  - 🚀 一键测试脚本（推荐）
  - 录音和播放测试
  - 常见问题解决方案
  - ⚠️ 包含 WAV 格式录音 bug 的解决方法

- **[音频测试脚本使用指南](audio-test-script-guide.md)** ⭐
  - 自动化音频测试脚本详细说明
  - 测试流程和检查项
  - 故障排查和解决方案
  - 脚本定制和最佳实践
  - 完成日期：2026-02-26

- **[ASR 识别测试脚本使用指南](asr-test-script-guide.md)** ⭐ **新增**
  - ASR 语音识别测试工具
  - 48000 Hz → 16000 Hz 降采样验证
  - 识别准确率测试
  - 完整的测试流程和故障排查
  - 完成日期：2026-02-26

---

## 📊 阶段完成报告

### Phase 1: 基础验证 ✅

**状态：** 完成（2026-01-18）

**成果：**
- ✅ 音频设备配置和测试
- ✅ LLM 服务验证（DeepSeek API）
- ✅ TTS 服务验证（Edge-TTS）
- ✅ 基础对话流程测试

### Phase 2: ASR 集成 ✅

**状态：** 完成（2026-01-18）

**文档：** [Phase 2 完成报告](phase2-completion-report.md)

**成果：**
- ✅ Paraformer INT8 模型集成
- ✅ 中文、英文、混合识别全部优秀
- ✅ 识别速度快（2-3秒）
- ✅ 解决录音采样率配置问题

### Phase 3: VAD 集成 ✅

**状态：** 完成（2026-01-18）

**文档：** [Phase 3 完成报告](phase3-completion-report.md)

**成果：**
- ✅ Silero VAD 模型集成
- ✅ 发现并解决录音格式问题（WAV bug）
- ✅ 开发基于能量的 VAD 算法
- ✅ 成功实现自动语音分割

**关键发现：**
- Orange Pi 录音必须使用 RAW 格式
- Silero VAD 对底噪敏感
- 基于能量的 VAD 更适合有底噪环境

### Phase 4: 系统集成 🔲

**状态：** 待开始

**目标：**
- 异步编排验证
- 端到端集成测试
- 打断机制实现

---

## 🔬 技术研究报告

### VAD 优化研究

**文档：** [VAD 优化研究报告](vad-optimization-report.md) ⭐ **新增**

**完成日期：** 2026-01-19

**研究内容：**
- RNNoise 降噪技术研究
- Silero VAD 深度分析
- 能量 VAD 验证
- sherpa-onnx 框架解析
- 配置优化方案

**关键发现：**
1. **音量反向特性**：Orange Pi 音频驱动音量值越小，录音信号越强
2. **sherpa-onnx vs 官方 Silero VAD**：实现差异和参数限制
3. **RNNoise 结论**：不推荐在当前硬件环境使用（信号衰减 53%）
4. **最佳配置**：threshold=0.2, min_silence_duration=0.5s

### VAD 任务总结

**文档：** [VAD 任务总结报告](vad-task-summary.md) ⭐ **新增**

**完成日期：** 2026-01-19

**内容：**
- 任务完成情况总览
- 技术研究成果（RNNoise、Silero VAD、能量 VAD）
- 重要发现（音量反向特性、VPN 使用问题）
- 配置优化和文档更新
- 工作量统计和技术收获

### RNNoise 降噪集成

**文档：** [RNNoise 集成报告](rnnoise-integration-report.md)

**状态：** [暂时搁置](rnnoise-status.md)

**结论：**
- ✅ 技术验证完成
- ❌ 不适合当前录音设备
- ⏸️ 等待设备升级后重新评估

**关键发现：**
- RNNoise 会降低信号强度 51.5%
- 降噪后 VAD 无法检测语音
- 基于能量的 VAD 更适合当前场景

### 录音采样率问题修复

**文档：** [录音采样率问题修复报告](audio-capture-sample-rate-fix.md) ⭐ **新增**

**完成日期：** 2026-02-26

**问题：**
- 语音识别准确率极低（< 10%）
- 录音产生"魔音"失真效果
- arecord 进程意外崩溃

**根本原因：**
- 硬件采样率 48000 Hz，代码使用 16000 Hz
- 采样率不匹配导致音频失真

**解决方案：**
- 录音使用硬件原生 48000 Hz
- 软件层降采样到 16000 Hz（每 3 个样本取 1 个）
- 创建 ASR 测试脚本验证修复效果

**修复效果：**
- ✅ 识别准确率提升 9 倍（< 10% → > 90%）
- ✅ 音频质量完美，无失真
- ✅ 系统稳定运行，进程不再崩溃

**总结文档：** [2026-02-26 系统问题修复总结](system-fix-summary-2026-02-26.md) ⭐

### 播放采样率问题修复

**文档：** [播放采样率问题修复报告](playback-sample-rate-fix.md) ⭐ **新增**

**完成日期：** 2026-02-26

**问题：**
- 播放速度快 3 倍（像开了倍速）
- 内容难以听清

**根本原因：**
- TTS 生成 16000 Hz，播放设备 48000 Hz
- 采样率不匹配导致速度异常

**解决方案：**
- TTS 改为生成 48000 Hz 音频
- 与播放设备采样率匹配

**修复效果：**
- ✅ 播放速度正常
- ✅ 音质清晰
- ✅ 用户满意

### 性能优化（延迟优化）

**文档：** [性能优化报告](performance-optimization.md) ⭐⭐⭐ **新增**

**完成日期：** 2026-02-26

**优化目标：**
- 降低从识别到回答的延迟
- 提升用户体验

**实施方案：**
1. **Phase 1: 并行优化**
   - 连接预热
   - 音频设备预设置
   - 异步任务优化
   - 预计提速：10-20%

2. **Phase 2: 流式处理** ⭐⭐⭐
   - LLM 流式输出
   - TTS 流式合成
   - 流式播放
   - 预计提速：50-70%

**优化效果：**
- ✅ 首字延迟：6-8秒 → 1-2秒（提升 70-80%）
- ✅ 用户体验：显著提升，接近实时对话
- ✅ 系统稳定性：保持稳定

**测试脚本：**
- `tests/test_streaming.py` - 流式处理测试套件

---

## 📖 Story 文档

### Epic 1: 音频设备配置

- **[Story 1.1: 音频设备配置和测试](stories/1.1-audio-device-setup.md)** ✅
  - 状态：完成
  - 质量门控：[QA Gate](qa/gates/1.1-audio-device-setup.yml)

---

## 🛠️ 快速开始

### 新手入门

1. **阅读 [README.md](../README.md)**
   - 项目简介和核心功能
   - 快速开始指南

2. **配置音频设备**
   - 参考 [音频配置指南](AUDIO_SETUP.md)
   - 完成 Story 1.1 的测试

3. **运行基础测试**
   ```bash
   # 测试 LLM
   python3 scripts/deepseek_chat.py "你好"
   
   # 测试 TTS
   python3 scripts/tts_generate.py "测试" output/test.wav
   
   # 测试 ASR
   python3 scripts/speech_to_text.py output/test.wav
   ```

### 开发者指南

1. **理解架构**
   - 阅读 [Brownfield 架构文档](brownfield-architecture.md)
   - 了解各模块的职责和依赖

2. **查看 PRD**
   - 阅读 [PRD 文档](prd.md)
   - 了解项目目标和实施计划

3. **参考完成报告**
   - Phase 2: ASR 集成经验
   - Phase 3: VAD 集成和问题解决

---

## 🔧 配置文件

### 主配置

- **`config/realtime_config.json`** - 系统主配置
- **`config/asr_config.json`** - ASR 配置
- **`config/vad_config.json`** - VAD 配置

### 重要参数

**音频设备：**
```json
{
  "sample_rate": 16000,
  "channels": 1,
  "device": "plughw:0,1"
}
```

**VAD 配置：**
```json
{
  "threshold": 0.3,
  "min_silence_duration": 1.5,
  "min_speech_duration": 0.3,
  "energy_threshold": 0.002
}
```

---

## 📝 内部提示

- **[PROJECT_NOTES.md](../PROJECT_NOTES.md)** ⭐
  - 系统密码和权限信息
  - VPN 配置和使用
  - 音频测试特别规定
  - 常用命令速查

---

## 🐛 问题排查

### 常见问题

1. **音频无声**
   - 参考：[AUDIO_SETUP.md](AUDIO_SETUP.md) - 问题排查章节

2. **录音格式问题**
   - 参考：[Phase 3 报告](phase3-completion-report.md) - 问题 1

3. **VAD 无法分割**
   - 参考：[Phase 3 报告](phase3-completion-report.md) - 问题 2

4. **ASR 识别失败**
   - 参考：[Phase 2 报告](phase2-completion-report.md)

---

## 📞 获取帮助

- 查看相关文档的"常见问题"章节
- 参考 Phase 完成报告中的问题解决方案
- 查看 [PROJECT_NOTES.md](../PROJECT_NOTES.md) 的快速命令

---

**文档维护者：** 哈雷酱（傲娇大小姐工程师）
**最后更新：** 2026-02-26

---

**哼，本小姐的文档可是非常完善的！笨蛋们要好好利用哦！(￣▽￣)ノ**
