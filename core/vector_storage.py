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
# [MISSION]: 为 Hanasuki 提供非结构化的感性记忆检索能力捏！🌸
# [ENGINE]: 基于 LanceDB 与 Sentence-Transformers 实现的语义搜索。
# =================================================================

import os
import lancedb
import pyarrow as pa
import re
from datetime import datetime

class VectorStorage:
    """
    [HERO-A+ 感性核心]:
    负责管理 Hanasuki 的语义片段记忆。不同于图谱的严谨逻辑，
    这里存储的是对话碎片与感性认知，为 RAG 架构提供长短期语义支持捏。
    """
    def __init__(self, config):
        """
        [LOGIC]: 初始化向量存储引擎。
        [FIX]: 修正了 config 读取深度，支持从主配置字典直接映射捏。
        """
        # 1. 自动校准物理路径捏
        self.db_path = config.get('vector_db_path', os.path.join("data", "vector_db"))
        self.model_path = config.get('embedding_model', 'models/embeddings/bge-small-zh-v1.5')
        self.table_name = 'hanasuki_memories'
        
        # 2. 路径解耦逻辑捏
        # 确保相对路径总是基于项目根目录计算，提升开源后的环境适配性捏。
        if not os.path.isabs(self.db_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, self.db_path)
            self.model_path = os.path.join(base_dir, self.model_path)

        # 3. 初始化 Embedding 编码器捏
        self.encoder = None
        self.vector_dim = 512 # 默认维度捏
        
        print(f"🌸 正在唤醒感性核心: {os.path.basename(self.model_path)}...")
        try:
            from sentence_transformers import SentenceTransformer
            # [8GB VRAM OPTIMIZATION]:
            # 物理锁定 device='cpu'，防止向量模型占用宝贵的显存，留给 Qwen 主模型捏！
            if os.path.exists(self.model_path):
                self.encoder = SentenceTransformer(self.model_path, device='cpu')
                self.vector_dim = self.encoder.get_sentence_embedding_dimension()
            else:
                print(f"⚠️ [警告]: 路径缺失捏 {self.model_path}，检索功能将进入降级模式捏。")
        except Exception as e:
            print(f"呜呜... 感性核心初始化失败捏: {e}")
        
        # 4. 初始化 LanceDB 持久化层捏
        os.makedirs(self.db_path, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        self._init_table()

    def _init_table(self):
        """
        [LOGIC]: 使用 PyArrow 定义物理存储 Schema 捏。
        包含了向量、文本、分类、来源及时间戳五个维度捏。
        """
        schema = pa.schema([
            pa.field("vector", pa.list_(pa.float32(), self.vector_dim)),
            pa.field("text", pa.string()),
            pa.field("category", pa.string()),
            pa.field("source", pa.string()),
            pa.field("timestamp", pa.string())
        ])
        try:
            self.table = self.db.open_table(self.table_name)
        except:
            # 如果表不存在则根据 Schema 物理创建捏
            self.table = self.db.create_table(self.table_name, schema=schema, exist_ok=True)

    def add_memory(self, text, category="chat", source="system"):
        """
        [LOGIC]: 将文本碎片转化为高维向量并存入数据库捏。
        这是 Hanasuki “内化”大大教诲的核心接口捏。
        """
        if not self.encoder or not text: return
        try:
            # 语义编码捏
            vector = self.encoder.encode(text).tolist()
            data = [{
                "vector": vector,
                "text": text,
                "category": category,
                "source": source,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            self.table.add(data)
        except Exception as e:
            print(f"[!] 记忆持久化失败捏: {e}")

    def search_memory(self, query, limit=3):
        """
        [LOGIC]: 基于余弦相似度 (Cosine Similarity) 的语义检索捏。
        为 LLM 提供最相关的历史片段，实现上下文增强 (RAG)。
        """
        if not self.encoder or not query: return []
        try:
            # 将查询句转化为检索向量捏
            query_vector = self.encoder.encode(query).tolist()
            # 显式使用 metric="cosine" 以确保语义匹配的精确性捏
            results = self.table.search(query_vector).metric("cosine").limit(limit).to_list()
            return [res['text'] for res in results]
        except:
            return []