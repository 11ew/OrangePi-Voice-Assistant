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

        # 预热连接（并行优化）
        self._warmup_task = None

    async def _ensure_session(self):
        """确保 HTTP 会话存在"""
        if self.session is None or self.session.closed:
            # 创建会话时设置连接池和超时
            timeout = aiohttp.ClientTimeout(total=self.timeout, connect=5)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)

    async def warmup(self):
        """预热 LLM 连接（并行优化）"""
        try:
            await self._ensure_session()
            self.logger.debug("🔥 LLM 连接预热完成")
        except Exception as e:
            self.logger.warning(f"⚠️  LLM 连接预热失败: {e}")

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

    async def _call_api(self, messages: List[Dict[str, str]], stream: bool = False):
        """
        调用 DeepSeek API

        参数:
            messages: 消息列表
            stream: 是否使用流式输出

        返回:
            助手回复（字符串）或流式生成器
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
            "max_tokens": 100,  # 限制回复长度（约50个中文字或30个英文词）
            "stream": stream
        }

        if not stream:
            # 非流式模式
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
        else:
            # 流式模式
            return self._stream_api(url, headers, payload)

    async def _stream_api(self, url: str, headers: dict, payload: dict):
        """
        流式调用 API（流式处理优化）

        参数:
            url: API URL
            headers: 请求头
            payload: 请求体

        生成:
            流式文本片段
        """
        import json

        async with self.session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API 返回错误: {response.status}, {error_text}")

            # 逐行读取流式响应（SSE 格式）
            buffer = b""
            async for chunk in response.content.iter_any():
                buffer += chunk

                # 按行分割
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    line = line.decode('utf-8').strip()

                    if not line or line == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # 去掉 "data: " 前缀
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

    async def chat_stream_async(self, user_message: str, use_history: bool = False):
        """
        流式对话（流式处理优化）

        参数:
            user_message: 用户消息
            use_history: 是否使用对话历史

        生成:
            流式文本片段
        """
        await self._ensure_session()

        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}]

        if use_history and self.conversation_history:
            messages.extend(self.conversation_history)

        messages.append({"role": "user", "content": user_message})

        # 流式调用 API
        full_response = ""
        async for chunk in await self._call_api(messages, stream=True):
            full_response += chunk
            yield chunk

        # 更新对话历史
        if use_history:
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": full_response})

            # 限制历史长度
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

        self.logger.info(f"💬 LLM 流式回复完成: {full_response}")

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
