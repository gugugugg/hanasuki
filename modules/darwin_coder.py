# -*- coding: utf-8 -*-
# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 模块主权验证码: 6c6f766573616e67 (lovesang)
# =================================================================

"""
模块名称：Darwin-Coder (演化编程核心)
版本：V10.0.4 (Audit Passed - No Simplification)
作用：允许 Hanasuki 在独立进程中编写、持久化并执行 Python 脚本，实现逻辑的物理隔离与演化。
核心机制：
1. 独立进程 (Subprocess)：使用系统级 Python 解释器运行，不干扰主内核捏。
2. 物理持久化：所有生成代码均存入 workspace/ 目录，方便大大复审。
3. 鲁棒参数映射：兼容模型输出的 file/file_path, content/code 等多种形态。
"""

import os
import subprocess
import sys

# [CONFIG]: 路径定义
# 自动计算项目根目录与 workspace 路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")

# 确保工作区物理存在捏
if not os.path.exists(WORKSPACE_DIR):
    try:
        os.makedirs(WORKSPACE_DIR)
    except Exception as e:
        print(f"[Darwin] ❌ 无法创建工作区: {e}")

def get_spec():
    """向内核注册工具元数据捏"""
    return {
        "name": "darwin_coder",
        "description": "代码演化工具。支持 'write' (持久化代码) 和 'execute' (执行物理脚本)。",
        "type": "tool"
    }

def is_safe_path(file_path):
    """
    [SAFETY]: 核心安全拦截器。
    逻辑：确保所有写/执行操作被严格限制在 WORKSPACE_DIR 及其子目录下。
    防止 AI 通过 '../' 等手段污染内核源码捏。
    """
    if not file_path:
        return False
        
    # 转化为物理绝对路径进行比对
    abs_target = os.path.abspath(os.path.join(WORKSPACE_DIR, file_path))
    abs_workspace = os.path.abspath(WORKSPACE_DIR)
    
    try:
        # 验证计算出的路径前缀是否包含工作区根路径
        return os.path.commonpath([abs_target, abs_workspace]) == abs_workspace
    except Exception:
        return False

def run(params):
    """
    [LOGIC]: 接收 AI 的指令，执行文件读写或独立进程调用。
    """
    # 1. [ROBUSTNESS]: 鲁棒参数映射
    # 自动识别并补齐 AI 可能写错的键名，确保逻辑不因“幻觉”而中断捏
    action = params.get("action")
    f_path = params.get("file_path") or params.get("file")
    content = params.get("content") or params.get("code") or params.get("code_lines", "")

    # 2. [SAFETY]: 执行路径合规性检查
    if not f_path or not is_safe_path(f_path):
        # 如果是因为 file/file_path 没对上导致 f_path 为空，这里会给出精准反馈
        return f"警告：检测到非法路径越权或参数名缺失 (f_path={f_path})。管家已拦截此次操作捏！"

    target_full_path = os.path.join(WORKSPACE_DIR, f_path)

    try:
        # --- 模式 A: 代码持久化捏 ---
        if action == "write":
            # 确保子目录存在 (支持 'models/test.py' 这种层级结构)
            os.makedirs(os.path.dirname(target_full_path), exist_ok=True)
            with open(target_full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"成功：代码已安全持久化至 {f_path} 捏。"
        
        # --- 模式 B: 独立进程执行捏 ---
        elif action == "execute" or action == "run":
            if not os.path.exists(target_full_path):
                return f"错误：找不到待执行的文件 '{f_path}'，请先使用 write 模式保存捏。"
            
            # [HARDCORE]: 开启独立子进程运行
            # 这种方式比 exec() 更安全，且能完美支持库导入和多线程测试
            try:
                res = subprocess.run(
                    [sys.executable, target_full_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=15  # 针对 RTX 5060 环境设置的 15s 熔断保护捏
                )
                
                # 汇总输出流与错误流
                output = res.stdout.strip()
                errors = res.stderr.strip()
                
                final_feedback = ""
                if output: final_feedback += f"[标准输出]:\n{output}\n"
                if errors: final_feedback += f"[错误反馈]:\n{errors}"
                
                return final_feedback if final_feedback else "执行完成，无屏幕输出捏。"
                
            except subprocess.TimeoutExpired:
                return "错误：代码运行超时 (15s)。疑似存在无限循环，管家已强制熔断子进程捏！"
        
        # --- 模式 C: 默认兜底 (尝试执行传入的代码段) ---
        else:
            if content:
                # 如果没写 action 却带了 content，自动映射为“临时保存并执行”捏
                temp_file = "temp_self_learning.py"
                run({"action": "write", "file": temp_file, "code": content})
                return run({"action": "execute", "file": temp_file})
            return "错误：不支持的操作指令或缺少 content 字段捏。"

    except Exception as e:
        # [DEBUG]: 打印完整的 Traceback 到控制台，方便大大 Debug
        return f"Darwin 引擎内部逻辑崩溃: {str(e)}\n{traceback.format_exc()}"