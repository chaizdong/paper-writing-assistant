"""
实验规划 Agent

设计实验方案，选择数据集、baseline 和评价指标
"""

import logging
from typing import Any, Optional

from agents.base import BaseAgent, TaskRequest, TaskResponse

logger = logging.getLogger(__name__)


class ExperimentAgent(BaseAgent):
    """
    实验规划 Agent

    职责:
    - 选择数据集
    - 选择 baseline 方法
    - 设计消融实验
    - 定义评价指标
    """

    def __init__(self, agent_id: str = "experiment_agent"):
        super().__init__(
            agent_id=agent_id,
            name="ExperimentAgent",
            description="实验规划 Agent - 设计实验方案、选择数据集和评价指标"
        )

    def get_capabilities(self) -> list[str]:
        return [
            "select_datasets - 选择数据集",
            "choose_baselines - 选择 baseline",
            "design_ablation - 设计消融实验",
            "define_metrics - 定义评价指标",
        ]

    def execute(self, task_request: TaskRequest) -> TaskResponse:
        """
        执行实验规划任务

        Args:
            task_request: 任务请求，包含 method 数据

        Returns:
            TaskResponse: 包含实验设计方案
        """
        try:
            # 解析输入
            input_data = task_request.input_data or {}
            method = input_data.get("method", {})
            method_name = method.get("name", "Our Method")
            method_keywords = method.get("keywords", [])

            logger.info(f"开始实验规划：方法={method_name}")

            # 发送进度更新
            self.send_progress(1, 5, "正在分析方法特点...")

            # 分析方法特点，确定任务类型
            task_type = self._analyze_task_type(method)

            self.send_progress(2, 5, "正在选择数据集...")

            # 选择数据集
            datasets = self._select_datasets(task_type, method_keywords)

            self.send_progress(3, 5, "正在选择 baseline 方法...")

            # 选择 baseline
            baselines = self._choose_baselines(task_type)

            self.send_progress(4, 5, "正在设计评价指标...")

            # 定义评价指标
            metrics = self._define_metrics(task_type)

            self.send_progress(5, 5, "正在设计消融实验...")

            # 设计消融实验
            ablation_studies = self._design_ablation(method)

            # 生成实验计划
            experiment_plan = self._generate_experiment_plan(
                method_name=method_name,
                datasets=datasets,
                baselines=baselines,
                metrics=metrics,
                ablation_studies=ablation_studies,
            )

            logger.info("实验规划完成")

            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": True,
                    "result": {
                        "task_type": task_type,
                        "datasets": datasets,
                        "baselines": baselines,
                        "metrics": metrics,
                        "ablation_studies": ablation_studies,
                        "experiment_plan": experiment_plan,
                    }
                }
            )

        except Exception as e:
            logger.exception(f"实验规划失败：{e}")
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": False,
                    "error_message": str(e),
                }
            )

    def _analyze_task_type(self, method: dict) -> str:
        """
        分析方法特点，确定任务类型
        """
        keywords = method.get("keywords", [])
        design_principle = method.get("design_principle", "")

        # 根据关键词判断任务类型
        if "分类" in design_principle or "Classification" in method.get("name", ""):
            return "classification"
        elif "检测" in design_principle or "Detection" in method.get("name", ""):
            return "detection"
        elif "分割" in design_principle or "Segmentation" in method.get("name", ""):
            return "segmentation"
        elif "预测" in design_principle or "Forecasting" in method.get("name", ""):
            return "forecasting"
        elif "生成" in design_principle or "Generation" in method.get("name", ""):
            return "generation"
        elif any(kw in keywords for kw in ["少样本", "FewShot"]):
            return "few_shot_learning"
        else:
            # 默认返回通用任务类型
            return "general"

    def _select_datasets(
        self,
        task_type: str,
        method_keywords: list[str]
    ) -> list[dict]:
        """
        选择合适的数据集
        """
        # 常见数据集映射
        dataset_map = {
            "classification": [
                {"name": "ImageNet", "description": "大规模图像分类数据集", "reason": "最广泛使用的分类 benchmark"},
                {"name": "CIFAR-10/100", "description": "标准图像分类数据集", "reason": "快速验证方法有效性"},
            ],
            "detection": [
                {"name": "COCO", "description": "目标检测标准数据集", "reason": "最权威的目标检测 benchmark"},
                {"name": "Pascal VOC", "description": "经典目标检测数据集", "reason": "便于对比历史方法"},
            ],
            "segmentation": [
                {"name": "ADE20K", "description": "场景解析数据集", "reason": "语义分割标准 benchmark"},
                {"name": "Cityscapes", "description": "城市场景分割数据集", "reason": "贴近实际应用"},
            ],
            "forecasting": [
                {"name": "ETT", "description": "电力变压器温度数据集", "reason": "时间序列预测常用"},
                {"name": "Weather", "description": "气象数据集", "reason": "标准时间序列 benchmark"},
            ],
            "generation": [
                {"name": "ImageNet", "description": "图像生成质量评估", "reason": "标准生成模型 benchmark"},
                {"name": "FFHQ", "description": "高质量人脸数据集", "reason": "人脸生成任务标准"},
            ],
            "few_shot_learning": [
                {"name": "miniImageNet", "description": "少样本学习标准数据集", "reason": "Few-shot 分类 benchmark"},
                {"name": "tieredImageNet", "description": "大规模少样本数据集", "reason": "更严格的评估"},
            ],
            "general": [
                {"name": "Standard Benchmark", "description": "领域标准数据集", "reason": "根据具体任务选择"},
            ],
        }

        return dataset_map.get(task_type, dataset_map["general"])

    def _choose_baselines(self, task_type: str) -> list[dict]:
        """
        选择 baseline 方法
        """
        # 常见 baseline 映射
        baseline_map = {
            "classification": [
                {"name": "ResNet-50", "citation": "He et al. CVPR 2016", "reason": "经典 baseline"},
                {"name": "Vision Transformer (ViT)", "citation": "Dosovitskiy et al. ICLR 2021", "reason": "Transformer 代表"},
                {"name": "SOTA-2024", "citation": "Latest work", "reason": "最新 SOTA 方法"},
            ],
            "detection": [
                {"name": "Faster R-CNN", "citation": "Ren et al. NeurIPS 2015", "reason": "两阶段代表"},
                {"name": "YOLO v8", "citation": "Ultralytics 2023", "reason": "单阶段代表"},
                {"name": "DETR", "citation": "Carion et al. ECCV 2020", "reason": "Transformer 检测"},
            ],
            "segmentation": [
                {"name": "DeepLab v3+", "citation": "Chen et al. ECCV 2018", "reason": "CNN 代表"},
                {"name": "SegFormer", "citation": "Xie et al. NeurIPS 2021", "reason": "Transformer 代表"},
            ],
            "forecasting": [
                {"name": "ARIMA", "citation": "经典方法", "reason": "传统统计 baseline"},
                {"name": "LSTM", "citation": "Hochreiter et al. 1997", "reason": "深度学习 baseline"},
                {"name": "Transformer", "citation": "Vaswani et al. 2017", "reason": "注意力机制 baseline"},
            ],
            "generation": [
                {"name": "GAN", "citation": "Goodfellow et al. 2014", "reason": "经典生成模型"},
                {"name": "Diffusion Model", "citation": "Ho et al. 2020", "reason": "最新 SOTA"},
            ],
            "few_shot_learning": [
                {"name": "ProtoNet", "citation": "Snell et al. NeurIPS 2017", "reason": "原型网络 baseline"},
                {"name": "MAML", "citation": "Finn et al. ICML 2017", "reason": "元学习代表"},
            ],
            "general": [
                {"name": "Standard Baseline", "citation": "TBD", "reason": "根据具体任务选择"},
            ],
        }

        return baseline_map.get(task_type, baseline_map["general"])

    def _define_metrics(self, task_type: str) -> list[dict]:
        """
        定义评价指标
        """
        metric_map = {
            "classification": [
                {"name": "Top-1 Accuracy", "description": "分类准确率", "type": "main"},
                {"name": "Top-5 Accuracy", "description": "Top-5 准确率", "type": "secondary"},
            ],
            "detection": [
                {"name": "mAP", "description": "平均精度均值", "type": "main"},
                {"name": "AP@0.5", "description": "IoU=0.5 时的 AP", "type": "secondary"},
                {"name": "FPS", "description": "推理速度", "type": "efficiency"},
            ],
            "segmentation": [
                {"name": "mIoU", "description": "平均交并比", "type": "main"},
                {"name": "Pixel Accuracy", "description": "像素级准确率", "type": "secondary"},
            ],
            "forecasting": [
                {"name": "MSE", "description": "均方误差", "type": "main"},
                {"name": "MAE", "description": "平均绝对误差", "type": "secondary"},
            ],
            "generation": [
                {"name": "FID", "description": "Fréchet Inception Distance", "type": "main"},
                {"name": "IS", "description": "Inception Score", "type": "secondary"},
            ],
            "few_shot_learning": [
                {"name": "Accuracy", "description": "少样本分类准确率", "type": "main"},
            ],
            "general": [
                {"name": "Accuracy", "description": "准确率", "type": "main"},
                {"name": "F1 Score", "description": "F1 分数", "type": "secondary"},
            ],
        }

        return metric_map.get(task_type, metric_map["general"])

    def _design_ablation(self, method: dict) -> list[dict]:
        """
        设计消融实验
        """
        components = method.get("components", [])

        ablation_studies = []

        # 为每个组件设计消融变体
        for i, comp in enumerate(components, 1):
            ablation_studies.append({
                "variant": f"w/o {comp['name']}",
                "purpose": f"验证{comp['name']}的作用",
                "description": f"移除{comp['name']}模块，观察性能变化",
            })

        # 如果没有组件，设计通用消融
        if not ablation_studies:
            ablation_studies = [
                {
                    "variant": "Base",
                    "purpose": "基础版本",
                    "description": "不包含任何改进的基础模型",
                },
                {
                    "variant": "+Module A",
                    "purpose": "验证模块 A",
                    "description": "在 Base 基础上添加模块 A",
                },
                {
                    "variant": "+Module A + B",
                    "purpose": "验证完整方法",
                    "description": "完整的方法",
                },
            ]

        return ablation_studies

    def _generate_experiment_plan(
        self,
        method_name: str,
        datasets: list[dict],
        baselines: list[dict],
        metrics: list[dict],
        ablation_studies: list[dict],
    ) -> str:
        """
        生成完整实验计划
        """
        plan = f"""# {method_name} 实验设计方案

## 一、数据集

我们将在以下数据集上验证{method_name}的有效性：

"""
        for ds in datasets:
            plan += f"- **{ds['name']}**: {ds['description']}\n"
            plan += f"  选择理由：{ds['reason']}\n\n"

        plan += """## 二、Baseline 方法

选择以下 SOTA 方法进行对比：

"""
        for bl in baselines:
            plan += f"- **{bl['name']}** ({bl['citation']})\n"
            plan += f"  选择理由：{bl['reason']}\n\n"

        plan += """## 三、评价指标

采用以下指标进行评估：

"""
        for m in metrics:
            plan += f"- **{m['name']}**: {m['description']} ({m['type']})\n"

        plan += """
## 四、消融实验

为验证各模块的有效性，设计以下消融实验：

"""
        for ab in ablation_studies:
            plan += f"- **{ab['variant']}**: {ab['purpose']}\n"
            plan += f"  {ab['description']}\n\n"

        plan += """## 五、实现细节

- **训练环境**: 建议使用 GPU 集群
- **优化器**: Adam/AdamW
- **学习率**: 需要根据数据集调整
- **Batch Size**: 根据显存大小调整
- **训练轮数**: 直到收敛

## 六、预期结果

预期{method_name}在主要指标上超越现有 SOTA 方法，同时保持合理的计算开销。
""".replace("{method_name}", method_name)

        return plan
