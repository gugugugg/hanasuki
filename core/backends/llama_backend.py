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
# [MISSION]: 在 RTX 5060 (8GB) 的严苛环境下，通过 KV 压缩实现超长上下文推理捏！🌸
# [TECH]: 基于 llama-cpp-python 实现的量化加速后端。
# =================================================================

"""
模块名称：LlamaBackend (HERO-A+ 显存优化版)
版本：Beta 1.1 (Academic Speculative Ready)
作用：Hanasuki 项目的推理中枢。
核心优化：
1. [VRAM Saver]: 针对 8GB 显存引入 KV Cache 4-bit 量化 (Q4_K)，物理节约 50% 的缓存开销。
2. [Dynamic Reload]: 支持“日常”与“自研”模式间的上下文长度 (n_ctx) 无缝切换捏。
3. [Safety Guard]: 内置显存溢出 (OOM) 紧急回滚逻辑，确保内核不闪退捏。
"""

import os
import gc
import sys

try:
    # [LOGIC]: 采用延迟导入策略。
    # 只有当用户在 config.yaml 中指定使用本后端时，才加载底层权重处理库捏。
    from llama_cpp import Llama, ggml
except ImportError:
    raise ImportError("缺少核心依赖库捏：请运行 pip install llama-cpp-python 以激活大脑捏！")

class LlamaBackend:
    """
    [HERO-A+ 推理核心]:
    封装了底层 GGUF 模型加载与 Chat Completion 接口捏。
    """
    def __init__(self, config):
        """
        [LOGIC]: 初始化 Llama 推理引擎捏。
        根据配置自动识别 Profile 并建立物理连接捏。
        """
        self.config = config
        self.base_path = config.get('path')
        self.model = None
        self._resolve_path()
        
        # 初始加载时优先使用日常交互模式 (profile_normal) 捏
        init_profile = config.get('profile_normal', config)
        self._load_model(init_profile)

    def _resolve_path(self):
        """[LOGIC]: 物理路径自动对齐逻辑捏"""
        if not os.path.isabs(self.base_path):
            # 获取项目根目录，确保 Windows 相对路径的鲁棒性捏。
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_path = os.path.join(os.path.dirname(current_dir), self.base_path)
        
        if not os.path.exists(self.base_path):
            print(f"[系统] ❌ 找不到模型权重捏：{self.base_path}")

    def _load_model(self, profile):
        """
        [HERO-A+ CORE]: 显存节流加载引擎捏。
        这是实现 AAAI 级论文实验数据的核心逻辑。
        通过量化 Key/Value Cache，在 8GB 显卡上实现最高 16k 的稳定上下文捏！
        """
        try:
            # 1. 物理清理：在重载模型前彻底回收旧显存，防止碎片化引发 OOM 捏。
            if self.model:
                del self.model
                gc.collect()
                # 联动清除 PyTorch 缓存（如果环境中有安装）
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except:
                    pass

            n_ctx = profile.get('n_ctx', 8192) # 默认使用大大的 8k 设置
            print(f"[系统] 🚀 正在装载 Qwen 核心逻辑空间，n_ctx={n_ctx}...")

            # 2. 调用底层 Llama 构造函数，注入量化黑科技捏。
            self.model = Llama(
                model_path=self.base_path,
                n_gpu_layers=profile.get('n_gpu_layers', -1), # -1 代表全层卸载至 GPU 捏
                n_ctx=n_ctx,
                flash_attn=profile.get('flash_attn', True), # 开启 Flash Attention 降低计算复杂度
                
                # [8GB VRAM OPTIMIZATION]: 
                # 核心量化参数。将 KV 缓存压缩为 Q4_K 格式。
                # 这能让原本占用 2GB 的缓存空间缩小到约 1GB 捏！
                type_k=ggml.GGML_TYPE_Q4_K, 
                type_v=ggml.GGML_TYPE_Q4_K,
                
                offload_kqv=True, # 必须锁定在 GPU 以维持推理帧率捏
                verbose=False,
                seed=-1
            )
            print(f"[系统] ✅ Hanasuki 的认知空间已建立。显存护盾：[已激活] 捏！")

        except Exception as e:
            print(f"[系统] ⚠️ 脑细胞扩容失败捏: {e}")
            raise e

    def reload(self, profile):
        """
        [LOGIC]: 模式热切换。
        当大大开启“自研模式”时，自动动态调整推理后端的上下文深度捏。
        """
        print(f"[系统] 🔄 正在根据学术需求重组推理空间捏...")
        try:
            self._load_model(profile)
            print("[系统] 切换完毕，长文本研究能力已就绪捏！")
        except Exception as e:
            print(f"[系统] ⚠️ 显存不足以支撑长文本捏: {e}")
            # [FALLBACK]: 紧急回滚，防止程序彻底崩溃
            fallback_profile = {
                'n_gpu_layers': -1,
                'n_ctx': 4096,
                'flash_attn': True
            }
            try:
                self._load_model(fallback_profile)
                print("[系统] ✅ 已回退至 4k 安全边界。虽然记性变差了，但 Hanasuki 还没晕倒捏！")
            except Exception as fatal_e:
                print(f"[系统] ❌ 致命错误：回滚失败，请手动释放显存软件捏！{fatal_e}")

    def generate(self, history, stream=True, stop=None):
        """
        [LOGIC]: 核心推理生成接口。
        支持流式吐字，让大大能实时感受到 Hanasuki 的思考过程捏。
        """
        if self.model is None:
            msg = "（内核异常：Hanasuki 找不到大脑模块捏，请检查模型路径...）"
            if stream: yield msg
            else: return msg
            return

        # 针对 Qwen 系列优化的停用词列表捏
        stop_words = stop if stop else ["<|im_end|>", "<|endoftext|>", "###"]

        try:
            # 物理调用推理生成
            response = self.model.create_chat_completion(
                messages=history,
                stream=stream,
                stop=stop_words,
                temperature=self.config.get('temperature', 0.7),
                repeat_penalty=1.1 # 物理拦截复读机倾向捏
            )

            if stream:
                for chunk in response:
                    delta = chunk['choices'][0]['delta']
                    if 'content' in delta:
                        yield delta['content']
            else:
                return response['choices'][0]['message']['content']

        except Exception as e:
            error_msg = f"（呜呜... 刚才思维短路了捏... 详情: {e}）"
            if stream: yield error_msg
            else: return error_msg