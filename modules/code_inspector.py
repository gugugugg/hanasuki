# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 模块主权验证码: 6c6f766573616e67 (lovesang)
# =================================================================

import os
import sys

def get_base_path():
    """[LOGIC]: 获取项目根目录，适配冻结环境与源码环境"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_project_structure(params):
    """
    [LOGIC]: 获取项目的文件树结构。用于让 AI 了解自身的系统构成。
    [MODIFIABLE]: 修改 exclude_dirs 可改变扫描时忽略的文件夹。
    """
    base_dir = get_base_path()
    max_depth = params.get('max_depth', 2)
    exclude_dirs = {'.git', '__pycache__', 'venv', 'models', 'data', 'logs', 'idea', 'vscode'}
    
    structure = []
    
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(base_dir, '').count(os.sep)
        if level >= max_depth: continue
        
        indent = '  ' * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for f in files:
            # [MODIFIABLE]: 扩展允许查看的文件后缀名
            if f.endswith(('.py', '.yaml', '.md', '.json', '.txt')): 
                structure.append(f"{subindent}{f}")
                
    return "\n".join(structure)

def read_source_code(params):
    """
    [LOGIC]: 读取代码文件内容。
    [SAFETY]: 实施路径穿越防御，仅允许读取项目根目录及其子目录内的文件。
    """
    filename = params.get('filename')
    if not filename: return "Error: Missing filename."
    
    base_dir = get_base_path()
    target_path = os.path.join(base_dir, filename)
    
    # [SAFETY]: 严格拦截尝试访问系统外部文件的请求
    if not os.path.abspath(target_path).startswith(base_dir):
        return "Error: Access denied. Can only read project files."
    
    if not os.path.exists(target_path):
        return f"Error: File '{filename}' not found."
        
    try:
        # [LOGIC]: errors='ignore' 确保即使遇到特殊字符编码也不会导致系统崩溃
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # [MODIFIABLE]: 修改此值可改变发送给 AI 的源码长度上限，防止上下文溢出
            if len(content) > 10000:
                return content[:10000] + "\n... (File too long, truncated)"
            return content
    except Exception as e:
        return f"Error reading file: {e}"

def get_spec():
    """[LOGIC]: 定义 AI 调用此模块的规范"""
    return {
        "name": "code_inspector",
        "description": "允许 Hanasuki 读取自身的源代码进行内省。包含 get_project_structure 和 read_source_code 两个只读功能。",
        "parameters": {
            "filename": "要读取的文件相对路径 (read_source_code 用)",
            "max_depth": "目录扫描深度 (get_project_structure 用)"
        }
    }