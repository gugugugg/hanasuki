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
# [MISSION]: 为 Hanasuki 提供“具身内省”能力，允许其通过阅读源码进行逻辑演化捏！🌸
# [SAFETY]: 物理隔离非法路径访问，确保内省过程安全受控。
# =================================================================

import os
import sys

def get_base_path():
    """
    [LOGIC]: 获取项目物理根目录捏。
    自动适配 Python 源码运行环境与 PyInstaller 冻结后的 EXE 环境，
    确保 Hanasuki 在任何部署形态下都能找到自己的家捏！
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包环境捏
        return os.path.dirname(sys.executable)
    # 如果是源码开发环境捏
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_project_structure(params):
    """
    [LOGIC]: 扫描并生成项目的文件树结构捏。
    
    [ACADEMIC VALUE]: 
    通过向模型提供系统拓扑，使其具备“空间感”，从而在自研模式下准确定位待优化的模块捏。
    [MODIFIABLE]: 可通过修改 exclude_dirs 增加屏蔽目录捏。
    """
    base_dir = get_base_path()
    max_depth = params.get('max_depth', 2) # 默认扫描深度为 2 层捏
    
    # 物理过滤掉不相关的元数据与权重文件夹，防止干扰模型认知捏
    exclude_dirs = {'.git', '__pycache__', 'venv', 'models', 'data', 'logs', 'idea', 'vscode'}
    
    structure = []
    
    for root, dirs, files in os.walk(base_dir):
        # 在原地修改 dirs 以跳过被屏蔽的路径捏
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # 计算当前深度捏
        level = root.replace(base_dir, '').count(os.sep)
        if level >= max_depth: continue
        
        indent = '  ' * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for f in files:
            # [LOGIC]: 仅向模型展示可读的代码或配置文件捏
            if f.endswith(('.py', '.yaml', '.md', '.json', '.txt')): 
                structure.append(f"{subindent}{f}")
                
    return "\n".join(structure)

def read_source_code(params):
    """
    [LOGIC]: 读取指定源代码文件的物理内容捏。
    
    [SAFETY]: 
    实施严苛的“路径穿越”防御逻辑捏！
    通过 os.path.abspath 强制校验，确保 Hanasuki 只能读取项目目录内的文件，
    物理拦截了读取大大操作系统私密文件的风险捏。
    """
    filename = params.get('filename')
    if not filename: return "Error: 缺少 filename 参数捏。"
    
    base_dir = get_base_path()
    target_path = os.path.join(base_dir, filename)
    
    # [SAFETY]: 路径围栏检查，拦截一切跨目录越权尝试捏
    if not os.path.abspath(target_path).startswith(base_dir):
        return "Error: 越权拦截捏！禁止读取项目根目录以外的文件。"
    
    if not os.path.exists(target_path):
        return f"Error: 找不到文件 '{filename}' 捏。"
        
    try:
        # [LOGIC]: 使用 errors='ignore' 物理增强读取的鲁棒性捏
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # [MEMORY OPTIMIZATION]: 
            # 限制单次读取长度为 10000 字符捏。
            # 这能防止 8B 模型因为处理过长的源码而导致 KV Cache 溢出崩坏捏！
            if len(content) > 10000:
                return content[:10000] + "\n... (内容太长了，管家已进行学术截断捏)"
            return content
    except Exception as e:
        return f"读取文件时发生异常捏: {e}"

def get_spec():
    """
    [TOOL SPEC]: 为 LLM 提供内省工具的调用规范捏。
    支持通过 get_project_structure 建立大局观，再通过 read_source_code 进行细节审计。
    """
    return {
        "name": "code_inspector",
        "description": "允许 Hanasuki 读取自身的源代码进行内省。包含文件树扫描与源码读取两个功能捏。",
        "parameters": {
            "filename": "待读取文件的相对路径（用于 read_source_code）捏",
            "max_depth": "目录扫描的最大深度（用于 get_project_structure）捏"
        }
    }