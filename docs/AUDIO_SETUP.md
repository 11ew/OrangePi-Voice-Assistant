# 🎵 Orange Pi AI Pro 音频配置完全指南

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **版本：** 1.0.1
> **日期：** 2026-01-18
> **适用设备：** Orange Pi AI Pro (Ascend 310B)

---

## ⚠️ 重要提示

### 项目特殊说明

1. **系统权限密码**
   - 如果需要 sudo 权限，密码为：`Mind@123`
   - 某些音频配置命令可能需要 root 权限

2. **网络配置（VPN）**
   - 如果需要访问 GitHub 或查找技术资料时使用
   - 主要用于：
     - 访问 GitHub（下载代码、查看文档、下载模型）
     - 查找技术资料（Stack Overflow、技术博客等）
   - 使用以下终端命令：
     ```bash
     vpn        # 开启 VPN
     vpntest    # 测试 VPN 连接
     vpnoff     # 关闭 VPN（⚠️ 用完及时关闭，避免网速过慢）
     ```
   - **⚠️ 重要：** VPN 会降低网速，用完后立即关闭
   - **注意：** DeepSeek API 和 Edge-TTS 是国内可访问的服务，不需要 VPN

3. **⚠️ 音频测试特别注意**
   - **本项目音频测试必须由用户亲自测试并反馈结果**
   - **不得由 AI 助手自行测试，可能会误判**
   - **所有音频功能以用户实际测试结果为准**
   - 测试时请确保：
     - 耳机已正确插入 3.5mm 接口
     - 麦克风正常工作
     - 音量已调整到合适水平
     - 在安静环境下测试

---

## 📋 目录

- [重要提示](#重要提示)
- [系统音频设备概述](#系统音频设备概述)
- [官方音频测试](#官方音频测试)
- [音频设备配置](#音频设备配置)
- [常见问题排查](#常见问题排查)
- [最佳实践](#最佳实践)

---

## 系统音频设备概述

### 硬件信息

Orange Pi AI Pro 使用 **Ascend 310B** 音频芯片，提供以下音频接口：

| 接口类型 | 说明 | 用途 |
|---------|------|------|
| **3.5mm 耳机接口** | 标准耳机插孔 | 音频输出（播放） |
| **板载麦克风** | 内置麦克风 | 音频输入（录音） |
| **HDMI 音频** | HDMI0/HDMI1 | 音频输出（可选） |

### ALSA 设备信息

使用以下命令查看系统音频设备：

```bash
# 查看录音设备
arecord -l

# 输出示例：
# **** CAPTURE 硬體裝置清單 ****
# card 0: ascend310b [ascend310b], device 1: ascend310b-capture ascend310b-hifi-1 []
#   子设备: 1/1
#   子设备 #0: subdevice #0

# 查看播放设备
aplay -l

# 输出示例：
# **** PLAYBACK 硬體裝置清單 ****
# card 0: ascend310b [ascend310b], device 0: ascend310b-playback ascend310b-hifi-0 []
#   子设备: 1/1
#   子设备 #0: subdevice #0
```

**关键信息：**
- **录音设备：** `card 0, device 1` → `plughw:0,1` 或 `hw:0,1`
- **播放设备：** `card 0, device 0` → `hw:ascend310b` 或 `hw:0,0`

---

## 官方音频测试

### 准备工作

1. **插入耳机**：将 3.5mm 耳机插入开发板的耳机接口
2. **进入测试目录**：
   ```bash
   sudo -i
   cd /opt/opi_test/audio
   ls
   # 输出：play_hdmi0.sh play_hdmi1.sh play_headset.sh record.sh tianlu.pcm tianlu.wav
   ```

### 测试 1：播放测试音频到耳机

**⚠️ 重要：此测试需要用户亲自执行并反馈结果，不得由 AI 助手自行判断！**

```bash
# 执行播放脚本
./play_headset.sh
```

**脚本内容：**
```bash
amixer set Playback 10        # 设置播放音量为 10
amixer set Deviceid 2         # 设置设备 ID 为 2（耳机）
aplay -Dhw:ascend310b -f S16_LE -r 48000 -t wav /opt/opi_test/audio/tianlu.wav
```

**参数说明：**
- `-D hw:ascend310b`：使用 ascend310b 播放设备
- `-f S16_LE`：音频格式为 16-bit 有符号小端序
- `-r 48000`：采样率 48000 Hz
- `-t wav`：文件类型为 WAV

**用户测试检查项：**
- [ ] 耳机中能听到测试音频（"天路"）
- [ ] 声音清晰，无杂音
- [ ] 音量适中，不过大或过小

**如果测试失败，请反馈：**
1. 是否有声音？（有/无）
2. 声音质量如何？（清晰/有杂音/失真）
3. 音量是否正常？（正常/过大/过小/无声）

---

### 测试 2：录音并播放

**⚠️ 重要：此测试需要用户亲自执行并反馈结果，不得由 AI 助手自行判断！**

```bash
# 执行录音脚本
./record.sh
```

**脚本内容：**
```bash
amixer set Capture 10                                    # 设置录音音量为 10
amixer set Deviceid 2                                    # 设置设备 ID 为 2
arecord -D plughw:0,1 -f S16_LE -r 48000 -t raw -d 5 record.pcm  # 录音 5 秒
aplay -Dhw:ascend310b -f S16_LE -r 48000 -t raw record.pcm       # 播放录音
```

**参数说明：**
- `-D plughw:0,1`：使用 card 0, device 1 录音设备（带插件层）
- `-d 5`：录音时长 5 秒
- `-t raw`：原始 PCM 格式（无文件头）

**用户测试步骤：**
1. 执行 `./record.sh` 命令
2. 看到提示后，对着麦克风清晰地说话（5 秒）
3. 录音完成后，脚本会自动播放录音
4. 通过耳机听录音内容

**用户测试检查项：**
- [ ] 录音过程正常（无错误提示）
- [ ] 能听到自己刚才说的话
- [ ] 录音清晰，能听清楚内容
- [ ] 无明显噪音或失真

**如果测试失败，请反馈：**
1. 录音是否成功？（成功/失败/有错误提示）
2. 播放时能否听到声音？（能/不能）
3. 录音质量如何？（清晰/有噪音/失真/无声）
4. 能否听清楚说话内容？（能/不能/部分能）

---

## 音频设备配置

### 配置原则

根据官方测试脚本，正确的音频设备配置如下：

| 用途 | 设备标识 | 采样率 | 格式 | 说明 |
|-----|---------|--------|------|------|
| **录音** | `plughw:0,1` | 48000 Hz | S16_LE | 使用插件层，自动转换采样率 |
| **播放** | `hw:ascend310b` | 48000 Hz | S16_LE | 直接访问硬件设备 |

### 实时语音助手配置

#### 1. 修改主配置文件

编辑 `config/realtime_config.json`：

```json
{
  "audio": {
    "sample_rate": 16000,        // ASR 模型要求 16kHz
    "channels": 1,               // 单声道
    "chunk_size": 1600,          // 100ms @ 16kHz
    "device": "plughw:0,1"       // ⚠️ 重要：使用 plughw:0,1
  }
}
```

**为什么使用 `plughw:0,1` 而不是 `hw:0,1`？**

- `plughw` 是 ALSA 的插件层，支持**自动采样率转换**
- 硬件设备支持 48000 Hz，但 ASR 模型需要 16000 Hz
- `plughw` 会自动将 48000 Hz 转换为 16000 Hz
- `hw` 直接访问硬件，不支持采样率转换

#### 2. 音频捕获模块配置

`realtime_assistant/audio_capture.py` 中的设备配置：

```python
class AudioCapture:
    def __init__(self, config: dict):
        self.sample_rate = config.get("sample_rate", 16000)  # 16kHz
        self.channels = config.get("channels", 1)            # 单声道
        self.chunk_size = config.get("chunk_size", 1600)     # 100ms
        self.device = config.get("device", "plughw:0,1")     # ⚠️ 重要
```

#### 3. arecord 命令参数

```bash
arecord \
  -D plughw:0,1 \      # 录音设备（带插件层）
  -f S16_LE \          # 16-bit 有符号小端序
  -r 16000 \           # 采样率 16kHz（会自动从 48kHz 转换）
  -c 1 \               # 单声道
  -t raw               # 原始 PCM 格式
```

---

## 常见问题排查

### 问题 1：录音无声音或噪音

**症状：** 录音文件无声音或全是噪音

**可能原因：**
1. 设备标识错误（使用了 `default` 或 `hw:0,0`）
2. 采样率不匹配
3. 麦克风音量过低

**解决方案：**

```bash
# 1. 检查录音设备
arecord -l

# 2. 设置麦克风音量
amixer set Capture 10

# 3. 测试录音（5秒）
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav -d 5 test.wav

# 4. 播放测试
aplay -Dhw:ascend310b test.wav
```

---

### 问题 2：播放无声音

**症状：** 播放音频文件时耳机无声音

**可能原因：**
1. 耳机未插好
2. 播放设备错误
3. 音量过低
4. 设备 ID 未设置

**解决方案：**

```bash
# 1. 检查播放设备
aplay -l

# 2. 设置播放音量和设备 ID
amixer set Playback 10
amixer set Deviceid 2

# 3. 测试播放
aplay -Dhw:ascend310b /opt/opi_test/audio/tianlu.wav
```

---

### 问题 3：采样率转换失败

**症状：** 提示 "Sample rate not available" 或音频失真

**可能原因：**
1. 使用了 `hw:0,1` 而不是 `plughw:0,1`
2. 硬件不支持目标采样率

**解决方案：**

```bash
# ❌ 错误：直接访问硬件（不支持 16kHz）
arecord -D hw:0,1 -f S16_LE -r 16000 -c 1 -t wav test.wav

# ✅ 正确：使用插件层（自动转换采样率）
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav test.wav
```

---

### 问题 4：设备忙碌（Device or resource busy）

**症状：** 提示 "Device or resource busy"

**可能原因：**
1. 其他进程正在使用音频设备
2. 之前的进程未正常退出

**解决方案：**

```bash
# 1. 查找占用音频设备的进程
lsof /dev/snd/*

# 2. 杀死占用进程
kill -9 <PID>

# 3. 或者重启 ALSA 服务
sudo systemctl restart alsa-restore
```

---

## 最佳实践

### 1. 音频设备选择

| 场景 | 推荐设备 | 说明 |
|-----|---------|------|
| **实时语音助手** | `plughw:0,1` | 支持采样率转换，兼容性好 |
| **高质量录音** | `hw:0,1` + 48kHz | 直接访问硬件，音质最佳 |
| **快速测试** | `default` | 使用默认设备，但可能不稳定 |

### 2. 采样率选择

| 用途 | 推荐采样率 | 说明 |
|-----|-----------|------|
| **ASR 识别** | 16000 Hz | Paraformer/SenseVoice 模型要求 |
| **TTS 合成** | 16000 Hz | Edge-TTS 输出 |
| **高质量录音** | 48000 Hz | 硬件原生支持 |

### 3. 音频格式选择

| 格式 | 说明 | 用途 |
|-----|------|------|
| **S16_LE** | 16-bit 有符号小端序 | 标准 PCM 格式，兼容性好 |
| **FLOAT_LE** | 32-bit 浮点小端序 | 高精度，但占用空间大 |

### 4. 配置检查清单

在启动实时语音助手前，请检查以下配置：

- [ ] 耳机已插入 3.5mm 接口
- [ ] 录音设备设置为 `plughw:0,1`
- [ ] 播放设备设置为 `hw:ascend310b`
- [ ] 采样率设置为 16000 Hz
- [ ] 声道数设置为 1（单声道）
- [ ] 音量已设置（Capture 10, Playback 10）
- [ ] 设备 ID 已设置为 2

### 5. 快速测试脚本

创建测试脚本 `test_audio.sh`：

```bash
#!/bin/bash

echo "🎵 Orange Pi AI Pro 音频测试"
echo "=============================="

# 1. 检查音频设备
echo ""
echo "📋 1. 检查音频设备..."
echo "录音设备："
arecord -l | grep ascend310b
echo "播放设备："
aplay -l | grep ascend310b

# 2. 设置音量
echo ""
echo "🔊 2. 设置音量..."
amixer set Capture 10
amixer set Playback 10
amixer set Deviceid 2

# 3. 录音测试
echo ""
echo "🎤 3. 录音测试（5秒）..."
echo "请对着麦克风说话..."
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav -d 5 /tmp/test_audio.wav

# 4. 播放测试
echo ""
echo "🔊 4. 播放测试..."
echo "请听耳机中的声音..."
aplay -Dhw:ascend310b /tmp/test_audio.wav

# 5. 清理
rm -f /tmp/test_audio.wav

echo ""
echo "✅ 测试完成！"
```

使用方法：

```bash
chmod +x test_audio.sh
./test_audio.sh
```

---

## 技术细节

### ALSA 设备命名规则

| 格式 | 说明 | 示例 |
|-----|------|------|
| `hw:X,Y` | 直接访问硬件，card X, device Y | `hw:0,1` |
| `plughw:X,Y` | 带插件层，支持格式转换 | `plughw:0,1` |
| `hw:NAME` | 使用设备名称 | `hw:ascend310b` |
| `default` | 默认设备 | `default` |

### 采样率转换原理

```
硬件设备 (48000 Hz)
        ↓
   ALSA 插件层 (plughw)
   - 重采样算法
   - 格式转换
        ↓
应用程序 (16000 Hz)
```

### 音频数据流

```
麦克风 → ALSA驱动 → plughw插件 → arecord → 应用程序
                    (48kHz→16kHz)

应用程序 → aplay → ALSA驱动 → 扬声器/耳机
```

---

## 参考资料

- [ALSA 官方文档](https://www.alsa-project.org/wiki/Main_Page)
- [Orange Pi AI Pro 用户手册](http://www.orangepi.org/)
- [Sherpa-ONNX 音频配置](https://k2-fsa.github.io/sherpa/onnx/)

---

## 更新日志

| 版本 | 日期 | 说明 |
|-----|------|------|
| 1.0.0 | 2026-01-18 | 初始版本，完整的音频配置指南 |

---

**本文档由哈雷酱精心编写，保证完美无缺！(￣▽￣)ノ**

如有问题，请参考[常见问题排查](#常见问题排查)章节，或者联系本小姐！
