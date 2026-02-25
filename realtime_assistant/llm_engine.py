#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 引擎模块
功能：封装 DeepSeek API，提供异步对话接口
作者：哈雷酱（傲娇大小姐工程师）
"""

import asyncio
import logging
from typing import Optional, List, Dict

try:
    import aiohttp
except ImportError:
    raise ImportError("未安装 aiohttp，请运行: pip install aiohttp")


class LLMEngine:
    """LLM 对话引擎"""

    def __init__(self, config: dict):
        """
        初始化 LLM 引擎

        参数:
            config: LLM 配置字典
        """
        self.logger = logging.getLogger("realtime_assistant.llm")
        self.config = config

        self.api_key = config["api_key"]
        self.api_base = config.get("api_base", "https://api.deepseek.com/v1")
        self.model = config.get("model", "deepseek-chat")
        self.timeout = config.get("timeout", 10)
        self.max_retries = config.get("max_retries", 3)
        self.system_prompt = config.get("system_prompt", "你是一个友好的语音助手。")

        # 对话历史
        self.conversation_history: List[Dict[str, str]] = []

        # HTTP 会话
        self.session: Optional[aiohttp.ClientSession] = None

        # 降级回复
        self.fallback_responses = {
            "你好": "你好！很高兴见到你。",
            "再见": "再见！祝你有美好的一天。",
            "谢谢": "不客气！很高兴能帮到你。",
            "default": "抱歉，我现在无法处理你的请求，请稍后再试。"
        }

        self.logger.info("✅ LLM 引擎初始化完成")
        self.logger.info(f"   - 模型: {self.model}")
        self.logger.info(f"   - 超时: {self.timeout}s")
        self.logger.info(f"   - 最大重试: {self.max_retries}")

    async def _ensure_session(self):
        """确保 HTTP 会话存在"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def chat_async(self, user_message: str, use_history: bool = False) -> str:
        """
        异步对话

        参数:
            user_message: 用户消息
            use_history: 是否使用对话历史

        返回:
            助手回复
        """
        await self._ensure_session()

        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}]

        if use_history and self.conversation_history:
            messages.extend(self.conversation_history)

        messages.append({"role": "user", "content": user_message})

        # 尝试调用 API
        for attempt in range(self.max_retries):
            try:
                response = await self._call_api(messages)

                # 更新对话历史
                if use_history:
                    self.conversation_history.append({"role": "user", "content": user_message})
                    self.conversation_history.append({"role": "assistant", "content": response})

                    # 限制历史长度（保留最近 10 轮对话）
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]

                self.logger.info(f"💬 LLM 回复: {response}")
                return response

            except asyncio.TimeoutError:
                self.logger.warning(f"⚠️  LLM 请求超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    return self._get_fallback_response(user_message)

            except Exception as e:
                self.logger.error(f"❌ LLM 请求失败: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    return self._get_fallback_response(user_message)

        return self._get_fallback_response(user_message)

    async def _call_api(self, messages: List[Dict[str, str]]) -> str:
        """
        调用 DeepSeek API

        参数:
            messages: 消息列表

        返回:
            助手回复
        """
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 100  # 限制回复长度（约50个中文字或30个英文词）
        }

        async with self.session.post(
            url,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API 返回错误: {response.status}, {error_text}")

            result = await response.json()
            return result["choices"][0]["message"]["content"].strip()

    def _get_fallback_response(self, user_message: str) -> str:
        """
        获取降级回复

        参数:
            user_message: 用户消息

        返回:
            降级回复
        """
        self.logger.info("🔄 使用降级回复")

        # 检查是否有匹配的预设回复
        for key, response in self.fallback_responses.items():
            if key in user_message:
                return response

        return self.fallback_responses["default"]

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        self.logger.info("🗑️  对话历史已清空")

    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history.copy()

    def get_stats(self) -> dict:
        """
        获取统计信息

        返回:
            统计信息字典
        """
        return {
            "model": self.model,
            "history_length": len(self.conversation_history),
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }

    async def close(self):
        """关闭 HTTP 会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("🔒 HTTP 会话已关闭")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
