#!/usr/bin/env python3
"""
论文写作辅助系统 - 主程序入口 (增强版)

一个基于 Agent 的论文写作辅助工具，支持：
- 文献调研
- Gap 分析
- 方法设计
- 实验规划
- 论文撰写

用法:
    python main.py              # 交互模式
    python main.py --help       # 显示帮助
    python main.py --new        # 创建新项目
"""

import argparse
import logging
import sys
from pathlib import Path

from core.config import get_config, Config
from core.state_manager import StateManager, get_state_manager
from agents.base import Orchestrator, get_orchestrator
from agents import (
    LiteratureAgent, GapAnalysisAgent, MethodAgent,
    ExperimentAgent, WritingAgent, ReviewAgent
)
from workflows.workflow_engine import WorkflowEngine
from ui.cli import EnhancedCLI
from ui.widgets import (
    print_header, print_status, print_panel, print_divider,
    print_workflow_status, print_welcome, bold, Colors
)
from ui.display import display_help


def setup_logging(config: Config):
    """设置日志"""
    log_config = config.get_section("logging")
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # 文件日志
    log_file = log_config.get("file", "./logs/paper_assistant.log")
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    # 配置根日志
    logging.root.setLevel(log_level)
    logging.root.addHandler(console_handler)
    logging.root.addHandler(file_handler)

    logging.info("日志系统已初始化")


def init_system(config_path: str = None) -> tuple:
    """
    初始化系统

    Returns:
        (config, state_manager, orchestrator, workflow_engine)
    """
    # 加载配置
    config = get_config(config_path)
    logging.info(f"系统版本：{config.get('system.version', 'unknown')}")

    # 初始化状态管理器
    state_manager = get_state_manager()
    logging.info("状态管理器已初始化")

    # 初始化编排器
    orchestrator = get_orchestrator()
    logging.info("编排器已初始化")

    # 注册所有 Agents
    agents = [
        LiteratureAgent(agent_id="literature", max_papers=20),
        GapAnalysisAgent(agent_id="gap"),
        MethodAgent(agent_id="method"),
        ExperimentAgent(agent_id="experiment"),
        WritingAgent(agent_id="writing", output_format="markdown"),
        ReviewAgent(agent_id="review"),
    ]

    for agent in agents:
        orchestrator.register_agent(agent)
    logging.info(f"已注册 {len(agents)} 个 Agent")

    # 初始化工作流引擎
    workflow_engine = WorkflowEngine(state_manager, orchestrator)
    logging.info("工作流引擎已初始化")

    return config, state_manager, orchestrator, workflow_engine


def create_new_project(cli: EnhancedCLI, state_manager: StateManager) -> dict:
    """创建新项目"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 创建新项目 ═══{Colors.RESET}\n")

    # CP1: 确认研究主题
    confirmed, user_data = cli.run_confirmation("cp1", "确认研究主题", {})

    if not confirmed:
        return None

    title = user_data.get("topic", "未命名项目")
    domain = user_data.get("domain", "通用")

    project = state_manager.create_project(title=title, domain=domain)
    print_status("success", f"已创建项目：{title}")
    return project


def run_workflow_stage(cli: EnhancedCLI, workflow_engine: WorkflowEngine, context: dict):
    """
    运行当前工作流阶段

    包含确认点交互
    """
    current_stage = workflow_engine.state_manager.get_current_stage()
    stage = workflow_engine.get_stage(current_stage)

    if not stage:
        print_status("error", f"未知阶段：{current_stage}")
        return

    print(f"\n{bold(f'执行阶段：{stage.name}')}")

    # 获取该阶段的确认点
    for cp_id in stage.confirmations:
        cp_info = {
            "cp1": {"name": "确认研究主题", "context_key": "topic"},
            "cp2": {"name": "确认文献筛选", "context_key": "papers"},
            "cp3": {"name": "确认 Gap 分析", "context_key": "gap_report"},
            "cp4": {"name": "确认技术方案", "context_key": "method"},
            "cp5": {"name": "确认创新性评估", "context_key": "novelty"},
            "cp6": {"name": "确认实验设计", "context_key": "experiment_plan"},
            "cp7": {"name": "确认评价指标", "context_key": "metrics"},
            "cp8": {"name": "确认论文大纲", "context_key": "outline"},
            "cp9": {"name": "逐章确认", "context_key": "section_content"},
            "cp10": {"name": "最终审阅", "context_key": "review_report"},
        }.get(cp_id, {"name": cp_id, "context_key": ""})

        # 获取确认点上下文
        cp_context = context.get(cp_info.get("context_key", ""), {})

        # 运行确认点交互
        confirmed, user_data = cli.run_confirmation(cp_id, cp_info["name"], cp_context)

        if not confirmed:
            print_status("warning", "操作已取消")
            return

        # 保存用户确认数据
        if user_data:
            context.update(user_data)

    # 执行阶段任务
    result = workflow_engine.execute_stage(current_stage, context)

    if result.get("success"):
        print_status("success", f"阶段 {stage.name} 执行完成")

        # 更新上下文
        for stage_result in result.get("results", []):
            if stage_result.get("response", {}).payload.get("success"):
                agent_id = stage_result["agent"]
                context[agent_id] = stage_result["response"].payload.get("result", {})

        # 进入下一阶段
        next_stage = workflow_engine.next_stage()
        if next_stage:
            print_status("info", f"已进入下一阶段：{next_stage}")
    else:
        print_status("error", f"阶段执行失败：{result.get('error', '')}")


def interactive_mode(cli: EnhancedCLI, state_manager: StateManager,
                     orchestrator: Orchestrator, workflow_engine: WorkflowEngine):
    """增强交互模式"""

    # 欢迎界面
    print_welcome()

    # 上下文数据
    context = {}

    while True:
        cmd = cli.get_command()
        command, args = cli.parse_command(cmd)

        if not command:
            continue

        # 退出命令
        if command in ("quit", "exit"):
            print(f"\n{Colors.CYAN}再见！{Colors.RESET}")
            break

        # 帮助命令
        elif command == "help":
            cli.show_help()

        # 教程命令
        elif command == "tutorial":
            cli.show_tutorial()

        # 速查命令
        elif command == "cheatsheet":
            cli.show_cheatsheet()

        # 创建新项目
        elif command == "new":
            project = create_new_project(cli, state_manager)
            if project:
                context["project_id"] = project.project_id
                print_status("success", "请输入 'run' 开始文献调研")

        # 运行当前阶段
        elif command == "run":
            if not context.get("project_id"):
                print_status("warning", "请先创建项目 (new)")
            else:
                run_workflow_stage(cli, workflow_engine, context)

        # 下一阶段
        elif command == "next":
            next_stage = workflow_engine.next_stage()
            if next_stage:
                print_status("success", f"已进入阶段：{next_stage}")
            else:
                print_status("info", "已是最后阶段")

        # 回滚
        elif command.startswith("rollback"):
            if args:
                cp_id = args[0]
                if workflow_engine.rollback_to_checkpoint(cp_id):
                    print_status("success", f"已回滚到 {cp_id}")
                else:
                    print_status("error", f"回滚失败：{cp_id}")
            else:
                print_status("error", "请指定确认点：rollback cp3")

        # 状态
        elif command == "status":
            cli.cmd_status(context)

        # 阶段列表
        elif command == "stage":
            cli.cmd_stage(workflow_engine)

        # 进度
        elif command == "progress":
            cli.cmd_progress(workflow_engine)

        # 查看命令
        elif command == "view":
            cli.cmd_view(args, context)

        # 导出
        elif command == "export":
            cli.cmd_export(context)

        # 审阅
        elif command == "review":
            review_data = context.get('review_report', {})
            if review_data:
                display_review_report(review_data)
            else:
                print_status("info", "暂无审阅报告")

        # 未知命令
        else:
            print_status("error", f"未知命令：{command}，输入 'help' 查看帮助")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="论文写作辅助系统 - 基于 Agent 的论文自动写作工具"
    )
    parser.add_argument("--config", "-c", type=str, help="配置文件路径")
    parser.add_argument("--new", "-n", action="store_true", help="创建新项目")
    parser.add_argument("--project", "-p", type=str, help="加载指定项目")
    parser.add_argument("--version", "-v", action="store_true", help="显示版本号")

    args = parser.parse_args()

    # 显示版本
    if args.version:
        print("论文写作辅助系统 v0.2.0")
        return 0

    # 初始化系统
    try:
        config, state_manager, orchestrator, workflow_engine = init_system(args.config)
    except Exception as e:
        logging.exception(f"初始化失败：{e}")
        print(f"错误：系统初始化失败 - {e}")
        return 1

    # 加载指定项目
    if args.project:
        project = state_manager.load_project(args.project)
        if project:
            print(f"已加载项目：{project.title}")
        else:
            print(f"警告：项目不存在 - {args.project}")

    # 创建新项目（命令行方式）
    if args.new and not args.project:
        print("\n请按照提示输入项目信息...")
        # 简单实现，完整实现应在交互模式中

    # 创建 CLI 并进入交互模式
    cli = EnhancedCLI()
    interactive_mode(cli, state_manager, orchestrator, workflow_engine)

    return 0


if __name__ == "__main__":
    sys.exit(main())
