# RNNoise 降噪方案 - 暂时搁置

> **状态：** 暂时搁置，等待更好的录音设备
> **原因：** 当前录音设备信号太弱，RNNoise 降噪后 VAD 无法检测
> **日期：** 2026-01-19

---

## 📌 快速说明

本方案已完成技术验证，但由于当前录音设备的信号强度不足，RNNoise 降噪后会导致 VAD 检测失效。

**决定：** 暂时搁置此方案，等换用更好的录音设备后再考虑启用。

---

## 📂 相关文件

### 已实现的代码（可用但不推荐）

1. **`realtime_assistant/rnnoise_denoiser.py`**
   - RNNoise 降噪模块
   - 状态：✅ 已实现并测试通过
   - 建议：暂不集成到主流程

2. **`scripts/test_rnnoise.py`**
   - RNNoise 测试脚本
   - 状态：✅ 可用于测试
   - 用途：未来设备升级后可重新测试

3. **`/usr/local/lib/librnnoise.so`**
   - RNNoise C 库
   - 状态：✅ 已安装
   - 说明：保留在系统中，不影响其他功能

### 文档

1. **`docs/rnnoise-integration-report.md`**
   - 完整的测试报告
   - 包含问题分析和解决方案
   - 未来参考使用

---

## 🔄 当前方案

**继续使用 Phase 3 的基于能量的 VAD 算法**

**配置文件：** `config/vad_config.json`

```json
{
  "model": "models/silero_vad.onnx",
  "threshold": 0.3,
  "min_silence_duration": 1.5,
  "min_speech_duration": 0.3,
  "window_size": 512,
  "sample_rate": 16000,
  "buffer_size_seconds": 30,
  "energy_threshold": 0.002
}
```

**能量 VAD 参数：**
```python
energy_threshold = 100          # 能量阈值
min_silence_duration = 0.8      # 最小静音时长（秒）
min_speech_duration = 0.3       # 最小语音时长（秒）
```

**测试结果：** ✅ 成功分割 3 个语音片段

---

## 🚀 未来启用条件

当满足以下条件时，可以重新考虑启用 RNNoise：

### 1. 硬件升级

- [ ] 使用更好的麦克风（外置 USB 麦克风）
- [ ] 录音信号强度提高（最大值 > 10000）
- [ ] 信噪比改善（SNR > 20dB）

### 2. 重新测试

```bash
# 1. 使用新设备录音
arecord -D <新设备> -f S16_LE -r 48000 -c 1 -t raw -d 5 test_new.pcm
ffmpeg -f s16le -ar 48000 -ac 1 -i test_new.pcm -y test_new.wav

# 2. 测试 RNNoise 降噪
python3 scripts/test_rnnoise.py test_new.wav test_new_denoised.wav

# 3. 测试 VAD 分割
python3 scripts/test_vad_simple.py test_new_denoised.wav

# 4. 对比效果
# 如果 VAD 能检测到语音片段，说明可以启用 RNNoise
```

### 3. 集成到主流程

如果测试通过，可以修改 `realtime_assistant/audio_capture.py`：

```python
from .rnnoise_denoiser import RNNoiseDenoiser

class AudioCapture:
    def __init__(self, config: dict):
        # ... 现有代码 ...

        # 添加 RNNoise 降噪器（可选）
        if config.get("enable_rnnoise", False):
            self.denoiser = RNNoiseDenoiser(sample_rate=48000)
        else:
            self.denoiser = None

    def _read_loop(self):
        # ... 现有代码 ...

        # 降噪处理（如果启用）
        if self.denoiser:
            _, audio_data = self.denoiser.process_frame(audio_data)

        # ... 现有代码 ...
```

---

## 📝 备注

- RNNoise 相关代码保留在代码库中，不删除
- 系统中的 RNNoise 库保留，不卸载
- 文档完整记录了测试过程和结果
- 未来可以随时重新启用

---

**创建者：** 哈雷酱（傲娇大小姐工程师）
**日期：** 2026-01-19
**状态：** 暂时搁置

---

**哼，虽然暂时不用，但本小姐的代码质量可是一流的！等你换了好设备，随时可以启用！(￣▽￣)ノ**
