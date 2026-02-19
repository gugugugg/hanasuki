# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This software is licensed under the GNU General Public License v3.
# [SAFETY]: 模块主权验证码: 6c6f766573616e67 (lovesang)
# =================================================================

"""
模块名称：Evolution Monitor Sidebar (进化监视侧边栏)
作用：实时监控 Hanasuki 的自研状态、课题权重及逻辑沉淀进度。
适配：完美适配 Hanasuki V9.6.0 钛合金内核。
[FIX]: 增加了字典遍历的线程安全保护 (Dict Copy)。
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QScrollArea, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

class LearningMonitorWidget(QWidget):
    def __init__(self, parent, bot):
        super().__init__(parent)
        self.bot = bot
        self.is_expanded = False # 初始状态为收起
        self.last_edge_count = -1 # [LOGIC]: 用于记录上次的知识点数量，判断是否更新
        self.init_ui()
        
        # [LOGIC]: 启动 UI 刷新定时器。
        # 由于内核数据是动态变化的，我们每隔 1000ms 定时同步一次状态。
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(1000)

    def init_ui(self):
        """[LOGIC]: 构建侧边栏视觉结构"""
        # 主布局：水平排列（展开按钮 + 内容容器）
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. [LOGIC]: 展开/收起切换按钮。
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

        # 2. [LOGIC]: 核心内容容器。
        self.container = QFrame()
        self.container.setObjectName("MonitorContainer")
        self.container.setFixedWidth(0)
        self.container.setStyleSheet("""
            #MonitorContainer { 
                background: rgba(30, 30, 30, 220); 
                border-left: 1px solid rgba(255, 183, 197, 50); 
            }
            QLabel { color: #FFB7C5; font-size: 11px; font-family: 'Segoe UI', 'Microsoft YaHei'; }
        """)
        
        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(10, 15, 10, 15)
        
        # --- 状态监视区 ---
        c_layout.addWidget(QLabel("<b>🧠 进化状态</b>"))
        self.status_tag = QLabel("模式: 待机中")
        self.status_tag.setStyleSheet("color: #AAA;")
        c_layout.addWidget(self.status_tag)
        
        c_layout.addSpacing(15)
        
        # --- 认知权重区 ---
        c_layout.addWidget(QLabel("<b>📚 认知领域分布</b>"))
        
        # 使用滚动区域承载可能过多的课题
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.topic_container = QWidget()
        self.topic_layout = QVBoxLayout(self.topic_container)
        self.topic_layout.setContentsMargins(0, 0, 0, 0)
        self.topic_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.topic_container)
        c_layout.addWidget(self.scroll)
        
        # --- 日志概览区 ---
        c_layout.addSpacing(10)
        c_layout.addWidget(QLabel("<b>✨ 最新逻辑片段</b>"))
        self.log_area = QLabel("等待数据沉淀...")
        self.log_area.setWordWrap(True)
        self.log_area.setStyleSheet("color: #888; font-size: 10px;")
        c_layout.addWidget(self.log_area)

        self.layout.addWidget(self.container)

    def toggle_sidebar(self):
        """[LOGIC]: 利用属性动画实现侧边栏的平滑抽拉效果。"""
        is_opening = not self.is_expanded
        target_width = 180 if is_opening else 0
        
        self.anim = QPropertyAnimation(self.container, b"minimumWidth")
        self.anim.setDuration(350)
        self.anim.setStartValue(self.container.width())
        self.anim.setEndValue(target_width)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.anim_max = QPropertyAnimation(self.container, b"maximumWidth")
        self.anim_max.setDuration(350)
        self.anim_max.setStartValue(self.container.width())
        self.anim_max.setEndValue(target_width)
        self.anim_max.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.toggle_btn.setText("▶" if is_opening else "◀")
        self.is_expanded = is_opening
        
        self.anim.start()
        self.anim_max.start()

    def refresh_data(self):
        """[LOGIC]: 从内核实时同步学习数据 (线程安全版)。"""
        try:
            # 1. 更新自研模式状态
            if getattr(self.bot, 'learning_active', False):
                self.status_tag.setText("模式: 🌙 深度梦境自研中")
                self.status_tag.setStyleSheet("color: #FFB7C5; font-weight: bold;")
            else:
                self.status_tag.setText("模式: 💤 待机/交互")
                self.status_tag.setStyleSheet("color: #AAA;")
                
            # 2. 动态更新课题进度条
            if self.is_expanded:
                # 清理旧条目
                for i in reversed(range(self.topic_layout.count())): 
                    item = self.topic_layout.itemAt(i)
                    if item.widget(): item.widget().setParent(None)
                    
                # [CRITICAL FIX]: 使用 .copy() 创建副本进行遍历！
                # 这能防止主线程遍历时，后台自研线程修改字典导致崩溃。
                topics = getattr(self.bot, 'topics', {}).copy()
                
                sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
                for name, weight in sorted_topics[:6]: 
                    t_label = QLabel(f"{name} ({weight:.2f})")
                    t_bar = QProgressBar()
                    t_bar.setFixedHeight(6)
                    t_bar.setTextVisible(False)
                    # 权重映射：将 0-5 映射为百分比进度
                    t_bar.setValue(min(100, int((weight / 5.0) * 100)))
                    t_bar.setStyleSheet("""
                        QProgressBar { background: rgba(255,255,255,10); border-radius: 3px; border: none; }
                        QProgressBar::chunk { background: #FFB7C5; border-radius: 3px; }
                    """)
                    self.topic_layout.addWidget(t_label)
                    self.topic_layout.addWidget(t_bar)

            # 3. 主动轮询新知识点数量
            current_count = getattr(self.bot, "latest_new_edge_count", 0)
            if current_count > self.last_edge_count:
                if current_count > 0:
                    self.log_area.setText(f"已捕获 {current_count} 条新逻辑关联。\n正在构建图谱...")
                    self.log_area.setStyleSheet("color: #89DCEB; font-size: 10px; font-weight: bold;")
                self.last_edge_count = current_count
                
        except (AttributeError, RuntimeError, KeyboardInterrupt):
            # 即使发生极端错误，侧边栏也只会在这一帧静默，不会拖垮主程序
            pass

    def update_log(self, text):
        """[LOGIC]: 外部调用接口"""
        self.log_area.setText(text)

# --- 模块协议接口 ---

def get_spec():
    return {
        "name": "learning_monitor",
        "description": "实时监视 Hanasuki 的认知进化与自研课题权重。",
        "type": "ui_extension",
        "is_main": False 
    }

def get_ui_entry(parent_window, bot_instance):
    return LearningMonitorWidget(parent_window, bot_instance)