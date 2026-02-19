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
# [MISSION]: 为 Hanasuki 提供“逻辑演化”能力，实现代码的物理持久化与隔离执行捏！🌸
# [ARCHITECTURE]: 基于独立子进程 (Subprocess) 的演化编程实验场捏。
# =================================================================

"""
模块名称：Darwin-Coder (演化编程核心)
版本：Beta 1.1 (Audit Passed - No Simplification)
作用：允许 Hanasuki 在独立进程中编写、持久化并执行 Python 脚本，实现逻辑的物理隔离与演化。
核心机制：
1. 独立进程 (Subprocess)：使用系统级 Python 解释器运行，不干扰主内核显存占用捏。
2. 物理持久化：所有生成代码均存入 workspace/ 目录，方便大大复审。
3. 鲁棒参数映射：兼容模型输出的多种参数键名，有效对抗 8B 模型的参数幻觉捏。
"""

import os
import subprocess
import sys
import traceback

# [CONFIG]: 物理路径定义捏
# 自动计算项目根目录与具身工作区路径，确保相对路径的平滑迁移捏。
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")

# 确保演化实验室（工作区）物理存在捏
if not os.path.exists(WORKSPACE_DIR):
    try:
        os.makedirs(WORKSPACE_DIR)
    except Exception as e:
        print(f"[Darwin] ❌ 无法创建演化空间捏: {e}")

def get_spec():
    """
    [TOOL SPEC]: 向内核注册演化工具元数据捏。
    支持 'write' (持久化逻辑) 和 'execute' (物理验证脚本) 两大核心功能。
    """
    return {
        "name": "darwin_coder",
        "description": "代码演化工具。支持 'write' (代码存档) 和 'execute' (独立进程执行)。",
        "parameters": {
            "action": "执行动作 (write/execute) 捏",
            "file_path": "工作区内的文件相对路径捏",
            "content": "待持久化的代码内容捏"
        }
    }

def is_safe_path(file_path):
    """
    [SAFETY]: 核心路径拦截器捏。
    逻辑：通过 os.path.commonpath 确保所有读写操作被严格限制在 workspace/ 及其子目录下。
    物理拦截了 AI 试图通过 '../' 路径穿越污染大大内核源码的企图捏！
    """
    if not file_path:
        return False
        
    # 转化为物理绝对路径进行比对捏
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
    接收模型指令，执行代码读写或独立子进程调用捏。
    """
    # 1. [ROBUSTNESS]: 参数鲁棒性映射捏
    # 自动识别并补齐 AI 可能写错的键名，确保自研逻辑不因微小的键名幻觉而中断捏。
    action = params.get("action")
    f_path = params.get("file_path") or params.get("file")
    content = params.get("content") or params.get("code") or params.get("code_lines", "")

    # 2. [SAFETY]: 执行路径安全围栏校验捏
    if not f_path or not is_safe_path(f_path):
        return f"警告：拦截到非法路径访问或参数名缺失 (f_path={f_path})。管家已锁定权限捏！"

    target_full_path = os.path.join(WORKSPACE_DIR, f_path)

    try:
        # --- 模式 A: 代码持久化 (存档) ---
        if action == "write":
            # 自动创建递归子目录，支持 'tests/unit/logic.py' 这种层级结构捏
            os.makedirs(os.path.dirname(target_full_path), exist_ok=True)
            with open(target_full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"成功：逻辑已安全存证至 {f_path} 捏。"
        
        # --- 模式 B: 独立进程执行 (验证) ---
        elif action == "execute" or action == "run":
            if not os.path.exists(target_full_path):
                return f"错误：找不到待验证的文件 '{f_path}'，请先使用 write 模式保存捏。"
            
            # [8GB VRAM PROTECTION]: 开启物理隔离子进程捏。
            # 这种方式比 exec() 更安全，且能完美支持外部库导入，同时不会抢占主程序的显存空间捏。
            try:
                res = subprocess.run(
                    [sys.executable, target_full_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=15  # 针对 RTX 5060 环境设置的 15s 熔断保护，防止死循环导致 CPU 爆满捏！
                )
                
                # 汇总标准输出流与错误反馈流捏
                output = res.stdout.strip()
                errors = res.stderr.strip()
                
                final_feedback = ""
                if output: final_feedback += f"[标准输出]:\n{output}\n"
                if errors: final_feedback += f"[错误反馈]:\n{errors}"
                
                return final_feedback if final_feedback else "执行完成，代码无屏幕输出反馈捏。"
                
            except subprocess.TimeoutExpired:
                return "错误：代码运行超时 (15s)。疑似存在计算黑洞，管家已物理熔断子进程捏！"
        
        # --- 模式 C: 默认兜底 (即写即走模式) ---
        else:
            if content:
                # 如果没写 action 却提供了代码，自动映射为“临时存档并执行”捏
                temp_file = "temp_self_evolution.py"
                run({"action": "write", "file": temp_file, "code": content})
                return run({"action": "execute", "file": temp_file})
            return "错误：不支持的操作指令或代码内容缺失捏。"

    except Exception as e:
        # [DEBUG]: 打印完整的 Traceback 到控制台，方便大大进行 Beta 版本的 Debug 捏
        return f"Darwin 演化引擎内部坍塌捏: {str(e)}\n{traceback.format_exc()}"