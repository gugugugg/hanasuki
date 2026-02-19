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
# [MISSION]: 基于受限硬件（RTX 5060 8GB）实现自演化、高可靠性的学术助手捏。
# [ARCHITECTURE]: HERO-A+ (Hierarchical Evolution & Reliability-Oriented)
# =================================================================

import yaml, time, threading, json, re, os, gc, traceback, random
from core.daily_reporter import DailyReporter

class Hanasuki:
    """
    Hanasuki 核心控制类。
    负责调度感性记忆 (Vector)、理性逻辑 (Graph) 与物理执行器 (Modules) 捏。
    """
    def __init__(self):
        print("🌸 [内核] Hanasuki HERO-A+ 架构正在初始化...")
        from core.module_manager import ModuleManager
        from core.model_wrapper import get_model_backend
        from core.storage.vector_storage import VectorStorage
        from core.storage.graph_storage import GraphStorage

        # 1. 基础资源装载捏 (对齐 GUI 命名的 ModuleManager)
        self.config = self._load_config()
        self.model = get_model_backend(self.config['model'])
        
        # 2. 挂载双轨记忆中枢：向量数据库 (感性) 与 逻辑图谱 (理性)
        self.vector_db = VectorStorage(self.config['modules'])
        self.graph_db = GraphStorage(self.config['modules'])
        
        # 3. 挂载工具管理与日报系统捏
        self.mm = ModuleManager(self.config['modules']) 
        self.reporter = DailyReporter()

        # 4. 初始化上下文状态机与并发安全锁
        self.history = []
        self.learning_active = False
        self._lock = threading.Lock()
        
        # 5. 物理环境自检，确保 data/ 结构完整捏
        self._check_environment()
        print("✅ [内核] Hanasuki Beta 1.1 逻辑对齐完毕，随时待命捏！")

    def _load_config(self):
        """[LOGIC]: 加载 config.yaml 动力参数捏"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        with open(path, 'r', encoding='utf-8') as f: return yaml.safe_load(f)

    def _check_environment(self):
        """[SAFETY]: 物理目录哨兵，防止运行期出现 FileNotFoundError 捏"""
        for d in ["data/logs", "data/reports", "data/vector_db", "workspace"]:
            os.makedirs(d, exist_ok=True)

    # --- [ACLA]: 自适应上下文逻辑锚定算法 ---
    def _trim_history_adaptive(self):
        """
        [ACLA - Adaptive Contextual Logic Anchoring]:
        不同于传统的 FIFO (先进先出)，ACLA 通过数学评估保留最重要的逻辑锚点捏。
        计算公式如下：
        $$S_{anchor} = \alpha \cdot \text{Recency} + \beta \cdot \frac{\text{Weight}}{\text{Threshold}}$$
        其中 $\alpha=0.4$ (时间权重), $\beta=0.6$ (逻辑重要性)。
        """
        if len(self.history) <= 15: return
        with self._lock:
            scored = []
            total_len = len(self.history)
            for i, msg in enumerate(self.history):
                # 1. 计算时间新鲜度 (Recency)
                recency = (i + 1) / total_len
                # 2. 提取消息中的实体并从图谱获取逻辑权重 (Logic Weight)
                entities = re.findall(r'[\u4e00-\u9fa5]{2,6}|[A-Za-z0-9\-]{3,15}', msg['content'])
                g_weight = sum([self.graph_db.get_node_importance(e) for e in entities])
                
                # 3. 综合评分，权重高的实体 (如科研课题关键定义) 将被物理锁定在显存中捏
                score = 0.4 * recency + 0.6 * min(1.0, g_weight / 20.0)
                scored.append((score, msg))
            
            # 排序并保留得分最高的 12 条核心锚点记忆，以及最后 3 条实时对话捏
            scored.sort(key=lambda x: x[0], reverse=True)
            self.history = sorted([x[1] for x in scored[:12]] + self.history[-3:], 
                                 key=lambda x: self.history.index(x) if x in self.history else 999)

    # --- [TOOL]: Relign 协议下的 JSON 自动化执行链条 ---
    def _parse_and_execute(self, text):
        """
        [RELIGN Protocol]: 物理执行 LLM 吐出的 JSON 指令捏。
        如果解析到 'clarify'，则触发犹豫机制，拦截潜在的工具幻觉。
        """
        pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if not match: return None
        
        try:
            call_data = json.loads(match.group(1))
            tool_name = call_data.get("tool")
            params = call_data.get("params", {})
            
            # [RELIGN]: 拦截不确定性捏
            if tool_name == "clarify":
                return f"【Relign 犹豫触发】: {params.get('reason')}"
            
            # 物理调用 ModuleManager 进行具身执行捏
            return self.mm.execute(tool_name, params)
        except:
            return "（Hanasuki 试图理解 JSON，但格式解析异常捏...）"

    # --- [CORE]: 具身化对话工作流 ---
    def chat(self, user_input, stream=True):
        """
        [HYBRID RAG]: 结合向量检索 (感性) 与图谱链条 (理性) 的生成逻辑捏。
        """
        # 1. 启动 ACLA 上下文自适应剪裁，保障 8GB 显存稳定捏
        self._trim_history_adaptive()
        
        # 2. 混合语义召回
        v_ctx = self.vector_db.search_memory(user_input, limit=2) # 检索相近的聊天片段
        entities = re.findall(r'[\u4e00-\u9fa5]{2,6}|[A-Za-z0-9\-]{3,15}', user_input)
        g_ctx = []
        for e in entities[:3]: g_ctx.extend(self.graph_db.query_logic_chain(e)) # 检索逻辑推理链条
        
        # 3. 构造 HERO-A+ 增强型 System Prompt
        sys_p = self._build_hero_prompt(v_ctx, g_ctx)
        msgs = [{"role": "system", "content": sys_p}] + self.history + [{"role": "user", "content": user_input}]
        
        # 4. 生成回复流捏
        full_res = ""
        for chunk in self.model.generate(msgs, stream=stream):
            full_res += chunk
            yield chunk

        # 5. [NEW]: 实时工具执行反馈
        tool_result = self._parse_and_execute(full_res)
        if tool_result:
            yield f"\n\n> ⚙️ **具身执行反馈**: {tool_result}"
            full_res += f"\n[Tool Output]: {tool_result}"

        # 6. 对话内化与持久化存储
        with self._lock:
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": full_res})
        
        # 异步更新记忆库，不干扰主线程响应捏
        threading.Thread(target=self._internalize, args=(user_input, full_res)).start()

    def _build_hero_prompt(self, v, g):
        """[LOGIC]: 注入当前召回的知识与 Relign 禁令捏"""
        tools = self.mm.get_module_descriptions()
        return f"""你现在是管家 Hanasuki。
## 当前关联背景：
- 相似记忆：{v}
- 逻辑关联：{g}
## 可用工具指令：
{tools}
## [Relign Protocol]：
如果工具参数（URL、文件名等）不确定，严禁编造！必须使用 clarify 工具说明困惑捏。"""

    def _internalize(self, u, a):
        """[LOGIC]: 知识沉淀，更新向量库与活动日志捏"""
        self.vector_db.add_memory(f"Q: {u} | A: {a}")
        self.reporter.log_activity("Chat", f"与大大同步了最新的逻辑节点捏")

    # --- [LEARNING]: 自研模式逻辑 ---
    def start_self_learning(self):
        """[LOGIC]: 开启 Hanasuki 的“深度梦境”自进化模式捏"""
        if self.learning_active: return
        self.learning_active = True
        threading.Thread(target=self._run_learning_loop, daemon=True).start()

    def _run_learning_loop(self):
        """[SELF-EVOLUTION]: 自动探索逻辑图谱并补全知识盲区捏"""
        print("[自研] 🌙 正在切换至 16k 深度上下文模式...")
        self.model.reload(self.config['model']['profile_learning'])
        try:
            while self.learning_active:
                # 1. 寻找图谱中的边缘节点捏
                target = self.graph_db.get_random_node()
                if not target: time.sleep(10); continue
                
                # 2. 模拟研究过程
                res = self.model.generate([{"role": "user", "content": f"深入分析并演化实体逻辑: {target}"}], stream=False)
                tool_res = self._parse_and_execute(res)
                
                # 3. 处理研究障碍捏 (如果卡住则记入早报)
                if "【Relign 犹豫触发】" in str(tool_res):
                    self.reporter.log_confusion(target, tool_res)
                else:
                    self.graph_db.add_relation(target, "已演化", "Academic_Node")
                
                # 4. 显存热量平衡休眠
                time.sleep(self.config.get('learning', {}).get('idle_threshold', 30))
        finally:
            self.model.reload(self.config['model']['profile_normal'])