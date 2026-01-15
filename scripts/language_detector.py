#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能语言检测模块
作者：哈雷酱（傲娇大小姐工程师）
功能：结合 langdetect 和字符统计，提供更准确的语言检测
"""

import re
from typing import Literal

try:
    from langdetect import detect, DetectorFactory, LangDetectException
    # 设置随机种子，确保结果可重复
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


LanguageCode = Literal['zh', 'en', 'mixed', 'unknown']


def detect_language_by_chars(text: str) -> LanguageCode:
    """
    基于字符统计的语言检测（备用方法）

    参数:
        text: 输入文本

    返回:
        'zh' (中文), 'en' (英文), 'mixed' (混合), 'unknown' (未知)
    """
    if not text:
        return 'unknown'

    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

    # 统计英文字母
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    # 计算有效字符总数
    total_chars = chinese_chars + english_chars

    if total_chars == 0:
        return 'unknown'

    # 计算比例
    chinese_ratio = chinese_chars / total_chars
    english_ratio = english_chars / total_chars

    # 判断主要语言（阈值 40%）
    if chinese_ratio > 0.4:
        return 'zh'
    elif english_ratio > 0.4:
        return 'en'
    else:
        return 'mixed'


def detect_language_by_langdetect(text: str) -> LanguageCode:
    """
    基于 langdetect 库的语言检测（主要方法）

    参数:
        text: 输入文本

    返回:
        'zh' (中文), 'en' (英文), 'mixed' (混合), 'unknown' (未知)
    """
    if not LANGDETECT_AVAILABLE:
        return 'unknown'

    if not text or len(text.strip()) == 0:
        return 'unknown'

    try:
        # 使用 langdetect 检测语言
        detected = detect(text)

        # 映射到我们的语言代码
        if detected == 'zh-cn' or detected == 'zh-tw' or detected == 'ko':
            # ko (韩语) 有时会被误判为中文，这里也归为中文
            return 'zh'
        elif detected == 'en':
            return 'en'
        else:
            # 其他语言暂时归为 unknown
            return 'unknown'

    except LangDetectException:
        # 检测失败，返回 unknown
        return 'unknown'


def detect_language(text: str, method: str = 'hybrid') -> LanguageCode:
    """
    智能语言检测（推荐使用）

    参数:
        text: 输入文本
        method: 检测方法
            - 'hybrid': 混合方法（推荐，结合 langdetect 和字符统计）
            - 'langdetect': 仅使用 langdetect
            - 'chars': 仅使用字符统计

    返回:
        'zh' (中文), 'en' (英文), 'mixed' (混合), 'unknown' (未知)
    """
    if not text or len(text.strip()) == 0:
        return 'unknown'

    # 根据方法选择检测策略
    if method == 'chars':
        return detect_language_by_chars(text)
    elif method == 'langdetect':
        if LANGDETECT_AVAILABLE:
            return detect_language_by_langdetect(text)
        else:
            # langdetect 不可用，降级到字符统计
            return detect_language_by_chars(text)
    else:  # hybrid
        # 混合方法：结合两种检测结果
        if LANGDETECT_AVAILABLE:
            langdetect_result = detect_language_by_langdetect(text)
            chars_result = detect_language_by_chars(text)

            # 如果两种方法结果一致，直接返回
            if langdetect_result == chars_result:
                return langdetect_result

            # 如果 langdetect 返回 unknown，使用字符统计结果
            if langdetect_result == 'unknown':
                return chars_result

            # 如果字符统计返回 mixed，使用 langdetect 结果
            if chars_result == 'mixed':
                return langdetect_result

            # 其他情况，优先使用 langdetect 结果（更准确）
            return langdetect_result
        else:
            # langdetect 不可用，使用字符统计
            return detect_language_by_chars(text)


def get_language_name(lang_code: LanguageCode) -> str:
    """
    获取语言代码的中文名称

    参数:
        lang_code: 语言代码

    返回:
        语言的中文名称
    """
    names = {
        'zh': '中文',
        'en': '英文',
        'mixed': '混合',
        'unknown': '未知'
    }
    return names.get(lang_code, '未知')


def main():
    """测试函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 language_detector.py \"文本\"", file=sys.stderr)
        print("示例: python3 language_detector.py \"你好世界\"", file=sys.stderr)
        sys.exit(1)

    text = sys.argv[1]

    print(f"📝 测试文本: {text}", file=sys.stderr)
    print("", file=sys.stderr)

    # 测试三种方法
    if LANGDETECT_AVAILABLE:
        langdetect_result = detect_language_by_langdetect(text)
        print(f"🔍 langdetect 检测: {langdetect_result} ({get_language_name(langdetect_result)})", file=sys.stderr)

    chars_result = detect_language_by_chars(text)
    print(f"🔍 字符统计检测: {chars_result} ({get_language_name(chars_result)})", file=sys.stderr)

    hybrid_result = detect_language(text, method='hybrid')
    print(f"🔍 混合方法检测: {hybrid_result} ({get_language_name(hybrid_result)})", file=sys.stderr)

    print("", file=sys.stderr)
    print(f"✅ 推荐结果: {hybrid_result}", file=sys.stderr)

    # 输出结果（只输出语言代码，方便脚本调用）
    print(hybrid_result)


if __name__ == "__main__":
    main()
