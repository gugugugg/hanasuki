# -*- coding: utf-8 -*-
# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 模块主权验证码: 6c6f766573616e67 (lovesang)
# =================================================================

"""
模块名称：Python Executor (Embodied Sandbox Edition)
版本：V1.0
作用：为 Hanasuki 提供“具身化”的代码执行环境。
核心进化：
1. 权限分层：全项目 Read-Only（读），仅 workspace/ 可 Read-Write（写）。
2. 自研闭环：允许 AI 读取 main.py 等源码进行自研分析，同时防止误伤。
3. 动态沙箱：通过函数劫持实时监控文件系统行为。
"""

import sys
import io
import math
import numpy as np
import os
import shutil
import traceback
import builtins

# [CONFIG]: 路径定义
# 获取项目根目录 (E:/lovesang/hanasuki)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 定义唯一的写操作工作区
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")

# [INIT]: 初始化工作区
if not os.path.exists(WORKSPACE_DIR):
    try:
        os.makedirs(WORKSPACE_DIR)
    except:
        pass

def verify_path(path, mode="r"):
    """
    [SECURITY]: 核心权限校验器。
    逻辑：
    - 只要是写操作 (w/a/x/+)：目标必须在 workspace 目录下。
    - 只是读操作 (r)：只要在项目根目录内即可（允许 AI 审阅自身源码）。
    """
    abs_base = os.path.abspath(BASE_DIR)
    abs_workspace = os.path.abspath(WORKSPACE_DIR)
    
    # 1. 转化为规范的绝对路径
    if not os.path.isabs(path):
        # 默认相对于 workspace
        target = os.path.abspath(os.path.join(WORKSPACE_DIR, path))
    else:
        target = os.path.abspath(path)

    # 2. 判断是否涉及写操作
    write_modes = ['w', 'a', 'x', '+', 'wb', 'ab', 'rb+']
    is_write = any(m in mode for m in write_modes)
    
    try:
        # 情况 A: 尝试写文件
        if is_write:
            if os.commonpath([abs_workspace, target]) == abs_workspace:
                return target
            raise PermissionError(f"🔒 越权拦截：严禁在沙箱目录(workspace/)以外进行写操作！")
        
        # 情况 B: 尝试读文件
        else:
            if os.commonpath([abs_base, target]) == abs_base:
                return target
            raise PermissionError(f"🔒 越权拦截：禁止读取项目根目录以外的文件！")
            
    except (ValueError, Exception):
        raise PermissionError("🔒 路径异常：无法验证该路径的合规性。")

# --- [HOOKS]: 安全劫持函数 ---

def safe_open(file, mode="r", *args, **kwargs):
    """
    劫持内置 open 函数。
    允许读取 main.py 等源码，但写入必须在 workspace。
    """
    valid_path = verify_path(file, mode)
    return builtins.open(valid_path, mode, *args, **kwargs)

class SafeOS:
    """劫持 os 模块，对敏感操作实施路径围栏"""
    def __init__(self):
        self.__dict__.update(os.__dict__)
        self.path = os.path
    
    # --- 写操作拦截区 (必须在 workspace) ---
    def remove(self, path, *args, **kwargs):
        return os.remove(verify_path(path, "w"), *args, **kwargs)
    
    def mkdir(self, path, *args, **kwargs):
        return os.mkdir(verify_path(path, "w"), *args, **kwargs)
    
    def makedirs(self, path, *args, **kwargs):
        return os.makedirs(verify_path(path, "w"), *args, **kwargs)
    
    def rename(self, src, dst, *args, **kwargs):
        return os.rename(verify_path(src, "w"), verify_path(dst, "w"), *args, **kwargs)
    
    # --- 读操作执行区 (可以在项目范围内) ---
    def listdir(self, path='.'):
        # 允许查看项目目录结构
        return os.listdir(verify_path(path, "r"))

    def getcwd(self):
        # 模拟当前路径为 workspace，给 AI 一种在沙箱内的错觉
        return WORKSPACE_DIR

class SafeShutil:
    """劫持 shutil 模块"""
    def __init__(self):
        self.__dict__.update(shutil.__dict__)
        
    def rmtree(self, path, *args, **kwargs):
        return shutil.rmtree(verify_path(path, "w"), *args, **kwargs)
    
    def copy(self, src, dst, *args, **kwargs):
        # 从项目读，拷贝到工作区写
        return shutil.copy(verify_path(src, "r"), verify_path(dst, "w"), *args, **kwargs)

# 实例化单例
safe_os_instance = SafeOS()
safe_shutil_instance = SafeShutil()

def run(params):
    """代码执行引擎入口"""
    code = params.get("code")
    if not code:
        return "错误：未检测到待执行代码。"

    # 捕获标准输出
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    
    # 注入安全环境
    safe_globals = {
        "math": math,
        "np": np,
        "numpy": np,
        "print": print,
        "open": safe_open,
        "os": safe_os_instance,
        "shutil": safe_shutil_instance,
        "builtins": builtins,
        # 允许基础的 __import__，但会被上面的 safe_open 限制
    }

    try:
        sys.stdout = output_capture
        # 执行代码
        exec(code, safe_globals)
        sys.stdout = original_stdout 
        
        result = output_capture.getvalue().strip()
        return result if result else "执行成功 (无屏幕输出)。"
    
    except PermissionError as e:
        sys.stdout = original_stdout
        return str(e)
        
    except Exception as e:
        sys.stdout = original_stdout
        return f"代码逻辑错误: {str(e)}\n{traceback.format_exc()}"