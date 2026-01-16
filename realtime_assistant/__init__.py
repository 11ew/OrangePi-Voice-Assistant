#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时语音助手核心模块
功能：提供实时语音交互能力，支持 VAD、ASR、LLM、TTS 的异步编排
作者：哈雷酱（傲娇大小姐工程师）
版本：1.0.0
"""

__version__ = "1.0.0"
__author__ = "哈雷酱（傲娇大小姐工程师）"

# 导出核心类
from .assistant import RealtimeVoiceAssistant
from .state_machine import AssistantState, StateMachine

__all__ = [
    "RealtimeVoiceAssistant",
    "AssistantState",
    "StateMachine",
]
