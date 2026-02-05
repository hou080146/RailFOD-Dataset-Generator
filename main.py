import sys
import os
import cv2
import numpy as np
import torch
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QCursor
from PyQt5.QtCore import Qt

from UI import Ui_MainWindow
from SAMpredictor import SAMWorkerThread

class RailFoDTool(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("标注抠图工具")

        self.img_list = []
        self.img_idx = -1
        self.current_img_bgr = None
        self.current_mask = None
        self.input_points = []
        self.input_labels = []
        self.output_dir = None
        self.zoom_factor = 1.0  # 缩放倍率
        self.brush_size = 5  # 画笔大小

        self.sam_thread = SAMWorkerThread(
            checkpoint="weights/sam_vit_h_4b8939.pth",
            model_type="vit_h",
            device="cuda" if torch.cuda.is_available() else "cpu",
        )

        self .init_connections()
        self.sam_thread.load_model_task()

    def init_connections(self):
        self.btn_input.clicked.connect(self.on_import_dir)
        self.btn_output.clicked.connect(self.on_export_dir)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_next.clicked.connect(self.on_next)

        self.image_label.clicked_signal.connect(self.on_click)

        self.sam_thread.status_msg.connect(self.status_bar.setText)
        self.sam_thread.mask_ready.connect(self.on_mask_ready)
        self.sam_thread.model_loaded.connect(lambda: self.btn_input.setEnabled(True))
        self.slider_zoom.valueChanged.connect(self.on_zoom_changed)
        self.spin_brush.valueChanged.connect(self.on_brush_changed)

    def on_import_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择输入目录")
        if path:
            self.lbl_input.setText(f"输入： {path}")
            self.img_list = [os.path.join(path, f) for f in os.listdir(path)
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if self.img_list:
                self.img_idx = 0
                self.load_current_image()

    def on_export_dir(self):
        path = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if path:
            self.output_dir = path
            self.lbl_output.setText(f"保存: {path}")

    def on_zoom_changed(self, value):
        self.zoom_factor = value / 100.0
        self.lbl_zoom.setText(f"图像缩放: {value}%")
        self.update_ui_display()
        self.update_brush_cursor()

    def on_brush_changed(self, value):
        self.brush_size = value
        self.update_ui_display()
        self.update_brush_cursor()

    def load_current_image(self):
        if 0 <= self.img_idx < len(self.img_list):
            self.current_img_bgr = cv2.imread(self.img_list[self.img_idx])
            self.on_clear()
            self.sam_thread.set_image_task(self.current_img_bgr)
            self.update_ui_display()
            self.update_brush_cursor()


    def on_click(self, x, y, is_left):
        self.input_points.append([x, y])
        self.input_labels.append(1 if is_left else 0)
        self.sam_thread.predict_task(self.input_points, self.input_labels)

    def on_mask_ready(self, mask):
        self.current_mask = mask
        self.update_ui_display()

    def update_ui_display(self):
        if self.current_img_bgr is None:
            return

        tmp_img = self.current_img_bgr.copy()
        h_orig, w_orig = tmp_img.shape[:2]

        # 1. 渲染 Mask 预览
        if self.current_mask is not None:
            mask_overlay = np.zeros_like(tmp_img)
            mask_overlay[:] = [0, 255, 0]
            idx = self.current_mask > 0
            tmp_img[idx] = cv2.addWeighted(tmp_img[idx], 0.7, mask_overlay[idx], 0.3, 0)

        # 2. 渲染点击的点 (使用设置好的 brush_size)
        # 注意：这里的点是在原图坐标上画的
        for i, pt in enumerate(self.input_points):
            color = (0, 255, 0) if self.input_labels[i] == 1 else (0, 0, 255)
            cv2.circle(tmp_img, (pt[0], pt[1]), self.brush_size, color, -1)

        # 3. 转换图像格式
        q_img = QImage(cv2.cvtColor(tmp_img, cv2.COLOR_BGR2RGB).data,
                       w_orig, h_orig, 3 * w_orig, QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(q_img)

        # 4. 根据滑块值计算缩放后的目标大小
        target_w = int(w_orig * self.zoom_factor)
        target_h = int(h_orig * self.zoom_factor)

        # 核心：执行缩放
        # 如果像素很小，可以使用 Qt.FastTransformation 保持像素感，
        # 或者使用 Qt.SmoothTransformation 保持平滑
        scaled_pix = pixmap.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 5. 更新 Label 的显示并计算偏移量
        self.image_label.setPixmap(scaled_pix)
        self.image_label.current_scale = self.zoom_factor

        # 计算由于 AlignCenter 产生的偏移（用于坐标映射）
        # offset = (Label总宽 - 图片实际宽) / 2
        self.image_label.offset_x = (self.image_label.width() - scaled_pix.width()) // 2
        self.image_label.offset_y = (self.image_label.height() - scaled_pix.height()) // 2

    def on_save(self):
        if self.current_mask is None or self.output_dir is None:
            self.status_bar.setText("保存失败：未生成掩码或未设置路径")
            return

        h, w = self.current_img_bgr.shape[:2]
        res = np.zeros((h, w, 4), dtype=np.uint8)
        res[:, :, 0:3] = self.current_img_bgr
        res[:, :, 3] = (self.current_mask * 255).astype(np.uint8)

        # 精确计算边界
        y_indices, x_indices = np.where(self.current_mask > 0)
        if len(y_indices) > 0:
            y0, y1 = y_indices.min(), y_indices.max()
            x0, x1 = x_indices.min(), x_indices.max()
            # 适当扩充 2 像素边缘防止切边太死
            y0, y1 = max(0, y0 - 2), min(h, y1 + 2)
            x0, x1 = max(0, x0 - 2), min(w, x1 + 2)
            res_cropped = res[y0:y1, x0:x1]

            fname = os.path.basename(self.img_list[self.img_idx]).split('.')[0] + '.png'
            save_path = os.path.join(self.output_dir, fname)
            # 使用 cv2.imencode 支持中文路径保存
            is_success, im_buf = cv2.imencode(".png", res_cropped)
            if is_success:
                im_buf.tofile(save_path)
                self.status_bar.setText(f"已保存: {fname}")

            self.on_next()

    def on_clear(self):
        self.input_points = []
        self.input_labels = []
        self.current_mask = None
        self.update_ui_display()

    def on_next(self):
        if self.img_idx < len(self.img_list) - 1:
            self.img_idx += 1
            self.load_current_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S: self.on_save()
        elif event.key() == Qt.Key_C: self.on_clear()
        elif event.key() == Qt.Key_Space: self.on_next()

    def update_brush_cursor(self):
        """根据画笔大小和缩放比例更新鼠标光标"""
        if self.current_img_bgr is None:
            return

        # 计算在显示屏上的实际视觉半径
        # 视觉半径 = 原始半径 * 缩放比例
        visual_radius = int(self.brush_size * self.zoom_factor)

        # 限制光标大小，防止超出操作系统限制（通常最大 128x128）
        cursor_size = max(8, min(visual_radius * 2 + 2, 128))
        half_size = cursor_size // 2

        # 创建一个透明的 Pixmap
        pixmap = QPixmap(cursor_size, cursor_size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 画圆圈：使用白边黑底（或反色）确保在任何背景下可见
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(1, 1, cursor_size - 2, cursor_size - 2)
        painter.setPen(QPen(Qt.white, 1))
        painter.drawEllipse(2, 2, cursor_size - 4, cursor_size - 4)

        painter.end()

        # 设置光标，热点设为中心点 (half_size, half_size)
        self.image_label.setCursor(QCursor(pixmap, half_size, half_size))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RailFoDTool()
    win.show()
    sys.exit(app.exec_())