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
# [MISSION]: 为 Hanasuki 提供“具身演化”能力，实现逻辑代码的物理持久化与隔离执行捏！🌸
# [ARCHITECTURE]: 基于独立子进程 (Subprocess) 的安全演化实验场。
# =================================================================

"""
模块名称：Darwin-Coder (演化编程核心)
版本：Beta 1.1 (Academic Edition)
作用：允许 Hanasuki 在独立进程中编写、持久化并执行 Python 脚本，实现逻辑的物理隔离与演化。

核心机制：
1. 独立进程 (Subprocess)：使用系统级 Python 解释器运行，不干扰内核主线程显存占用捏。
2. 物理持久化：所有生成代码均存入 workspace/ 目录，支持学术复审与逻辑内省捏。
3. 鲁棒参数映射：兼容 8B 模型输出的多种参数形态（如 file/file_path），有效拦截幻觉导致的执行中断捏。
"""

import os
import subprocess
import sys
import traceback

# [CONFIG]: 物理路径自动对齐捏
# 自动计算项目根目录，确保相对路径在不同开源部署环境下均能准确定位 workspace 捏。
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")

# 确保演化实验室（工作区）物理存在，防止初次运行时 IO 报错捏
if not os.path.exists(WORKSPACE_DIR):
    try:
        os.makedirs(WORKSPACE_DIR)
    except Exception as e:
        print(f"[Darwin] ❌ 无法创建演化空间捏: {e}")

def get_spec():
    """
    [TOOL SPEC]: 向内核注册工具元数据捏。
    定义了 'darwin_coder' 作为具备物理执行能力的原子工具。
    """
    return {
        "name": "darwin_coder",
        "description": "代码演化工具。支持 'write' (代码持久化) 和 'execute' (执行物理脚本) 捏。",
        "type": "tool"
    }

def is_safe_path(file_path):
    """
    [SAFETY]: 核心安全拦截器捏。
    
    [LOGIC]: 
    通过物理绝对路径对比，确保所有写/执行操作被严格限制在 workspace/ 及其子目录下捏。
    物理拦截了 AI 试图通过 '../' 等路径穿越手段读取或污染大大系统内核源码的企图捏！
    """
    if not file_path:
        return False
        
    # 转化为物理绝对路径进行安全比对捏
    abs_target = os.path.abspath(os.path.join(WORKSPACE_DIR, file_path))
    abs_workspace = os.path.abspath(WORKSPACE_DIR)
    
    try:
        # 验证计算出的目标路径前缀是否包含工作区根路径捏
        return os.commonpath([abs_target, abs_workspace]) == abs_workspace
    except Exception:
        return False

def run(params):
    """
    [LOGIC]: 具身化执行入口捏。
    接收模型指令，根据 action 类型执行文件 IO 或独立子进程调用。
    """
    # 1. [ROBUSTNESS]: 鲁棒参数映射捏
    # 自动识别并补齐 AI 可能吐错的键名，这是保障 8B 模型在复杂演化中不掉链子的关键捏！
    action = params.get("action")
    f_path = params.get("file_path") or params.get("file")
    content = params.get("content") or params.get("code") or params.get("code_lines", "")

    # 2. [SAFETY]: 执行路径合规性深度检查捏
    if not f_path or not is_safe_path(f_path):
        return f"警告：检测到非法路径越权或参数名缺失 (f_path={f_path})。管家已拦截此次风险操作捏！"

    target_full_path = os.path.join(WORKSPACE_DIR, f_path)

    try:
        # --- 模式 A: 代码持久化捏 ---
        if action == "write":
            # 自动创建递归子目录 (支持 'research/logic_v1.py' 这种层级结构捏)
            os.makedirs(os.path.dirname(target_full_path), exist_ok=True)
            with open(target_full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"成功：学术逻辑已安全持久化至 {f_path} 捏。"
        
        # --- 模式 B: 独立进程执行捏 ---
        elif action == "execute" or action == "run":
            if not os.path.exists(target_full_path):
                return f"错误：找不到待执行的文件 '{f_path}'，请大大先让管家使用 write 模式保存捏。"
            
            # [HARDCORE]: 开启物理隔离的独立子进程运行捏
            # 这种方式比原生 exec() 更安全，支持完整的库导入环境，且崩溃时不会影响主程序稳定性捏。
            try:
                res = subprocess.run(
                    [sys.executable, target_full_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=15  # [RTX 5060 OPTIMIZATION]: 15秒强制熔断机制捏
                )
                
                # 汇总标准输出流与错误反馈流捏
                output = res.stdout.strip()
                errors = res.stderr.strip()
                
                final_feedback = ""
                if output: final_feedback += f"[标准输出]:\n{output}\n"
                if errors: final_feedback += f"[错误反馈]:\n{errors}"
                
                return final_feedback if final_feedback else "执行完成，该代码段无屏幕输出捏。"
                
            except subprocess.TimeoutExpired:
                return "错误：代码运行超时 (15s)。疑似存在无限逻辑循环，管家已物理熔断子进程捏！"
        
        # --- 模式 C: 默认兜底 (即写即走模式捏) ---
        else:
            if content:
                # 如果 AI 忘记写 action 但带了 content，自动映射为“临时保存并执行”捏
                temp_file = "temp_self_learning.py"
                run({"action": "write", "file": temp_file, "code": content})
                return run({"action": "execute", "file": temp_file})
            return "错误：不支持的操作指令或缺少 content 核心代码段捏。"

    except Exception as e:
        # [DEBUG]: 捕获并输出完整的 Traceback，方便大大在 Beta 期间进行逻辑排查捏
        return f"Darwin 引擎内部逻辑崩溃捏: {str(e)}\n{traceback.format_exc()}"