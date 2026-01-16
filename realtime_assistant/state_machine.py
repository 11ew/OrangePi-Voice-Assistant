#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态机模块
功能：管理实时语音助手的状态转换
作者：哈雷酱（傲娇大小姐工程师）
"""

from enum import Enum
from typing import Callable, Dict, Optional
import logging


class AssistantState(Enum):
    """助手状态枚举"""
    IDLE = "空闲"
    LISTENING = "监听中"
    PROCESSING = "处理中"
    SPEAKING = "播放中"
    ERROR = "错误"


class StateMachine:
    """状态机"""

    def __init__(self, initial_state: AssistantState = AssistantState.IDLE):
        """
        初始化状态机

        参数:
            initial_state: 初始状态
        """
        self.state = initial_state
        self.previous_state = None
        self.state_callbacks: Dict[AssistantState, list] = {
            state: [] for state in AssistantState
        }
        self.transition_callbacks: Dict[tuple, list] = {}
        self.logger = logging.getLogger("realtime_assistant.state_machine")

        self.logger.info(f"🎬 状态机初始化: {self.state.value}")

    def register_callback(self, state: AssistantState, callback: Callable):
        """
        注册状态回调

        参数:
            state: 状态
            callback: 回调函数
        """
        self.state_callbacks[state].append(callback)
        self.logger.debug(f"注册状态回调: {state.value}")

    def register_transition_callback(
        self,
        from_state: AssistantState,
        to_state: AssistantState,
        callback: Callable
    ):
        """
        注册状态转换回调

        参数:
            from_state: 源状态
            to_state: 目标状态
            callback: 回调函数
        """
        key = (from_state, to_state)
        if key not in self.transition_callbacks:
            self.transition_callbacks[key] = []
        self.transition_callbacks[key].append(callback)
        self.logger.debug(f"注册转换回调: {from_state.value} -> {to_state.value}")

    def transition(self, new_state: AssistantState):
        """
        状态转换

        参数:
            new_state: 新状态
        """
        if self.state == new_state:
            return

        old_state = self.state
        self.previous_state = old_state
        self.state = new_state

        # 记录状态转换
        self.logger.info(f"🔄 状态转换: {old_state.value} -> {new_state.value}")

        # 触发转换回调
        transition_key = (old_state, new_state)
        if transition_key in self.transition_callbacks:
            for callback in self.transition_callbacks[transition_key]:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"转换回调执行失败: {e}")

        # 触发状态回调
        if new_state in self.state_callbacks:
            for callback in self.state_callbacks[new_state]:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"状态回调执行失败: {e}")

    def get_state(self) -> AssistantState:
        """获取当前状态"""
        return self.state

    def get_previous_state(self) -> Optional[AssistantState]:
        """获取前一个状态"""
        return self.previous_state

    def is_state(self, state: AssistantState) -> bool:
        """
        检查是否为指定状态

        参数:
            state: 要检查的状态

        返回:
            是否为指定状态
        """
        return self.state == state

    def reset(self):
        """重置状态机到初始状态"""
        self.transition(AssistantState.IDLE)
        self.previous_state = None
        self.logger.info("🔄 状态机已重置")
