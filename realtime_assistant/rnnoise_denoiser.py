#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RNNoise 降噪模块
功能：使用 RNNoise 进行实时音频降噪
作者：哈雷酱（傲娇大小姐工程师）
"""

import ctypes
import numpy as np
import logging
from typing import Optional
from ctypes import util


class RNNoiseDenoiser:
    """RNNoise 降噪器"""

    def __init__(self, sample_rate: int = 48000):
        """
        初始化 RNNoise 降噪器

        参数:
            sample_rate: 采样率（RNNoise 要求 48000 Hz）
        """
        self.logger = logging.getLogger("realtime_assistant.rnnoise")

        # RNNoise 只支持 48kHz
        if sample_rate != 48000:
            self.logger.warning(f"⚠️  RNNoise 只支持 48kHz，当前采样率 {sample_rate} Hz")
            self.logger.warning("   音频将被重采样到 48kHz")

        self.sample_rate = 48000
        self.frame_size = 480  # RNNoise 固定帧大小：480 样本 (10ms @ 48kHz)

        # 加载 RNNoise 库
        try:
            lib_path = util.find_library("rnnoise")
            if not lib_path:
                # 尝试直接加载
                lib_path = "/usr/local/lib/librnnoise.so"

            self.lib = ctypes.cdll.LoadLibrary(lib_path)
            self.logger.info(f"✅ RNNoise 库加载成功: {lib_path}")
        except Exception as e:
            self.logger.error(f"❌ RNNoise 库加载失败: {e}")
            raise RuntimeError(f"无法加载 RNNoise 库: {e}")

        # 设置函数签名
        # rnnoise_create 接受一个 RNNModel* 参数（可以是 NULL）
        self.lib.rnnoise_create.argtypes = [ctypes.c_void_p]
        self.lib.rnnoise_create.restype = ctypes.c_void_p
        self.lib.rnnoise_destroy.argtypes = [ctypes.c_void_p]
        self.lib.rnnoise_process_frame.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float)
        ]
        self.lib.rnnoise_process_frame.restype = ctypes.c_float

        # 创建 RNNoise 状态（传入 NULL 使用默认模型）
        self.state = self.lib.rnnoise_create(None)
        # 注意：rnnoise_create 返回的是指针（整数），0 表示失败
        if self.state == 0 or self.state is None:
            raise RuntimeError("RNNoise 状态创建失败")

        self.logger.info("✅ RNNoise 降噪器初始化完成")
        self.logger.info(f"   - 采样率: {self.sample_rate} Hz")
        self.logger.info(f"   - 帧大小: {self.frame_size} 样本 (10ms)")

    def process_frame(self, audio_frame: np.ndarray) -> tuple:
        """
        处理单个音频帧

        参数:
            audio_frame: 音频帧数据 (480 个 int16 样本)

        返回:
            (vad_prob, denoised_frame): VAD 概率和降噪后的音频帧
        """
        # 确保输入是 480 个样本
        if len(audio_frame) != self.frame_size:
            raise ValueError(f"音频帧大小必须是 {self.frame_size} 样本，当前为 {len(audio_frame)}")

        # 转换为 float32 类型 (RNNoise 要求)
        # RNNoise 期望的输入范围是 short 的范围（不需要归一化）
        if audio_frame.dtype == np.int16:
            audio_float = audio_frame.astype(np.float32)
        elif audio_frame.dtype == np.float32:
            # 如果已经是 float32，检查范围
            if np.max(np.abs(audio_frame)) <= 1.0:
                # 范围是 [-1, 1]，需要转换到 [-32768, 32767]
                audio_float = audio_frame * 32768.0
            else:
                audio_float = audio_frame.copy()
        else:
            raise ValueError(f"不支持的音频数据类型: {audio_frame.dtype}")

        # 创建输出缓冲区（必须是独立的数组）
        output_buffer = np.zeros(self.frame_size, dtype=np.float32)

        # 获取指针
        input_ptr = audio_float.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        output_ptr = output_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        # 调用 RNNoise 处理（注意参数顺序：state, out, in）
        vad_prob = self.lib.rnnoise_process_frame(self.state, output_ptr, input_ptr)

        # 转换回 int16
        denoised_frame = output_buffer.astype(np.int16)

        return vad_prob, denoised_frame

    def process_audio(self, audio_data: np.ndarray) -> tuple:
        """
        处理完整的音频数据

        参数:
            audio_data: 音频数据 (int16 或 float32)

        返回:
            (vad_probs, denoised_audio): VAD 概率列表和降噪后的音频
        """
        # 确保是 int16 类型
        if audio_data.dtype == np.float32:
            if np.max(np.abs(audio_data)) <= 1.0:
                audio_data = (audio_data * 32768.0).astype(np.int16)
            else:
                audio_data = audio_data.astype(np.int16)

        # 计算需要处理的帧数
        num_frames = len(audio_data) // self.frame_size

        if num_frames == 0:
            self.logger.warning(f"⚠️  音频数据太短 ({len(audio_data)} 样本)，至少需要 {self.frame_size} 样本")
            return [], audio_data

        # 处理每一帧
        vad_probs = []
        denoised_frames = []

        for i in range(num_frames):
            start = i * self.frame_size
            end = start + self.frame_size
            frame = audio_data[start:end]

            vad_prob, denoised_frame = self.process_frame(frame)
            vad_probs.append(vad_prob)
            denoised_frames.append(denoised_frame)

        # 合并所有帧
        denoised_audio = np.concatenate(denoised_frames)

        # 如果有剩余样本，直接添加（不处理）
        remaining = len(audio_data) % self.frame_size
        if remaining > 0:
            denoised_audio = np.concatenate([denoised_audio, audio_data[-remaining:]])

        self.logger.debug(f"✅ 处理完成: {num_frames} 帧，平均 VAD 概率: {np.mean(vad_probs):.3f}")

        return vad_probs, denoised_audio

    def destroy(self):
        """销毁 RNNoise 状态"""
        if self.state:
            self.lib.rnnoise_destroy(self.state)
            self.state = None
            self.logger.info("🗑️  RNNoise 状态已销毁")

    def __del__(self):
        """析构函数"""
        self.destroy()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.destroy()


def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    重采样音频数据

    参数:
        audio_data: 原始音频数据
        orig_sr: 原始采样率
        target_sr: 目标采样率

    返回:
        重采样后的音频数据
    """
    if orig_sr == target_sr:
        return audio_data

    # 简单的线性插值重采样
    ratio = target_sr / orig_sr
    new_length = int(len(audio_data) * ratio)

    # 使用 numpy 的插值
    x_old = np.arange(len(audio_data))
    x_new = np.linspace(0, len(audio_data) - 1, new_length)

    resampled = np.interp(x_new, x_old, audio_data)

    return resampled.astype(audio_data.dtype)
