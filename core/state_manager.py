"""
状态管理器

负责管理论文写作项目的全局状态和工作流检查点
支持：
- 项目状态持久化（SQLite）
- 检查点保存/恢复
- 状态查询与导出
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WorkflowStage:
    """工作流阶段定义"""
    RESEARCH = "research"           # 文献调研
    GAP_ANALYSIS = "gap_analysis"   # Gap 分析
    METHOD_DESIGN = "method_design" # 方法设计
    EXPERIMENT = "experiment"       # 实验规划
    WRITING = "writing"             # 论文撰写
    COMPLETED = "completed"         # 已完成


# 检查点定义
CHECKPOINTS = {
    "cp1": {"stage": WorkflowStage.RESEARCH, "name": "确认研究主题"},
    "cp2": {"stage": WorkflowStage.RESEARCH, "name": "确认文献筛选结果"},
    "cp3": {"stage": WorkflowStage.GAP_ANALYSIS, "name": "确认 Gap 分析报告"},
    "cp4": {"stage": WorkflowStage.METHOD_DESIGN, "name": "确认技术方案"},
    "cp5": {"stage": WorkflowStage.METHOD_DESIGN, "name": "确认创新性评估"},
    "cp6": {"stage": WorkflowStage.EXPERIMENT, "name": "确认实验设计"},
    "cp7": {"stage": WorkflowStage.EXPERIMENT, "name": "确认评价指标"},
    "cp8": {"stage": WorkflowStage.WRITING, "name": "确认论文大纲"},
    "cp9": {"stage": WorkflowStage.WRITING, "name": "逐章确认"},
    "cp10": {"stage": WorkflowStage.WRITING, "name": "最终审阅"},
}


class PaperProject:
    """
    论文项目数据模型

    包含项目的所有状态信息
    """

    def __init__(self, project_id: str = None):
        import uuid
        self.project_id = project_id or str(uuid.uuid4())
        self.title: str = ""
        self.domain: str = ""
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

        # 当前阶段
        self.current_stage: str = WorkflowStage.RESEARCH

        # 文献综述数据
        self.literature_review: dict = {
            "search_queries": [],
            "papers": [],
            "selected_papers": [],
            "summary": "",
        }

        # Gap 分析数据
        self.gap_analysis: dict = {
            "existing_methods": [],
            "limitations": [],
            "research_gaps": [],
            "confirmed": False,
        }

        # 方法设计数据
        self.method_design: dict = {
            "proposed_method": {},
            "technical_route": [],
            "novelty_score": 0.0,
            "confirmed": False,
        }

        # 实验计划数据
        self.experiment_plan: dict = {
            "datasets": [],
            "baselines": [],
            "ablation_studies": [],
            "metrics": [],
            "confirmed": False,
        }

        # 论文草稿数据
        self.paper_draft: dict = {
            "outline": {},
            "sections": {},
            "references": [],
            "format": "latex",
        }

        # 检查点历史
        self.checkpoint_history: list[dict] = []

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "project_id": self.project_id,
            "title": self.title,
            "domain": self.domain,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "current_stage": self.current_stage,
            "literature_review": self.literature_review,
            "gap_analysis": self.gap_analysis,
            "method_design": self.method_design,
            "experiment_plan": self.experiment_plan,
            "paper_draft": self.paper_draft,
            "checkpoint_history": self.checkpoint_history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PaperProject":
        """从字典创建"""
        project = cls(data.get("project_id"))
        project.title = data.get("title", "")
        project.domain = data.get("domain", "")
        project.created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        project.updated_at = datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        project.current_stage = data.get("current_stage", WorkflowStage.RESEARCH)
        project.literature_review = data.get("literature_review", project.literature_review)
        project.gap_analysis = data.get("gap_analysis", project.gap_analysis)
        project.method_design = data.get("method_design", project.method_design)
        project.experiment_plan = data.get("experiment_plan", project.experiment_plan)
        project.paper_draft = data.get("paper_draft", project.paper_draft)
        project.checkpoint_history = data.get("checkpoint_history", [])
        return project

    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now()


class StateManager:
    """
    状态管理器

    使用 SQLite 存储项目状态，支持检查点机制
    """

    def __init__(self, db_path: str = None, project_id: str = None):
        """
        初始化状态管理器

        Args:
            db_path: SQLite 数据库路径
            project_id: 项目 ID（可选，不传则创建新项目）
        """
        self.db_path = db_path or "paper_assistant.db"
        self.current_project: Optional[PaperProject] = None
        self._init_db()

        if project_id:
            self.load_project(project_id)
        else:
            self.create_project()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 项目表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                title TEXT,
                domain TEXT,
                created_at TEXT,
                updated_at TEXT,
                current_stage TEXT,
                state_data TEXT
            )
        """)

        # 检查点表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                checkpoint_id TEXT,
                stage TEXT,
                name TEXT,
                data TEXT,
                created_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"数据库已初始化：{self.db_path}")

    def create_project(self, title: str = "", domain: str = "") -> PaperProject:
        """
        创建新项目

        Args:
            title: 项目标题
            domain: 研究领域

        Returns:
            PaperProject: 创建的项目
        """
        project = PaperProject()
        project.title = title
        project.domain = domain
        self.current_project = project
        self._save_project()
        logger.info(f"已创建新项目：{project.project_id}")
        return project

    def load_project(self, project_id: str) -> Optional[PaperProject]:
        """
        加载项目

        Args:
            project_id: 项目 ID

        Returns:
            PaperProject: 项目实例
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT state_data FROM projects WHERE project_id = ?",
            (project_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            data = json.loads(row[0])
            self.current_project = PaperProject.from_dict(data)
            logger.info(f"已加载项目：{project_id}")
            return self.current_project
        else:
            logger.warning(f"项目不存在：{project_id}")
            return None

    def _save_project(self):
        """保存项目到数据库"""
        if not self.current_project:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        self.current_project.update_timestamp()
        data = self.current_project.to_dict()

        cursor.execute("""
            INSERT OR REPLACE INTO projects
            (project_id, title, domain, created_at, updated_at, current_stage, state_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.current_project.project_id,
            self.current_project.title,
            self.current_project.domain,
            self.current_project.created_at.isoformat(),
            self.current_project.updated_at.isoformat(),
            self.current_project.current_stage,
            json.dumps(data),
        ))

        conn.commit()
        conn.close()

    def save_checkpoint(self, checkpoint_id: str, data: dict = None) -> bool:
        """
        保存检查点

        Args:
            checkpoint_id: 检查点 ID (如 "cp1", "cp2")
            data: 要保存的数据

        Returns:
            是否成功
        """
        if not self.current_project:
            return False

        checkpoint_info = CHECKPOINTS.get(checkpoint_id)
        if not checkpoint_info:
            logger.warning(f"未知检查点：{checkpoint_id}")
            return False

        # 保存检查点到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO checkpoints (project_id, checkpoint_id, stage, name, data, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.current_project.project_id,
            checkpoint_id,
            checkpoint_info["stage"],
            checkpoint_info["name"],
            json.dumps(data or {}),
            datetime.now().isoformat(),
        ))

        conn.commit()
        conn.close()

        # 更新项目状态
        self.current_project.checkpoint_history.append({
            "checkpoint_id": checkpoint_id,
            "stage": checkpoint_info["stage"],
            "name": checkpoint_info["name"],
            "data": data,
            "created_at": datetime.now().isoformat(),
        })

        # 更新当前阶段
        self.current_project.current_stage = checkpoint_info["stage"]
        self._save_project()

        logger.info(f"已保存检查点：{checkpoint_id}")
        return True

    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        恢复检查点

        Args:
            checkpoint_id: 检查点 ID

        Returns:
            是否成功
        """
        if not self.current_project:
            return False

        # 从数据库获取检查点
        checkpoint_key = next(
            (k for k, v in CHECKPOINTS.items() if k == checkpoint_id),
            None
        )
        if not checkpoint_key:
            logger.warning(f"未知检查点：{checkpoint_id}")
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT data FROM checkpoints WHERE project_id = ? AND checkpoint_id = ?",
            (self.current_project.project_id, checkpoint_id)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            data = json.loads(row[0])
            self.current_project.state = data
            logger.info(f"已恢复检查点：{checkpoint_id}")
            return True
        else:
            logger.warning(f"检查点不存在：{checkpoint_id}")
            return False

    def get_checkpoint(self, checkpoint_id: str) -> Optional[dict]:
        """获取检查点数据"""
        if not self.current_project:
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT data FROM checkpoints WHERE project_id = ? AND checkpoint_id = ?",
            (self.current_project.project_id, checkpoint_id)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def list_checkpoints(self) -> list[dict]:
        """列出所有检查点"""
        if not self.current_project:
            return []

        return self.current_project.checkpoint_history

    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        回滚到指定检查点

        Args:
            checkpoint_id: 检查点 ID

        Returns:
            是否成功
        """
        if not self.current_project:
            return False

        # 获取检查点数据
        checkpoint_data = self.get_checkpoint(checkpoint_id)
        if checkpoint_data is None:
            return False

        # 恢复检查点对应的阶段数据
        checkpoint_info = CHECKPOINTS.get(checkpoint_id)
        if not checkpoint_info:
            return False

        stage = checkpoint_info["stage"]

        # 根据阶段恢复数据
        if stage == WorkflowStage.RESEARCH:
            self.current_project.literature_review = checkpoint_data.get("literature_review", {})
        elif stage == WorkflowStage.GAP_ANALYSIS:
            self.current_project.gap_analysis = checkpoint_data.get("gap_analysis", {})
        elif stage == WorkflowStage.METHOD_DESIGN:
            self.current_project.method_design = checkpoint_data.get("method_design", {})
        elif stage == WorkflowStage.EXPERIMENT:
            self.current_project.experiment_plan = checkpoint_data.get("experiment_plan", {})
        elif stage == WorkflowStage.WRITING:
            self.current_project.paper_draft = checkpoint_data.get("paper_draft", {})

        self.current_project.current_stage = stage
        self._save_project()

        logger.info(f"已回滚到检查点：{checkpoint_id}")
        return True

    def get_current_stage(self) -> str:
        """获取当前阶段"""
        if not self.current_project:
            return WorkflowStage.RESEARCH
        return self.current_project.current_stage

    def set_stage(self, stage: str):
        """设置当前阶段"""
        if self.current_project:
            self.current_project.current_stage = stage
            self._save_project()

    # ==================== 项目数据访问 ====================

    def update_literature_review(self, data: dict):
        """更新文献综述数据"""
        if self.current_project:
            self.current_project.literature_review.update(data)
            self._save_project()

    def update_gap_analysis(self, data: dict):
        """更新 Gap 分析数据"""
        if self.current_project:
            self.current_project.gap_analysis.update(data)
            self._save_project()

    def update_method_design(self, data: dict):
        """更新方法设计数据"""
        if self.current_project:
            self.current_project.method_design.update(data)
            self._save_project()

    def update_experiment_plan(self, data: dict):
        """更新实验计划数据"""
        if self.current_project:
            self.current_project.experiment_plan.update(data)
            self._save_project()

    def update_paper_draft(self, data: dict):
        """更新论文草稿数据"""
        if self.current_project:
            self.current_project.paper_draft.update(data)
            self._save_project()

    def get_project_state(self) -> Optional[dict]:
        """获取完整的项目状态"""
        if not self.current_project:
            return None
        return self.current_project.to_dict()

    def export_state(self, filepath: str):
        """导出项目状态到 JSON 文件"""
        if not self.current_project:
            return

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.current_project.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"项目状态已导出：{filepath}")

    def import_state(self, filepath: str) -> bool:
        """从 JSON 文件导入项目状态"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.current_project = PaperProject.from_dict(data)
            self._save_project()
            logger.info(f"项目状态已导入：{filepath}")
            return True
        except Exception as e:
            logger.exception(f"导入失败：{e}")
            return False

    # ==================== 上下文管理 ====================

    def __enter__(self) -> "StateManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.current_project:
            self._save_project()


# 全局状态管理器实例
_state_manager: Optional[StateManager] = None


def get_state_manager(db_path: str = None) -> StateManager:
    """获取全局状态管理器"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager(db_path)
    return _state_manager


def reset_state_manager():
    """重置状态管理器"""
    global _state_manager
    _state_manager = None
