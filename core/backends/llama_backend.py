# -*- coding: utf-8 -*-
# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 内核完整性校验令牌 ID: 6c6f766573616e67 (lovesang)
# =================================================================

"""
模块名称：LlamaBackend (推理引擎核心)
作用：Hanasuki 项目的推理中枢，支持 GGUF 模型加载与动态配置热切换捏。
[FIX]: 增加了显存溢出 (OOM) 时的自动降级回滚机制。
"""

try:
    # [LOGIC]: 采用延迟导入，只有在后端被激活时才加载底层库
    from llama_cpp import Llama
except ImportError:
    raise ImportError("缺少依赖库: 请运行 pip install llama-cpp-python")

import os
import gc 

class LlamaBackend:
    def __init__(self, config):
        """
        [LOGIC]: 初始化 Llama 推理引擎。
        [MODIFIABLE]: 默认优先加载 config.yaml 中的 profile_normal 配置捏。
        """
        self.base_path = config.get('path')
        self._resolve_path()
        
        # 初始加载日常模式
        init_profile = config.get('profile_normal', config)
        self._load_model(init_profile)

    def _resolve_path(self):
        """
        [LOGIC]: 路径增强处理。
        [SAFETY]: 自动检测模型文件是否存在，支持绝对路径与项目相对路径的智能转换。
        """
        if not os.path.exists(self.base_path):
            # 尝试从当前脚本的上三级目录定位项目根目录捏
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            abs_path = os.path.join(base_dir, self.base_path)
            if os.path.exists(abs_path):
                self.base_path = abs_path
            else:
                raise FileNotFoundError(f"找不到模型文件捏: {self.base_path}")

    def _load_model(self, profile):
        """
        [LOGIC]: 底层加载逻辑，负责分配显存层数与上下文窗口捏。
        """
        print(f"[*] 正在为大大加载模型 (Layers: {profile.get('n_gpu_layers')}, Ctx: {profile.get('n_ctx')})...")
        
        self.model = Llama(
            model_path=self.base_path,
            n_gpu_layers=profile.get('n_gpu_layers', -1),
            n_ctx=profile.get('n_ctx', 4096),
            verbose=False # 保持控制台清爽捏
        )

    def reload(self, profile):
        """
        [LOGIC]: ⚡ 核心黑科技：思维模式热切换 (Hot-Swap) [带防崩保护]。
        """
        print("\n[系统] 正在为大大执行思维模式热切换 (Hot-Swap)...")
        
        # 1. [SAFETY]: 显式销毁旧的模型对象
        if hasattr(self, 'model'):
            del self.model
            self.model = None # 显式置空，切断引用
        
        # 2. [LOGIC]: 强制垃圾回收，整理显存碎片
        gc.collect()
        
        # 3. [CRITICAL FIX]: 尝试加载新配置，带 OOM 降级保护
        try:
            self._load_model(profile)
            print("[系统] 切换完毕，新模式已就绪捏！")
        except Exception as e:
            print(f"[系统] ⚠️ 显存不足或碎片化严重，切换失败: {e}")
            print("[系统] 正在紧急回滚至安全模式 (4k Context)...")
            
            # [SAFETY]: 构造降级配置 (强制 4096 上下文)
            fallback_profile = {
                'n_gpu_layers': profile.get('n_gpu_layers', -1),
                'n_ctx': 4096 
            }
            
            try:
                self._load_model(fallback_profile)
                print("[系统] ✅ 回滚成功，内核已恢复生命体征。")
            except Exception as fatal_e:
                print(f"[系统] ❌ 致命错误：回滚也失败了。请检查显存占用！{fatal_e}")
                # 这里不抛出异常，防止主线程崩溃，只是模型不可用

    def generate(self, history, stream=True, stop=None):
        """
        [LOGIC]: 对话生成入口捏。
        """
        # [SAFETY]: 防止模型在 reload 失败变为 None 后被调用导致崩溃
        if self.model is None:
            if stream:
                yield "（内核错误：模型未正确加载，请检查后台日志捏...）"
            else:
                return "（内核错误：模型未正确加载，请检查后台日志捏...）"
            return

        response = self.model.create_chat_completion(
            messages=history,
            temperature=0.7,
            stream=stream,
            stop=stop 
        )
        
        if stream:
            for chunk in response:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    yield delta['content']
        else:
            yield response['choices'][0]['message']['content']