# Codex Progress

更新时间: 2026-03-24

## 项目概览

- 项目名称: `Multi-defect-type-beam-bridge-dataset-GYU-DET`
- 当前目标: 梳理仓库结构，建立持续维护的进展文档，作为后续数据集整理、训练、验证和问题修复的工作基线。
- 仓库核心组成:
  - `ultralytics/`: 本项目内置的 YOLOv11 训练代码与配置目录。
  - `txt2coco.py`: 将 YOLO 标注转换为 COCO `json`。
  - `txt2xml.py`: 将 YOLO 标注转换为 VOC `xml`。
  - `README.md`: 项目简介、依赖说明和基础使用方式。

## 已检查内容

### 1. 根目录结构

- 已确认当前仓库根目录主要包含:
  - `README.md`
  - `txt2coco.py`
  - `txt2xml.py`
  - `ultralytics/`

### 2. 训练相关代码

- `ultralytics/mytrain.py` 使用如下训练入口:
  - `model = YOLO("yolo11.yaml")`
  - `model.train(data='./GZ-DET.yaml', epochs=300)`
- 由此可知:
  - 仓库中的 `ultralytics` 目录确实是对应 YOLOv11 的训练代码。
  - 当前默认训练配置依赖 `ultralytics/GZ-DET.yaml`。
- `ultralytics/cfg/models/11/yolo11.yaml` 已存在，说明模型结构文件已随仓库提供。

### 3. 数据集配置

- `ultralytics/GZ-DET.yaml` 当前定义了 6 个类别:
  - `Crack`
  - `Breakage`
  - `Comb`
  - `Hole`
  - `Reinforcement`
  - `Seepage`
- 当前 `train` 与 `val` 路径写法分别为:
  - `/train`
  - `/valid`
- 文件中暂未看到 `path:` 根路径字段，后续训练前需要结合实际数据目录确认是否可被正确解析。

### 4. 标注转换脚本

- `txt2coco.py`
  - 读取 `images/`、`labels/`、`classes.txt`
  - 支持直接导出 COCO 标注
  - 支持随机划分或基于 `train.txt / val.txt / test.txt` 划分
- `txt2xml.py`
  - 将 YOLO 框转换为 VOC XML
  - 当前脚本主函数里的默认路径仍是本地绝对路径示例:
    - `F:/voc2014/JPEGImages/`
    - `F:/voc2014/labels/`
    - `F:/voc2014/Annotations/`
  - 后续如果要在本仓库直接使用，需要先改成项目内可配置路径

## 当前发现的问题

### 1. README 与实际文件名不一致

- `README.md` 的 Quick Start 写的是修改 `ultralytics/GYU-DET.yaml`
- 仓库实际存在的是 `ultralytics/GZ-DET.yaml`
- 这会直接影响首次使用者按文档启动训练

### 2. `txt2xml.py` 的类别映射与数据集配置不一致

- `txt2xml.py` 当前类别映射包含 7 项，且顺序与名称存在明显偏差:
  - 包含 `fengwo`
  - `Comb` 与 `Hole` 的编号位置和 `GZ-DET.yaml` 不一致
- 但 `GZ-DET.yaml` 中当前只定义了 6 类
- 这意味着若直接使用 `txt2xml.py`，有较高概率生成错误类别名

### 3. `txt2coco.py` 的划分断言存在风险

- `train_test_val_split_random()` 中使用:
  - `assert int(ratio_train + ratio_test + ratio_val) == 1`
- 这对默认 `0.8 + 0.1 + 0.1` 可以工作，但写法不够稳健
- 后续如果使用其他浮点比例，可能带来不必要的断言风险

### 4. README 依赖说明存在重复

- `README.md` 中 `ultralytics` 同时出现:
  - `8.3.33`
  - `8.0.227`
- 后续需要确认本仓库实际适配版本

## 当前结论

- 仓库是一个“数据集 + 转换脚本 + 内置 YOLOv11 训练代码”的组合项目。
- `ultralytics/` 目录可视为该项目的训练核心。
- 当前仓库已经具备基础训练入口，但文档和转换脚本还存在一致性问题，后续应优先修正。

## YOLO Baseline 代码阅读记录

### 1. 代码基线版本

- 当前仓库内置的 `ultralytics` 版本号来自 `ultralytics/__init__.py`
- 已确认版本为:
  - `8.3.126`
- 这与 `README.md` 中列出的 `8.3.33`、`8.0.227` 都不一致
- 后续所有 baseline 修改，应以仓库内实际代码为准，而不是仅参考 README

### 2. 当前训练入口主链路

- 本项目的训练入口是 `ultralytics/mytrain.py`
- 当前入口逻辑非常简单:
  - `YOLO("yolo11.yaml")`
  - `model.train(data="./GZ-DET.yaml", epochs=300)`
- 也就是说当前 baseline 默认行为是:
  - 从模型结构 YAML 新建检测模型
  - 使用数据集配置 `GZ-DET.yaml`
  - 训练 300 轮
- 重要说明:
  - 这里传入的是 `yolo11.yaml`，不是 `yolo11n.pt`
  - 因此当前脚本默认更接近“从结构配置构建模型”而不是“直接加载现成预训练权重”
  - 若后续要做真正的迁移学习 baseline，通常需要改成加载 `.pt` 或显式指定 `pretrained`

### 3. 模型对象与任务分发

- `ultralytics/models/yolo/model.py` 中 `YOLO` 继承自 `Model`
- `YOLO.task_map` 将不同任务映射到不同实现
- 对当前项目最相关的是 `detect` 分支:
  - `model -> DetectionModel`
  - `trainer -> DetectionTrainer`
  - `validator -> DetectionValidator`
  - `predictor -> DetectionPredictor`
- 因此当前项目的训练主链路可以概括为:
  - `mytrain.py`
  - `YOLO(...)`
  - `Model.train(...)`
  - `DetectionTrainer`
  - `DetectionModel`
  - `v8DetectionLoss`

### 4. `Model.train()` 的作用

- `ultralytics/engine/model.py` 中的 `Model.train()` 负责:
  - 合并默认配置、模型覆盖项和用户传参
  - 根据当前 task 自动选择 trainer
  - 在非 resume 情况下构建训练用模型
  - 启动 trainer 训练
  - 训练结束后重新加载 `best.pt` 或 `last.pt`
- 当前代码里 `train()` 的关键特点:
  - 最终 trainer 由 `self._smart_load("trainer")` 自动选择
  - 对 detect 任务会落到 `DetectionTrainer`
  - 训练结束后 `self.model` 会被更新为训练后的 checkpoint 模型

### 5. `BaseTrainer` 的核心职责

- `ultralytics/engine/trainer.py` 中 `BaseTrainer` 是训练总控
- 它负责的关键流程包括:
  - 读取并解析默认配置 `ultralytics/cfg/default.yaml`
  - 选择设备 `cpu/cuda`
  - 创建输出目录与权重保存目录
  - 读取数据集配置并解析 train/val 路径
  - 初始化模型、优化器、学习率调度器、AMP、EMA
  - 执行 epoch / iter 训练循环
  - 运行验证并保存 `last.pt`、`best.pt`
- 当前 baseline 中比较重要的训练行为:
  - 支持 DDP 多卡训练
  - 支持 AMP 混合精度
  - 支持 EMA
  - 支持 warmup
  - 支持 early stopping
  - 支持 `optimizer=auto`
  - 支持 `close_mosaic` 在训练后期关闭 mosaic

### 6. `DetectionTrainer` 的检测任务定制逻辑

- `ultralytics/models/yolo/detect/train.py` 中 `DetectionTrainer` 在 `BaseTrainer` 基础上补充了检测任务逻辑
- 它主要负责:
  - `build_dataset()`: 创建 YOLO 检测数据集
  - `get_dataloader()`: 创建训练/验证 dataloader
  - `preprocess_batch()`: 图像转 float 并归一化到 `[0, 1]`
  - `set_model_attributes()`: 将 `nc`、`names`、`args` 挂到模型上
  - `get_model()`: 构建 `DetectionModel`
  - `get_validator()`: 创建检测验证器
- 当前检测损失名固定为:
  - `box_loss`
  - `cls_loss`
  - `dfl_loss`

### 7. 数据集读取与标签格式要求

- 数据集入口检查位于 `ultralytics/data/utils.py` 的 `check_det_dataset()`
- 当前 detect 数据集 YAML 至少要求:
  - `train`
  - `val`
  - `names` 或 `nc`
- 路径解析规则是:
  - 优先使用 YAML 里的 `path`
  - 如果没有 `path`，则以 YAML 文件所在目录作为根目录
  - 再拼接 `train/val/test`
- 结合本项目当前的 `ultralytics/GZ-DET.yaml`，这里有一个额外风险:
  - 当前 `train: /train`
  - 当前 `val: /valid`
  - 由于路径以 `/` 开头，后续很可能被解释为绝对路径，而不是相对数据集根目录
  - 训练前应优先修正这一点
- 实际标签加载由 `YOLODataset` 完成，位于 `ultralytics/data/dataset.py`
- 当前 baseline 对检测标签的要求:
  - 图片目录通常为 `images/`
  - 标签目录通常为 `labels/`
  - 每个标签文件为 YOLO 格式
  - 每行 5 列: `class x_center y_center width height`
  - 坐标必须归一化到 `[0, 1]`
- 数据集读取的附加行为:
  - 会扫描图片和标签一致性
  - 会生成 `.cache`
  - 会移除重复标签
  - 会对错误图像或标签给出 warning

### 8. 数据增强与 batch 组织

- 数据构建位于 `ultralytics/data/build.py`
- 检测训练默认通过 `build_yolo_dataset()` 创建 `YOLODataset`
- `YOLODataset.build_transforms()` 的主要逻辑:
  - 训练阶段启用 `v8_transforms`
  - 验证阶段使用 `LetterBox`
  - 最后统一经过 `Format(...)`
- 当前默认增强超参数来自 `ultralytics/cfg/default.yaml`
- 其中对 detect baseline 最关键的默认项包括:
  - `imgsz: 640`
  - `batch: 16`
  - `mosaic: 1.0`
  - `mixup: 0.0`
  - `copy_paste: 0.0`
  - `fliplr: 0.5`
  - `scale: 0.5`
  - `translate: 0.1`
- `YOLODataset.collate_fn()` 会把一个 batch 中的:
  - `img`
  - `cls`
  - `bboxes`
  - `batch_idx`
  等字段打包到训练所需格式

### 9. 检测模型构建方式

- `DetectionModel` 位于 `ultralytics/nn/tasks.py`
- 当前模型构建流程是:
  - 读取 `yolo11.yaml`
  - 如果数据集类别数和 YAML 中 `nc` 不一致，则用数据集类别数覆盖
  - 调用 `parse_model()` 解析 backbone/head
  - 构建最终 PyTorch 模型
  - 自动推导 stride
  - 初始化权重和 Detect head bias
- `parse_model()` 会根据 YAML 中的:
  - `backbone`
  - `head`
  - `scales`
  组装网络
- 当前 `ultralytics/cfg/models/11/yolo11.yaml` 是 YOLO11 检测结构定义
- 该模型最后输出的是标准 Detect 头，多尺度输出来自:
  - P3
  - P4
  - P5

### 10. 检测损失实现

- 当前检测损失位于 `ultralytics/utils/loss.py`
- `DetectionModel.init_criterion()` 默认返回 `v8DetectionLoss`
- `v8DetectionLoss` 由三部分组成:
  - `box_loss`
  - `cls_loss`
  - `dfl_loss`
- 关键实现特点:
  - 分类损失使用 `BCEWithLogitsLoss`
  - 框分配器使用 `TaskAlignedAssigner`
  - 框回归使用 IoU + DFL 组合
  - loss 最后乘以超参数中的 `box / cls / dfl`
- 这意味着如果后续要改 baseline 损失，最直接的入口通常是:
  - `ultralytics/utils/loss.py`
  - 或 `ultralytics/nn/tasks.py` 中 `DetectionModel.init_criterion()`

### 11. 当前 baseline 最可能的修改入口

- 如果要改训练超参数:
  - 优先看 `ultralytics/cfg/default.yaml`
  - 或直接改 `mytrain.py` 的 `model.train(...)` 参数
- 如果要改数据集路径/类别:
  - 优先看 `ultralytics/GZ-DET.yaml`
- 如果要改模型结构:
  - 优先看 `ultralytics/cfg/models/11/yolo11.yaml`
  - 以及 `ultralytics/nn/tasks.py` 的 `parse_model()`
- 如果要改训练循环、优化器、冻结策略、保存逻辑:
  - 优先看 `ultralytics/engine/trainer.py`
- 如果要改检测任务专属逻辑:
  - 优先看 `ultralytics/models/yolo/detect/train.py`
- 如果要改标签读取、增强、batch 结构:
  - 优先看 `ultralytics/data/dataset.py`
  - `ultralytics/data/build.py`
  - `ultralytics/data/utils.py`
- 如果要改损失函数或正负样本分配:
  - 优先看 `ultralytics/utils/loss.py`
  - `ultralytics/utils/tal.py`

## `target.md` 需求对照结果

### 对照口径说明

- 本节对照的是“当前项目实际 baseline 训练流程”而不是 `ultralytics` 理论上支持的全部任务。
- 因此状态分为 3 类:
  - `已实现`: 当前项目代码和默认训练流程已经具备。
  - `框架支持但当前未接入`: `ultralytics` 代码里有能力，但当前项目入口、数据和配置没有真正用起来。
  - `未实现`: 当前仓库中没有看到对应模块或可直接使用的实现。

### 1. 与 `target.md` 对照后的已实现项

#### 1.1 基于 YOLO 的多类别病害检测 baseline

- 状态: `已实现`
- 依据:
  - 当前训练入口 `ultralytics/mytrain.py` 使用的是 YOLO 检测训练链路
  - `ultralytics/GZ-DET.yaml` 当前定义了 6 个类别
  - 满足 `target.md` 中“至少检测 3 类桥梁病害”的最低要求
- 当前已具备:
  - 多类别目标检测训练
  - 检测验证
  - mAP 指标统计
  - 检测结果输出基础能力

#### 1.2 通用数据增强与训练流程

- 状态: `已实现`
- 依据:
  - `YOLODataset` 和 `build_yolo_dataset()` 已接入训练流程
  - `default.yaml` 中已有标准增强参数
- 当前已具备的通用增强包括:
  - mosaic
  - 缩放
  - 平移
  - 左右翻转
  - HSV 扰动
  - multi-scale 可选开关

#### 1.3 基本训练工程能力

- 状态: `已实现`
- 当前已具备:
  - PyTorch 训练框架
  - AMP 混合精度
  - DDP 多卡训练
  - EMA
  - early stopping
  - checkpoint 保存与恢复
  - 训练 / 验证日志记录

#### 1.4 检测精度评估指标基础能力

- 状态: `已实现`
- 依据:
  - 检测验证器中已实现 `mAP@0.5:0.95` 统计
  - 检测评估中使用 IoU 阈值序列进行评估
- 说明:
  - 这是“代码层面支持评估”
  - 但当前仓库还没有给出该项目数据集上的实际评测结果

### 2. 框架支持但当前项目未接入的内容

#### 2.1 实例分割训练与 Mask 输出

- 状态: `框架支持但当前未接入`
- 依据:
  - 仓库内存在 `ultralytics/models/yolo/segment/`
  - `SegmentationModel`、`SegmentationTrainer`、`v8SegmentationLoss` 均已存在
- 但当前项目没有接入的地方:
  - `mytrain.py` 走的是 detect，不是 segment
  - 当前项目没有看到桥梁病害实例分割数据配置
  - 当前项目没有 segment 训练入口脚本
- 结论:
  - “像素级分割”能力在框架层面存在
  - 但对本项目当前 baseline 来说，仍然不能算已实现

#### 2.2 掩膜（Mask）结果输出

- 状态: `框架支持但当前未接入`
- 依据:
  - segmentation 分支理论上可输出 mask
- 当前限制:
  - 现有 baseline 使用检测模型，只输出框、类别和置信度
  - 未形成符合 `target.md` 预期的“类别 + Mask + confidence”当前项目结果链路

### 3. 当前 baseline 未实现或明显不足的内容

#### 3.1 面向桥梁病害场景的小目标/细长目标结构优化

- 状态: `未实现`
- `target.md` 明确要求:
  - 针对小目标
  - 针对细长裂缝等极端长宽比目标
  - 做网络结构优化
- 当前情况:
  - 当前项目直接使用标准 `yolo11.yaml`
  - 没有看到针对桥梁裂缝、小目标、长宽比极端目标的专门结构修改
  - 没有看到新增 neck/head、注意力模块、特征融合模块或专门 anchor/free 策略调整记录

#### 3.2 针对复杂干扰场景的专门抗干扰设计

- 状态: `未实现`
- `target.md` 提到的干扰包括:
  - 阴影
  - 污渍
  - 接缝
  - 爬墙虎
  - 反光与遮挡
- 当前情况:
  - 现有 baseline 只有通用训练和通用增强
  - 没看到专门的抗干扰模块、损失约束、难例挖掘或专门负样本策略
- 结论:
  - 当前只能算“依赖通用训练带来的有限鲁棒性”
  - 不能算已经完成业务目标里的抗干扰能力设计

#### 3.3 针对桥下光照不均、运动模糊的专门图像预处理

- 状态: `未实现`
- 当前情况:
  - 训练前处理主要是标准数据增强与归一化
  - 没看到低照度增强、去模糊、反光抑制或阴影校正等专门预处理流程

#### 3.4 基于分割结果的量化计算模块

- 状态: `未实现`
- `target.md` 明确要求:
  - 基于分割结果估算病害物理长度
  - 估算最大宽度
  - 结合像素到物理尺寸转换系数
- 当前情况:
  - 仓库中没有看到该类几何量化模块
  - 没有看到病害长度、宽度、面积占比计算脚本
  - 没有看到报告生成前的量化结果导出逻辑

#### 3.5 当前项目层面的像素级分割任务落地

- 状态: `未实现`
- 虽然框架里有 segment 能力，但对本项目来说当前仍未落地
- 缺失内容包括:
  - 分割数据组织
  - 分割训练入口
  - 分割评测结果
  - 面向桥梁病害的 mask 推理流程

#### 3.6 4K 图像 200ms 内推理效率验证

- 状态: `未实现`
- 当前情况:
  - 没有看到 benchmark 脚本或实测记录
  - 没有看到针对 4K 单图推理时延的专门优化与验证

#### 3.7 达到或超过基线模型的效果证明

- 状态: `未实现`
- 当前情况:
  - 代码里有评测能力
  - 但仓库没有提供当前项目在参考测试集上的 mAP、IoU、速度对比结果
- 结论:
  - 目前无法证明“达到或不低于现有 YOLO / Transformer 基线”

### 4. 当前项目总体判断

- 当前仓库已经具备一个可运行的 YOLO 检测 baseline。
- 如果目标只是“多类别病害检测 baseline 训练”，当前代码基本够用。
- 如果目标是完成 `target.md` 里的完整任务，则当前差距主要集中在:
  - 实例分割任务正式接入
  - 面向桥梁病害的小目标/细长目标结构改进
  - 复杂干扰场景鲁棒性设计
  - 专门图像增强与预处理
  - 病害几何量化模块
  - 速度与精度实测验证

### 5. 按优先级建议的后续改造顺序

1. 先修正数据集 YAML 路径问题，确保 baseline 可以稳定训练和验证。
2. 明确本项目下一阶段是否走 `detect` 还是 `segment` 主线。
3. 如果要满足 `target.md`，优先把实例分割链路接通。
4. 在分割或检测主线确定后，再做桥梁病害场景定制化结构改进。
5. 最后补充量化计算模块、速度测试和效果对比报告。

## 建议的下一阶段工作

1. 统一文档与配置命名，先修正 `README.md` 中的 `GYU-DET.yaml / GZ-DET.yaml` 不一致问题。
2. 核对真实数据集目录结构，确认 `ultralytics/GZ-DET.yaml` 的 `train/val/test/path` 写法。
3. 修复 `txt2xml.py` 的类别映射，使其与 `GZ-DET.yaml` 完全一致。
4. 视需要补充训练、验证、推理的可复现命令说明。

## 已完成阶段记录

### 阶段 1

- 已浏览项目根目录与核心文件。
- 已确认 `ultralytics` 为 YOLOv11 训练代码目录。
- 已创建并初始化 `codex.md`，后续每完成一个小阶段将继续更新。
- 已检查 `codex.md` 文件字节内容，确认以 UTF-8 形式保存。

### 阶段 2

- 已阅读当前 YOLO baseline 训练主链路。
- 已梳理 `mytrain.py -> YOLO -> Model.train -> DetectionTrainer -> DetectionModel -> v8DetectionLoss` 的调用关系。
- 已记录训练循环、数据加载、模型构建、损失函数和默认配置的关键实现位置。
- 已将后续最可能修改的代码入口整理到文档中，便于基于 baseline 继续开发。

### 阶段 3

- 已读取并解析 `target.md` 的任务要求。
- 已对照当前 baseline 训练流程，区分出 `已实现 / 框架支持但当前未接入 / 未实现` 三类状态。
- 已确认当前仓库本质上只完成了“多类别目标检测 baseline”，尚未完成 `target.md` 所要求的实例分割、量化计算和面向桥梁场景的定制化优化。

### 阶段 4

- 已围绕“像素级分割是否适合采用 `diffusion-for-ood`”完成一次外部文献调研与项目适配性分析。
- 已确认 `Diffusion for Out-of-Distribution Detection on Road Scenes and Beyond` 为 ECCV 2024 方法，核心目标是 `语义分割场景中的像素级 OOD/异常区域检测`，不是多类别病害实例分割主干。
- 已确认该方法 DOoD 的基本依赖关系是:
  - 先有一个已训练好的语义分割模型提取 embedding
  - 再在 embedding 上训练一个 MLP diffusion 模型
  - 推理时输出的是 `pixel-wise OOD score`
- 这与本项目 `target.md` 里要求的输出存在关键差异:
  - 本项目目标是输出 `病害类别 + mask + confidence`
  - DOoD 更直接输出的是 `是否偏离已知分布/是否异常` 的像素级分数
  - 因此它不能直接替代多类别病害分割主模型
- 已确认官方实现工程形态与当前仓库也不一致:
  - 官方仓库基于 `MMSegmentation`
  - 当前项目主训练链路基于 `Ultralytics / YOLO`
  - 官方 README 里训练代码仍标注为 “coming soon”，说明直接复用难度不低
- 当前适配性判断:
  - `可以作为辅助模块考虑`
  - `不建议作为本项目像素级多类别分割的第一主线`
- 更合理的使用位置有 3 类:
  - 作为开放集识别模块，用来发现训练类别之外的未知病害或异常干扰区域
  - 作为误检抑制或困难区域重打分模块，辅助主分割网络过滤不可信区域
  - 在标注不足时，作为二阶段异常粗定位工具，帮助人工筛图或生成候选 mask
- 若本项目下一阶段追求的是“先做出可验收的像素级病害分割结果”，当前更推荐的主线仍然是:
  - 先接通 `ultralytics` 自带 `segment` 训练链路，建立 supervised segmentation baseline
  - 再视需要叠加 OOD / anomaly 分支

### 阶段 5

- 已围绕“当前项目是否可以改为 `RT-DETR` 架构”完成一次本地代码核对和官方能力确认。
- 本地代码层面的确认结果:
  - `ultralytics/nn/tasks.py` 中已存在 `RTDETRDetectionModel`
  - `ultralytics/cfg/__init__.py` 中也存在对 `rtdetr` 模型名的分发逻辑
  - 说明当前仓库的这份 `ultralytics` 代码并非完全不认识 RT-DETR
- 但本地仓库还存在一个关键工程问题:
  - `ultralytics/models/__init__.py` 里导入了 `fastsam / nas / rtdetr / sam`
  - 当前仓库实际缺少这些对应模块目录
  - 直接执行 `from ultralytics import RTDETR` 时会先因为 `ultralytics.models.fastsam` 缺失而报错
  - 这说明当前仓库内置的 `ultralytics` 拷贝并不完整，若直接切换到 RT-DETR，首先要补齐或修正包结构
- 官方能力层面的确认结果:
  - Ultralytics 官方文档当前支持 RT-DETR 的 `train / val / predict / export`
  - 但任务类型仅标为 `Object Detection`
  - 因此 RT-DETR 在当前官方主链路里是 `检测模型`，不是像素级分割模型
- 面向本项目目标的适配结论:
  - `可以改成 RT-DETR 检测 baseline`
  - `不能把 RT-DETR 直接当成像素级分割方案`
- 更准确地说，RT-DETR 对本项目的作用主要是:
  - 作为目标检测主干，与 YOLO 检测 baseline 做性能对比
  - 用于验证 Transformer 检测器在桥梁病害、小目标和复杂背景上的收益
  - 若要做像素级分割，仍需额外接入 mask 分支或改用真正的 segmentation 架构
- 当前最现实的实施顺序仍然是:
  - 若先做检测对比实验，可把 `mytrain.py` 改为 RT-DETR 训练入口
  - 若目标是完成 `target.md` 的像素级分割交付，不建议把 RT-DETR 当作主线终点
