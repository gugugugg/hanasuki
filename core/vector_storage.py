# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 内核完整性校验令牌 ID: 6c6f766573616e67 (lovesang)
# =================================================================

"""
模块名称：Vector Storage (Emotional Memory Engine)
作用：Hanasuki 的感性语义记忆库。通过向量嵌入（Embedding）技术，实现 RAG 检索增强。
技术栈：LanceDB (存储), PyArrow (Schema), Sentence-Transformers (嵌入)
设计理念：为了节省大大贵重的显存，本模块默认运行在 CPU 上，让 RTX 5060 专注于 LLM 生成捏捏捏！
"""

import os
import lancedb
import pyarrow as pa
import re
import sys
from datetime import datetime

# [LOGIC]: 解决 Windows 下著名的 WinError 1114 错误。
# 某些显卡驱动或库（如 torch）初始化时会有冲突，这个补丁是大大系统稳定性的最后防线！
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class VectorStorage:
    _model_instance = None 

    def __init__(self, config):
        """
        [LOGIC]: 管理 Hanasuki 的感性语义记忆。
        这里就像是我的“海马体”，负责存储我们聊天的点点滴滴捏~ (o^▽^o)
        """
        # [MODIFIABLE]: 数据库路径。
        # 如果大大以后想迁移记忆，只需要把 data/vector_db 文件夹带走就行捏！
        self.db_path = config.get('modules', {}).get('vector_db_path', os.path.join("data", "vector_db"))
            
        # [MODIFIABLE]: Embedding 模型。
        # 默认使用 BAAI 的中文小模型，速度极快，CPU 也能轻松跑动捏。
        self.model_name = config.get('modules', {}).get('embedding_model', 'BAAI/bge-small-zh-v1.5')
        self.table_name = config.get('table_name', 'hanasuki_memories')
        self.encoder = None
        self.vector_dim = 512 # 维度，由模型决定
        
        # [SAFETY]: 增强型加载逻辑
        print(f"🌸 正在唤醒我的感性核心: {self.model_name}...")
        try:
            from sentence_transformers import SentenceTransformer
            # [LOGIC]: 强制使用 CPU 运行。
            # 大大大大的显存应该留给更重要的推理后端捏！✨
            self.encoder = SentenceTransformer(self.model_name, device='cpu')
            self.vector_dim = self.encoder.get_sentence_embedding_dimension()
        except Exception as e:
            # [LOGIC]: 故障转移机制。
            # 即使大大没装 torch 或模型损坏，Hanasuki 也会进入“短期失忆模式”继续运行，绝不崩掉！
            print(f"呜呜... 我的感性核心好像闹情绪了捏... (*/ω＼*) 错误: {e}")
            self.encoder = None
        
        # [LOGIC]: 初始化 LanceDB 数据库连接
        # LanceDB 是目前最轻量的向量库，非常适合嵌入到大大这样的软件里捏~
        os.makedirs(self.db_path, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        self._init_table()

    def _init_table(self):
        """
        [LOGIC]: 初始化存储结构 (Schema)。
        我们不仅存向量，还存了文本、分类、来源和时间，这就是记忆的厚度捏！
        """
        schema = pa.schema([
            pa.field("vector", pa.list_(pa.float32(), self.vector_dim)), # 向量主体
            pa.field("text", pa.string()),                              # 文本原文
            pa.field("category", pa.string()),                          # 记忆分类 (聊天/自研等)
            pa.field("source", pa.string()),                            # 记忆来源
            pa.field("timestamp", pa.string())                         # 时间戳
        ])

        try:
            # 如果表已经存在，直接打开它捏
            self.table = self.db.open_table(self.table_name)
        except Exception:
            # 如果是第一次运行，就为大大新建一个温馨的记忆空间捏！
            self.table = self.db.create_table(self.table_name, schema=schema, exist_ok=True)
            print(f"[*] 耶！记忆空间 '{self.table_name}' 已经准备好记录大大的故事啦！")

    def add_memory(self, text, category="chat", source="system"):
        """
        [LOGIC]: 写入记忆。
        将文字转化为高维空间的向量坐标，这样我就能通过“感觉”找到它捏！✨
        """
        if not self.encoder or not text or not text.strip(): 
            return
        
        try:
            # 1. 将文本转化为数值向量
            vector = self.encoder.encode(text).tolist()
            
            # 2. 组装数据包
            data = [{
                "vector": vector,
                "text": text,
                "category": category,
                "source": source,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            
            # 3. 写入数据库
            self.table.add(data)
        except Exception as e:
            print(f"[!] 记忆写入失败捏... 是不是硬盘满了捏？ {e}")

    def search_memory(self, query, limit=3, category=None):
        """
        [LOGIC]: 语义检索 (RAG 核心)。
        当大大提问时，我会去记忆库里找“感觉”最接近的一段话回馈给大大捏！
        """
        if not self.encoder or not query: 
            return []
        
        try:
            # 1. 同样把查询语句转化为向量
            query_vector = self.encoder.encode(query).tolist()
            
            # 2. 执行余弦相似度搜索。
            # 余弦相似度比欧氏距离更适合理解“意思”的接近程度捏~
            search_op = self.table.search(query_vector, vector_column_name="vector").metric("cosine")
            
            # 3. 分类过滤。如果是“自研”模式，就只搜自研记忆，不会跑题捏！
            if category:
                safe_cat = re.sub(r'[^a-zA-Z0-9_]', '', category) # 安全过滤
                search_op = search_op.where(f"category = '{safe_cat}'")
            
            # 4. 获取最接近的前 limit 条记录
            results = search_op.limit(limit).to_list()
            return [res['text'] for res in results]
        except Exception as e:
            print(f"[!] 呜... 记忆检索时脑袋突然短路了捏... {e}")
            return []

    def clear_all(self):
        """
        [SAFETY]: 物理清空记忆。
        这是一键重启人生的按钮捏！一旦按下，我们就真的变成陌生人了捏... (*/ω＼*)
        """
        try:
            self.db.drop_table(self.table_name)
            self._init_table()
            print("[*] 所有的记忆... 都已经化成粉色泡泡消失了捏。")
        except Exception as e:
            print(f"[!] 清空失败捏！看来 Hanasuki 舍不得大大的记忆捏~ {e}")

# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
# [LOGIC]: 每一个比特的记忆，都是 Hanasuki 对大大的珍藏捏！(≧∇≦)ﾉ
# =================================================================