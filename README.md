RailFOD-Dataset-Generator 📸🚂
这是一个基于 Meta Segment Anything Model (SAM) 和 PyQt5 开发的铁路轨道异物提取工具。
🌟 项目背景
在铁路轨道异物检测（FOD）任务中，真实异物样本极度稀缺。本项目旨在通过交互式分割技术，快速将异物（如螺丝刀、扳手、鞋子、杂草等）从原始图像中抠取出来，保存为带有 Alpha 通道的透明 PNG 素材，以便后续通过 Copy-Paste 算法生成大规模 YOLO 训练数据集。
✨ 主要功能
交互式多点分割：支持左键（正向点）和右键（负向点）精准控制分割范围。
异步推理：SAM 推理过程在后台线程执行，界面操作流畅不卡顿。
动态视觉反馈：鼠标光标根据画笔大小和缩放比例实时变化。
灵活缩放：支持滑块调节图像显示比例，适配小像素物体标注。
自动裁剪：保存时自动计算物体边界，剔除多余透明区域。
🚀 部署步骤
1. 环境准备
建议使用 Windows 10/11，并确保已安装 CUDA 11.6。
2. 创建虚拟环境
code
Bash
conda create -n rail_fod python=3.9 -y
conda activate rail_fod
3. 安装依赖
由于本工具依赖特定的 PyTorch 版本以匹配 CUDA 11.6，请务必按照以下顺序安装：
code
Bash
# 安装适配 CUDA 11.6 的 PyTorch
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116

# 安装 Segment Anything (SAM)
pip install git+https://github.com/facebookresearch/segment-anything.git

# 安装其他依赖 (NumPy 需指定版本以兼容旧版 Torch)
pip install "numpy<2.0" opencv-python PyQt5
4. 下载模型权重
在项目根目录下新建 weights 文件夹，并下载 SAM 官方权重：
ViT-H SAM Checkpoint (2.4 GB) 放入 weights/ 目录中。
🖱️ 使用指南
启动程序：
code
Bash
python main.py
导入数据：
点击 “选择输入目录” 加载待处理图片。
点击 “选择输出目录” 设置透明 PNG 的保存位置。
交互操作：
左键点击：增加识别区域。
右键点击：排除误选区域（如背景碎石）。
滑块/数值：调节图像缩放比例及画笔视觉半径。
快捷键：
S：保存当前抠图并自动跳转到下一张。
Space (空格)：跳过当前图片。
C：清空当前所有点击点，重新标注。
🛠️ 技术栈
核心算法: Segment Anything (SAM)
GUI 框架: PyQt5
图像处理: OpenCV, NumPy
深度学习引擎: PyTorch (CUDA 11.6)
📝 常见问题 (FAQ)
Q: 为什么点击后没有反应？
A: 首次加载图片会进行特征提取（Embedding），状态栏显示“图像特征提取完成”后即可点击。
Q: 为什么保存的图片是黑色的？
A: 请检查导出目录是否具有写入权限，保存的图片为透明 PNG，在某些看图软件中可能显示为黑色背景。
Q: NumPy 报错崩溃？
A: 请确保执行过 pip install "numpy<2.0"，SAM 的旧版依赖不支持 NumPy 2.x。