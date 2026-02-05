import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from segment_anything import sam_model_registry, SamPredictor

class SAMWorkerThread(QThread):
    model_loaded = pyqtSignal(bool)
    mask_ready = pyqtSignal(object)
    status_msg = pyqtSignal(str)

    def __init__(self, checkpoint, model_type, device):
        super().__init__()
        self.checkpoint = checkpoint
        self.model_type = model_type
        self.device = device
        self.predictor = None

        self._task_type = None
        self._pending_img = None
        self._pending_points = None
        self._pending_labels = None

    def load_model_task(self):
        self._task_type = 'load_model'
        self.start()

    def set_image_task(self, img_bgr):
        self._pending_img = img_bgr
        self._task_type = 'set_image'
        self.start()

    def predict_task(self, points, labels):
        self._pending_points = np.array(points)
        self._pending_labels = np.array(labels)
        self._task_type = 'predict'
        self.start()

    def run(self):
        try:
            if self._task_type == 'load_model':
                self.status_msg.emit("正在加载 SAM 模型...")
                sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint)
                sam.to(device=self.device)
                self.predictor = SamPredictor(sam)
                self.model_loaded.emit(True)
                self.status_msg.emit("模型加载成功！")

            elif self._task_type == 'set_image':
                if self.predictor and self._pending_img is not None:
                    img_rgb = cv2.cvtColor(self._pending_img, cv2.COLOR_BGR2RGB)
                    self.predictor.set_image(img_rgb)
                    self.status_msg.emit("图像特征提取完成")

            elif self._task_type == 'predict':
                if self.predictor and len(self._pending_points) > 0:
                    masks, scores, _ = self.predictor.predict(
                        point_coords=self._pending_points,
                        point_labels=self._pending_labels,
                        multimask_output=True
                    )
                    best_mask = masks[np.argmax(scores)]
                    self.mask_ready.emit(best_mask)
        except Exception as e:
            self.status_msg.emit(f"错误: {str(e)}")