/**
 * @file simple_player.c
 * @brief 简单的WAV音频播放器 - 使用aplay命令
 * @author 哈雷酱(本小姐)
 * @date 2026-01-03
 *
 * 设计理念：
 * - 使用系统自带的aplay命令，保证稳定性
 * - 简单直接，避免复杂的ALSA配置
 * - 适合初学者学习
 *
 * 编译：
 *   gcc -o simple_player simple_player.c
 *
 * 使用：
 *   ./simple_player audio.wav
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>

/* ==================== WAV文件结构 ==================== */

typedef struct {
    char riff_id[4];      // "RIFF"
    uint32_t riff_size;   // 文件大小-8
    char wave_id[4];      // "WAVE"
} __attribute__((packed)) wav_riff_t;

typedef struct {
    char chunk_id[4];     // "fmt "
    uint32_t chunk_size;  // fmt块大小(通常是16)
    uint16_t audio_format;
    uint16_t num_channels;
    uint32_t sample_rate;
    uint32_t byte_rate;
    uint16_t block_align;
    uint16_t bits_per_sample;
} __attribute__((packed)) wav_fmt_t;

// WAV信息结构(用于返回解析结果)
typedef struct {
    uint16_t num_channels;
    uint32_t sample_rate;
    uint16_t bits_per_sample;
    uint32_t data_size;
} wav_info_t;

/* ==================== WAV文件解析 ==================== */

/**
 * @brief 读取WAV文件信息(正确处理所有块类型)
 * @return 0成功, -1失败
 */
int read_wav_info(const char *filepath, wav_info_t *info)
{
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        fprintf(stderr, "❌ 无法打开文件\n");
        return -1;
    }

    // 1. 读取RIFF头
    wav_riff_t riff;
    if (fread(&riff, sizeof(riff), 1, fp) != 1) {
        fprintf(stderr, "❌ 无法读取RIFF头\n");
        fclose(fp);
        return -1;
    }

    if (memcmp(riff.riff_id, "RIFF", 4) != 0 || memcmp(riff.wave_id, "WAVE", 4) != 0) {
        fprintf(stderr, "❌ 不是有效的WAV文件\n");
        fclose(fp);
        return -1;
    }

    // 2. 循环读取所有块,直到找到fmt和data块
    int found_fmt = 0, found_data = 0;
    wav_fmt_t fmt;

    while (!feof(fp) && (!found_fmt || !found_data)) {
        char chunk_id[4];
        uint32_t chunk_size;

        // 读取块ID和大小
        if (fread(chunk_id, 4, 1, fp) != 1) break;
        if (fread(&chunk_size, 4, 1, fp) != 1) break;

        if (memcmp(chunk_id, "fmt ", 4) == 0) {
            // 找到fmt块
            if (fread(&fmt.audio_format, sizeof(wav_fmt_t) - 8, 1, fp) != 1) {
                fprintf(stderr, "❌ 读取fmt块失败\n");
                fclose(fp);
                return -1;
            }
            // 如果fmt块比标准大,跳过多余部分
            if (chunk_size > 16) {
                fseek(fp, chunk_size - 16, SEEK_CUR);
            }
            found_fmt = 1;

        } else if (memcmp(chunk_id, "data", 4) == 0) {
            // 找到data块
            info->data_size = chunk_size;
            found_data = 1;
            break;  // data块之后就是音频数据,不需要继续读了

        } else {
            // 跳过未知块(LIST, INFO等)
            fseek(fp, chunk_size, SEEK_CUR);
        }
    }

    fclose(fp);

    if (!found_fmt || !found_data) {
        fprintf(stderr, "❌ WAV文件缺少必要的块(fmt=%d, data=%d)\n", found_fmt, found_data);
        return -1;
    }

    // 填充返回信息
    info->num_channels = fmt.num_channels;
    info->sample_rate = fmt.sample_rate;
    info->bits_per_sample = fmt.bits_per_sample;

    return 0;
}

/* ==================== 主函数 ==================== */

int main(int argc, char *argv[])
{
    // 1. 检查命令行参数
    if (argc < 2) {
        printf("\n");
        printf("╔════════════════════════════════════════╗\n");
        printf("║   🎵 简单WAV播放器 v2.0 🎵            ║\n");
        printf("╠════════════════════════════════════════╣\n");
        printf("║  用法: %s <WAV文件>       ║\n", argv[0]);
        printf("║                                        ║\n");
        printf("║  示例:                                 ║\n");
        printf("║    %s output/hello.wav  ║\n", argv[0]);
        printf("╚════════════════════════════════════════╝\n\n");
        return 1;
    }

    const char *filepath = argv[1];

    // 2. 检查文件是否存在
    if (access(filepath, F_OK) != 0) {
        fprintf(stderr, "❌ 文件不存在: %s\n", filepath);
        return 1;
    }

    // 3. 读取WAV文件信息
    wav_info_t wav_info;
    if (read_wav_info(filepath, &wav_info) != 0) {
        return 1;
    }

    // 4. 计算播放时长
    uint32_t bytes_per_sample = wav_info.bits_per_sample / 8;
    uint32_t total_samples = wav_info.data_size / (wav_info.num_channels * bytes_per_sample);
    uint32_t duration_sec = total_samples / wav_info.sample_rate;
    float duration_float = (float)wav_info.data_size / (wav_info.sample_rate * wav_info.num_channels * bytes_per_sample);

    // 5. 显示文件信息
    printf("\n");
    printf("╔════════════════════════════════════════╗\n");
    printf("║   🎵 开始播放音频 🎵                  ║\n");
    printf("╚════════════════════════════════════════╝\n");
    printf("📁 文件: %s\n\n", filepath);

    printf("\n");
    printf("╔══════════════════════════════════════╗\n");
    printf("║       🎵 WAV 文件信息 🎵            ║\n");
    printf("╠══════════════════════════════════════╣\n");

    // 判断音频格式
    printf("║ 音频格式: PCM (未压缩)                   ║\n");

    // 声道数
    printf("║ 声道数:   %-2d (%-10s)          ║\n",
           wav_info.num_channels,
           wav_info.num_channels == 1 ? "单声道" : "立体声");

    // 采样率
    printf("║ 采样率:   %-6u Hz                 ║\n", wav_info.sample_rate);

    // 位深度
    printf("║ 位深度:   %-2d bit                   ║\n", wav_info.bits_per_sample);

    // 比特率
    uint32_t bitrate = wav_info.sample_rate * wav_info.num_channels * wav_info.bits_per_sample;
    printf("║ 比特率:   %-6u bps                ║\n", bitrate);

    // 数据大小
    printf("║ 数据大小: %-8u 字节          ║\n", wav_info.data_size);

    // 播放时长
    printf("║ 播放时长: %.2f 秒                  ║\n", duration_float);

    printf("╚══════════════════════════════════════╝\n\n");

    // 6. 配置音频设备
    printf("🎧 正在配置Orange Pi耳机输出...\n");
    system("amixer -q set Playback 10 2>/dev/null");   // 设置音量
    system("amixer -q set Deviceid 2 2>/dev/null");    // 设置为耳机输出
    printf("✅ 耳机输出配置完成(音量:50, 设备:耳机)\n\n");

    // 7. 使用aplay播放音频
    printf("🎵 正在播放...\n");

    char cmd[512];
    snprintf(cmd, sizeof(cmd),
             "aplay -q -Dhw:ascend310b -f S16_LE -r %u -c %u -t wav \"%s\"",
             wav_info.sample_rate,
             wav_info.num_channels,
             filepath);

    int ret = system(cmd);

    printf("\n");

    if (ret == 0) {
        printf("╔════════════════════════════════════════╗\n");
        printf("║   ✅ 播放完成！                       ║\n");
        printf("╚════════════════════════════════════════╝\n\n");
        return 0;
    } else {
        printf("╔════════════════════════════════════════╗\n");
        printf("║   ❌ 播放失败！                       ║\n");
        printf("╚════════════════════════════════════════╝\n\n");
        return 1;
    }
}

/*
 * ┌────────────────────────────────────────────────────┐
 * │  ✨ 本小姐的简化设计 v2.0 ✨                       │
 * ├────────────────────────────────────────────────────┤
 * │  优势：                                            │
 * │  1. 稳定性: 使用系统自带的aplay命令                │
 * │  2. 兼容性: 避免ALSA配置问题                       │
 * │  3. 简洁性: 代码简单易懂，适合学习                 │
 * │  4. 可靠性: WAV解析支持非标准块                    │
 * │                                                    │
 * │  学习要点：                                        │
 * │  - WAV文件格式解析                                 │
 * │  - 系统命令调用 (system函数)                       │
 * │  - 进程管理基础                                    │
 * └────────────────────────────────────────────────────┘
 */
