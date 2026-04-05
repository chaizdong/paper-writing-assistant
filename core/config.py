"""
配置管理

加载和管理系统配置
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


class Config:
    """
    配置管理器

    支持：
    - 从 YAML 文件加载配置
    - 环境变量覆盖
    - 配置项访问和修改
    """

    def __init__(self, config_path: str = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径
        """
        self._config: dict = {}
        self._config_path = config_path

        if config_path and os.path.exists(config_path):
            self.load(config_path)
        else:
            self._load_default()

    def _load_default(self):
        """加载默认配置"""
        default_path = Path(__file__).parent / "default.yaml"
        if default_path.exists():
            self.load(str(default_path))
        else:
            logger.warning("默认配置文件不存在，使用空配置")
            self._config = self._get_empty_config()

    def _get_empty_config(self) -> dict:
        """获取空配置模板"""
        return {
            "system": {
                "name": "论文写作辅助系统",
                "version": "0.1.0",
                "language": "zh-CN",
            },
            "mcp_servers": {},
            "tools": {},
            "agents": {},
            "workflow": {
                "auto_save": True,
                "checkpoint_on_confirm": True,
                "allow_skip_stage": False,
            },
            "output": {
                "project_dir": "./projects",
                "default_format": "latex",
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

    def load(self, path: str) -> bool:
        """
        从文件加载配置

        Args:
            path: 配置文件路径

        Returns:
            是否成功
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
            logger.info(f"配置已加载：{path}")
            return True
        except Exception as e:
            logger.exception(f"加载配置失败：{e}")
            return False

    def reload(self):
        """重新加载配置"""
        if self._config_path:
            self.load(self._config_path)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键（支持点分隔，如 "mcp_servers.arxiv"）
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        设置配置项

        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_section(self, section: str) -> dict:
        """获取配置节"""
        return self.get(section, {})

    def save(self, path: str = None) -> bool:
        """
        保存配置到文件

        Args:
            path: 保存路径（不传则使用原路径）

        Returns:
            是否成功
        """
        save_path = path or self._config_path
        if not save_path:
            logger.error("没有指定保存路径")
            return False

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(self._config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"配置已保存：{save_path}")
            return True
        except Exception as e:
            logger.exception(f"保存配置失败：{e}")
            return False

    def to_dict(self) -> dict:
        """转换为字典"""
        return self._config.copy()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False
        return True


# 全局配置实例
_config: Optional[Config] = None


def get_config(config_path: str = None) -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reset_config():
    """重置配置"""
    global _config
    _config = None
