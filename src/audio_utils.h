/**
 * @file audio_utils.h
 * @brief 音频工具函数头文件 - Orange Pi Ascend 310B 底层驱动库
 * @author 哈雷酱(本小姐)
 * @date 2025-12-31
 * @version 1.0
 *
 * 这是一个精简高效的ALSA音频底层封装库的头文件，专为Orange Pi Ascend 310B优化。
 * 可直接复用到其他项目中，只需包含 audio_utils.c 和 audio_utils.h 即可。
 *
 * 主要功能：
 * - WAV文件头解析
 * - ALSA设备初始化和配置
 * - 音频数据播放
 * - 自动采样率协商
 * - 错误恢复机制
 * - 工具函数（时长计算、声道检测）
 *
 * 设计原则：
 * - KISS: 保持简单，易于理解和维护
 * - DRY: 无重复代码
 * - 单一职责: 只负责底层ALSA操作
 */

#ifndef AUDIO_UTILS_H
#define AUDIO_UTILS_H

#include <stdint.h>
#include <alsa/asoundlib.h>

/* ==================== 数据结构定义 ==================== */

/**
 * @brief WAV文件头结构体
 * 类比: 就像音乐CD的"封面信息"
 * 包含了音频文件的所有基本信息(采样率、声道数、位深度等)
 */
typedef struct {
    // RIFF块描述符 (12字节)
    char riff_id[4];        // "RIFF" 标识
    uint32_t riff_size;     // 文件大小-8
    char wave_id[4];        // "WAVE" 标识

    // fmt子块 (24字节)
    char fmt_id[4];         // "fmt " 标识
    uint32_t fmt_size;      // fmt块大小(通常为16)
    uint16_t audio_format;  // 音频格式(1=PCM)
    uint16_t num_channels;  // 声道数(1=单声道, 2=立体声)
    uint32_t sample_rate;   // 采样率(如44100Hz)
    uint32_t byte_rate;     // 每秒字节数
    uint16_t block_align;   // 块对齐
    uint16_t bits_per_sample; // 每个采样的位数(如16bit)

    // data子块
    char data_id[4];        // "data" 标识
    uint32_t data_size;     // 音频数据大小
} wav_header_t;

/**
 * @brief 音频播放器配置结构体
 * 类比: 播放器的"设置面板"
 */
typedef struct {
    char *device_name;      // ALSA设备名称(如"default")
    unsigned int sample_rate; // 采样率
    unsigned int channels;  // 声道数
    unsigned int bits_per_sample; // 位深度
    snd_pcm_format_t format; // PCM格式
    unsigned int buffer_time; // 缓冲区时间(微秒)
    unsigned int period_time; // 周期时间(微秒)
} audio_config_t;

/* ==================== 函数声明 ==================== */

/**
 * @brief 读取并解析WAV文件头
 * @param filename WAV文件路径
 * @param header 输出的WAV头信息
 * @return 0成功, -1失败
 *
 * 类比: 就像打开音乐CD,先读取封面上的信息
 */
int read_wav_header(const char *filename, wav_header_t *header);

/**
 * @brief 打印WAV文件信息(调试用)
 * @param header WAV头信息
 *
 * 类比: 把CD封面上的信息读出来给你听
 */
void print_wav_info(const wav_header_t *header);

/**
 * @brief 初始化ALSA播放设备
 * @param handle PCM设备句柄指针
 * @param config 音频配置
 * @return 0成功, <0失败
 *
 * 类比: 打开音响电源,调整到正确的频道和音量
 */
int init_alsa_device(snd_pcm_t **handle, const audio_config_t *config);

/**
 * @brief 播放音频数据
 * @param handle PCM设备句柄
 * @param buffer 音频数据缓冲区
 * @param frames 帧数
 * @return 实际播放的帧数, <0表示错误
 *
 * 类比: 把音乐数据送进音响进行播放
 */
snd_pcm_sframes_t play_audio_frames(snd_pcm_t *handle, const void *buffer, snd_pcm_uframes_t frames);

/**
 * @brief 关闭ALSA设备并释放资源
 * @param handle PCM设备句柄
 *
 * 类比: 关闭音响电源,收拾好设备
 */
void close_alsa_device(snd_pcm_t *handle);

/**
 * @brief 从WAV头信息创建音频配置
 * @param header WAV文件头
 * @param config 输出的音频配置
 * @return 0成功, -1失败
 *
 * 类比: 根据CD封面信息,自动调整音响设置
 */
int wav_header_to_config(const wav_header_t *header, audio_config_t *config);

/* ==================== 实用工具函数 ==================== */

/**
 * @brief 获取WAV文件的播放时长（秒）
 * @param header WAV文件头
 * @return 播放时长（秒）
 */
float get_wav_duration(const wav_header_t *header);

/**
 * @brief 检查WAV文件是否为单声道
 * @param header WAV文件头
 * @return 1单声道, 0立体声
 */
int is_mono_wav(const wav_header_t *header);

#endif /* AUDIO_UTILS_H */
