#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 对话脚本
功能：调用 DeepSeek API 进行对话
作者：哈雷酱（傲娇大小姐工程师）
"""

import sys
import json
import requests

# DeepSeek API 配置
API_KEY = "sk-8729b6bbc81b49bda752005da63185c6"
API_BASE = "https://api.deepseek.com/v1"
API_ENDPOINT = f"{API_BASE}/chat/completions"

# 默认模型
DEFAULT_MODEL = "deepseek-chat"

def chat_with_deepseek(user_message, model=DEFAULT_MODEL, system_prompt=None):
    """
    与 DeepSeek 进行对话

    参数:
        user_message: 用户输入的消息
        model: 使用的模型名称
        system_prompt: 系统提示词（可选）

    返回:
        DeepSeek 的回复文本
    """
    # 构建消息列表
    messages = []

    # 添加系统提示词（如果有）
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    # 添加用户消息
    messages.append({
        "role": "user",
        "content": user_message
    })

    # 构建请求数据
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000,
        "stream": False
    }

    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        # 发送请求
        print("🤖 正在思考中...", file=sys.stderr)
        response = requests.post(
            API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )

        # 检查响应状态
        response.raise_for_status()

        # 解析响应
        result = response.json()

        # 提取回复内容
        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            return reply
        else:
            return "抱歉，没有收到有效的回复。"

    except requests.exceptions.Timeout:
        return "请求超时，请稍后重试。"
    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"
    except json.JSONDecodeError:
        return "响应解析失败。"
    except Exception as e:
        return f"发生错误: {str(e)}"


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 deepseek_chat.py \"你的问题\"", file=sys.stderr)
        print("示例: python3 deepseek_chat.py \"你好，请介绍一下自己\"", file=sys.stderr)
        sys.exit(1)

    # 获取用户输入
    user_message = sys.argv[1]

    # 可选：自定义系统提示词
    system_prompt = None
    if len(sys.argv) > 2:
        system_prompt = sys.argv[2]

    # 调用 DeepSeek
    reply = chat_with_deepseek(user_message, system_prompt=system_prompt)

    # 输出回复（只输出纯文本，方便后续处理）
    print(reply)


if __name__ == "__main__":
    main()
