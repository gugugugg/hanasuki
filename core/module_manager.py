# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# You may obtain a copy of the License at: https://www.gnu.org/licenses/gpl-3.0.html
#
# [SAFETY]: 内核完整性校验令牌 ID: 6c6f766573616e67 (lovesang)
# =================================================================

import os
import importlib.util
import traceback

class ModuleManager:
    def __init__(self, config):
        """
        Hanasuki 模块管理器 V3.0 (多 UI 挂载版)
        职责：
        1. 动态加载底层功能功能（Tools），供 LLM 推理调用。
        2. 自动识别并区分主/副 UI 模块，支持侧边栏扩展。
        """
        # [MODIFIABLE]: 插件默认存放路径
        self.modules_dir = config.get('directory', 'modules')
        
        # 存储区初始化
        self.modules = {}      # 存储功能性模块 (具有 run 函数)
        self.main_ui = None    # 存储唯一的主界面
        self.sub_uis = []      # 存储所有的副界面/侧边栏插件
        
        self.load_modules()

    def load_modules(self):
        """
        [LOGIC]: 扫描目录并动态分类加载所有 .py 模块。
        支持热重载：每次调用时都会清空现有列表重新扫描。
        """
        if not os.path.exists(self.modules_dir):
            os.makedirs(self.modules_dir)
            
        # 重置当前状态
        self.modules = {}
        self.main_ui = None
        self.sub_uis = []
            
        for file in os.listdir(self.modules_dir):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                path = os.path.join(self.modules_dir, file)
                
                try:
                    # [LOGIC]: 利用 importlib 动态反射加载 Python 脚本
                    spec = importlib.util.spec_from_file_location(module_name, path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    # 1. 提取元数据 (get_spec)
                    spec_func = getattr(mod, "get_spec", None)
                    module_spec = spec_func() if spec_func else {"type": "utility"}
                    module_type = module_spec.get("type", "utility")

                    # 2. [LOGIC]: UI 插件多级挂载逻辑
                    if module_type == "ui_extension" and hasattr(mod, "get_ui_entry"):
                        ui_data = {
                            "name": module_name,
                            "instance": mod,
                            "entry": getattr(mod, "get_ui_entry"),
                            "spec": module_spec
                        }
                        
                        # [MODIFIABLE]: 判定规则——如果 spec 明确标注 is_main 为 True，且当前没主 UI
                        # 则将其设为主界面；否则全部塞进副界面列表
                        is_main = module_spec.get("is_main", False)
                        
                        if is_main and self.main_ui is None:
                            self.main_ui = ui_data
                            print(f"[UI] ✅ 主界面模块 '{module_name}' 已挂载。")
                        else:
                            self.sub_uis.append(ui_data)
                            print(f"[UI] 📎 副界面插件 '{module_name}' 已加入侧边栏列表。")

                    # 3. 功能模块处理 (Tools)
                    if hasattr(mod, "run"):
                        self.modules[module_name] = {
                            "instance": mod,
                            "spec": module_spec,
                            "entry": getattr(mod, "run")
                        }
                        # 仅在非 UI 模块加载时打印工具信息
                        if module_type != "ui_extension":
                            print(f"[Tool] 🛠️ 功能模块 '{module_name}' 加载就绪。")

                except Exception as e:
                    print(f"[!] 模块 {module_name} 加载异常: {e}")
                    
        # [SAFETY]: 鲁棒性检查——如果所有 UI 都没有标 is_main，则强行指定第一个 UI 插件为主界面
        if self.main_ui is None and self.sub_uis:
            self.main_ui = self.sub_uis.pop(0)
            print(f"[UI] ⚠️ 未发现明确的主界面标识，已自动提升 '{self.main_ui['name']}' 为主界面。")

    def get_module_descriptions(self):
        """
        [LOGIC]: 提取功能工具的描述文本，供 LLM 的 System Prompt 使用。
        排除所有 UI 插件，防止 AI 生成界面代码导致冗余。
        """
        desc_list = []
        for name, info in self.modules.items():
            if info['spec'].get("type") != "ui_extension":
                desc_list.append(f"- {name}: {info['spec'].get('description')}")
        return "\n".join(desc_list)

    def execute(self, module_name, params):
        """
        [LOGIC]: 动态执行 LLM 请求的功能函数。
        [SAFETY]: 捕获所有执行异常，返回给 LLM 进行自我修正。
        """
        if module_name not in self.modules:
            return f"错误：未找到功能模块 '{module_name}'"
        try:
            return self.modules[module_name]['entry'](params)
        except Exception:
            return f"模块执行崩溃: {traceback.format_exc()}"

    def get_ui_manifest(self):
        """
        [LOGIC]: 为 app_gui 宿主提供所有已识别界面的清单。
        Returns: (main_ui_dict, sub_uis_list)
        """
        return self.main_ui, self.sub_uis