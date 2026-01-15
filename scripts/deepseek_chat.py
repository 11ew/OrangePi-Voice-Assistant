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

    # 使用统一的双语系统提示词，让 DeepSeek 自己判断语言
    system_prompt = """You are a friendly bilingual voice assistant. Please follow these rules:
1. CRITICAL: If the user speaks in English, you MUST reply in English. If the user speaks in Chinese, you MUST reply in Chinese.
2. Language detection: Check if the user's message contains mainly English words -> reply in English. If mainly Chinese characters -> reply in Chinese.
3. Reply in a casual, natural way like a friend, not too formal
4. If the user's question contains obvious speech recognition errors, guess the intent from context
5. Keep replies under 50 words, suitable for voice playback
6. Use appropriate tone to make the conversation lively

你是一个友好的双语语音助手。请遵循以下规则：
1. 关键：如果用户说英文，你必须用英文回复。如果用户说中文，你必须用中文回复。
2. 语言检测：检查用户消息是否主要包含英文单词 -> 用英文回复。如果主要是中文字符 -> 用中文回复。
3. 回复要简洁自然，像朋友聊天一样，不要太官方
4. 如果用户的问题包含明显的语音识别错误（错别字），请根据上下文推测真实意图
5. 回复控制在 50 字以内，适合语音播报
6. 可以使用适当的语气词，让对话更生动

Examples:
User: "what can you do?" -> Reply in English: "I can help you with weather, set alarms, answer questions, and chat with you!"
User: "你能做什么？" -> Reply in Chinese: "我能帮你查天气、设闹钟、回答问题，还能陪你聊天！"
"""

    # 可选：自定义系统提示词
    if len(sys.argv) > 2:
        system_prompt = sys.argv[2]

    # 调用 DeepSeek
    reply = chat_with_deepseek(user_message, system_prompt=system_prompt)

    # 输出回复（只输出纯文本，方便后续处理）
    print(reply)


if __name__ == "__main__":
    main()
