# -*- coding: utf-8 -*-
# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# You may obtain a copy of the License at: https://www.gnu.org/licenses/gpl-3.0.html
#
# [SAFETY]: 模块主权验证码: 6c6f766573616e67 (lovesang)
# =================================================================

"""
模块名称：Classic Chat UI (Glassmorphism & Evolution Edition)
作用：Hanasuki 项目的核心交互界面。
[FIX]: 彻底移除中间深色背景，实现与宿主窗口的高级磨砂一致性捏。
[NEW]: 增加针对“模块进化提议”的视觉渲染逻辑捏。
"""

import re
import threading
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QLineEdit, 
                             QPushButton, QHBoxLayout, QSizeGrip)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor
import os

# [LOGIC]: 尝试导入渲染引擎捏
try:
    import markdown2
except ImportError:
    markdown2 = None

# --- 后台对话工作线程捏 ---
class ChatWorker(QThread):
    chunk_ready = pyqtSignal(str) 

    def __init__(self, bot, text):
        super().__init__()
        self.bot = bot  
        self.text = text 

    def run(self):
        full_text = ""
        try:
            # [LOGIC]: 对接内核对话接口捏
            for chunk in self.bot.chat(self.text):
                full_text += chunk
                self.chunk_ready.emit(full_text)
        except Exception as e:
            self.chunk_ready.emit(f"呜呜...大大的内核好像闹情绪了捏: {e}")

# --- 主界面组件捏 ---
class ClassicChatWidget(QWidget):
    def __init__(self, parent, bot):
        super().__init__(parent)
        self.bot = bot
        # [STYLE]: 开启磨砂透明属性捏
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        
    def init_ui(self):
        """[LOGIC]: 布局构建，实现视觉一体化捏捏捏！"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 5)
        layout.setSpacing(12)
        
        # 1. 聊天记录显示区 (QTextBrowser)
        self.display = QTextBrowser()
        self.display.setOpenExternalLinks(True) 
        
        # [STYLE]: 核心修正 —— 彻底透明化捏！
        # background: transparent; -> 移除深色背景块捏。
        # border: none; -> 移除边框，让文字浮动捏。
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
        self.display.setHtml(f"<b style='color:#FFB7C5;'>[花好き]:</b> 大大，欢迎回来捏！正式运行的第一天，我们要先研究什么捏？🌸")
        layout.addWidget(self.display)
        
        # 2. 底部输入区捏
        bottom_container = QHBoxLayout()
        bottom_container.setSpacing(10)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("在这里输入指令捏...")
        self.input.setStyleSheet("""
            QLineEdit { 
                background: rgba(49, 50, 68, 120); 
                border: 1px solid rgba(245, 194, 231, 30); 
                border-radius: 18px; 
                color: #CDD6F4; 
                padding: 10px 15px; 
            }
            QLineEdit:focus { border: 1px solid #FFB7C5; } 
        """)
        self.input.returnPressed.connect(self.send) 
        
        self.btn = QPushButton("发送 ✨")
        self.btn.setFixedSize(85, 40)
        self.btn.setStyleSheet("""
            QPushButton { 
                background: #FFB7C5; 
                color: #1E1E2E; 
                border-radius: 18px; 
                font-weight: bold; 
            }
            QPushButton:hover { background: #FFC0CB; }
        """)
        self.btn.clicked.connect(self.send)
        
        bottom_container.addWidget(self.input)
        bottom_container.addWidget(self.btn)
        layout.addLayout(bottom_container)

        # 3. 缩放手柄捏
        grip_layout = QHBoxLayout()
        grip_layout.addStretch()
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(15, 15)
        grip_layout.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        layout.addLayout(grip_layout)
        
    def send(self):
        text = self.input.text().strip()
        if not text: return
        self.input.clear()
        self.display.append(f"<div align='right' style='margin-bottom:12px;'><b style='color:#89DCEB;'>[大大]:</b> {text}</div>")
        self.display.moveCursor(QTextCursor.MoveOperation.End)
        self.worker = ChatWorker(self.bot, text)
        self.worker.chunk_ready.connect(self.render_markdown)
        self.worker.start()
        
    def render_markdown(self, full_text):
        """[LOGIC]: 核心渲染与美颜滤镜，包含进化提议提取捏。"""
        # 1. 提取自演化建议
        suggestions = re.findall(r"\[NEW_MODULE_SUGGESTION:\s*(.*?)\]", full_text)

        # 2. 强力人设纠偏：过滤后台标签与顽固口癖捏
        clean_text = re.sub(r"\[CALL:.*?\]|\[TRIPLET:.*?\]|\[NEW_TOPIC:.*?\]|\[CORRECTION.*?\]|\[NEW_MODULE_SUGGESTION:.*?\]", "", full_text).strip()
        
        # 封杀死板前缀与顽固英文口癖捏捏捏！
        clean_text = re.sub(r"^计算任务[:：].*?\n|^分析[:：].*?\n", "", clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r"\bAh,\s*|\bAhaha,?\s*", "", clean_text, flags=re.IGNORECASE)
        
        # 3. HTML 渲染捏
        if markdown2:
            html = markdown2.markdown(clean_text, extras=['fenced-code-blocks', 'tables'])
        else:
            html = f"<pre style='white-space: pre-wrap;'>{clean_text}</pre>"
            
        # 4. 追加进化提议的 UI 组件捏 (使用大大最爱的粉色边框)
        if suggestions:
            for s in suggestions:
                html += f"""
                <div style='background: rgba(255, 183, 197, 30); border-left: 4px solid #FFB7C5; 
                            padding: 10px; margin-top: 15px; border-radius: 4px;'>
                    <b style='color:#FFB7C5;'>🌸 Hanasuki 的进化提议：</b><br>
                    <i style='color:#D9E0EE;'>{s}捏！</i>
                </div>
                """

        style = "<style>pre { background: rgba(0, 0, 0, 100); padding: 10px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 10); } code { color: #FAB387; }</style>"
        self.display.setHtml(f"{style}<b style='color:#FFB7C5;'>[花好き]:</b><br>{html}")
        self.display.moveCursor(QTextCursor.MoveOperation.End)

# --- 模块协议接口捏 ---

def get_spec():
    return {
        "name": "classic_chat_ui",
        "description": "花好き 专用磨砂玻璃交互界面 (全透明自进化版)捏",
        "type": "ui_extension",
        "is_main": True 
    }

def get_ui_entry(parent_window, bot_instance):
    return ClassicChatWidget(parent_window, bot_instance)