# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 内核完整性校验令牌 ID: 6c6f766573616e67 (lovesang)
# =================================================================

import os
import sys
import binascii

# [SAFETY] ⚡ 核心环境补丁
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
try:
    import torch
except ImportError:
    pass

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QSystemTrayIcon, QMenu, QStyle)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal

from main import Hanasuki

class InitWorker(QThread):
    finished = pyqtSignal(object)
    progress = pyqtSignal(str)

    def run(self):
        try:
            self.progress.emit("正在唤醒 花好き...")
            bot = Hanasuki() 
            self.finished.emit(bot)
        except Exception as e:
            self.finished.emit(e)

class HanasukiHost(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bot = None
        self._drag_pos = QPoint()
        
        # [LOGIC] 窗口属性初始化
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(320, 500) 
        
        self.init_host_ui()
        self.init_tray()
        
        self.worker = InitWorker()
        self.worker.progress.connect(self.loading_label.setText)
        self.worker.finished.connect(self.on_core_loaded)
        self.worker.start()

    def init_host_ui(self):
        """[LOGIC] 核心 UI 架构逻辑 - 统一使用 root_layout"""
        self.central_widget = QWidget()
        self.central_widget.setObjectName("HostContainer")
        self.central_widget.setStyleSheet("""
            #HostContainer { 
                background-color: rgba(20, 20, 20, 160); 
                border: 1px solid rgba(255, 255, 255, 30); 
                border-radius: 12px; 
            }
            QLabel { color: #BBB; font-size: 12px; }
        """)
        
        # 1. [LOGIC] 顶层垂直布局 (垂直管理标题栏与下方内容)
        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        
        # --- 顶部交互标题栏 ---
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("background-color: rgba(0, 0, 0, 20); border-top-left-radius: 12px; border-top-right-radius: 12px;")
        
        t_layout = QHBoxLayout(self.title_bar)
        t_layout.setContentsMargins(10, 0, 5, 0)
        
        self.status_label = QLabel("") 
        t_layout.addWidget(self.status_label)
        t_layout.addStretch()
        
        for icon, func in [("一", self.showMinimized), ("✕", self.close)]:
            btn = QPushButton(icon)
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("""
                QPushButton { border:none; color:#888; font-weight:bold; }
                QPushButton:hover { color: white; background: rgba(255, 255, 255, 30); border-radius: 4px; }
            """)
            btn.clicked.connect(func)
            t_layout.addWidget(btn)
        
        # [LOGIC] 将标题栏挂载到垂直根布局
        self.root_layout.addWidget(self.title_bar)
        
        # 2. [LOGIC] 核心内容水平容器 (横向并列挂载所有 UI 插件)
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # [LOGIC] 挂载水平容器到垂直根布局
        self.root_layout.addWidget(self.content_container)
        
        # 初始加载提示
        self.loading_label = QLabel("正在唤醒 花好き...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.loading_label)
        
        self.setCentralWidget(self.central_widget)

    def on_core_loaded(self, bot):
        """[LOGIC] 异步加载回调：分配主/副 UI 插件"""
        if isinstance(bot, Exception):
            self.loading_label.setText(f"启动失败:\n{bot}")
            return
            
        self.bot = bot
        main_ui_spec, sub_uis_list = self.bot.mm.get_ui_manifest()
        
        # 移除加载文字
        if self.loading_label:
            self.loading_label.deleteLater()
        
        # [LOGIC] 挂载主界面
        if main_ui_spec:
            try:
                main_widget = main_ui_spec['entry'](self, self.bot)
                self.content_layout.addWidget(main_widget, stretch=1)
            except Exception as e:
                self.content_layout.addWidget(QLabel(f"主UI加载错误: {e}"))
        
        # [LOGIC] 挂载所有副界面（侧边栏等）
        for sub in sub_uis_list:
            try:
                sub_widget = sub['entry'](self, self.bot)
                self.content_layout.addWidget(sub_widget)
            except Exception as e:
                print(f"[UI] 副插件 '{sub['name']}' 挂载失败: {e}")

    # --- 窗口交互引擎 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 30:
             self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
             self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e): 
        self._drag_pos = QPoint()

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        menu = QMenu()
        menu.addAction("唤醒", self.showNormal)
        menu.addAction("完全退出", QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if binascii.unhexlify("6c6f766573616e67").decode() != "lovesang":
        sys.exit(1)
    win = HanasukiHost()
    win.show()
    sys.exit(app.exec())