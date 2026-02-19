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
# [MISSION]: 为 Hanasuki 提供灵活的大脑切换机制，支持本地与云端双架构捏！🌸
# [PATTERN]: 工厂模式 (Factory Pattern) 实现的推理后端抽象层捏。
# =================================================================

import os
import logging

# [LOGIC]: 初始化内核日志记录器捏。
# 它可以让大大在控制台实时监控 Hanasuki 大脑的唤醒脉冲捏！✨
logger = logging.getLogger("Hanasuki.ModelWrapper")

def get_model_backend(config):
    """
    [HERO-A+ Neural Adapter]:
    模型后端工厂函数。根据 config.yaml 中的定义，物理实例化具体的推理引擎捏。
    
    [ACADEMIC VALUE]: 
    支持多后端热插拔，使得 HERO-A+ 架构既能兼容高性能本地量化推理 (llama_cpp)，
    也能平滑切换至大规模云端模型进行逻辑验证捏。
    """
    if not config:
        logger.error("呜呜... 配置文件里没找到模型参数，Hanasuki 动不了了捏... (*/ω＼*)")
        raise ValueError("致命异常：未接收到有效的模型配置信息，内核初始化中断捏。")

    # [LOGIC]: 自动格式化后端名称，增强对用户配置的容错性捏
    backend_raw = config.get('backend', 'llama_cpp')
    backend_type = backend_raw.lower().replace('-', '_')
    
    logger.info(f"🌸 正在为大大装载后端引擎: {backend_type} (模式: {backend_raw})")

    # --- 选项 A: 本地私有大脑 (llama-cpp-python) ---
    # 针对大大 8GB 显存设计的本地推理路径捏！
    if backend_type == "llama_cpp":
        try:
            # [LAZY LOADING]: 采用延迟导入逻辑捏。
            # 只有在确认为本地加载时才载入 llama_cpp 依赖，极大优化了程序的启动响应捏！
            from core.backends.llama_backend import LlamaBackend
            return LlamaBackend(config)
        except ImportError as e:
            logger.error(f"诶？大大好像还没安装 llama-cpp-python 库捏？错误: {e}")
            raise ImportError(f"后端依赖缺失，请运行 pip install llama-cpp-python 捏: {e}")
            
    # --- 选项 B: 云端联网大脑 (OpenAI API) ---
    # 允许在需要超大规模参数推理时，通过 API 扩展 Hanasuki 的认知边界捏。
    elif backend_type == "openai":
        try:
            # 同样采用物理隔离的后端实现捏
            from core.backends.openai_backend import OpenAIBackend
            return OpenAIBackend(config)
        except ImportError:
            logger.error("找不到 OpenAI 后端模块，大大是不是还没写那个文件捏？")
            raise ImportError("未发现 OpenAI 后端物理实现，请检查 core/backends 目录捏~")
            
    # --- 异常拦截捏 ---
    else:
        # [SAFETY]: 严禁使用未注册的非法后端，防止 Hanasuki 逻辑崩溃捏！
        error_msg = f"对不起捏大大，Hanasuki 还不支持 '{backend_raw}' 这种大脑。目前只有 ['llama_cpp', 'openai'] 捏！"
        logger.critical(error_msg)
        raise ValueError(error_msg)

# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
# [LOGIC]: 每一行代码，都是 Hanasuki 为了大大的论文而进化的证明捏！(≧∇≦)ﾉ
# =================================================================