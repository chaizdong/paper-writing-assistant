#!/usr/bin/env python3
"""
框架测试脚本

测试核心模块功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_agents_base():
    """测试 Agent 基础模块"""
    print("\n" + "=" * 50)
    print("  测试 Agent 基础模块")
    print("=" * 50)

    from agents.base import (
        BaseAgent, AgentStatus,
        Orchestrator, get_orchestrator,
        MessageType, TaskRequest, TaskResponse
    )

    # 测试消息类型
    print("\n[1] 测试消息类型...")
    msg = TaskRequest(
        sender="test",
        receiver="agent1",
        payload={"task_type": "test", "input_data": {"key": "value"}}
    )
    assert msg.task_type == "test"
    assert msg.input_data == {"key": "value"}
    print("  ✓ TaskRequest 正常")

    # 测试编排器
    print("\n[2] 测试编排器...")
    orch = get_orchestrator()
    assert orch is not None
    print("  ✓ 编排器初始化正常")

    # 测试 Agent 注册
    print("\n[3] 测试 Agent 注册...")
    from agents.base import BaseAgent

    class TestAgent(BaseAgent):
        def execute(self, task_request):
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                payload={"success": True, "result": "test result"}
            )

        def get_capabilities(self):
            return ["test_capability"]

    agent = TestAgent("test_agent_1", "Test Agent")
    orch.register_agent(agent)

    agents = orch.registry.list_agents()
    assert len(agents) == 1
    assert agents[0]["name"] == "Test Agent"
    print("  ✓ Agent 注册正常")

    # 测试任务执行
    print("\n[4] 测试任务执行...")
    response = orch.execute_task(
        agent_id="test_agent_1",
        task_type="test",
        input_data={"test": "data"}
    )
    assert response.success == True
    print("  ✓ 任务执行正常")

    print("\n✓ Agent 基础模块测试通过")
    return True


def test_state_manager():
    """测试状态管理器"""
    print("\n" + "=" * 50)
    print("  测试状态管理器")
    print("=" * 50)

    import tempfile
    from core.state_manager import StateManager, WorkflowStage, CHECKPOINTS

    # 使用临时文件数据库
    db_path = tempfile.mktemp(suffix=".db")

    # 测试项目创建
    print("\n[1] 测试项目创建...")
    state = StateManager(db_path=db_path)
    project = state.current_project
    assert project is not None
    assert project.current_stage == WorkflowStage.RESEARCH
    print(f"  ✓ 项目创建正常 (ID: {project.project_id})")

    # 测试检查点
    print("\n[2] 测试检查点保存...")
    test_data = {"test": "checkpoint_data"}
    result = state.save_checkpoint("cp1", test_data)
    assert result == True

    checkpoints = state.list_checkpoints()
    assert len(checkpoints) == 1
    assert checkpoints[0]["checkpoint_id"] == "cp1"
    print("  ✓ 检查点保存正常")

    # 测试阶段更新
    print("\n[3] 测试阶段更新...")
    state.update_literature_review({"papers": ["paper1", "paper2"]})
    project_state = state.get_project_state()
    assert len(project_state["literature_review"]["papers"]) == 2
    print("  ✓ 状态更新正常")

    # 测试检查点定义
    print("\n[4] 测试检查点定义...")
    assert len(CHECKPOINTS) == 10
    assert CHECKPOINTS["cp1"]["name"] == "确认研究主题"
    assert CHECKPOINTS["cp10"]["name"] == "最终审阅"
    print("  ✓ 检查点定义正常 (共 10 个)")

    print("\n✓ 状态管理器测试通过")
    return True


def test_workflow_engine():
    """测试工作流引擎"""
    print("\n" + "=" * 50)
    print("  测试工作流引擎")
    print("=" * 50)

    import tempfile
    from core.state_manager import StateManager
    from agents.base import get_orchestrator
    from workflows.workflow_engine import WorkflowEngine

    # 初始化
    print("\n[1] 测试工作流引擎初始化...")
    db_path = tempfile.mktemp(suffix=".db")
    state = StateManager(db_path=db_path)
    orch = get_orchestrator()
    engine = WorkflowEngine(state, orch)
    print("  ✓ 工作流引擎初始化正常")

    # 测试阶段列表
    print("\n[2] 测试阶段列表...")
    stages = engine.list_stages()
    assert len(stages) == 5
    stage_names = [s["name"] for s in stages]
    assert stage_names == ["文献调研", "Gap 分析", "方法设计", "实验规划", "论文撰写"]
    print("  ✓ 阶段列表正常")

    # 测试进度
    print("\n[3] 测试进度查询...")
    progress = engine.get_progress()
    assert progress["current_stage"] == "research"
    assert progress["percent"] == 20.0  # 第一阶段
    print(f"  ✓ 进度查询正常 (当前：{progress['current_stage']}, {progress['percent']:.1f}%)")

    # 测试阶段跳转
    print("\n[4] 测试阶段跳转...")
    result = engine.goto_stage("gap_analysis")
    assert result == True
    assert state.get_current_stage() == "gap_analysis"
    print("  ✓ 阶段跳转正常")

    print("\n✓ 工作流引擎测试通过")
    return True


def test_mcp_registry():
    """测试 MCP 工具注册中心"""
    print("\n" + "=" * 50)
    print("  测试 MCP 工具注册中心")
    print("=" * 50)

    from mcp.tool_registry import ToolRegistry, MCPServer, get_registry

    # 测试注册表初始化
    print("\n[1] 测试注册表初始化...")
    registry = get_registry()
    assert registry is not None
    print("  ✓ 注册表初始化正常")

    # 测试服务器注册
    print("\n[2] 测试服务器注册...")
    server = MCPServer(
        name="test_server",
        command="echo",
        args=["test"],
        capabilities=["test_cap"]
    )
    result = registry.register_server(server)
    assert result == True

    servers = registry.list_servers()
    assert len(servers) == 1
    print("  ✓ 服务器注册正常")

    # 测试工具注册
    print("\n[3] 测试工具注册...")

    @registry.tool(description="测试工具", name="test_tool")
    def test_func(x: int) -> int:
        return x * 2

    tools = registry.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "test_tool"
    print("  ✓ 工具注册正常")

    # 测试工具调用
    print("\n[4] 测试工具调用...")
    result = registry.call("test_tool", {"x": 5})
    assert result.success == True
    assert result.data == 10
    print("  ✓ 工具调用正常")

    # 测试缓存
    print("\n[5] 测试缓存功能...")
    result2 = registry.call("test_tool", {"x": 5}, use_cache=True)
    assert result2.success == True
    assert result2.data == 10  # 应该从缓存命中
    print("  ✓ 缓存功能正常")

    print("\n✓ MCP 工具注册中心测试通过")
    return True


def test_config():
    """测试配置管理"""
    print("\n" + "=" * 50)
    print("  测试配置管理")
    print("=" * 50)

    from core.config import Config, get_config

    # 测试配置加载
    print("\n[1] 测试配置加载...")
    config = get_config("config/default.yaml")
    assert config is not None
    print("  ✓ 配置加载正常")

    # 测试配置访问
    print("\n[2] 测试配置访问...")
    system_name = config.get("system.name")
    assert system_name == "论文写作辅助系统"

    workflow_config = config.get("workflow.auto_save")
    assert workflow_config == True
    print("  ✓ 配置访问正常")

    # 测试配置节
    print("\n[3] 测试配置节...")
    agents_config = config.get_section("agents")
    assert "literature_agent" in agents_config
    print("  ✓ 配置节访问正常")

    print("\n✓ 配置管理测试通过")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  论文写作辅助系统 - 框架测试")
    print("=" * 60)

    results = []

    try:
        results.append(("Agent 基础模块", test_agents_base()))
    except Exception as e:
        print(f"\n✗ Agent 基础模块测试失败：{e}")
        results.append(("Agent 基础模块", False))

    try:
        results.append(("状态管理器", test_state_manager()))
    except Exception as e:
        print(f"\n✗ 状态管理器测试失败：{e}")
        results.append(("状态管理器", False))

    try:
        results.append(("工作流引擎", test_workflow_engine()))
    except Exception as e:
        print(f"\n✗ 工作流引擎测试失败：{e}")
        results.append(("工作流引擎", False))

    try:
        results.append(("MCP 工具注册中心", test_mcp_registry()))
    except Exception as e:
        print(f"\n✗ MCP 工具注册中心测试失败：{e}")
        results.append(("MCP 工具注册中心", False))

    try:
        results.append(("配置管理", test_config()))
    except Exception as e:
        print(f"\n✗ 配置管理测试失败：{e}")
        results.append(("配置管理", False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")

    print("\n" + "-" * 60)
    print(f"  总计：{passed}/{total} 通过")

    if passed == total:
        print("\n  ✓ 所有测试通过！框架运行正常")
        return 0
    else:
        print(f"\n  ✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
