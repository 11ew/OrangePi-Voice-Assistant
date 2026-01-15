#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言检测工具
检测文本是中文还是英文
"""

import sys
import re


def detect_language(text):
    """
    检测文本的主要语言

    参数:
        text: 输入文本

    返回:
        'zh' (中文), 'en' (英文), 'mixed' (混合)
    """
    if not text:
        return 'unknown'

    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

    # 统计英文字母
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    # 统计数字
    digit_chars = len(re.findall(r'[0-9]', text))

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


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 detect_language.py \"文本\"", file=sys.stderr)
        print("示例: python3 detect_language.py \"你好世界\"", file=sys.stderr)
        sys.exit(1)

    text = sys.argv[1]
    lang = detect_language(text)

    # 输出语言代码
    print(lang)


if __name__ == "__main__":
    main()
