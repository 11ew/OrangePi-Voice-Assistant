# 🎓 新手入门指南

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **适合人群：** 刚接触Linux，刚学完STM32的初学者
> **阅读时间：** 15分钟

---

## 👋 欢迎，笨蛋新人！

哼，既然你选择了本小姐的项目，那就要好好学习哦！这份指南会手把手教你从零开始使用Edge-TTS，连笨蛋都能学会！(￣▽￣)ノ

---

## 📋 学习路线图

```
第1步: 环境准备 (10分钟)
   ↓
第2步: 快速测试 (5分钟)
   ↓
第3步: 理解原理 (10分钟)
   ↓
第4步: 实战练习 (30分钟)
   ↓
第5步: 深入学习 (持续)
```

---

## 🚀 第1步：环境准备

### 1.1 检查系统环境

打开终端，输入以下命令检查系统：

```bash
# 检查Linux版本
uname -a

# 检查Python版本（需要3.7+）
python3 --version

# 检查是否有音频设备
aplay -l
```

**预期输出：**
```
Python 3.8.10 或更高版本
**** List of PLAYBACK Hardware Devices ****
card 0: xxx [xxx]
  device 0: xxx
```

如果看到类似输出，说明你的系统准备好了！✅

### 1.2 安装依赖

本小姐提供了一键安装脚本，笨蛋也不会出错！

```bash
# 进入项目目录
cd EdgeTTSdemo

# 一键安装所有依赖
make install-deps
```

这个命令会自动安装：
- ✅ Python3 和 pip
- ✅ FFmpeg（音频转换工具）
- ✅ ALSA工具（音频播放）
- ✅ GCC编译器
- ✅ Edge-TTS Python包

**安装时间：** 约2-5分钟（取决于网络速度）

### 1.3 验证安装

运行以下命令验证是否安装成功：

```bash
# 检查FFmpeg
ffmpeg -version | head -1

# 检查Edge-TTS
python3 -c "import edge_tts; print('Edge-TTS OK')"

# 检查GCC
gcc --version | head -1
```

**全部显示OK？** 恭喜你，环境准备完成！🎉

---

## ⚡ 第2步：快速测试（5分钟）

### 2.1 一键运行

本小姐准备了超级简单的快速开始脚本：

```bash
bash quickstart.sh
```

**这个脚本会做什么？**
1. ✅ 检查所有依赖
2. ✅ 编译C程序
3. ✅ 生成测试语音
4. ✅ 播放测试语音

**预期效果：**
你会听到："你好，欢迎使用Edge TTS文字转语音系统！..."

### 2.2 手动测试（理解原理）

如果你想理解每一步在做什么，可以手动执行：

```bash
# 步骤1: 生成语音文件
python3 scripts/tts_generate.py "你好，世界" output/hello.wav

# 步骤2: 编译播放器
make

# 步骤3: 播放音频
./simple_player output/hello.wav
```

**听到声音了？** 太棒了！你已经成功了！🎉

**没听到声音？** 别慌，跳到[常见问题](#常见问题)章节

---

## 🧠 第3步：理解原理（10分钟）

### 3.1 项目架构

```
┌─────────────────────────────────────┐
│  你输入的文本："你好，世界"         │
└──────────────┬──────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  Python层 (scripts/tts_generate.py)  │
│  - 调用Edge-TTS API                  │
│  - 生成MP3文件                       │
│  - 转换为WAV格式                     │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  WAV音频文件 (output/hello.wav)      │
│  - 单声道                            │
│  - 48kHz采样率                       │
│  - 16bit位深度                       │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  C语言层 (src/simple_player.c)       │
│  - 解析WAV文件                       │
│  - 初始化ALSA设备                    │
│  - 播放音频数据                      │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  硬件输出 (3.5mm耳机接口)            │
└──────────────────────────────────────┘
```

### 3.2 核心文件说明

| 文件 | 作用 | 类比STM32 |
|------|------|-----------|
| `scripts/tts_generate.py` | 生成语音文件 | HAL库（高层API） |
| `src/audio_utils.c` | ALSA底层驱动 | 寄存器操作 |
| `src/simple_player.c` | 播放器主程序 | main()函数 |
| `Makefile` | 构建脚本 | Keil工程文件 |

### 3.3 关键概念

#### 什么是Edge-TTS？
- 微软Edge浏览器的文字转语音引擎
- **免费**、**高质量**、**无需API密钥**
- 支持多种语言和语音

#### 什么是WAV文件？
- 未压缩的音频格式
- 包含文件头（44字节）+ 音频数据
- **类比STM32：** 就像UART数据帧（帧头 + 数据）

#### 什么是ALSA？
- Linux的音频驱动架构
- **类比STM32：** 就像HAL_I2S库

---

## 💪 第4步：实战练习（30分钟）

### 练习1：修改语音内容（难度：⭐）

**任务：** 生成你自己的语音

```bash
# 修改这里的文本内容
python3 scripts/tts_generate.py "我是新手，正在学习Edge-TTS" output/my_voice.wav

# 播放
./simple_player output/my_voice.wav
```

**提示：**
- 可以使用中文标点符号
- 可以是任意长度的文本
- 文本越长，生成时间越久

### 练习2：尝试不同语音（难度：⭐）

**任务：** 对比男声和女声

```bash
# 女声（温柔）
python3 scripts/tts_generate.py "你好" output/female.wav xiaoxiao

# 男声（沉稳）
python3 scripts/tts_generate.py "你好" output/male.wav yunjian

# 播放对比
./simple_player output/female.wav
./simple_player output/male.wav
```

**可用语音：**
- `xiaoxiao` - 女声（温柔）
- `xiaoyi` - 女声（活泼）
- `yunjian` - 男声（沉稳）
- `yunxi` - 男声（年轻）

### 练习3：批量生成（难度：⭐⭐）

**任务：** 一次生成多个语音文件

```bash
# 创建文本列表
cat > my_list.txt <<EOF
早上好
中午好
晚上好
EOF

# 使用批量生成脚本
bash examples/05_batch_generate.sh my_list.txt
```

### 练习4：定时提醒（难度：⭐⭐）

**任务：** 设置你的专属提醒

```bash
# 1. 复制示例脚本
cp examples/03_timer_reminder.sh my_reminder.sh

# 2. 编辑脚本（使用你喜欢的编辑器）
nano my_reminder.sh

# 3. 修改提醒时间和内容
# 找到这一行：
#   "08:00 早上好，该起床了"
# 改成：
#   "07:30 起床锻炼"

# 4. 运行
bash my_reminder.sh
```

---

## 📖 第5步：深入学习

### 5.1 阅读进阶教程

打开详细教程文档：

```bash
# 使用文本编辑器阅读
cat docs/tutorial.md

# 或在浏览器中查看（如果有图形界面）
```

**教程内容包括：**
- ✅ 从STM32到Linux的知识迁移
- ✅ WAV文件格式详解
- ✅ ALSA音频编程原理
- ✅ 更多实战案例
- ✅ 性能优化技巧

### 5.2 运行示例程序

尝试所有示例脚本：

```bash
# 语音对比
bash examples/04_compare_voices.sh

# 智能时钟
bash examples/01_voice_clock.sh

# 系统监控
bash examples/02_system_monitor.sh
```

### 5.3 修改源代码

**初级挑战：**
- 修改默认语音（编辑 `scripts/tts_generate.py`）
- 修改音量设置（编辑 `src/audio_utils.c`）
- 添加新的提醒时间（编辑 `examples/03_timer_reminder.sh`）

**中级挑战：**
- 添加语速控制参数
- 实现语音队列播放
- 添加进度显示

**高级挑战：**
- 实现流式播放（边生成边播放）
- 添加语音识别功能
- 移植到其他硬件平台

---

## ❓ 常见问题

### Q1: 听不到声音怎么办？

**检查步骤：**

```bash
# 1. 检查耳机是否插好
# 2. 检查音频设备
aplay -l

# 3. 测试音频设备
speaker-test -t wav -c 1

# 4. 检查音量
amixer

# 5. 调整音量
amixer set Playback 80
```

### Q2: Edge-TTS下载失败

**原因：** 网络问题或Python pip源太慢

**解决：**
```bash
# 使用国内镜像重新安装
pip3 install edge-tts -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 编译报错

**错误：** `fatal error: alsa/asoundlib.h`

**解决：**
```bash
sudo apt install libasound2-dev
make clean
make
```

### Q4: 播放声音混乱

**原因：** 可能使用了立体声文件

**解决：**
```bash
# 转换为单声道
ffmpeg -i input.wav -ac 1 output_mono.wav
```

### Q5: Python脚本运行很慢

**原因：** 首次运行需要下载模型

**解决：** 耐心等待，后续会快很多

---

## 🎯 学习检查清单

完成以下检查，确保你已经掌握基础知识：

- [ ] ✅ 成功安装所有依赖
- [ ] ✅ 运行quickstart.sh并听到声音
- [ ] ✅ 生成自己的语音文件
- [ ] ✅ 尝试至少3种不同语音
- [ ] ✅ 理解项目架构（Python层 + C层）
- [ ] ✅ 运行至少2个示例脚本
- [ ] ✅ 阅读进阶教程的前3章
- [ ] ✅ 完成至少1个自定义功能

**全部打✅了？** 恭喜你，你已经入门了！🎉

---

## 📚 下一步

### 如果你是...

**STM32开发者：**
- 阅读"从STM32到Linux"章节
- 理解ALSA与I2S的对应关系
- 学习Linux驱动开发

**Python爱好者：**
- 深入学习Edge-TTS API
- 研究异步编程（asyncio）
- 尝试其他TTS引擎

**音频处理初学者：**
- 学习WAV文件格式
- 理解采样率、位深度
- 研究音频处理算法

**嵌入式工程师：**
- 移植到其他平台（树莓派、BeagleBone等）
- 优化内存和性能
- 集成到产品中

---

## 🔗 资源链接

### 项目文档
- [README.md](../README.md) - 项目总览
- [tutorial.md](tutorial.md) - 进阶教程
- [examples/README.md](../examples/README.md) - 实战案例集

### 官方文档
- [Edge-TTS GitHub](https://github.com/rany2/edge-tts)
- [ALSA文档](https://www.alsa-project.org/)
- [FFmpeg文档](https://ffmpeg.org/documentation.html)

### 社区支持
- [Linux音频论坛](https://alsa.opensrc.org/)
- [Python中文社区](https://python-chinese.org/)

---

## 💬 给新手的话

哼，笨蛋新人！如果你能看到这里，说明你还算有点毅力！(￣▽￣)ゞ

学习编程最重要的是：
1. **多动手** - 光看不练永远学不会
2. **多思考** - 理解为什么，而不是死记硬背
3. **多尝试** - 不要怕出错，错误是最好的老师
4. **多提问** - 遇到问题及时查资料、问社区

本小姐的这个项目虽然简单，但包含了很多重要概念：
- 跨语言编程（Python + C）
- 系统编程（文件I/O、进程管理）
- 音频处理（WAV格式、ALSA驱动）
- 网络通信（Edge-TTS API）

掌握这些，你就能：
- ✅ 开发Linux应用
- ✅ 理解音频处理流程
- ✅ 集成TTS功能到你的项目
- ✅ 为更复杂的项目打下基础

**最后，记住：**

> 编程是一门手艺，需要不断练习。
> 本小姐当年也是从零开始，一步步成长的。
> 相信自己，你也可以！

哼，才不是在鼓励你呢，本小姐只是不想看到笨蛋放弃而已！(*/ω\*)

加油吧，未来的工程师！

---

**版本：** v1.0
**更新日期：** 2026-01-03
**作者：** 哈雷酱（傲娇大小姐工程师）

> 有问题就好好查文档，别总想着偷懒问人！(￣へ￣)
