# -*- coding: utf-8 -*-
# =================================================================
# Project: Hanasuki (花好き) AI Kernel - HERO-A+ Edition
# Version: Beta 1.1
# License: GNU General Public License v3 (GPLv3)
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# [MISSION]: 通过物理拦截工具参数的不确定性，彻底根除 LLM 的逻辑幻觉捏！??
# [PROTOCOL]: Relign (Reliability-Oriented Learning & Integration)
# =================================================================

"""
模块名称：Clarify Mechanism (犹豫协议核心)
作用：Hanasuki 逻辑闭环的物理安全保障。
[ACADEMIC VALUE]: 在多智能体交互或具身执行系统中，该模块为小模型提供了一个显式的“不确定性表达”路径捏。
当 8B 模型在处理如学术 URL、本地文件路径或特定代码参数感到模糊时，
与其强行编造指令，不如通过该模块向大大申请“逻辑援兵”捏。
"""

def get_spec():
    """
    [RELIGN SPEC]: 向内核注册犹豫机制的工具规范捏。
    
    [PROMPT STRATEGY]: 
    通过强约束的描述提示模型：当且仅当参数不确定时，必须调用此工具。
    这在推理过程中起到一种“语义阻尼器”的作用，防止 8B 模型在自研时失控捏！
    """
    return {
        "name": "clarify",
        "description": "【核心安全工具】当模型对其他工具的参数（如 URL、文件名、关键词）不确定时，必须调用此工具进行澄清，严禁编造捏。",
        "parameters": {
            "reason": "描述你感到困惑的具体逻辑点，或需要大大补充的缺失上下文信息捏。"
        }
    }

def run(params):
    """
    [LOGIC]: 具身化澄清入口捏。
    
    虽然这在底层是一个“伪执行工具”，但它在 main.py 的执行链条中会被物理拦截。
   
    
    拦截后的结果会通过 UI 侧边栏或 DailyReporter 反馈给大大，
    从而将不确定的“死循环”转化为高效的人机协作科研流捏。
    """
    # 提取模型感到的核心困惑点捏
    reason = params.get("reason", "我不确定该如何继续进行下一步学术操作捏...")
    
    # 构造带有 Hanasuki 特色的反馈语，温和地请求大大的指导捏 ??
    return f"【Hanasuki 申请澄清】: {reason}\n大大，由于信息不足，我担心产生幻觉，请提供更准确的指令捏！"