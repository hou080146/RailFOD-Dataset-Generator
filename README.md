# RailFOD-Dataset-Generator 📸🚂

这是一个基于 **Meta Segment Anything Model (SAM)** 和 **PyQt5** 开发的铁路轨道异物提取工具。

## 🌟 项目背景

在铁路轨道异物检测（FOD）任务中，真实异物样本极度稀缺。本项目旨在通过交互式分割技术，快速将异物（如螺丝刀、扳手、鞋子、杂草等）从原始图像中抠取出来，保存为带有 **Alpha 通道的透明 PNG 素材**，以便后续通过 **Copy-Paste** 算法生成大规模 YOLO 训练数据集。

## ✨ 主要功能

- **交互式多点分割**：支持左键（正向点）和右键（负向点）精准控制分割范围。
- **异步推理**：SAM 推理过程在后台线程执行，界面操作流畅不卡顿。
- **动态视觉反馈**：鼠标光标根据画笔大小和缩放比例实时变化。
- **灵活缩放**：支持滑块调节图像显示比例，适配小像素物体标注。
- **自动裁剪**：保存时自动计算物体边界，剔除多余透明区域。

---
<img width="1200" height="880" alt="image" src="https://github.com/user-attachments/assets/661c15ac-e90d-429b-90a6-9c9654b1c91b" />

<img width="380" height="252" alt="image" src="https://github.com/user-attachments/assets/96284507-3586-4b5e-80df-802843f7e391" />

## 🚀 部署步骤

### 1. 环境准备
建议使用 Windows 10/11，并确保已安装 **CUDA 11.6**。

### 2. 创建虚拟环境
```bash
conda create -n rail_fod python=3.9 -y
conda activate rail_fod
```
### 3. 安装依赖
由于本工具依赖特定的 PyTorch 版本以匹配 CUDA 11.6，请务必按照以下顺序安装：
```bash
# 1. 安装适配 CUDA 11.6 的 PyTorch
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116

# 2. 安装 Segment Anything (SAM)
pip install git+https://github.com/facebookresearch/segment-anything.git

# 3. 安装其他依赖 (NumPy 需指定版本以兼容旧版 Torch)
pip install "numpy<2.0" opencv-python PyQt5
```
### 4. 下载模型权重
在项目根目录下新建 weights 文件夹。
下载 SAM 官方权重：sam_vit_h_4b8939.pth (2.4 GB)。
将下载的文件放入 weights/ 目录中。
🖱️ 使用指南
启动程序
```bash
python main.py
```
数据导入<br>
选择输入目录：加载待处理的原始图片文件夹。<br>
选择输出目录：设置提取后的透明 PNG 存放位置。<br>
交互操作<br>
左键点击：增加识别区域（Positive Prompt）。<br>
右键点击：排除误选区域（Negative Prompt）。<br>
滑块/数值：调节图像缩放比例及画笔视觉半径。<br>
快捷键<br>

| 按键 | 功能 | 
|-----|-----|
| S  | 保存当前抠图并自动跳转到下一张   | 
| Space   | 跳过当前图片   |
| C   | 清空当前所有点击点，重新标注   |

按键	功能
S	保存当前抠图并自动跳转到下一张
Space (空格)	跳过当前图片
C	清空当前所有点击点，重新标注
## 🛠️ 技术栈
核心算法: Segment Anything (SAM)<br>
GUI 框架: PyQt5<br>
图像处理: OpenCV, NumPy<br>
深度学习引擎: PyTorch (CUDA 11.6)<br>
📝 常见问题 (FAQ)<br>
Q: 为什么点击后没有反应？<br>
A: 首次加载图片时，后台线程会进行图像特征提取（Embedding）。请观察状态栏，显示“图像特征提取完成”后即可开始点击。<br>
Q: 为什么保存的图片是黑色的？<br>
A: 本工具保存的是带 Alpha 通道的透明 PNG。许多默认看图软件会将透明背景显示为黑色。你可以尝试将图片拖入 Photoshop 或网页浏览器查看。<br>
Q: NumPy 报错崩溃？<br>
A: SAM 的旧版依赖与 NumPy 2.x 不兼容。请确保你执行过 pip install "numpy<2.0"。<br>
💡 建议<br>
为了获得最佳的 YOLO 训练效果，建议在不同光照和角度下为同一种异物采集多张素材（PNG），并在合成阶段结合轨道透视关系进行随机缩放与旋转。<br>
