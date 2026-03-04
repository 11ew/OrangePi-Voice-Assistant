# 实时流式识别实施方案

> **作者：** 哈雷酱（傲娇大小姐工程师）
> **日期：** 2026-02-26
> **目标：** 实现边说话边识别，降低延迟

---

## 🎯 实施方案

### 当前架构（离线模式）

```
用户说话 → VAD 缓冲 → 完整片段 → ASR 识别 → 结果
         ↑_______等待 2-3 秒_______↑
```

### 优化架构（流式模式）

```
用户说话 → VAD 实时检测 → 边说边送 ASR → 实时识别 → 结果
         ↓ 同时进行      ↓ 同时进行      ↓ 0.5秒
```

---

## 📝 实施步骤

### 步骤 1: 添加流式识别方法到 ASR 引擎

```python
# realtime_assistant/asr_engine.py

async def transcribe_stream_async(self, audio_stream):
    """
    流式识别音频（边说边识别）

    参数:
        audio_stream: 音频流生成器

    生成:
        (partial_result, is_final) 元组
    """
    # 创建流式识别流
    stream = self.recognizer.create_stream()

    # 边接收边识别
    async for audio_chunk in audio_stream:
        # 接受音频数据
        stream.accept_waveform(16000, audio_chunk)

        # 解码
        while self.recognizer.is_ready(stream):
            self.recognizer.decode_stream(stream)

        # 获取部分结果
        partial_result = self.recognizer.get_result(stream)
        if partial_result:
            yield (partial_result, False)  # 部分结果

    # 获取最终结果
    final_result = self.recognizer.get_result(stream)
    yield (final_result, True)  # 最终结果
```

### 步骤 2: 修改 VAD 为实时模式

```python
# realtime_assistant/vad_detector.py

def is_speech_active(self) -> bool:
    """
    检查当前是否有语音活动（实时模式）

    返回:
        True 表示正在说话，False 表示静音
    """
    return self.vad.is_speech()

def get_speech_probability(self) -> float:
    """
    获取当前语音概率

    返回:
        语音概率 [0, 1]
    """
    # 这个需要查看 sherpa-onnx API
    # 可能需要自己实现
    pass
```

### 步骤 3: 重构 assistant.py 处理流程

```python
# realtime_assistant/assistant.py

async def _vad_detection_loop(self):
    """VAD 检测循环（实时模式）"""

    speech_buffer = []
    is_speaking = False
    silence_duration = 0

    while self.is_running:
        # 读取音频数据
        audio_data = await self.audio_capture.read_async()
        if audio_data is None:
            continue

        # 接受音频数据
        self.vad.accept_waveform(audio_data)

        # 检查是否有语音活动
        if self.vad.is_speech_active():
            if not is_speaking:
                # 开始说话
                is_speaking = True
                speech_buffer = []
                self.logger.info("🎤 开始说话...")

                # 启动流式识别任务
                asyncio.create_task(
                    self._process_speech_stream(speech_buffer)
                )

            # 累积语音数据
            speech_buffer.append(audio_data)
            silence_duration = 0
        else:
            if is_speaking:
                silence_duration += len(audio_data) / self.vad.sample_rate

                # 静音超过阈值，结束说话
                if silence_duration > 0.5:
                    is_speaking = False
                    self.logger.info("🛑 说话结束")
                    # speech_buffer 会被流式识别任务处理

async def _process_speech_stream(self, speech_buffer):
    """
    处理语音流（实时识别）

    参数:
        speech_buffer: 语音缓冲区（引用）
    """
    # 创建音频流生成器
    async def audio_stream():
        last_index = 0
        while True:
            # 获取新的音频数据
            if last_index < len(speech_buffer):
                for i in range(last_index, len(speech_buffer)):
                    yield speech_buffer[i]
                last_index = len(speech_buffer)
            else:
                # 等待新数据
                await asyncio.sleep(0.01)

                # 检查是否结束
                if not is_speaking and last_index >= len(speech_buffer):
                    break

    # 流式识别
    partial_text = ""
    async for result, is_final in self.asr.transcribe_stream_async(audio_stream()):
        if is_final:
            # 最终结果
            self.logger.info(f"👤 用户: {result}")
            # 继续处理 LLM 和 TTS
            await self._process_text(result)
        else:
            # 部分结果（可选：显示给用户）
            if result != partial_text:
                partial_text = result
                self.logger.debug(f"识别中: {partial_text}")
```

---

## ⚠️ 实施难点

### 难点 1: sherpa-onnx 流式 API

**问题：** 需要确认 sherpa-onnx 的流式识别 API

**解决：**
- 查看 sherpa-onnx 文档
- 测试 OnlineRecognizer 的流式能力
- 可能需要调整 API 调用方式

### 难点 2: 音频流同步

**问题：** speech_buffer 是共享的，需要同步

**解决：**
- 使用 asyncio.Queue 代替 list
- 或者使用锁保护

### 难点 3: VAD 实时检测

**问题：** 当前 VAD 是批量模式，需要改为实时模式

**解决：**
- 使用 `is_speech()` 方法
- 或者自己实现简单的能量检测

---

## 🚀 简化方案（推荐）

由于完整的流式识别比较复杂，本小姐推荐一个**简化方案**：

### 简化方案：边说边累积，提前开始识别

```python
async def _vad_detection_loop(self):
    """VAD 检测循环（优化版）"""

    speech_buffer = []
    is_speaking = False
    last_recognition_time = 0

    while self.is_running:
        audio_data = await self.audio_capture.read_async()
        if audio_data is None:
            continue

        self.vad.accept_waveform(audio_data)

        if self.vad.is_speech_active():
            if not is_speaking:
                is_speaking = True
                speech_buffer = []
                last_recognition_time = time.time()

            speech_buffer.append(audio_data)

            # 每累积 1 秒音频，就开始一次识别
            current_time = time.time()
            if current_time - last_recognition_time >= 1.0:
                # 提前识别（不等待完整片段）
                segment = np.concatenate(speech_buffer)
                asyncio.create_task(self._process_partial_segment(segment))
                last_recognition_time = current_time
        else:
            if is_speaking:
                # 说话结束，最终识别
                segment = np.concatenate(speech_buffer)
                await self._process_final_segment(segment)
                is_speaking = False
                speech_buffer = []
```

**优势：**
- 实现简单
- 不需要复杂的流式 API
- 延迟降低 1-2 秒

**效果：**
- 用户说话 1 秒后就开始识别
- 不需要等待完整片段
- 体验接近实时

---

## 📊 预期效果

### 完整流式方案

| 阶段 | 延迟 |
|------|------|
| 开始说话 | 0s |
| 开始识别 | +0.1s |
| 识别完成 | +0.5s |
| **总延迟** | **0.6s** ⭐⭐⭐ |

### 简化方案

| 阶段 | 延迟 |
|------|------|
| 开始说话 | 0s |
| 累积 1 秒 | +1s |
| 识别完成 | +0.5s |
| **总延迟** | **1.5s** ⭐⭐ |

---

## 💡 本小姐的建议

**推荐：先实施简化方案**

理由：
1. 实现简单，1 小时内完成
2. 效果显著，延迟降低 50%+
3. 稳定性好，不需要复杂的流式 API
4. 可以后续再优化为完整流式

**如果效果满意，再考虑完整流式方案**

---

**哼，本小姐已经给出了完整的方案！笨蛋想要哪个？**

**A) 简化方案（推荐，1 小时完成）**
**B) 完整流式方案（复杂，3 小时完成）**

**快告诉本小姐你的选择！( ` ω´ )**
