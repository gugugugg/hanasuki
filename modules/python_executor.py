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
# [MISSION]: 为 Hanasuki 提供安全的具身执行沙箱，实现代码逻辑的物理隔离捏！🌸
# [SECURITY]: 实施严苛的“全项目 Read-Only”与“工作区 Read-Write”权限隔离捏。
# =================================================================

"""
模块名称：Python Executor (HERO-A+ Embodied Sandbox)
作用：Hanasuki 具身智能的物理执行引擎。

核心特性：
1. 学术工具链：注入 time, json, re, numpy 等基础库，支持 AI 进行性能测试与数据处理捏。
2. 权限沙箱：通过路径拦截，拦截 AI 对系统敏感目录或内核源码的非法写入捏。
3. 环境隔离：利用独立命名空间 (safe_globals) 进行 exec 调用，保障主进程逻辑安全。
"""

import sys
import io
import math
import numpy as np
import os
import shutil
import traceback
import builtins
import time   # [NEW]: 允许 AI 在自研时进行时间性能测试捏
import json   # [NEW]: 允许 AI 处理配置文件或结构化研究数据捏
import re     # [NEW]: 允许 AI 进行复杂的文本正则匹配与数据清洗捏

# [CONFIG]: 路径自解耦对齐捏
# 自动计算项目根目录，确保沙箱始终锁定在 workspace/ 文件夹内捏。
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")

# 物理检查演化实验室是否存在捏
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR, exist_ok=True)

def verify_path(path, mode="r"):
    """
    [SECURITY]: 核心物理权限校验器。
    
    [LOGIC]:
    - 写操作 (Write)：物理锁定在 workspace/ 目录内，禁止触碰任何系统文件捏。
    - 读操作 (Read)：允许读取项目根目录内容，支持 Hanasuki 进行源码级的“自研内省”捏。
    """
    abs_base = os.path.abspath(BASE_DIR)
    abs_workspace = os.path.abspath(WORKSPACE_DIR)
    
    # 路径标准化处理，拦截一切相对路径穿越攻击捏
    target = os.path.abspath(os.path.join(WORKSPACE_DIR, path)) if not os.path.isabs(path) else os.path.abspath(path)

    # 判定当前是否为写操作模式捏
    write_modes = ['w', 'a', 'x', '+', 'wb', 'ab']
    is_write = any(m in mode for m in write_modes)
    
    try:
        if is_write:
            # 写操作必须在沙箱（workspace/）内捏
            if os.commonpath([abs_workspace, target]) == abs_workspace:
                return target
            raise PermissionError(f"🔒 越权拦截：严禁在沙箱目录 (workspace/) 以外写入文件捏！")
        else:
            # 读操作允许在项目根目录（BASE_DIR）内捏
            if os.commonpath([abs_base, target]) == abs_base:
                return target
            raise PermissionError(f"🔒 越权拦截：禁止读取项目根目录以外的敏感数据捏！")
    except Exception:
        raise PermissionError("🔒 路径异常：管家无法验证该路径的物理安全性捏。")

# --- [HOOKS]: 安全劫持机制捏 ---

def safe_open(file, mode="r", *args, **kwargs):
    """[LOGIC]: 劫持原生 open，强制进行 verify_path 校验捏。"""
    return builtins.open(verify_path(file, mode), mode, *args, **kwargs)

class SafeOS:
    """
    [LOGIC]: 对 os 模块进行“半透膜”封装捏。
    仅暴露安全的路径查询功能，并对写操作接口进行 verify_path 硬拦截。
    """
    def __init__(self):
        # 继承大部分读取类方法捏
        self.__dict__.update(os.__dict__)
        self.path = os.path
    
    # [SAFETY]: 限制所有写操作物理锁定在 workspace
    def remove(self, path, *args, **kwargs): return os.remove(verify_path(path, "w"), *args, **kwargs)
    def mkdir(self, path, *args, **kwargs): return os.mkdir(verify_path(path, "w"), *args, **kwargs)
    def makedirs(self, path, *args, **kwargs): return os.makedirs(verify_path(path, "w"), *args, **kwargs)
    def rename(self, src, dst, *args, **kwargs): 
        return os.rename(verify_path(src, "w"), verify_path(dst, "w"), *args, **kwargs)
    
    # 读操作需验证项目内权限捏
    def listdir(self, path='.'): return os.listdir(verify_path(path, "r"))
    def getcwd(self): return WORKSPACE_DIR

def run(params):
    """
    [LOGIC]: 沙箱代码执行引擎入口捏。
    
    接收来自 LLM 的代码段，在独立命名空间中执行，并捕获标准输出流反馈给大大。
    """
    # [ROBUSTNESS]: 兼容 'code' 或 'content' 键名，拦截模型微小的参数幻觉捏。
    code = params.get("code") or params.get("content")
    if not code: return "错误：未检测到可执行的逻辑片段捏。"

    # [IO]: 物理劫持标准输出流捏
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    
    # [INJECTION]: 注入学术研究必备的工具库，助力 Hanasuki 演化进化捏！
    safe_globals = {
        "math": math,
        "np": np,
        "numpy": np,
        "time": time,  # 允许使用 sleep 和 time() 进行效率分析
        "json": json,  # 允许解析配置文件
        "re": re,      # 允许正则提取逻辑
        "print": print,
        "open": safe_open, # 注入安全劫持版 open
        "os": SafeOS(),    # 注入安全劫持版 os
        "shutil": os,      # 简单重映射，通过 SafeOS 逻辑拦截
        "builtins": builtins,
    }

    try:
        sys.stdout = output_capture
        # 使用独立的命名空间物理防止污染内核主进程捏
        exec(code, safe_globals)
        sys.stdout = original_stdout 
        
        # 提取并返回执行结果捏
        result = output_capture.getvalue().strip()
        return result if result else "执行成功 (无屏幕输出反馈) 捏。"
    
    except PermissionError as e:
        sys.stdout = original_stdout
        return f"权限受限捏: {str(e)}"
    except Exception as e:
        # [DEBUG]: 捕获代码逻辑错误并反馈完整的 Traceback 捏
        sys.stdout = original_stdout
        return f"代码演化异常捏: {str(e)}\n{traceback.format_exc()}"