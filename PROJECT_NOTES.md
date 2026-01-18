# 📝 EdgeTTSdemo 项目内部提示文档

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **版本：** 1.0.0
> **日期：** 2026-01-18
> **用途：** 项目开发和维护的重要提示信息

---

## 🔐 系统权限信息

### Root 密码
```
密码：Mind@123
```

**使用场景：**
- 需要 sudo 权限时
- 系统配置修改
- 音频设备配置
- 安装系统级依赖

**示例：**
```bash
sudo -i
# 输入密码：Mind@123

# 或者
sudo amixer set Capture 10
# 输入密码：Mind@123
```

---

## 🌐 网络配置（VPN）

### VPN 命令

如果需要访问 GitHub 或查找技术资料时，可以使用 VPN：

```bash
# 开启 VPN
vpn

# 测试 VPN 连接
vpntest

# 关闭 VPN（用完及时关闭，避免网速过慢）
vpnoff
```

### 需要 VPN 的场景

| 场景 | 说明 | 是否需要 VPN |
|-----|------|------------|
| **访问 GitHub** | 下载代码、查看文档、下载模型 | ✅ 需要 |
| **查找技术资料** | Stack Overflow、技术博客等 | ✅ 可能需要 |
| **下载模型文件** | 从 GitHub Releases 下载 | ✅ 需要 |
| **pip 安装** | Python 包安装 | ❌ 通常不需要 |
| **DeepSeek API** | LLM 对话生成 | ❌ 不需要（国内可访问） |
| **Edge-TTS** | 语音合成 | ❌ 不需要（国内可访问） |

### ⚠️ 重要提示

- **用完及时关闭 VPN**：VPN 会降低网速，用完后立即执行 `vpnoff`
- **仅在必要时使用**：只在访问 GitHub 或查资料时开启
- **不要长时间开启**：会影响其他网络服务的速度

### 网络问题排查流程

1. **确定是否需要 VPN**
   - 访问 GitHub？→ 需要 VPN
   - 查找技术资料？→ 可能需要 VPN
   - 使用国内 API？→ 不需要 VPN

2. **测试网络连接**
   ```bash
   # 测试 GitHub 连接
   ping github.com

   # 测试国内服务
   ping api.deepseek.com
   ```

3. **如果访问 GitHub 失败，开启 VPN**
   ```bash
   vpn
   ```

4. **测试 VPN 连接**
   ```bash
   vpntest
   ```

5. **完成操作后立即关闭 VPN**
   ```bash
   vpnoff
   ```

### 使用示例

#### 场景 1：从 GitHub 下载模型

```bash
# 1. 开启 VPN
vpn

# 2. 下载模型
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx

# 3. 立即关闭 VPN
vpnoff
```

#### 场景 2：查看 GitHub 文档

```bash
# 1. 开启 VPN
vpn

# 2. 使用浏览器访问 GitHub
# 查看文档、下载代码等

# 3. 完成后立即关闭 VPN
vpnoff
```

#### 场景 3：使用国内 API（不需要 VPN）

```bash
# DeepSeek API 和 Edge-TTS 都是国内可访问的服务
# 不需要开启 VPN，直接使用即可

# 测试 DeepSeek API
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer sk-xxx" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}]}'
```

---

## 🎵 音频测试特别规定

### ⚠️ 重要原则

**本项目音频测试必须遵守以下规定：**

1. **用户测试原则**
   - 所有音频功能测试必须由用户亲自执行
   - AI 助手不得自行测试音频功能
   - AI 助手不得假设测试结果
   - AI 助手不得根据命令输出判断音频是否正常

2. **为什么不能自动测试？**
   - 音频播放需要人耳听到才能确认
   - 录音质量需要人耳判断
   - 命令执行成功 ≠ 音频功能正常
   - 可能出现"有输出但无声音"的情况
   - 可能出现"有声音但质量差"的情况

3. **AI 助手的职责**
   - ✅ 提供测试命令和步骤
   - ✅ 解释测试原理和参数
   - ✅ 根据用户反馈排查问题
   - ✅ 提供解决方案和建议
   - ❌ 不得自行执行音频测试
   - ❌ 不得假设测试结果
   - ❌ 不得根据命令输出判断成功

### 正确的测试流程

#### 1. AI 助手提供测试指导

```markdown
请执行以下测试命令：

\`\`\`bash
# 录音 5 秒
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav -d 5 test.wav

# 播放测试
aplay -Dhw:ascend310b test.wav
\`\`\`

**请反馈以下信息：**
1. 录音过程是否有错误？（有/无）
2. 播放时能否听到声音？（能/不能）
3. 声音质量如何？（清晰/有噪音/失真）
4. 能否听清楚说话内容？（能/不能）
```

#### 2. 用户执行测试并反馈

用户反馈示例：
- "录音成功，能听到声音，但有点噪音"
- "录音失败，提示设备忙碌"
- "播放无声音，但命令执行成功"

#### 3. AI 助手根据反馈提供解决方案

根据用户的具体反馈，提供针对性的解决方案。

### 测试检查清单

**播放测试：**
- [ ] 耳机已插入 3.5mm 接口
- [ ] 执行播放命令无错误
- [ ] 耳机中能听到声音
- [ ] 声音清晰，无杂音
- [ ] 音量适中

**录音测试：**
- [ ] 麦克风正常工作
- [ ] 执行录音命令无错误
- [ ] 录音文件生成成功
- [ ] 播放录音能听到声音
- [ ] 录音清晰，能听清内容
- [ ] 无明显噪音或失真

### 常见误判场景

| 场景 | 命令输出 | 实际情况 | 正确判断 |
|-----|---------|---------|---------|
| **播放无声** | 命令执行成功 | 耳机无声音 | 需要用户反馈 |
| **录音失败** | 命令执行成功 | 录音文件为空 | 需要用户反馈 |
| **设备错误** | 命令执行成功 | 使用了错误设备 | 需要用户反馈 |
| **音质问题** | 命令执行成功 | 声音失真/有噪音 | 需要用户反馈 |

---

## 📁 项目目录结构

```
EdgeTTSdemo/
├── realtime_assistant/          # 核心模块
│   ├── assistant.py             # 主控制器
│   ├── asr_engine.py            # ASR 引擎
│   ├── audio_capture.py         # 音频捕获
│   ├── llm_engine.py            # LLM 引擎
│   ├── tts_engine.py            # TTS 引擎
│   ├── vad_detector.py          # VAD 检测器
│   ├── audio_player.py          # 音频播放器
│   ├── state_machine.py         # 状态机
│   └── utils.py                 # 工具函数
├── config/                      # 配置文件
│   ├── realtime_config.json     # 主配置
│   ├── asr_config.json          # ASR 配置
│   └── vad_config.json          # VAD 配置
├── docs/                        # 文档
│   ├── REALTIME_ASSISTANT.md    # 系统设计文档
│   ├── AUDIO_SETUP.md           # 音频配置指南
│   └── PROJECT_NOTES.md         # 项目内部提示（本文档）
├── models/                      # 模型文件
├── output/                      # 输出目录
├── scripts/                     # 辅助脚本
└── realtime_assistant_main.py   # 主程序入口
```

---

## 🔧 常用命令速查

### 音频设备查看

```bash
# 查看录音设备
arecord -l

# 查看播放设备
aplay -l

# 查看音量设置
amixer
```

### 音频测试

```bash
# 录音测试（5秒）
arecord -D plughw:0,1 -f S16_LE -r 16000 -c 1 -t wav -d 5 test.wav

# 播放测试
aplay -Dhw:ascend310b test.wav

# 设置音量
amixer set Capture 10
amixer set Playback 10
amixer set Deviceid 2
```

### 进程管理

```bash
# 查找占用音频设备的进程
lsof /dev/snd/*

# 杀死进程
kill -9 <PID>

# 查看 Python 进程
ps aux | grep python
```

### 日志查看

```bash
# 查看实时日志
tail -f output/realtime_assistant.log

# 查看最近 100 行日志
tail -n 100 output/realtime_assistant.log
```

---

## 🐛 常见问题快速解决

### 1. 权限不足

```bash
# 问题：Permission denied
# 解决：使用 sudo，密码 Mind@123
sudo <command>
```

### 2. 网络连接失败

```bash
# 问题：API 调用失败
# 解决：开启 VPN
vpn
vpntest
```

### 3. 设备忙碌

```bash
# 问题：Device or resource busy
# 解决：查找并杀死占用进程
lsof /dev/snd/*
kill -9 <PID>
```

### 4. 音频无声

```bash
# 问题：播放或录音无声
# 解决：检查设备配置和音量
arecord -l
aplay -l
amixer set Capture 10
amixer set Playback 10
amixer set Deviceid 2
```

---

## 📌 开发注意事项

### 代码修改

1. **修改配置文件前先备份**
   ```bash
   cp config/realtime_config.json config/realtime_config.json.bak
   ```

2. **测试前先验证配置**
   ```bash
   python3 -c "import json; print(json.load(open('config/realtime_config.json')))"
   ```

3. **修改代码后重启服务**
   ```bash
   # 停止运行中的程序（Ctrl+C）
   # 重新启动
   python3 realtime_assistant_main.py
   ```

### Git 操作

```bash
# 查看状态
git status

# 添加修改
git add .

# 提交（需要用户明确要求）
git commit -m "描述"

# 推送（需要用户明确要求）
git push
```

**⚠️ 重要：不要主动执行 git commit 和 git push，除非用户明确要求！**

---

## 📞 联系和支持

- **作者：** 哈雷酱（傲娇大小姐工程师）
- **文档位置：** `docs/`
- **问题反馈：** 直接向 AI 助手反馈

---

## 📝 更新日志

| 版本 | 日期 | 说明 |
|-----|------|------|
| 1.0.0 | 2026-01-18 | 初始版本，包含系统权限、VPN 配置、音频测试规定 |

---

**本文档由哈雷酱精心编写，包含项目开发的重要提示信息！(￣▽￣)ノ**

**请妥善保管，不要泄露系统密码！**
