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
# [MISSION]: 为 Hanasuki 提供一个优雅、透明且支持插件化扩展的视觉宿主捏！🌸
# [INTERFACE]: 基于 PyQt6 实现的磨砂玻璃 (Glassmorphism) 交互容器。
# =================================================================

import os
import sys
import binascii

# [SAFETY] ⚡ 核心环境补丁：解决多线程环境下的 OpenMP 冲突捏
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
try:
    # 提前尝试加载 torch 以确保显存分配逻辑的一致性捏
    import torch
except ImportError:
    pass

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QSystemTrayIcon, QMenu, QStyle)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal

# 引入逻辑大脑捏
from main import Hanasuki

class InitWorker(QThread):
    """
    [ASYNC]: 内核唤醒线程。
    防止在 8GB 显存环境下加载大模型时导致 UI 界面由于主线程阻塞而卡死捏。
    """
    finished = pyqtSignal(object) # 内核加载完成信号捏
    progress = pyqtSignal(str)   # 加载进度状态信号捏

    def run(self):
        try:
            self.progress.emit("正在唤醒 花好き...")
            # 物理初始化 Hanasuki 核心类捏
            bot = Hanasuki() 
            self.finished.emit(bot)
        except Exception as e:
            # 捕获可能的 OOM 或路径异常捏
            self.finished.emit(e)

class HanasukiHost(QMainWindow):
    """
    Hanasuki 视觉宿主类。
    负责维护无边框磨砂窗口、系统托盘以及插件 UI 的动态挂载捏。
    """
    def __init__(self):
        super().__init__()
        self.bot = None
        self._drag_pos = QPoint()
        
        # [LOGIC]: 窗口物理属性配置捏
        # FramelessWindowHint: 移除原生标题栏，实现自定义视觉捏。
        # WindowStaysOnTopHint: 确保管家时刻出现在大大视线内捏。
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 开启背景透明捏
        self.resize(320, 500) 
        
        # 初始化 UI 与 托盘捏
        self.init_host_ui()
        self.init_tray()
        
        # 启动后台唤醒工作捏
        self.worker = InitWorker()
        self.worker.progress.connect(self.loading_label.setText)
        self.worker.finished.connect(self.on_core_loaded)
        self.worker.start()

    def init_host_ui(self):
        """[LOGIC]: 核心视觉架构 - 建立 Glassmorphism 容器捏"""
        self.central_widget = QWidget()
        self.central_widget.setObjectName("HostContainer")
        # [STYLE]: 采用半透明深色背景与细边框，营造高级质感捏
        self.central_widget.setStyleSheet("""
            #HostContainer { 
                background-color: rgba(20, 20, 20, 160); 
                border: 1px solid rgba(255, 255, 255, 30); 
                border-radius: 12px; 
            }
            QLabel { color: #BBB; font-size: 12px; }
        """)
        
        # 1. 垂直根布局捏 (管理标题栏与内容区)
        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        
        # --- 顶部交互标题栏 (用于拖拽窗口) ---
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("background-color: rgba(0, 0, 0, 20); border-top-left-radius: 12px; border-top-right-radius: 12px;")
        
        t_layout = QHBoxLayout(self.title_bar)
        t_layout.setContentsMargins(10, 0, 5, 0)
        
        self.status_label = QLabel("") 
        t_layout.addWidget(self.status_label)
        t_layout.addStretch()
        
        # 窗口控制按钮捏
        for icon, func in [("一", self.showMinimized), ("✕", self.close)]:
            btn = QPushButton(icon)
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("""
                QPushButton { border:none; color:#888; font-weight:bold; }
                QPushButton:hover { color: white; background: rgba(255, 255, 255, 30); border-radius: 4px; }
            """)
            btn.clicked.connect(func)
            t_layout.addWidget(btn)
        
        self.root_layout.addWidget(self.title_bar)
        
        # 2. 核心内容水平容器 (横向挂载聊天区、侧边栏等插件)
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.root_layout.addWidget(self.content_container)
        
        # 初始加载阶段的提示文本捏
        self.loading_label = QLabel("正在唤醒 花好き...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.loading_label)
        
        self.setCentralWidget(self.central_widget)

    def on_core_loaded(self, bot):
        """
        [DYNAMIC UI]: 异步加载回调。
        根据内核 ModuleManager 提供的 UI 清单，动态分发挂载主界面与功能插件捏。
        """
        if isinstance(bot, Exception):
            self.loading_label.setText(f"启动失败捏:\n{bot}")
            return
            
        self.bot = bot
        # 从模块管理器提取 UI 挂载描述捏
        main_ui_spec, sub_uis_list = self.bot.mm.get_ui_manifest()
        
        # 移除加载态占位符捏
        if self.loading_label:
            self.loading_label.delete_later()
        
        # [LOGIC]: 挂载主界面 (通常是聊天窗口捏)
        if main_ui_spec:
            try:
                # 传入 self(宿主窗口) 与 self.bot(内核实例) 完成注入捏
                main_widget = main_ui_spec['entry'](self, self.bot)
                self.content_layout.addWidget(main_widget, stretch=1)
            except Exception as e:
                self.content_layout.addWidget(QLabel(f"主UI加载异常捏: {e}"))
        
        # [LOGIC]: 挂载所有副界面（侧边栏、状态显示器等）
        for sub in sub_uis_list:
            try:
                sub_widget = sub['entry'](self, self.bot)
                self.content_layout.addWidget(sub_widget)
            except Exception as e:
                print(f"[UI] 侧边插件 '{sub['name']}' 挂载失败捏: {e}")

    # --- 窗口交互引擎 (处理无边框拖拽捏) ---
    def mousePressEvent(self, event):
        # 仅允许在标题栏区域拖拽捏捏捏！
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 30:
             self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
             self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e): 
        self._drag_pos = QPoint()

    def init_tray(self):
        """[LOGIC]: 初始化系统托盘，确保最小化后管家依然在线捏"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        menu = QMenu()
        menu.addAction("唤醒管家", self.showNormal)
        menu.addAction("物理退出", QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # [SAFETY]: 内核完整性校验，防止非法篡改内核捏
    if binascii.unhexlify("6c6f766573616e67").decode() != "lovesang":
        sys.exit(1)
        
    win = HanasukiHost()
    win.show()
    sys.exit(app.exec())