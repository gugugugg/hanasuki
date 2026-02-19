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
# [MISSION]: 为大大提供最优雅的磨砂玻璃交互体验，让科研对话充满温度捏！🌸
# [STYLE]: Glassmorphism (磨砂玻璃) 视觉风格适配。
# =================================================================

"""
模块名称：Classic Chat UI (HERO-A+ Glassmorphism Edition)
版本：Beta 1.1 (Final Connectivity Patch)
作用：Hanasuki 项目的核心对话交互界面。
核心特性：
1. 磨砂玻璃视觉：深度适配宿主窗口的半透明特效，实现视觉一体化捏。
2. 异步生成流：通过 QThread 确保在 RTX 5060 满载推理时 UI 依然丝滑不卡顿捏。
3. 进化建议渲染：物理识别并美化模型吐出的自研灵感标签捏。
"""

import re
import threading
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QLineEdit, 
                             QPushButton, QHBoxLayout, QSizeGrip)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor
import os

# [LOGIC]: 尝试导入 Markdown 渲染引擎捏。
try:
    import markdown2
except ImportError:
    markdown2 = None

class ChatWorker(QThread):
    """
    [ASYNC]: 后台对话工作线程。
    逻辑：在独立线程中执行推理，防止 8B 模型生成长文本时导致 GUI 主线程阻塞捏。
    """
    chunk_ready = pyqtSignal(str) # 实时向 UI 反馈生成的文本片段捏

    def __init__(self, bot, text):
        super().__init__()
        self.bot = bot  
        self.text = text 

    def run(self):
        """[CORE]: 对接 main.py 的对话逻辑执行闭环捏。"""
        full_text = ""
        try:
            # 持续监听内核吐出的每一个思考片段捏
            for chunk in self.bot.chat(self.text):
                full_text += chunk
                self.chunk_ready.emit(full_text)
        except Exception as e:
            # 捕获内核异常（如 OOM）并反馈给大大捏
            self.chunk_ready.emit(f"呜呜...大大的内核好像闹情绪了捏: {e}")

class ClassicChatWidget(QWidget):
    """
    Hanasuki 经典对话组件。
    实现了全透明磨砂背景与精致的 Markdown 渲染逻辑捏。
    """
    def __init__(self, parent, bot):
        super().__init__(parent)
        self.bot = bot
        # [STYLE]: 显式继承宿主窗口的半透明属性，实现磨砂质感捏。
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        
    def init_ui(self):
        """[LOGIC]: 视觉布局构建，建立学术美感捏。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 5)
        layout.setSpacing(12)
        
        # 1. [DISPLAY]: 对话展示区。
        # 采用 QTextBrowser 并开启外部链接跳转，方便大大查看搜索结果捏。
        self.display = QTextBrowser()
        self.display.setOpenExternalLinks(True) 
        self.display.setStyleSheet("""
            QTextBrowser { 
                background: transparent; 
                border: none; 
                color: #D9E0EE; 
                font-size: 14px; 
                line-height: 1.6; 
                padding: 10px;
            }
        """)
        self.display.setHtml(f"<b style='color:#FFB7C5;'>[花好き]:</b> 大大，内核已就绪，我们要开始研究什么捏？🌸")
        layout.addWidget(self.display)
        
        # 2. [INPUT]: 交互输入容器。
        bottom_container = QHBoxLayout()
        bottom_container.setSpacing(10)
        
        # 圆角半透明输入框捏
        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入学术指令...")
        self.input.setStyleSheet("""
            QLineEdit { 
                background: rgba(49, 50, 68, 120); 
                border: 1px solid rgba(245, 194, 231, 30); 
                border-radius: 18px; 
                color: #CDD6F4; 
                padding: 8px 15px; 
            }
            QLineEdit:focus { border: 1px solid #FFB7C5; } 
        """)
        self.input.returnPressed.connect(self.send) # 回车即发送捏
        
        # 具身化按钮设计
        self.btn = QPushButton("发送 ✨")
        self.btn.setFixedSize(80, 36)
        self.btn.setStyleSheet("""
            QPushButton { background: #FFB7C5; color: #1E1E2E; border-radius: 18px; font-weight: bold; }
            QPushButton:hover { background: #FFC0CB; }
        """)
        self.btn.clicked.connect(self.send)
        
        bottom_container.addWidget(self.input)
        bottom_container.addWidget(self.btn)
        layout.addLayout(bottom_container)

        # 3. [DECOR]: 右下角物理缩放手柄捏。
        self.size_grip = QSizeGrip(self)
        layout.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
    def send(self):
        """[LOGIC]: 发送指令并唤醒后台推理线程捏。"""
        text = self.input.text().strip()
        if not text: return
        self.input.clear()
        
        # 展示大大发送的内容捏
        self.display.append(f"<div align='right'><b style='color:#89DCEB;'>[大大]:</b> {text}</div>")
        
        # 启动异步工作流
        self.worker = ChatWorker(self.bot, text)
        self.worker.chunk_ready.connect(self.render_markdown)
        self.worker.start()
        
    def render_markdown(self, full_text):
        """
        [LOGIC]: Markdown 实时渲染与进化建议提取。
        该函数负责将原始文本转化为带有样式的 HTML，并拦截后台逻辑标签捏。
        """
        # 1. [EVOLUTION]: 提取特殊的自进化标签
        suggestions = re.findall(r"\[NEW_MODULE_SUGGESTION:\s*(.*?)\]", full_text)
        
        # 2. [CLEANUP]: 物理屏蔽后台专用的逻辑标签，保持大大视野的纯净捏
        clean_text = re.sub(r"\[CALL:.*?\]|\[NEW_MODULE_SUGGESTION:.*?\]|\[TRIPLET:.*?\]", "", full_text).strip()
        
        # 3. [HTML]: 执行样式转化捏
        if markdown2:
            html = markdown2.markdown(clean_text, extras=['fenced-code-blocks', 'tables'])
        else:
            html = f"<pre style='white-space: pre-wrap;'>{clean_text}</pre>"
            
        # 4. [BEAUTIFY]: 针对进化提议进行“粉色卡片”美化渲染捏
        if suggestions:
            for s in suggestions:
                html += f"""
                <div style='background: rgba(255, 183, 197, 25); border-left: 3px solid #FFB7C5; 
                            padding: 8px; margin-top: 10px; border-radius: 4px;'>
                    <b style='color:#FFB7C5;'>🌸 Hanasuki 的进化提议：</b><br>
                    <i style='color:#D9E0EE;'>{s}</i>
                </div>
                """

        # 5. [RENDER]: 应用最终视觉样式并滚动到底部捏
        style = "<style>pre { background: rgba(0, 0, 0, 100); padding: 8px; border-radius: 6px; } code { color: #FAB387; }</style>"
        self.display.setHtml(f"{style}<b style='color:#FFB7C5;'>[花好き]:</b><br>{html}")
        self.display.moveCursor(QTextCursor.MoveOperation.End)

# --- [INTERFACE]: 模块协议接口捏 ---

def get_spec():
    """[LOGIC]: 向 ModuleManager 注册本 UI 插件的身份捏。"""
    return {
        "name": "classic_chat_ui",
        "description": "花好き 专用交互界面，支持磨砂玻璃特效捏",
        "type": "ui_extension",
        "is_main": True # 标记为主交互窗口捏
    }

def get_ui_entry(parent_window, bot_instance):
    """[FIX]: 统一的入口命名，由 app_gui.py 在启动时调用挂载捏。"""
    return ClassicChatWidget(parent_window, bot_instance)