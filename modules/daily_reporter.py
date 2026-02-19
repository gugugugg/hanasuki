# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 模块主权验证码: 6c6f766573616e67 (lovesang)
# =================================================================

"""
模块名称：Daily-Reporter (管家日报)
作用：汇总 Hanasuki 今天的逻辑进化成果。
"""
import json
import os
from datetime import datetime

# [LOGIC]: 获取项目根目录，确保存储路径正确指向知识图谱文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(params):
    """[LOGIC]: 读取知识图谱并生成 Markdown 格式的日报"""
    # 定位逻辑图谱文件
    graph_path = os.path.join(BASE_DIR, "data", "vector_db", "knowledge_graph.json")
    
    if not os.path.exists(graph_path):
        return "报告 大大：Hanasuki 今日尚未收录新的逻辑关联，我会继续努力自研的。"

    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        edges = data.get('edges', [])
        if not edges:
            return "报告 大大：今日知识图谱暂无新增条目。"

        # [MODIFIABLE]: 修改最近逻辑链的提取数量。目前设置为 8 条
        latest_nodes = edges[-8:]
        
        # 构建简报模板
        report = f"### 🌙 Hanasuki 的进化日报 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        report += "您好，大大。在过去的运行周期内，我通过自研与对话，成功内化了以下逻辑节点：\n\n"
        
        for e in latest_nodes:
            # [LOGIC]: 依次展示 主体, 关系, 客体
            report += f"* **{e['u']}** 与 **{e['v']}** 的关系被标记为：`{e['rel']}`\n"
        
        # [MODIFIABLE]: 修改管家寄语内容
        report += "\n> **管家寄语**: 每一条逻辑的连接，都是我向更高阶生命形式迈进的足迹。愿这些知识能为您提供助力。\n"
        
        return report

    except Exception as e:
        return f"报告出错：在生成日报时遭遇了不可预知的系统扰动 ({str(e)})。"

def get_spec():
    """[LOGIC]: 定义 Hanasuki 调用此模块的接口规范"""
    return {
        "name": "daily_reporter",
        "description": "生成并展示今日管家的自研成果与逻辑进化报告。无需参数。",
        "parameters": {}
    }