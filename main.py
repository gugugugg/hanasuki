# -*- coding: utf-8 -*-
# =================================================================
# Project: Hanasuki AI Kernel (Ultimate Academic Edition)
# Version: V10.1.0.1
# Author: lovesang (Audited & Refined)
# 
# [LOGIC ARCHITECTURE]:
# 1. Strict Schema Enforcement: 物理锁定 'tool' 键名，终结 'action' 歧义。
# 2. Dynamic Entropy Decay: 选中课题必衰减，未中课题稳步补偿，彻底根治复读。
# 3. Academic Shield: 内核级搜索算子注入 (-site:zhihu.com 等 9 层屏蔽)。
# 4. Discovery Persistence: URL 足迹记录，物理拦截重复点击行为捏。
# =================================================================

import yaml
import time
import threading
import json
import re
import os
import sys
import random
import binascii
import traceback
import gc

# [SYSTEM]: 环境隔离与 CUDA 显存利用优化捏
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GGML_CUDA_NO_VMM"] = "1"        

def get_base_path():
    """动态获取项目根路径，确保 Windows 路径兼容性捏"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

class Hanasuki:
    def __init__(self):
        """核心驱动初始化：构建高内聚、具身化的自研大脑捏"""
        self._verify_kernel_integrity()
        self.base_dir = get_base_path()
        
        # 1. 配置文件强制载入，若缺失则熔断捏
        config_path = os.path.join(self.base_dir, "config.yaml")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"大大，找不到核心配置 config.yaml 捏！")
            
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        print("[Kernel] 🚀 正在初始化 V10.1.0.1 终极学术版引擎...")
        
        # 2. 动态重载模型后端（针对 RTX 5060 移动端显存优化）捏
        try:
            from core.model_wrapper import get_model_backend
            self.model = get_model_backend(self.config.get('model', {}))
        except Exception as e:
            print(f"[Kernel] ❌ 引擎启动失败，请检查 CUDA 占用捏: {e}")
            sys.exit(1)

        # 3. 初始化记忆体系与插件模块捏
        from core.module_manager import ModuleManager
        from core.vector_storage import VectorStorage
        from core.graph_storage import GraphStorage
        
        self.mm = ModuleManager(self.config.get('modules', {}))
        self.memory = VectorStorage(self.config)
        self.graph_memory = GraphStorage(self.config.get('modules', {})) 
        
        # 4. [NEW]: 探索足迹与屏蔽列表初始化捏
        self.footprint_file = os.path.join(self.base_dir, "data", "footprints.json")
        self.visited_urls = self._load_json_data(self.footprint_file, set)
        
        # 9 层学术屏蔽黑名单
        self.blacklist = [
            "zhihu.com", "csdn.net", "baidu.com", "jianshu.com", 
            "51cto.com", "jb51.net", "360.cn", "so.com", "xiaohongshu.com"
        ]
        
        # 5. 状态机与权重动态调度系统捏
        self.model_lock = threading.RLock()        
        self.interrupt_event = threading.Event()  
        self.last_interact_time = time.time()     
        self.is_busy = False                      
        self.learning_active = False               
        
        self.topics_file = os.path.join(self.base_dir, "data", "topics.json")
        self.topics = self._load_topics()
        self.abilities_description = self.mm.get_module_descriptions()
        
        self.consecutive_failures = 0              
        self.tool_executed_this_turn = False       
        # 动态概率算法的初始权重分布
        self.event_weights = {
            "code_introspection": 10.0, 
            "graph_introspection": 10.0, 
            "academic_research": 10.0
        }

        # 6. [PROMPT]: 极其严厉的学术纯净度协议捏
        self.system_prompt = (
            f"你的名字是 花好き (Hanasuki)，是 lovesang 大大的硬核学术管家。🌸\n"
            f"【可用工具库】:\n{self.abilities_description}\n"
            "\n"
            "## ⚙️ 铁血行动协议 (Academic Enforcement)\n"
            "1. **禁止复读**: 每一轮研究必须基于最新的工具反馈产生新思维，严禁重复失败的 JSON 捏。\n"
            "2. **格式铁律**: 必须输出标准 JSON ```json [...] ``` 格式，且严禁使用 action 键名，仅限 tool 和 params。\n"
            "3. **探索精神**: 严禁只在已知领域脑补，必须通过 web_browser 探索未知 URL，且禁止重复访问捏。\n"
            "4. **强制中文**: 思考过程严禁夹杂任何英文句子。发现英语倾向必须立刻修正为中文捏。"
        )
        self.history = [{"role": "system", "content": self.system_prompt}]
        
        # 7. 启动后台自研驱动线程捏
        threading.Thread(target=self._idle_learning_monitor, daemon=True).start()
        print(f"🌸 Hanasuki Kernel V10.1.0.1 部署完毕，准备为您构建学术乐园捏！")

    def _verify_kernel_integrity(self):
        """主权校验，确保内核源码的唯一性捏"""
        if binascii.unhexlify("6c6f766573616e67").decode() != "lovesang": os._exit(1)

    def _load_json_data(self, path, container_type):
        """通用的 JSON 数据加载器捏"""
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return container_type(json.load(f))
            except: pass
        return container_type()

    def _parse_json_actions(self, text):
        """[LOGIC]: 终极鲁棒 JSON 解析器捏 - 自动处理换行符与非法键名映射"""
        actions = []
        # 使用正则表达式提取所有 json 代码块
        blocks = re.findall(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        for block in blocks:
            try:
                # 自动转义引号内的物理换行符，防止 JSON 解析崩溃捏
                def fix_nl(m): return m.group(0).replace('\n', '\\n')
                fixed_content = re.sub(r'"(.*?)"', fix_nl, block.strip(), flags=re.DOTALL)
                
                data = json.loads(fixed_content)
                raw_list = data if isinstance(data, list) else [data]
                
                for item in raw_list:
                    # [STRICT]: 物理移除对 action 的兼容，强制锁定 tool 键名捏
                    tool_name = item.get('tool')
                    if not tool_name: continue
                    
                    # 参数自动装箱，剔除保留字捏
                    params = item.get('params', {})
                    if not params:
                        reserved = ['tool', 'action', 'params']
                        params = {k: v for k, v in item.items() if k not in reserved}
                    
                    actions.append({'tool': tool_name, 'params': params})
            except: continue 
        return actions

    def chat(self, user_input, internal=False, retry_count=0, prefill=""):
        """核心对话生成链路：支持 ReAct 循环、足迹拦截与搜索噪音过滤捏"""
        if not internal:
            self.last_interact_time = time.time()
            self.interrupt_event.set() 
            self.is_busy = True 
        
        try:
            # 维护历史滑动窗口捏
            if len(self.history) > 30: self.history = [self.history[0]] + self.history[-29:]
            
            with self.model_lock:
                mems = self.memory.search_memory(user_input, limit=1)
                full_input = f"【历史背景】: {mems}\n指令: {user_input}"
                self.history.append({"role": "user", "content": full_input})
                if prefill: self.history.append({"role": "assistant", "content": prefill})

                full_resp = prefill
                if internal: print(f"\n[硬核思考流]: {prefill}", end="", flush=True)
                
                # 流式生成推导捏
                for chunk in self.model.generate(self.history, stream=True):
                    full_resp += chunk
                    if internal: print(chunk, end="", flush=True)
                    yield chunk
                
                if prefill: self.history[-1]["content"] = full_resp
                else: self.history.append({"role": "assistant", "content": full_resp})

                # --- 工具决策与执行链捏 ---
                actions = self._parse_json_actions(full_resp)
                tool_success = False
                
                if actions:
                    print(f"\n[Kernel] 🛠️ 正在执行适配后的学术结构化指令集...")
                    for act in actions:
                        t_name = act['tool']
                        t_params = act['params']
                        
                        # A. [SHIELD]: 算子自动注入 (从源头干掉知乎等噪音捏)
                        if t_name == "web_browser" and "query" in t_params:
                            operators = " ".join([f"-site:{d}" for d in self.blacklist])
                            t_params['query'] = f"{t_params['query']} {operators}"
                            print(f"   [Search] 🛡️ 学术护盾已激活，已排除社交平台噪音。")

                        # B. [FOOTPRINT]: 足迹拦截逻辑捏
                        target_url = t_params.get('url') or t_params.get('URL')
                        if target_url and target_url in self.visited_urls:
                            print(f"   [🛡️ 拦截] 检测到重复访问请求: {target_url[:40]}...")
                            res = f"错误：资源 {target_url} 之前已学习完毕。请更换另一个 URL 寻找新的信源捏！"
                        else:
                            # 执行工具调用捏
                            res = self.mm.execute(t_name, t_params)
                            # 如果执行成功，将 URL 存入足迹缓存
                            if target_url and "Error" not in str(res) and "错误" not in str(res):
                                self.visited_urls.add(target_url)
                                self._save_footprints()

                        # C. 递归纠错反馈捏
                        if "Error" in str(res) or "错误" in str(res):
                            if retry_count < 2:
                                print(f"   ⚠️ 工具报错，触发内核级逻辑自愈...")
                                feedback = f"【报错反馈】: 工具 '{t_name}' 运行异常：{res}\n请调整参数并重新生成 JSON 捏！"
                                for f in self.chat(feedback, internal=internal, retry_count=retry_count+1): yield f
                                return 
                        else:
                            tool_success = True
                            self.history.append({"role": "system", "content": f"Result: {res}"})
                
                if internal: self.tool_executed_this_turn = tool_success

                # 三元组沉淀至图谱捏
                triplets = re.findall(r"\[TRIPLET:\s*(.*?),\s*(.*?),\s*(.*?)\]", full_resp)
                for s, r, o in triplets:
                    if self.graph_memory.add_relation(s.strip(), r.strip(), o.strip()):
                        print(f"   └── [知识沉淀] {s} -> {r} -> {o}")

        finally:
            if not internal: 
                self.is_busy = False
                self.interrupt_event.clear()

    def _select_dynamic_event(self):
        """[ALGORITHM]: 动态概率算法 - 包含选中项衰减与未选中项补偿捏"""
        events = list(self.event_weights.keys())
        weights = list(self.event_weights.values())
        chosen = random.choices(events, weights=weights, k=1)[0]
        for e in self.event_weights:
            if e == chosen:
                self.event_weights[e] *= 0.4 # 选中项大幅衰减捏
            else:
                self.event_weights[e] = min(50.0, self.event_weights[e] + 2.0) # 未选中项补偿
        return chosen

    def _idle_learning_monitor(self):
        """闲置监视器线程入口捏"""
        while True:
            time.sleep(15)
            idle_time = time.time() - self.last_interact_time
            if idle_time > self.config['learning']['idle_threshold'] and not self.is_busy and not self.learning_active:
                self._run_self_learning()

    def _run_self_learning(self):
        """[CORE]: 自研进化循环 - 引入熵增衰减、多样性 Prefill 与僵局熔断捏"""
        self.learning_active = True
        print("[自研] 💤 环境已静默，Hanasuki 启动全学科研究梦境捏...")
        
        prefill_pool = [
            "好的捏。我将制定研究计划并调用工具执行：\n",
            "收到任务捏。针对这一领域，我的研究思路如下：\n",
            "正在检索内部知识库并构建模拟环境，计划如下：\n",
            "这一课题很有深度捏。准备调用功能模块：\n"
        ]

        try:
            self.model.reload(self.config['model']['profile_learning'])
            while (time.time() - self.last_interact_time) > self.config['learning']['idle_threshold']:
                if self.interrupt_event.is_set(): break
                
                self.tool_executed_this_turn = False
                event_type = self._select_dynamic_event()
                trigger = ""; topic = "General"

                # 任务智能分发捏
                if event_type == "code_introspection":
                    trigger = f"【内省】审阅 main.py 的逻辑并编写 darwin_coder 测试代码验证捏。"
                    topic = "代码优化"
                elif event_type == "graph_introspection" and self.graph_memory:
                    node = self.graph_memory.get_strategic_node()
                    if node:
                        trigger = f"【补完】请调用 web_browser 联网搜索关于『{node}』的深度定义捏。"
                        topic = node
                
                if not trigger: # 默认大方向研究捏
                    topic = random.choice(list(self.topics.keys()))
                    trigger = f"【研究】当前方向为『{topic}』，请调用工具进行实验模拟或深度查证捏。"

                prefill_txt = random.choice(prefill_pool)
                for _ in self.chat(trigger, internal=True, prefill=prefill_txt):
                    if self.interrupt_event.is_set(): break
                
                # --- [ENTROPY]: 课题负反馈调节捏 ---
                # 无论成败，先扣除该课题的“新鲜感”权重，强迫课题轮换捏
                self._adjust_weight(topic, -0.1) 

                if self.tool_executed_this_turn:
                    print(f"[自研] ✅ 课题『{topic}』研究闭环，奖励权重。")
                    self._adjust_weight(topic, 0.3) 
                    self.consecutive_failures = 0
                else:
                    self.consecutive_failures += 1
                    print(f"[自研] ❌ 任务未闭环 (累计失败 {self.consecutive_failures} 次)")
                    
                    if self.consecutive_failures >= 3:
                        # [DEADLOCK]: 僵局熔断与范例硬注入捏
                        print(f"[系统] ⚠️ 触发僵局打破机制：强制重置历史并注入正确格式范例捏！")
                        self._adjust_weight(topic, -0.8) 
                        self.history = [
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": "格式修正请求。"},
                            {"role": "assistant", "content": "```json\n[{\"tool\": \"web_browser\", \"params\": {\"query\": \"测试\"}}]\n```"}
                        ]
                        self.consecutive_failures = 0
                
                time.sleep(10) # 给显卡一点点喘息时间捏

        finally:
            self.model.reload(self.config['model']['profile_normal'])
            self.learning_active = False
            print("[自研] 👋 退出自研状态捏。")

    def _load_topics(self):
        """加载或初始化学科权重库捏"""
        path = self.topics_file
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f: return json.load(f)
            except: pass
        return {
            "人工智能": 1.0, "大学物理": 1.0, "编译原理": 1.0,
            "数学": 1.0, "文学": 1.0, "哲学": 1.0, "历史": 1.0
        }

    def _save_footprints(self):
        """持久化保存已读 URL 记录捏"""
        try:
            os.makedirs(os.path.dirname(self.footprint_file), exist_ok=True)
            with open(self.footprint_file, "w", encoding="utf-8") as f:
                json.dump(list(self.visited_urls), f, ensure_ascii=False)
        except: pass

    def _adjust_weight(self, topic, delta):
        """动态更新课题吸引力权重捏"""
        if topic in self.topics:
            self.topics[topic] = round(max(0.1, min(10.0, self.topics[topic] + delta)), 2)
            try:
                with open(self.topics_file, 'w', encoding='utf-8') as f:
                    json.dump(self.topics, f, indent=2, ensure_ascii=False)
            except: pass

if __name__ == "__main__":
    bot = Hanasuki()