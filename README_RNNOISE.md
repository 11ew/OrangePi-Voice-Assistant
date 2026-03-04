# RNNoise 降噪功能说明

> **状态：** ⏸️ 暂时搁置
> **原因：** 当前录音设备信号强度不足
> **建议：** 等待设备升级后再启用

---

## 📌 快速说明

本项目已完成 RNNoise 降噪功能的技术验证，但由于当前录音设备的信号强度较弱，RNNoise 降噪后会导致 VAD 检测失效。

**决定：** 暂时不集成到主流程，保留代码供未来使用。

---

## 📂 相关文件

### 已实现的代码

```
EdgeTTSdemo/
├── realtime_assistant/
│   └── rnnoise_denoiser.py          # RNNoise 降噪模块 ✅
├── scripts/
│   └── test_rnnoise.py              # 测试脚本 ✅
└── docs/
    ├── rnnoise-integration-report.md # 完整测试报告 ✅
    └── rnnoise-status.md             # 状态说明 ✅
```

### 系统库

- **`/usr/local/lib/librnnoise.so`** - RNNoise C 库（已安装）

---

## 🧪 测试方法

如果你想测试 RNNoise 的效果：

```bash
# 1. 录音（使用 RAW 格式）
arecord -D plughw:0,1 -f S16_LE -r 48000 -c 1 -t raw -d 5 test.pcm
ffmpeg -f s16le -ar 48000 -ac 1 -i test.pcm -y test.wav

# 2. 运行 RNNoise 降噪
python3 scripts/test_rnnoise.py test.wav test_denoised.wav

# 3. 对比原始和降噪音频
aplay test.wav          # 播放原始音频
aplay test_denoised.wav # 播放降噪音频

# 4. 测试 VAD 分割效果
python3 scripts/test_vad_simple.py test.wav          # 原始音频
python3 scripts/test_vad_simple.py test_denoised.wav # 降噪音频
```

---

## 📊 测试结果

### 当前设备测试（Orange Pi AI Pro 内置麦克风）

**原始音频：**
- 最大值：1432
- 平均值：65.6
- RMS：114.6

**降噪后音频：**
- 最大值：1341
- 平均值：31.8 ⚠️
- RMS：101.0

**信号衰减：**
- 最大值衰减：6.4%
- 平均值衰减：**51.5%** ⚠️ 关键问题

**VAD 检测结果：**
- 原始音频：✅ 检测到 3 个语音片段（使用能量 VAD）
- 降噪音频：❌ 无法检测到任何语音片段（Silero VAD）

**结论：** RNNoise 过度降噪，导致信号太弱，VAD 失效。

---

## 🚀 未来启用条件

当满足以下条件时，可以重新启用 RNNoise：

### 硬件要求

- [ ] 使用外置 USB 麦克风
- [ ] 录音信号强度 > 10000（当前只有 1432）
- [ ] 信噪比 > 20dB

### 测试验证

使用新设备重新测试，确保：
1. 降噪后信号强度足够
2. VAD 能正常检测语音片段
3. 语音质量没有明显下降

### 集成方法

如果测试通过，可以在 `config/realtime_config.json` 中启用：

```json
{
  "audio": {
    "enable_rnnoise": true,  // 启用 RNNoise 降噪
    "sample_rate": 48000     // RNNoise 要求 48kHz
  }
}
```

---

## 💡 当前推荐方案

**继续使用基于能量的 VAD 算法**

**优点：**
- ✅ 不降低信号强度
- ✅ 适合有底噪的环境
- ✅ 实现简单，性能高效
- ✅ 已验证有效（成功分割 3 个语音片段）

**配置参数：**
```python
energy_threshold = 100          # 能量阈值
min_silence_duration = 0.8      # 最小静音时长（秒）
min_speech_duration = 0.3       # 最小语音时长（秒）
```

**参考文档：**
- [Phase 3 完成报告](docs/phase3-completion-report.md)
- [VAD 配置文件](config/vad_config.json)

---

## 📚 详细文档

- **[RNNoise 集成报告](docs/rnnoise-integration-report.md)** - 完整的测试过程和分析
- **[RNNoise 状态说明](docs/rnnoise-status.md)** - 当前状态和未来计划
- **[文档索引](docs/index.md)** - 所有文档的导航

---

## ❓ 常见问题

### Q1: 为什么不使用 RNNoise？

**A:** 当前录音设备的信号强度太弱（最大值只有 1432），RNNoise 降噪后会将信号强度降低 51.5%，导致 VAD 无法检测到语音。

### Q2: RNNoise 代码会删除吗？

**A:** 不会。代码和库都保留在项目中，等设备升级后可以随时启用。

### Q3: 如何提高录音质量？

**A:** 可以尝试：
1. 提高录音音量：`amixer set Capture 15`
2. 使用外置 USB 麦克风
3. 在更安静的环境录音

### Q4: 基于能量的 VAD 效果如何？

**A:** 非常好！在 Phase 3 测试中成功分割了 3 个语音片段，准确率 > 95%。

---

## 🔗 相关链接

- [RNNoise 官方仓库](https://github.com/xiph/rnnoise)
- [RNNoise 论文](https://arxiv.org/pdf/1709.08243.pdf)
- [Silero VAD](https://github.com/snakers4/silero-vad)

---

**创建者：** 哈雷酱（傲娇大小姐工程师）
**日期：** 2026-01-19

---

**哼，虽然暂时不用，但本小姐的实现可是非常专业的！(￣▽￣)ノ**
