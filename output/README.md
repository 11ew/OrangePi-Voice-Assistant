# output 目录说明

这个目录用于存放生成的音频文件。

## 📝 说明

- ✅ 所有通过 `scripts/tts_generate.py` 生成的WAV文件都会保存在这里
- ✅ 示例脚本 `examples/*.sh` 也会将音频输出到这里
- ✅ 临时MP3文件会自动清理

## 🗂️ 文件命名规范

- `hello.wav` - 简单测试文件
- `time.wav` - 时间播报
- `status.wav` - 系统状态
- `reminder.wav` - 定时提醒
- `batch_YYYYMMDD_HHMMSS/*.wav` - 批量生成的文件

## 🧹 清理

如果想清理所有生成的音频文件：

```bash
# 清理所有WAV文件
rm -f output/*.wav

# 清理所有批量生成的目录
rm -rf output/batch_*/
```

## 💡 提示

- 音频文件可以安全删除，需要时会自动重新生成
- 批量生成的文件会保存在带时间戳的子目录中

---

**本小姐提醒你：** 定期清理这个目录，避免占用太多磁盘空间哦！(￣▽￣)ノ
