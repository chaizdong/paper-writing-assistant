"""
MCP 工具注册中心

统一管理 MCP 工具的注册、发现和调用
支持：
- 工具注册与注销
- 能力查询
- 统一调用接口
- 错误处理与重试
- 结果缓存
"""

import logging
import hashlib
import json
from typing import Any, Callable, Optional
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class ToolResult:
    """工具执行结果"""

    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error

    def __repr__(self) -> str:
        if self.success:
            return f"ToolResult(success=True, data={type(self.data).__name__})"
        return f"ToolResult(success=False, error={self.error})"


class MCPServer:
    """
    MCP 服务器表示

    封装一个 MCP 服务器的连接和调用
    """

    def __init__(
        self,
        name: str,
        command: str,
        args: list[str],
        capabilities: list[str] = None,
        enabled: bool = True,
    ):
        self.name = name
        self.command = command
        self.args = args
        self.capabilities = capabilities or []
        self.enabled = enabled
        self._connected = False

    def connect(self) -> bool:
        """连接到 MCP 服务器"""
        # 实际实现中这里会启动 subprocess 并建立通信
        self._connected = True
        logger.info(f"MCP 服务器已连接：{self.name}")
        return True

    def disconnect(self):
        """断开连接"""
        self._connected = False
        logger.info(f"MCP 服务器已断开：{self.name}")

    def call(self, tool_name: str, args: dict) -> ToolResult:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            ToolResult: 执行结果
        """
        if not self._connected:
            return ToolResult(success=False, error="MCP 服务器未连接")

        # 实际实现中这里会通过 stdio 与 MCP 服务器通信
        # 这里提供一个模拟实现
        logger.debug(f"调用 MCP 工具：{self.name}/{tool_name}, args={args}")
        return ToolResult(success=True, data={"mock": True})

    def __repr__(self) -> str:
        status = "connected" if self._connected else "disconnected"
        return f"<MCPServer {self.name} ({status})>"


class CacheEntry:
    """缓存条目"""

    def __init__(self, data: Any, ttl_seconds: int = 300):
        self.data = data
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class ToolRegistry:
    """
    工具注册中心

    单例模式，管理所有可用的 MCP 工具
    """

    _instance: Optional["ToolRegistry"] = None

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._servers: dict[str, MCPServer] = {}
        self._tools: dict[str, dict] = {}  # tool_name -> {server, handler, ...}
        self._cache: dict[str, CacheEntry] = {}
        self._cache_enabled = True
        self._default_ttl = 300  # 5 分钟
        self._initialized = True
        logger.info("ToolRegistry 已初始化")

    # ==================== 服务器管理 ====================

    def register_server(self, server: MCPServer) -> bool:
        """
        注册 MCP 服务器

        Args:
            server: MCP 服务器实例

        Returns:
            是否成功
        """
        if server.name in self._servers:
            logger.warning(f"MCP 服务器已存在：{server.name}")
            return False

        self._servers[server.name] = server
        logger.info(f"已注册 MCP 服务器：{server.name}")
        return True

    def unregister_server(self, name: str) -> bool:
        """注销 MCP 服务器"""
        if name not in self._servers:
            return False

        server = self._servers.pop(name)
        server.disconnect()
        logger.info(f"已注销 MCP 服务器：{name}")
        return True

    def get_server(self, name: str) -> Optional[MCPServer]:
        """获取 MCP 服务器"""
        return self._servers.get(name)

    def list_servers(self) -> list[dict]:
        """列出所有 MCP 服务器"""
        return [
            {
                "name": s.name,
                "command": s.command,
                "capabilities": s.capabilities,
                "enabled": s.enabled,
                "connected": s._connected,
            }
            for s in self._servers.values()
        ]

    # ==================== 工具注册 ====================

    def register_tool(
        self,
        name: str,
        server_name: str = None,
        handler: Callable = None,
        description: str = "",
        parameters: dict = None,
    ):
        """
        注册工具

        Args:
            name: 工具名称
            server_name: 所属 MCP 服务器名称
            handler: 处理函数（本地工具）
            description: 工具描述
            parameters: 参数 schema
        """
        self._tools[name] = {
            "name": name,
            "server_name": server_name,
            "handler": handler,
            "description": description,
            "parameters": parameters or {},
        }
        logger.info(f"已注册工具：{name}")

    def unregister_tool(self, name: str) -> bool:
        """注销工具"""
        if name not in self._tools:
            return False
        del self._tools[name]
        logger.info(f"已注销工具：{name}")
        return True

    def get_tool(self, name: str) -> Optional[dict]:
        """获取工具信息"""
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        """列出所有可用工具"""
        return list(self._tools.values())

    def has_tool(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools

    # ==================== 工具调用 ====================

    def call(
        self,
        tool_name: str,
        args: dict = None,
        use_cache: bool = True,
        ttl: int = None,
        retries: int = 1,
    ) -> ToolResult:
        """
        调用工具

        Args:
            tool_name: 工具名称
            args: 工具参数
            use_cache: 是否使用缓存
            ttl: 缓存 TTL（秒）
            retries: 重试次数

        Returns:
            ToolResult: 执行结果
        """
        args = args or {}

        # 检查缓存
        cache_key = self._get_cache_key(tool_name, args)
        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired():
                logger.debug(f"缓存命中：{tool_name}")
                return ToolResult(success=True, data=entry.data)
            else:
                # 清除过期缓存
                del self._cache[cache_key]

        # 获取工具信息
        tool_info = self.get_tool(tool_name)
        if not tool_info:
            return ToolResult(success=False, error=f"工具不存在：{tool_name}")

        # 执行工具
        result = None
        last_error = None

        for attempt in range(retries + 1):
            try:
                result = self._execute_tool(tool_info, args)
                if result.success:
                    break
                last_error = result.error
            except Exception as e:
                logger.exception(f"工具执行失败：{tool_name}, attempt={attempt + 1}")
                last_error = str(e)

        if not result.success:
            return result

        # 缓存结果
        if use_cache and result.success:
            self._cache[cache_key] = CacheEntry(
                result.data, ttl_seconds=ttl or self._default_ttl
            )

        return result

    def _execute_tool(self, tool_info: dict, args: dict) -> ToolResult:
        """执行工具"""
        server_name = tool_info.get("server_name")
        handler = tool_info.get("handler")

        # 本地处理函数
        if handler:
            try:
                data = handler(**args)
                return ToolResult(success=True, data=data)
            except Exception as e:
                return ToolResult(success=False, error=str(e))

        # MCP 服务器工具
        if server_name:
            server = self.get_server(server_name)
            if not server:
                return ToolResult(success=False, error=f"MCP 服务器不存在：{server_name}")
            return server.call(tool_info["name"], args)

        return ToolResult(success=False, error="工具没有处理器或服务器")

    def _get_cache_key(self, tool_name: str, args: dict) -> str:
        """生成缓存键"""
        key_str = f"{tool_name}:{json.dumps(args, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    # ==================== 缓存管理 ====================

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("缓存已清空")

    def invalidate_cache(self, tool_name: str, args: dict = None):
        """使特定缓存失效"""
        if args:
            cache_key = self._get_cache_key(tool_name, args)
            self._cache.pop(cache_key, None)
        else:
            # 清除所有该工具的缓存
            prefix = hashlib.md5(f"{tool_name}:".encode()).hexdigest()
            keys_to_remove = [
                k for k in self._cache.keys() if k.startswith(prefix[:16])
            ]
            for key in keys_to_remove:
                del self._cache[key]
        logger.debug(f"缓存已失效：{tool_name}")

    def set_cache_enabled(self, enabled: bool):
        """启用/禁用缓存"""
        self._cache_enabled = enabled

    # ==================== 工具装饰器 ====================

    def tool(
        self,
        name: str = None,
        description: str = "",
        parameters: dict = None,
    ):
        """
        工具注册装饰器

        用法:
            @registry.tool(description="搜索论文")
            def search_papers(query: str) -> list:
                ...
        """

        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            self.register_tool(
                name=tool_name,
                handler=func,
                description=description,
                parameters=parameters,
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    # ==================== 批量加载 ====================

    def load_from_config(self, config: dict):
        """
        从配置加载 MCP 服务器和工具

        Args:
            config: 配置字典
                {
                    "mcp_servers": {
                        "arxiv": {
                            "command": "npx",
                            "args": ["-y", "mcp-server-arxiv"],
                            "capabilities": ["search", "download"],
                            "enabled": true
                        }
                    },
                    "tools": {
                        "search_papers": {
                            "server": "arxiv",
                            "description": "..."
                        }
                    }
                }
        """
        # 加载服务器
        servers_config = config.get("mcp_servers", {})
        for name, server_config in servers_config.items():
            if server_config.get("enabled", True):
                server = MCPServer(
                    name=name,
                    command=server_config["command"],
                    args=server_config.get("args", []),
                    capabilities=server_config.get("capabilities", []),
                )
                self.register_server(server)
                server.connect()

        # 加载工具
        tools_config = config.get("tools", {})
        for name, tool_config in tools_config.items():
            self.register_tool(
                name=name,
                server_name=tool_config.get("server"),
                description=tool_config.get("description", ""),
            )

        logger.info(f"从配置加载完成：{len(self._servers)} servers, {len(self._tools)} tools")


# 全局实例
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """获取全局工具注册中心实例"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def reset_registry():
    """重置全局实例"""
    global _registry
    _registry = ToolRegistry()
