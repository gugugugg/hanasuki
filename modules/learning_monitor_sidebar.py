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
# [MISSION]: 实时可视化 Hanasuki 的认知进化状态，监控学术课题的权重分布捏！🌸
# [STYLE]: 采用侧抽屉式动效设计，深度适配磨砂交互层捏。
# =================================================================

"""
模块名称：Evolution Monitor Sidebar (进化监视侧边栏)
版本：Beta 1.1 (Stability Patch)
作用：实时同步内核中的逻辑图谱权重，并以可视化进度条形式展现捏。

核心修复：
1. [Safety Lock]: 增加了进度条 setValue 的物理限额 (min 100)，防止权重溢出导致渲染异常捏。
2. [Concurrency]: 优化了线程安全的字典遍历逻辑，使用 .copy() 拦截由于自研线程写入导致的运行时错误捏。
3. [Performance]: 设定 1000ms 同步频率，确保在 8GB 显存推理时 UI 不抢占总线资源捏。
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QScrollArea, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

class LearningMonitorWidget(QWidget):
    """
    Hanasuki 进化状态监视组件。
    负责从 bot 内核中提取 topics 权重并进行动态映射捏。
    """
    def __init__(self, parent, bot):
        super().__init__(parent)
        self.bot = bot
        self.is_expanded = False 
        self.last_edge_count = -1 
        self.init_ui()
        
        # [LOGIC]: UI 同步定时器。
        # 设定 1000ms 刷新一次。
        # 这是一个针对 RTX 5060 设计的平衡点：既能实时反馈，又不会因频繁重绘干扰大模型的 Token 生成速度捏！
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(1000)

    def init_ui(self):
        """[LOGIC]: 构建侧边栏布局与视觉样式捏。"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. [INTERACT]: 侧边抽拉触控按钮捏
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(16, 60)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton { 
                background: rgba(255, 183, 197, 100); 
                color: black; 
                border-top-left-radius: 6px; 
                border-bottom-left-radius: 6px; 
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(255, 183, 197, 200); }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.layout.addWidget(self.toggle_btn)

        # 2. [CONTAINER]: 监视内容主容器
        self.container = QFrame()
        self.container.setObjectName("MonitorContainer")
        self.container.setFixedWidth(0) # 初始宽度为 0 捏
        self.container.setStyleSheet("""
            #MonitorContainer { 
                background: rgba(30, 30, 30, 220); 
                border-left: 1px solid rgba(255, 183, 197, 50); 
            }
            QLabel { color: #FFB7C5; font-size: 11px; }
        """)
        
        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(10, 15, 10, 15)
        
        # 状态标题区
        c_layout.addWidget(QLabel("<b>🧠 进化状态</b>"))
        self.status_tag = QLabel("模式: 待机中")
        c_layout.addWidget(self.status_tag)
        
        c_layout.addSpacing(15)
        c_layout.addWidget(QLabel("<b>📚 认知分布</b>"))
        
        # 滚动区域，支持课题海量堆叠捏
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.topic_container = QWidget()
        self.topic_layout = QVBoxLayout(self.topic_container)
        self.topic_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.topic_container)
        c_layout.addWidget(self.scroll)

        self.layout.addWidget(self.container)

    def toggle_sidebar(self):
        """
        [ANIMATION]: 抽屉平滑动画控制捏。
        通过 QPropertyAnimation 实现 350ms 的贝塞尔曲线弹出效果。
        """
        is_opening = not self.is_expanded
        target_width = 180 if is_opening else 0
        
        # 物理调整宽度阈值捏
        self.anim = QPropertyAnimation(self.container, b"minimumWidth")
        self.anim.setDuration(350)
        self.anim.setEndValue(target_width)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.anim_max = QPropertyAnimation(self.container, b"maximumWidth")
        self.anim_max.setDuration(350)
        self.anim_max.setEndValue(target_width)
        
        self.toggle_btn.setText("▶" if is_opening else "◀")
        self.is_expanded = is_opening
        self.anim.start()
        self.anim_max.start()

    def refresh_data(self):
        """
        [DATA SYNC]: 物理同步内核数据捏。
        
        [RTX 5060 ADAPTATION]: 
        仅当侧边栏展开时才执行高负荷的 UI 重新挂载。
        当侧边栏收起时，保持逻辑静默，将性能留给大大捏！
        """
        try:
            # 1. 同步自研状态捏
            if getattr(self.bot, 'learning_active', False):
                self.status_tag.setText("模式: 🌙 深度自研中")
                self.status_tag.setStyleSheet("color: #FFB7C5;")
            else:
                self.status_tag.setText("模式: 💤 待机中")
                self.status_tag.setStyleSheet("color: #AAA;")
                
            # 2. 动态映射课题权重至进度条捏
            if self.is_expanded:
                # 递归清理旧有的 UI 部件，为新数据腾地方捏
                for i in reversed(range(self.topic_layout.count())): 
                    widget = self.topic_layout.itemAt(i).widget()
                    if widget: widget.setParent(None)
                    
                # [CRITICAL SAFETY]: 多线程遍历安全拦截
                # 使用 .copy() 获取副本。防止在遍历过程中，
                # bot 的自研线程突然写入新节点导致程序抛出 RuntimeError 崩溃捏！
                topics = getattr(self.bot, 'topics', {}).copy()
                
                # 取权重前 6 名的课题进行展示捏
                for name, weight in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:6]: 
                    t_label = QLabel(f"{name} ({weight:.2f})")
                    t_bar = QProgressBar()
                    t_bar.setFixedHeight(6)
                    t_bar.setTextVisible(False)
                    
                    # [VRAM SAFETY LOCK]: 物理防溢出
                    # 将权重映射为 0-100% 的进度条数值捏。
                    # 使用 min(100, ...) 确保即使某个课题研究得非常透彻（权重 > 5.0），
                    # UI 也不会因为数值爆表而产生渲染逻辑错误捏！
                    progress_val = min(100, int((weight / 5.0) * 100))
                    t_bar.setValue(progress_val)
                    
                    t_bar.setStyleSheet("""
                        QProgressBar { background: rgba(255,255,255,10); border-radius: 3px; border: none; }
                        QProgressBar::chunk { background: #FFB7C5; border-radius: 3px; }
                    """)
                    self.topic_layout.addWidget(t_label)
                    self.topic_layout.addWidget(t_bar)

        except: 
            # 捕获可能的同步干扰，静默处理捏
            pass

# --- [PROTOCOL]: 模块协议接口捏 ---

def get_spec():
    """[LOGIC]: 向 ModuleManager 注册监视组件捏。"""
    return {
        "name": "learning_monitor",
        "description": "实时监视认知进化与自研权重，支持物理溢出拦截捏",
        "type": "ui_extension",
        "is_main": False # 标记为侧边副窗口捏
    }

def get_ui_entry(parent_window, bot_instance):
    """[FIX]: 统一的入口命名，方便 app_gui.py 在启动时动态唤醒捏。"""
    return LearningMonitorWidget(parent_window, bot_instance)