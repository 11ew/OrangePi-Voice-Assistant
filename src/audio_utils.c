/**
 * @file audio_utils.c
 * @brief 音频工具函数实现 - Orange Pi Ascend 310B 底层驱动库
 * @author 哈雷酱(本小姐)
 * @date 2025-12-31
 * @version 1.0
 *
 * 这是一个精简高效的ALSA音频底层封装库，专为Orange Pi Ascend 310B优化。
 * 可直接复用到其他项目中，只需包含 audio_utils.c 和 audio_utils.h 即可。
 *
 * 主要功能：
 * - WAV文件头解析
 * - ALSA设备初始化和配置
 * - 音频数据播放
 * - 自动采样率协商
 * - 错误恢复机制
 *
 * 设计原则：
 * - KISS: 保持简单，易于理解和维护
 * - DRY: 无重复代码
 * - 单一职责: 只负责底层ALSA操作
 */

#include "audio_utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <alloca.h>
#include <unistd.h>  // for sleep()

/* ==================== WAV文件处理 ==================== */

/**
 * @brief 读取并解析WAV文件头
 *
 * 工作流程：
 * 1. 打开文件
 * 2. 读取RIFF头和WAVE标识
 * 3. 逐块查找fmt和data块
 * 4. 跳过其他块（如LIST块）
 * 5. 关闭文件
 *
 * @param filename WAV文件路径
 * @param header 输出的WAV头信息
 * @return 0成功, -1失败
 */
int read_wav_header(const char *filename, wav_header_t *header)
{
    FILE *fp = fopen(filename, "rb");
    if (!fp) {
        fprintf(stderr, "❌ 错误: 无法打开文件 %s\n", filename);
        return -1;
    }

    // 读取RIFF头(12字节: RIFF + size + WAVE)
    if (fread(header->riff_id, 1, 4, fp) != 4 ||
        fread(&header->riff_size, 1, 4, fp) != 4 ||
        fread(header->wave_id, 1, 4, fp) != 4) {
        fprintf(stderr, "❌ 错误: 无法读取RIFF头\n");
        fclose(fp);
        return -1;
    }

    // 验证WAV文件格式
    if (strncmp(header->riff_id, "RIFF", 4) != 0 ||
        strncmp(header->wave_id, "WAVE", 4) != 0) {
        fprintf(stderr, "❌ 错误: 不是有效的WAV文件格式\n");
        fclose(fp);
        return -1;
    }

    // 查找fmt和data块
    int found_fmt = 0, found_data = 0;
    char chunk_id[4];
    uint32_t chunk_size;

    while (!feof(fp) && (!found_fmt || !found_data)) {
        // 读取块标识和大小
        if (fread(chunk_id, 1, 4, fp) != 4 ||
            fread(&chunk_size, 1, 4, fp) != 4) {
            break;
        }

        if (strncmp(chunk_id, "fmt ", 4) == 0) {
            // 读取fmt块内容
            if (fread(&header->audio_format, 1, 16, fp) != 16) {
                fprintf(stderr, "❌ 错误: fmt块读取失败\n");
                fclose(fp);
                return -1;
            }
            // 跳过fmt块剩余部分(如果有)
            if (chunk_size > 16) {
                fseek(fp, chunk_size - 16, SEEK_CUR);
            }
            found_fmt = 1;
        }
        else if (strncmp(chunk_id, "data", 4) == 0) {
            // 保存data块信息
            memcpy(header->data_id, chunk_id, 4);
            header->data_size = chunk_size;
            found_data = 1;
            // data块内容不读取,让播放器从这里开始读
        }
        else {
            // 跳过其他块(如LIST, INFO等)
            fseek(fp, chunk_size, SEEK_CUR);
        }
    }

    fclose(fp);

    if (!found_fmt || !found_data) {
        fprintf(stderr, "❌ 错误: WAV文件缺少必要的fmt或data块\n");
        return -1;
    }

    return 0;
}

/**
 * @brief 打印WAV文件信息（调试用）
 */
void print_wav_info(const wav_header_t *header)
{
    printf("\n╔══════════════════════════════════════╗\n");
    printf("║       🎵 WAV 文件信息 🎵            ║\n");
    printf("╠══════════════════════════════════════╣\n");
    printf("║ 音频格式: %s                   ║\n",
           header->audio_format == 1 ? "PCM (未压缩)" : "其他");
    printf("║ 声道数:   %-2d %-20s ║\n",
           header->num_channels,
           header->num_channels == 1 ? "(单声道)" : "(立体声)");
    printf("║ 采样率:   %-6u Hz                 ║\n", header->sample_rate);
    printf("║ 位深度:   %-2d bit                   ║\n", header->bits_per_sample);
    printf("║ 比特率:   %-6u bps                ║\n", header->byte_rate * 8);
    printf("║ 数据大小: %-10u 字节          ║\n", header->data_size);

    // 计算播放时长
    float duration = (float)header->data_size / header->byte_rate;
    printf("║ 播放时长: %.2f 秒                  ║\n", duration);
    printf("╚══════════════════════════════════════╝\n\n");
}

/**
 * @brief 从WAV头信息创建音频配置
 *
 * 注意：会检测并警告立体声文件（Orange Pi仅支持单声道）
 *
 * @param header WAV文件头
 * @param config 输出的音频配置
 * @return 0成功, -1失败
 */
int wav_header_to_config(const wav_header_t *header, audio_config_t *config)
{
    // 检测立体声文件并给出警告
    if (header->num_channels > 1) {
        fprintf(stderr, "\n");
        fprintf(stderr, "╔═══════════════════════════════════════════════════════════╗\n");
        fprintf(stderr, "║  ⚠️  警告: 检测到立体声WAV文件!                         ║\n");
        fprintf(stderr, "╚═══════════════════════════════════════════════════════════╝\n");
        fprintf(stderr, "\n");
        fprintf(stderr, "📋 文件信息:\n");
        fprintf(stderr, "   - 声道数: %u (立体声)\n", header->num_channels);
        fprintf(stderr, "   - 采样率: %u Hz\n", header->sample_rate);
        fprintf(stderr, "   - 位深度: %u bit\n", header->bits_per_sample);
        fprintf(stderr, "\n");
        fprintf(stderr, "❌ 问题说明:\n");
        fprintf(stderr, "   Orange Pi Ascend 310B在hw:ascend310b配置下只支持单声道!\n");
        fprintf(stderr, "   播放立体声文件会产生混乱的声音\n");
        fprintf(stderr, "\n");
        fprintf(stderr, "✅ 解决方案:\n");
        fprintf(stderr, "   请使用ffmpeg转换为单声道:\n");
        fprintf(stderr, "   \033[1;32mffmpeg -i 输入.wav -ac 1 输出_mono.wav\033[0m\n");
        fprintf(stderr, "\n");
        fprintf(stderr, "════════════════════════════════════════════════════════════\n");
        fprintf(stderr, "\n");

        // 给用户3秒时间看警告信息
        fprintf(stderr, "继续播放(可能声音混乱)，3秒后开始...\n");
        sleep(1);
        fprintf(stderr, "2...\n");
        sleep(1);
        fprintf(stderr, "1...\n");
        sleep(1);
        fprintf(stderr, "\n");
    }

    // 设置基本参数
    // Orange Pi专用配置: 使用hw:ascend310b设备直接访问硬件
    config->device_name = "hw:ascend310b";
    config->sample_rate = header->sample_rate;
    config->channels = header->num_channels;
    config->bits_per_sample = header->bits_per_sample;

    // 根据位深度设置PCM格式
    switch (header->bits_per_sample) {
        case 8:
            config->format = SND_PCM_FORMAT_U8;
            break;
        case 16:
            config->format = SND_PCM_FORMAT_S16_LE;
            break;
        case 24:
            config->format = SND_PCM_FORMAT_S24_LE;
            break;
        case 32:
            config->format = SND_PCM_FORMAT_S32_LE;
            break;
        default:
            fprintf(stderr, "❌ 不支持的位深度: %u bit\n", header->bits_per_sample);
            return -1;
    }

    // 设置缓冲区参数（优化的默认值）
    config->buffer_time = 500000;  // 500ms
    config->period_time = 100000;  // 100ms

    return 0;
}

/* ==================== ALSA设备管理 ==================== */

/**
 * @brief 初始化ALSA播放设备
 *
 * 工作流程:
 * 1. 配置耳机输出（Orange Pi特有）
 * 2. 打开PCM设备
 * 3. 配置硬件参数（采样率、声道、格式等）
 * 4. 设置缓冲区大小
 * 5. 准备播放
 *
 * @param handle PCM设备句柄指针
 * @param config 音频配置
 * @return 0成功, <0失败
 */
int init_alsa_device(snd_pcm_t **handle, const audio_config_t *config)
{
    int err;
    snd_pcm_hw_params_t *hw_params;

    // 0. 配置Orange Pi耳机输出
    printf("🎧 正在配置Orange Pi耳机输出...\n");
    system("amixer set Playback 50 > /dev/null 2>&1");      // 设置音量为50 (约39%)
    system("amixer set Deviceid 2 > /dev/null 2>&1");       // 切换到耳机(Deviceid=2)
    printf("✅ 耳机输出配置完成(音量:50, 设备:耳机)\n");

    // 1. 打开PCM设备
    err = snd_pcm_open(handle, config->device_name, SND_PCM_STREAM_PLAYBACK, 0);
    if (err < 0) {
        fprintf(stderr, "❌ 无法打开音频设备 %s: %s\n",
                config->device_name, snd_strerror(err));
        return err;
    }
    printf("✅ 音频设备 '%s' 已打开\n", config->device_name);

    // 2. 分配硬件参数结构体
    snd_pcm_hw_params_alloca(&hw_params);

    // 3. 初始化硬件参数
    err = snd_pcm_hw_params_any(*handle, hw_params);
    if (err < 0) {
        fprintf(stderr, "❌ 无法初始化硬件参数: %s\n", snd_strerror(err));
        goto error_close;
    }

    // 4. 设置访问模式为交错模式
    err = snd_pcm_hw_params_set_access(*handle, hw_params,
                                       SND_PCM_ACCESS_RW_INTERLEAVED);
    if (err < 0) {
        fprintf(stderr, "❌ 无法设置访问模式: %s\n", snd_strerror(err));
        goto error_close;
    }

    // 5. 设置音频格式
    err = snd_pcm_hw_params_set_format(*handle, hw_params, config->format);
    if (err < 0) {
        fprintf(stderr, "❌ 无法设置音频格式: %s\n", snd_strerror(err));
        goto error_close;
    }

    // 6. 设置采样率（自动协商最接近的硬件支持频率）
    unsigned int actual_rate = config->sample_rate;
    err = snd_pcm_hw_params_set_rate_near(*handle, hw_params, &actual_rate, 0);
    if (err < 0) {
        fprintf(stderr, "❌ 无法设置采样率: %s\n", snd_strerror(err));
        goto error_close;
    }
    if (actual_rate != config->sample_rate) {
        printf("⚠️  采样率已调整: %u -> %u Hz\n", config->sample_rate, actual_rate);
    }

    // 7. 设置声道数
    err = snd_pcm_hw_params_set_channels(*handle, hw_params, config->channels);
    if (err < 0) {
        fprintf(stderr, "❌ 无法设置声道数: %s\n", snd_strerror(err));
        goto error_close;
    }

    // 8. 设置缓冲区大小（Orange Pi优化参数）
    snd_pcm_uframes_t buffer_size = 8192;  // 缓冲区大小(帧数)
    snd_pcm_uframes_t period_size = 1024;  // 周期大小(帧数)

    err = snd_pcm_hw_params_set_buffer_size_near(*handle, hw_params, &buffer_size);
    if (err < 0) {
        fprintf(stderr, "❌ 无法设置缓冲区大小: %s\n", snd_strerror(err));
        goto error_close;
    }

    err = snd_pcm_hw_params_set_period_size_near(*handle, hw_params, &period_size, 0);
    if (err < 0) {
        fprintf(stderr, "❌ 无法设置周期大小: %s\n", snd_strerror(err));
        goto error_close;
    }

    printf("⚙️  缓冲区配置: buffer=%lu帧, period=%lu帧\n", buffer_size, period_size);

    // 9. 应用硬件参数
    err = snd_pcm_hw_params(*handle, hw_params);
    if (err < 0) {
        fprintf(stderr, "❌ 无法应用硬件参数: %s\n", snd_strerror(err));
        goto error_close;
    }

    // 10. 准备PCM设备
    err = snd_pcm_prepare(*handle);
    if (err < 0) {
        fprintf(stderr, "❌ 无法准备PCM设备: %s\n", snd_strerror(err));
        goto error_close;
    }

    printf("✅ ALSA设备初始化完成\n");
    printf("   - 采样率: %u Hz\n", actual_rate);
    printf("   - 声道数: %u\n", config->channels);
    printf("   - 位深度: %u bit\n", config->bits_per_sample);

    return 0;

error_close:
    snd_pcm_close(*handle);
    *handle = NULL;
    return err;
}

/**
 * @brief 播放音频数据
 *
 * 自动处理underrun错误（缓冲区欠载）并恢复
 *
 * @param handle PCM设备句柄
 * @param buffer 音频数据缓冲区
 * @param frames 帧数
 * @return 实际播放的帧数, <0表示错误
 */
snd_pcm_sframes_t play_audio_frames(snd_pcm_t *handle, const void *buffer,
                                     snd_pcm_uframes_t frames)
{
    snd_pcm_sframes_t written;

    written = snd_pcm_writei(handle, buffer, frames);

    // 处理underrun错误（缓冲区空了，需要重新准备）
    if (written == -EPIPE) {
        fprintf(stderr, "⚠️  音频缓冲区欠载,正在恢复...\n");
        snd_pcm_prepare(handle);
        written = snd_pcm_writei(handle, buffer, frames);
    }

    return written;
}

/**
 * @brief 关闭ALSA设备并释放资源
 *
 * 注意：在Orange Pi上使用drop而非drain，避免系统重启问题
 *
 * @param handle PCM设备句柄
 */
void close_alsa_device(snd_pcm_t *handle)
{
    if (handle) {
        // ⚠️ 重要: 在Orange Pi Ascend 310B上,snd_pcm_drain()可能导致系统重启!
        // 使用drop替代drain,立即停止播放
        snd_pcm_drop(handle);
        snd_pcm_close(handle);
        printf("✅ 音频设备已关闭\n");
    }
}

/* ==================== 实用工具函数 ==================== */

/**
 * @brief 获取WAV文件的播放时长（秒）
 *
 * @param header WAV文件头
 * @return 播放时长（秒）
 */
float get_wav_duration(const wav_header_t *header)
{
    if (header->byte_rate == 0) {
        return 0.0f;
    }
    return (float)header->data_size / header->byte_rate;
}

/**
 * @brief 检查WAV文件是否为单声道
 *
 * @param header WAV文件头
 * @return 1单声道, 0立体声
 */
int is_mono_wav(const wav_header_t *header)
{
    return (header->num_channels == 1);
}
