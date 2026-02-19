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
# [MISSION]: 为 Hanasuki 提供结构化的理性逻辑记忆，支持复杂推理与一致性校验捏！🌸
# [ARCHITECTURE]: 基于 NetworkX 实现的具身化知识图谱 (Knowledge Graph)。
# =================================================================

"""
模块名称：GraphStorage (HERO-A+ Rational Memory Engine)
版本：Beta 1.1 (Academic Edition)
作用：Hanasuki 的理性逻辑中枢。
核心特性：
1. LightRAG 双层索引：实体级 (Local) + 社区摘要级 (Global) 捏。
2. ACLA 支撑：物理计算节点中心度，为上下文剪裁提供逻辑权重。
3. 逻辑冲突拦截：防止“A是B”与“A不是B”等悖论污染认知图谱。
"""

import os
import json
import threading
import random
import networkx as nx
from collections import Counter

class GraphStorage:
    """
    [HERO-A+ 理性核心]:
    管理结构化的逻辑链条。与向量库 (VectorStorage) 的感性语义检索不同，
    图谱专注于实体间的物理关联，是 Hanasuki 进行逻辑推演的基石捏。
    """
    def __init__(self, config):
        """[LOGIC]: 初始化具备层级演化能力的逻辑图谱存储捏。"""
        self.lock = threading.Lock() # 线程锁，确保自研模式与对话模式并发安全捏
        
        # 1. 路径自动解耦与对齐
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(current_dir)
        
        # 兼容配置字典，提取数据库物理路径捏
        if isinstance(config, dict):
            rel_path = config.get('vector_db_path', 'data/vector_db')
        else:
            rel_path = 'data/vector_db'
            
        self.db_dir = os.path.join(base_dir, rel_path)
        os.makedirs(self.db_dir, exist_ok=True)
        self.graph_file = os.path.join(self.db_dir, "knowledge_graph.json")
        
        # 2. 初始化 NetworkX 多向有向图对象捏
        # MultiDiGraph 允许两个实体间存在多种逻辑关系（如“属于”与“研究”）捏。
        self.graph = nx.MultiDiGraph()
        self.load_graph()

    def load_graph(self):
        """[LOGIC]: 从物理 JSON 文件内化逻辑链条捏。"""
        if os.path.exists(self.graph_file):
            try:
                with open(self.graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for node in data.get('nodes', []):
                        self.graph.add_node(node['id'], **node)
                    for edge in data.get('edges', []):
                        self.graph.add_edge(edge['from'], edge['to'], 
                                          relation=edge['relation'], 
                                          weight=edge.get('weight', 1.0))
                print(f"[图谱] ✅ 成功内化了 {self.graph.number_of_nodes()} 个逻辑节点捏。")
            except Exception as e:
                print(f"[图谱] ⚠️ 读取失败，可能存在格式冲突: {e}")

    def save_graph(self):
        """[LOGIC]: 持久化逻辑资产至物理硬盘捏。"""
        try:
            with self.lock:
                data = {
                    "nodes": [{"id": n, **self.graph.nodes[n]} for n in self.graph.nodes],
                    "edges": [{"from": u, "to": v, **d} for u, v, k, d in self.graph.edges(data=True, keys=True)]
                }
                with open(self.graph_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[图谱] ❌ 存档失败捏: {e}")

    # --- HERO-A+ 核心算法：节点重要性 (ACLA 支撑) ---
    def get_node_importance(self, node_id):
        """
        [ACLA - Adaptive Contextual Logic Anchoring]:
        计算节点在逻辑网络中的重要性（中心度）。
        
        数学模型：
        $$Importance(v) = Degree(v) \cdot \lambda$$
        其中 summary 节点的 $\lambda = 1.5$。权重越高，代表该节点是科研课题的核心前提，
        越不容易在 ACLA 剪裁中被丢弃捏！
        """
        if node_id not in self.graph:
            return 0.0
        # 采用度中心度 (Degree Centrality)，兼顾出度与入度捏
        degree = self.graph.degree(node_id)
        # 宏观摘要节点具备更高的权重加成，因为它们承载了社区共识捏
        if self.graph.nodes[node_id].get('type') == 'summary':
            return float(degree) * 1.5
        return float(degree)

    # --- HERO-A+ 核心算法：一致性校验 ---
    def check_conflict(self, subject, relation, object_node):
        """
        [LOGIC]: 逻辑悖论防御系统。
        拦截并检测模型是否试图写入与既有知识冲突的信息（如语义反转）捏。
        """
        if self.graph.has_edge(subject, object_node):
            existing_relations = [d['relation'] for _, _, d in self.graph.edges(subject, data=True) if _ == subject]
            # 简单的互斥词拦截逻辑捏
            negations = ["不是", "不属于", "拒绝", "禁止", "not", "no"]
            for rel in existing_relations:
                # 语义冲突判定：一正一反则视为逻辑污染捏
                if (any(n in relation for n in negations)) != (any(n in rel for n in negations)):
                    return True
        return False

    def add_relation(self, subject, relation, object_node, weight=1.0):
        """[LOGIC]: 写入逻辑关联，内置 ASR 一致性拦截捏。"""
        with self.lock:
            # 1. 自动对齐实体节点并打上类别标签
            if subject not in self.graph: self.graph.add_node(subject, type="entity")
            if object_node not in self.graph: self.graph.add_node(object_node, type="entity")
            
            # 2. 逻辑一致性校验捏
            if self.check_conflict(subject, relation, object_node):
                print(f"[图谱] 🛡️ 发现逻辑冲突: {subject} --{relation}--> {object_node}。已拦截捏！")
                return False
            
            # 3. 物理写入逻辑边捏
            self.graph.add_edge(subject, object_node, relation=relation, weight=weight)
            self.save_graph()
            return True

    # --- HERO-A+ 核心算法：LightRAG 双层索引演化 ---
    def update_community_summaries(self, llm_callback):
        """
        [LightRAG]: 自动领域聚类并生成高层摘要节点。
        解决 8B 模型在处理海量信息时“不见森林”的局限性捏。
        """
        try:
            # 采用贪婪模块度算法寻找知识簇 (Louvain-like Community Detection)
            from networkx.algorithms import community
            communities = sorted(community.greedy_modularity_communities(self.graph.to_undirected()), key=len, reverse=True)
            
            for i, comm in enumerate(communities):
                if len(comm) < 5: continue # 太小的知识点簇暂不抽象捏
                
                comm_nodes = list(comm)
                summary_id = f"CLUSTER_SUMMARY_{i}"
                
                # 随机采样更新策略，防止过度消耗 LLM 算力捏
                if summary_id in self.graph and random.random() > 0.1: continue
                
                # 调用 LLM 回调生成该领域的宏观综述捏
                prompt = f"请总结以下知识点之间的核心逻辑联系，形成简短的学术综述捏：{', '.join(comm_nodes)}"
                summary_text = llm_callback(prompt)
                
                with self.lock:
                    # 将摘要节点挂载至图谱顶部捏
                    self.graph.add_node(summary_id, type="summary", desc=summary_text, member_count=len(comm_nodes))
                    for node in comm_nodes:
                        self.graph.add_edge(summary_id, node, relation="contains")
            
            self.save_graph()
            print(f"[图谱] 🏛️ 已完成 {len(communities)} 个领域的层级摘要构建捏。")
        except Exception as e:
            print(f"[图谱] 摘要演化异常: {e}")

    def query_logic_chain(self, entity, depth=2):
        """[LOGIC]: 提取指定实体的邻居逻辑，为 ACLA 提供推理上下文 (RAG Context) 捏。"""
        if entity not in self.graph: return []
        try:
            # 使用自我中心图 (Ego Graph) 提取局部关系捏
            sub_graph = nx.ego_graph(self.graph, entity, radius=depth)
            chains = []
            for u, v, d in sub_graph.edges(data=True):
                chains.append(f"{u} --({d.get('relation')})--> {v}")
            return chains
        except:
            return []

    def get_random_node(self, strategy="leaf"):
        """[LOGIC]: 为自研模式提供目标锚点，实现知识补全捏。"""
        if not self.graph.nodes: return None
        nodes = list(self.graph.nodes)
        if strategy == "leaf":
            # 优先选择边缘节点进行深度补全捏
            degrees = dict(self.graph.degree())
            sorted_nodes = sorted(degrees.items(), key=lambda x: x[1])
            return sorted_nodes[0][0]
        return random.choice(nodes)