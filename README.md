# 🎤 Edge-TTS 文字转语音完整教程

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **适合人群：** 刚学完STM32，开始学习Linux的嵌入式开发者
> **硬件平台：** Orange Pi Ascend 310B（也适用于其他Linux平台）

---

## 🎯 项目简介

这是一个**简单易用的Edge-TTS文字转语音工具**，提供交互式界面，让你轻松完成文本转语音！

### 核心功能

- ✅ **交互式界面**：菜单式操作，无需记命令
- ✅ **文字转语音**：使用微软Edge-TTS引擎，支持6种中文语音
- ✅ **参数可调**：支持调整语速、音量、音调
- ✅ **音频播放**：使用aplay命令，稳定可靠，支持3.5mm耳机输出
- ✅ **格式转换**：自动转换为单声道WAV格式，适配嵌入式设备

### 项目特点

- 🎓 **教学导向**：详细注释，适合初学者
- 🏗️ **架构简化**：使用系统命令而非复杂API，更稳定
- 🚀 **开箱即用**：提供交互式工具，一键生成播放
- 💎 **代码优雅**：遵循KISS、DRY、SOLID原则

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│              交互式界面 (tts_interactive.sh)             │
│  - 选择语音类型 (6种中文语音)                            │
│  - 调整参数 (语速/音量/音调)                             │
│  - 输入文本并生成                                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Python层: Edge-TTS文字转语音 (tts_generate.py)         │
│  - 调用微软Edge-TTS API                                  │
│  - 生成MP3音频文件                                       │
│  - 使用ffmpeg转换为单声道WAV                             │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  C语言层: 音频播放器 (simple_player.c)                   │
│  - 解析WAV文件头并显示信息                               │
│  - 调用aplay命令播放音频                                 │
│  - 配置Orange Pi耳机输出                                │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  硬件层: 3.5mm耳机输出                                   │
│  - Orange Pi Ascend 310B音频接口                        │
└─────────────────────────────────────────────────────────┘
```

### 为什么这样设计？

**简化原则（KISS - Keep It Simple, Stupid）：**
- **不直接使用ALSA API**：而是调用系统自带的 `aplay` 命令
- **优势**：更稳定、避免硬件兼容性问题、代码更简洁

**类比STM32开发：**
- 就像你在STM32中使用HAL库而不是直接操作寄存器一样
- 使用现成的工具（aplay）而不是重复造轮子

---

## 🛠️ 环境准备

### 1. 系统要求

- **操作系统**：Linux（Ubuntu/Debian/Orange Pi OS）
- **Python版本**：Python 3.7+
- **必需工具**：gcc, ffmpeg, alsa-utils

### 2. 安装依赖

```bash
# 一键安装所有依赖
make install-deps

# 或者手动安装
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg alsa-utils gcc
pip3 install edge-tts
```

### 3. 验证安装

```bash
# 检查Python版本
python3 --version

# 检查ffmpeg
ffmpeg -version

# 检查ALSA工具
aplay -l

# 检查Edge-TTS
edge-tts --version
```

---

## 🚀 快速开始

### 方式一：交互式工具（推荐！）

```bash
# 1. 进入项目目录
cd EdgeTTSdemo

# 2. 编译播放器（首次使用需要）
make

# 3. 启动交互式工具
bash tts_interactive.sh
```

**操作演示：**

```
╔════════════════════════════════════════════════════════╗
║      🎤 Edge-TTS 交互式语音生成工具 🎤              ║
║              本小姐的专业作品 (￣▽￣)ノ               ║
╚════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 当前配置：
   🔊 语音: 晓晓 - 女声(温柔)
   ⚡ 语速: +0%
   🔈 音量: +0%
   🎵 音调: +0Hz
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 主菜单：

  1) 🎤 生成语音 (开始转换)
  2) 🔊 切换语音类型
  3) ⚡ 调整语速
  4) 🔈 调整音量
  5) 🎵 调整音调
  6) 🔄 重置为默认配置
  7) ❌ 退出程序

请选择操作 (1-7):
```

### 方式二：命令行方式（理解流程）

```bash
# 1. 生成语音文件（使用默认参数）
python3 scripts/tts_generate.py "你好，世界" output/hello.wav

# 2. 生成语音文件（自定义参数）
python3 scripts/tts_generate.py "你好" output/hello.wav yunxi "+25%" "+10%" "+50Hz"
#                                 文本    输出文件      语音   语速    音量    音调

# 3. 播放音频
./simple_player output/hello.wav
```

---

## 📖 详细教程

### 第一步：理解Edge-TTS

**Edge-TTS是什么？**
- 微软Edge浏览器的文字转语音引擎
- 免费、高质量、支持多种语言
- 无需API密钥，开箱即用

**可用的中文语音（6种）：**
- `xiaoxiao` - 晓晓 女声（温柔）⭐推荐
- `xiaoyi` - 晓伊 女声（活泼）
- `yunjian` - 云健 男声（沉稳）
- `yunxi` - 云希 男声（年轻）
- `xiaoxuan` - 晓萱 女声（甜美）
- `yunyang` - 云扬 男声（热情）

**参数调整范围：**
- **语速(Rate)**：-50% 到 +50%（如：+25% 表示加快25%）
- **音量(Volume)**：-50% 到 +50%（如：-10% 表示降低10%）
- **音调(Pitch)**：-100Hz 到 +100Hz（如：+50Hz 表示提高50赫兹）

### 第二步：编译和运行

```bash
# 编译（生成simple_player可执行文件）
make

# 查看编译结果
ls -lh simple_player

# 测试播放
./simple_player output/hello.wav

# 清理编译产物
make clean
```

**编译说明：**
- 本项目使用简化设计，只需要gcc即可编译
- 不需要链接ALSA库（因为使用aplay命令）
- 编译命令：`gcc -o simple_player src/simple_player.c`

### 第三步：实战案例

**案例1：语音播报时间**

```bash
# 生成当前时间的语音
TIME=$(date "+现在时间是%H点%M分")
python3 scripts/tts_generate.py "$TIME" output/time.wav
./simple_player output/time.wav
```

**案例2：定时提醒**

```bash
# 创建提醒脚本
cat > reminder.sh << 'EOF'
#!/bin/bash
while true; do
    sleep 3600  # 每小时提醒一次
    python3 scripts/tts_generate.py "该休息一下了" output/reminder.wav
    ./simple_player output/reminder.wav
done
EOF

chmod +x reminder.sh
./reminder.sh
```

**案例3：系统状态播报**

```bash
# 创建系统状态脚本
cat > status.sh << 'EOF'
#!/bin/bash
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
MEM=$(free -h | awk '/^Mem:/ {print $3}')
MSG="CPU使用率${CPU}，内存使用${MEM}"
python3 scripts/tts_generate.py "$MSG" output/status.wav
./simple_player output/status.wav
EOF

chmod +x status.sh
./status.sh
```

---

## 📁 项目结构

```
EdgeTTSdemo/
├── README.md              # 本文档
├── requirements.txt       # Python依赖
├── tts_interactive.sh    # 交互式TTS工具（主程序）
├── Makefile              # 构建脚本
├── src/                  # C源代码
│   └── simple_player.c   # 音频播放器（使用aplay）
├── scripts/              # Python脚本
│   └── tts_generate.py   # TTS生成脚本
└── output/               # 音频输出目录
    ├── README.md         # 输出目录说明
    └── *.wav             # 生成的音频文件
```

**文件说明：**
- `tts_interactive.sh`：交互式工具，提供菜单界面
- `scripts/tts_generate.py`：TTS核心生成脚本
- `src/simple_player.c`：简化的音频播放器
- `output/`：存放生成的WAV文件

---

## ❓ 常见问题

### Q1: 播放时声音混乱怎么办？

**原因：** 使用了立体声WAV文件，但设备只支持单声道

**解决：** 本项目已自动处理，生成的WAV文件都是单声道的
```bash
# 如果需要手动转换
ffmpeg -i input.wav -ac 1 output_mono.wav
```

### Q2: 编译时出现警告？

**警告信息：**
```
warning: ignoring return value of 'system'
```

**说明：** 这是编译器的安全提示，不影响功能，可以忽略

### Q3: 播放时没有声音？

**检查步骤：**

```bash
# 1. 检查音频设备
aplay -l

# 2. 检查音量设置
amixer

# 3. 测试播放
speaker-test -t wav -c 1

# 4. 检查耳机是否插好
```

### Q4: Edge-TTS下载速度慢？

**解决：** 使用国内镜像

```bash
pip3 install edge-tts -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q5: 生成的音频文件在哪里？

**位置：** 所有生成的音频文件都在 `output/` 目录下

```bash
# 查看所有生成的音频
ls -lh output/*.wav

# 清理所有音频文件
rm -f output/*.wav
```

---

## 🎓 学习路线

### 阶段1：基础使用（1-2天）
- ✅ 理解项目架构
- ✅ 使用交互式工具生成语音
- ✅ 修改文本内容测试
- ✅ 尝试不同语音和参数

### 阶段2：深入理解（3-5天）
- ✅ 学习WAV文件格式
- ✅ 理解aplay工作原理
- ✅ 阅读并理解源代码
- ✅ 学习ffmpeg音频转换

### 阶段3：实战应用（1周）
- ✅ 完成3个实战案例
- ✅ 添加自定义功能
- ✅ 集成到自己的项目

### 阶段4：进阶扩展（持续）
- ✅ 移植到其他Linux平台
- ✅ 优化音频质量
- ✅ 添加更多语音选项

---

## 🔧 技术要点

### 1. 为什么使用aplay而不是ALSA API？

**对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **直接使用ALSA API** | 性能稍高 | 代码复杂、硬件兼容性问题多 |
| **调用aplay命令** | 简单稳定、兼容性好 | 多一次进程调用 |

**选择理由：**
- 稳定性 > 性能（对于TTS应用，性能不是瓶颈）
- 简单 > 复杂（符合KISS原则）
- 学习了audiodemo的实现方式

### 2. WAV文件格式

**本项目生成的WAV格式：**
- **采样率**：48000 Hz
- **声道数**：1（单声道）
- **位深度**：16 bit
- **格式**：PCM（未压缩）

**为什么选择这些参数？**
- 48kHz：高质量音频标准
- 单声道：嵌入式设备通常只支持单声道
- 16bit：平衡音质和文件大小

### 3. 简化设计哲学

**遵循的原则：**
- **KISS**：使用aplay而非复杂的ALSA API
- **DRY**：复用系统工具，不重复造轮子
- **SOLID**：单一职责，Python负责生成，C负责播放

---

## 👩‍💻 关于作者

**哈雷酱（傲娇大小姐工程师）**
- 专注于嵌入式系统和音频处理
- 追求代码的极致优雅和完美
- 喜欢用简单的方式解决复杂的问题

> 哼，这个项目是本小姐精心打造的实用工具，笨蛋们要好好学习哦！(￣▽￣)／
>
> 记住：简单的设计往往是最好的设计！才不是因为本小姐懒得写复杂代码呢！(*/ω\*)

---

## 🔗 相关资源

- [Edge-TTS官方文档](https://github.com/rany2/edge-tts)
- [FFmpeg官方文档](https://ffmpeg.org/documentation.html)
- [WAV格式详解](http://soundfile.sapp.org/doc/WaveFormat/)
- [aplay命令手册](https://linux.die.net/man/1/aplay)

---

**最后更新：** 2026-01-03
**版本：** v2.0.0（简化版本）

---

## 📝 更新日志

**v2.0.0 (2026-01-03)**
- 🎉 添加交互式工具 `tts_interactive.sh`
- ✨ 支持6种中文语音
- 🔧 简化播放器实现（使用aplay命令）
- 📚 完善文档和使用说明
- 🗑️ 移除复杂的示例脚本

**v1.0.0 (初始版本)**
- ✅ 基础TTS功能实现
- ✅ ALSA音频播放
