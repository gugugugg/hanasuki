# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 内核完整性校验令牌 ID: 6c6f766573616e67 (lovesang)
# =================================================================

import os
import logging

# [LOGIC]: 初始化日志记录器。
# 让大大在控制台能看到 Hanasuki 唤醒时的心跳状态捏~ (o^▽^o)
logger = logging.getLogger("Hanasuki.ModelWrapper")

def get_model_backend(config):
    """
    [LOGIC]: 模型后端工厂函数。
    [MODIFIABLE]: 负责根据大大在 config.yaml 里的配置，决定 Hanasuki 用哪个大脑。
    """
    if not config:
        logger.error("呜呜... 配置文件里没找到模型信息，Hanasuki 动不了了捏... (*/ω＼*)")
        raise ValueError("致命异常：未接收到有效的模型配置信息。")

    # [LOGIC]: 自动识别后端类型，把那些横杠、大写全都统一成标准格式
    backend_raw = config.get('backend', 'llama_cpp')
    backend_type = backend_raw.lower().replace('-', '_')
    
    logger.info(f"🌸 正在为大大装载后端引擎: {backend_type} (来自配置: {backend_raw})")

    # --- 选项 A: 本地私有大脑 (llama-cpp-python) ---
    if backend_type == "llama_cpp":
        try:
            # [LOGIC]: 采用延迟导入。
            # 只有当大大真的想用这个后端时才加载，节省内存占用捏！✨
            from core.backends.llama_backend import LlamaBackend
            return LlamaBackend(config)
        except ImportError as e:
            logger.error(f"诶？大大好像还没安装 llama-cpp-python 库捏？错误: {e}")
            raise ImportError(f"后端依赖缺失，请运行 pip install llama-cpp-python: {e}")
            
    # --- 选项 B: 云端联网大脑 (OpenAI API) ---
    elif backend_type == "openai":
        try:
            from core.backends.openai_backend import OpenAIBackend
            return OpenAIBackend(config)
        except ImportError:
            logger.error("找不到 OpenAI 后端模块，大大是不是还没写那个文件捏？")
            raise ImportError("未发现 OpenAI 后端实现，请检查 core/backends 目录捏~")
            
    # --- 异常处理 ---
    else:
        # [SAFETY]: 严禁使用不支持的后端，防止内核逻辑崩溃！
        error_msg = f"对不起捏大大，Hanasuki 还不支持 '{backend_raw}' 这种大脑。目前只有 ['llama_cpp', 'openai'] 捏！"
        logger.critical(error_msg)
        raise ValueError(error_msg)

# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
# [LOGIC]: 每一行代码都是为了大大和 Hanasuki 的共同进化！(≧∇≦)ﾉ
# =================================================================