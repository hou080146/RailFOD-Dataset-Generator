import sys

from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QPushButton, QFrame, QSlider, QSpinBox, QLabel,)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap



class ClickableLabel(QLabel):
    clicked_signal = pyqtSignal(int, int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0


    def mousePressEvent(self, event):
        if self.pixmap():
            # 这里的坐标是相对于 Label 的
            lx, ly = event.x(), event.y()

            # 只有点在图片内容区域内才有效
            if self.offset_x <= lx <= self.offset_x + self.pixmap().width() and \
                    self.offset_y <= ly <= self.offset_y + self.pixmap().height():
                # 核心逻辑：减去偏移量后除以当前的缩放比例
                real_x = int((lx - self.offset_x) / self.current_scale)
                real_y = int((ly - self.offset_y) / self.current_scale)

                is_left = (event.button() == Qt.LeftButton)
                self.clicked_signal.emit(real_x, real_y, is_left)

class Ui_MainWindow:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 850)

        self.central_widget = QWidget(MainWindow)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.image_label = ClickableLabel(self.central_widget)
        self.image_label.setAlignment(Qt.AlignCenter)  # 强制居中
        self.image_label.setStyleSheet("background-color: #1a1a1a;")
        # 关键：不要设置 setScaledContents(True)，否则会破坏坐标映射
        self.image_label.setScaledContents(False)
        self.main_layout.addWidget(self.image_label, 4)

        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(280)
        self.right_panel.setStyleSheet("QFrame { background-color: #2b2b2b; color:white;}")

        self.v_layout = QVBoxLayout(self.right_panel)

        self.lbl_input = QLabel("导入路径：未设置")
        self.lbl_input.setWordWrap(True)
        self.btn_input = QPushButton("选择目录")

        self.lbl_output = QLabel("导出路径：未设置")
        self.lbl_output.setWordWrap(True)
        self.btn_output = QPushButton("选择目录")

        self.btn_save = QPushButton("保存&下一张[S]")
        self.btn_clear = QPushButton("清除[C]")
        self.btn_next = QPushButton("跳过[Space]")

        self.status_bar = QLabel("状态：准备就绪")
        self.status_bar.setStyleSheet("color: #00ff00;")
        self.status_bar.setWordWrap(True)

        # --- 缩放控制 ---
        self.lbl_zoom = QLabel("图像缩放: 100%")
        self.v_layout.addWidget(self.lbl_zoom)
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setMinimum(10)  # 10%
        self.slider_zoom.setMaximum(500)  # 500%
        self.slider_zoom.setValue(100)  # 默认 100%
        self.v_layout.addWidget(self.slider_zoom)

        # --- 画笔大小控制 ---
        self.lbl_brush = QLabel("画笔半径:")
        self.v_layout.addWidget(self.lbl_brush)
        self.spin_brush = QSpinBox()
        self.spin_brush.setRange(1, 50)
        self.spin_brush.setValue(5)
        self.v_layout.addWidget(self.spin_brush)

        self.v_layout.addWidget(self.lbl_input)
        self.v_layout.addWidget(self.btn_input)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.lbl_output)
        self.v_layout.addWidget(self.btn_output)
        self.v_layout.addSpacing(20)
        self.v_layout.addWidget(self.btn_save)
        self.v_layout.addWidget(self.btn_clear)
        self.v_layout.addWidget(self.btn_next)
        self.v_layout.addStretch()
        self.v_layout.addWidget(self.status_bar)

        self.main_layout.addWidget(self.right_panel)
        MainWindow.setCentralWidget(self.central_widget)

        # 禁用所有按钮的焦点，防止空格键冲突
        self.btn_input.setFocusPolicy(Qt.NoFocus)
        self.btn_output.setFocusPolicy(Qt.NoFocus)
        self.btn_save.setFocusPolicy(Qt.NoFocus)
        self.btn_clear.setFocusPolicy(Qt.NoFocus)
        self.btn_next.setFocusPolicy(Qt.NoFocus)
        # 如果还有滑块或输入框，也建议设置
        self.slider_zoom.setFocusPolicy(Qt.NoFocus)
        self.spin_brush.setFocusPolicy(Qt.NoFocus)

