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
# [MISSION]: 作为内核的神经突触，管理所有工具与 UI 插件的生命周期捏！🌸
# [ARCHITECTURE]: 基于 HERO-A+ 协议的动态反射加载引擎。
# =================================================================

import os
import json
import importlib.util
import traceback

class ModuleManager:
    """
    [HERO-A+ 协议管理器]:
    负责扫描、加载并执行所有符合规范的 Python 模块。
    支持原子级工具调用 (Tools) 与 视觉扩展组件 (UI Extensions) 的物理隔离捏。
    """
    def __init__(self, config):
        """
        [LOGIC]: 初始化管理器并自动同步插件目录捏。
        """
        # 从配置中动态获取插件存放目录，默认路径为项目根目录下的 'modules' 捏。
        self.modules_dir = config.get('directory', 'modules')
        self.modules = {}      
        self.load_modules()

    def load_modules(self):
        """
        [DYNAMIC REFLECTION]: 深度扫描模块目录捏。
        采用 importlib 动态反射技术，确保每一个工具模块在加载时与内核逻辑物理隔离捏。
        """
        if not os.path.exists(self.modules_dir): 
            os.makedirs(self.modules_dir, exist_ok=True)
            return
        
        for f in os.listdir(self.modules_dir):
            # 过滤非 Python 文件及私有属性文件捏
            if f.endswith(".py") and not f.startswith("__"):
                module_name = f[:-3]
                try:
                    # 1. 动态构建模块规范并装载文件
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(self.modules_dir, f))
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    # 2. 检查模块是否遵守 HERO 协议（必须具备 get_spec 接口）
                    if hasattr(mod, "get_spec"):
                        m_spec = mod.get_spec()
                        # 存储元数据、执行入口及模块对象，以便后续动态提取 UI 接口捏
                        self.modules[module_name] = {
                            "spec": m_spec, 
                            "run": getattr(mod, "run", None),
                            "module_obj": mod
                        }
                        print(f"[HERO-Tool] 🛠️ {module_name} 模块协议挂载成功捏！")
                except Exception as e:
                    print(f"[!] 模块 {module_name} 初始化时遭遇逻辑坍塌捏: {e}")

    def get_ui_manifest(self):
        """
        [UI ADAPTER]: 为 app_gui.py 提供视觉组件清单。
        物理识别 UI 类型的插件，并将其分类为“核心交互区”或“功能侧边栏”捏。
        """
        main_ui_spec = None
        sub_uis_list = []
        
        for name, info in self.modules.items():
            spec = info['spec']
            # 筛选 UI 扩展协议类型
            if spec.get('type') == 'ui_extension':
                # 兼容性设计：支持 get_ui_entry 或 entry 两种入口命名规范捏
                entry_func = getattr(info['module_obj'], "get_ui_entry", None) or \
                             getattr(info['module_obj'], "entry", None)
                
                ui_data = {"name": name, "entry": entry_func}
                
                # 区分主次 UI，用于 app_gui 的垂直/水平布局分发捏
                if spec.get('is_main'):
                    main_ui_spec = ui_data
                else:
                    sub_uis_list.append(ui_data)
        
        return main_ui_spec, sub_uis_list

    def get_module_descriptions(self):
        """
        [RELIGN PROTOCOL]: 为大模型构建“感知边界”捏。
        将所有可用工具转化为结构化文本，并注入强有力的 Relign 负向约束。
        公式可简化为：$Prompt_{tools} = \sum (Desc + Params) + Constraint_{hallucination}$。
        """
        desc_list = []
        for name, info in self.modules.items():
            spec = info['spec']
            # 物理隔离：禁止向模型暴露 UI 插件，防止产生“操作界面”的幻觉捏
            if spec.get('type') == 'ui_extension': continue
                
            desc = f"- {name}: {spec.get('description')}"
            params = json.dumps(spec.get('parameters', {}), ensure_ascii=False)
            
            # [PROMPT HACK]: 注入硬核约束。
            # 强制要求 8B 模型在参数不确定时“认怂”调用 clarify，而非脑补捏！
            constraint = " (注意捏：若具体参数不明，严禁强行编造，必须调用 clarify 进行核实捏)"
            desc_list.append(f"{desc}\n  参数规范: {params}{constraint}")
            
        return "\n".join(desc_list)

    def execute(self, module_name, params):
        """
        [LOGIC]: 具身化工具执行入口。
        封装了工具调用的异常捕获机制，确保单个插件崩溃不会拖垮整个内核捏。
        """
        if module_name not in self.modules or not self.modules[module_name]["run"]:
            return f"错误捏：管家找不到名为 '{module_name}' 的物理工具。"
        try:
            # 物理调用工具模块的 run 接口并返回学术反馈捏
            return self.modules[module_name]["run"](params)
        except Exception as e:
            # 捕获并追踪完整的工具链崩溃堆栈捏
            return f"工具执行链条意外断裂捏... 详情: {e}\n{traceback.format_exc()}"