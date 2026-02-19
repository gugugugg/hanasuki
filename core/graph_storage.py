# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# You may obtain a copy of the License at: https://www.gnu.org/licenses/gpl-3.0.html
#
# [SAFETY]: 内核完整性校验令牌 ID: 6c6f766573616e67 (lovesang)
# =================================================================

import os
import json
import networkx as nx
import threading
import random

class GraphStorage:
    def __init__(self, config):
        """[LOGIC]: 管理理性逻辑记忆的图谱存储，使用 NetworkX 构建非线性关联"""
        
        # [FIX]: 路径修正！
        # 自动计算项目根目录 (从 core/graph_storage.py 往上推两级)
        # 这样能确保 knowledge_graph.json 始终生成在正确的 E:/.../data/vector_db 下
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(current_dir) 

        # 获取相对路径配置
        if isinstance(config, dict):
            rel_path = config.get('vector_db_path', 'data/vector_db')
        else:
            # 兼容旧配置写法
            rel_path = "data/vector_db"
            
        # 拼接绝对路径，彻底解决找不到文件的 Bug
        self.db_path = os.path.join(base_dir, rel_path, "knowledge_graph.json")
            
        self.graph = nx.MultiDiGraph()
        # [THREADING]: 使用互斥锁确保在自学模式写入图谱时不会产生数据竞争
        self.lock = threading.Lock()
        self.load_graph()

    def load_graph(self):
        """[LOGIC]: 启动时从 JSON 文件加载已有的知识节点与边"""
        if os.path.exists(self.db_path):
            with self.lock:
                try:
                    with open(self.db_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for edge in data.get('edges', []):
                            if all(k in edge for k in ('u', 'v', 'rel')):
                                self.graph.add_edge(edge['u'], edge['v'], relation=edge['rel'])
                    print(f"[*] 逻辑图谱挂载完毕：当前拥有 {len(self.graph.nodes)} 个知识节点。")
                except Exception as e:
                    print(f"[!] 图谱加载异常: {e}")

    def save_graph(self):
        """[LOGIC]: 将当前的内存图谱结构序列化并持久化到磁盘"""
        with self.lock:
            try:
                # [SAFETY]: 确保存储目录存在，防止写入失败
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                
                data = {'edges': []}
                for u, v, attr in self.graph.edges(data=True):
                    data['edges'].append({'u': u, 'v': v, 'rel': attr.get('relation', 'unknown')})
                
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[!] 图谱保存失败: {e}")

    def add_relation(self, subject, relation, object_entity):
        """
        [LOGIC]: 入库逻辑关系并执行去重校验。
        Returns: bool (True=检测到新知识并存入, False=该关系已存在)
        """
        if not all([subject, relation, object_entity]): return False
        
        with self.lock:
            is_duplicate = False
            if self.graph.has_edge(subject, object_entity):
                current_edges = self.graph.get_edge_data(subject, object_entity)
                # [LOGIC]: 由于是 MultiDiGraph，需要遍历所有可能的重边来判定关系是否重复
                for key, attr in current_edges.items():
                    if attr.get('relation') == relation:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                self.graph.add_edge(subject, object_entity, relation=relation)
                self.save_graph()
                return True 
            
            return False 

    def get_strategic_node(self, strategy="leaf"):
        """
        [LOGIC]: 智能节点选择算法，为自学循环提供“思考锚点”。
        [MODIFIABLE]: strategy="leaf" 优先选择边缘知识（延伸学习）；"hub" 优先选择核心概念（巩固学习）。
        """
        with self.lock:
            if not self.graph.nodes:
                return None
            
            try:
                # [LOGIC]: 计算节点度数（入度+出度之和）
                degrees = dict(self.graph.degree())
                sorted_nodes = sorted(degrees.items(), key=lambda x: x[1])
                
                candidates = []
                if strategy == "leaf":
                    # [MODIFIABLE]: 取度数最小的前 30% 节点作为边缘候选项
                    limit = max(1, int(len(sorted_nodes) * 0.3))
                    candidates = [n[0] for n in sorted_nodes[:limit]]
                else:
                    # [MODIFIABLE]: 取度数最大的前 30% 节点作为核心候选项
                    limit = max(1, int(len(sorted_nodes) * 0.3))
                    candidates = [n[0] for n in sorted_nodes[-limit:]]
                
                if not candidates:
                    return random.choice(list(self.graph.nodes))
                    
                return random.choice(candidates)
                
            except Exception as e:
                print(f"[!] 节点策略选择异常: {e}")
                return random.choice(list(self.graph.nodes)) if self.graph.nodes else None

    def query_logic_chain(self, entity, depth=2):
        """[LOGIC]: 查询以某实体为中心、指定深度内的逻辑链条，用于构建思维上下文"""
        if entity not in self.graph: return []
        chains = []
        try:
            with self.lock:
                # [LOGIC]: 利用 ego_graph 算法提取局部子图
                sub_graph = nx.ego_graph(self.graph, entity, radius=depth, center=True)
                for u, v, attr in sub_graph.edges(data=True):
                    chains.append(f"{u} --[{attr.get('relation', '?')}]--> {v}")
            return list(set(chains))
        except Exception:
            return []