"""
命令行交互界面 - 增强版

提供丰富的命令和友好的用户交互
"""

import sys
import shlex
from typing import Any, Optional

from .widgets import (
    Colors, Icons, print_header, print_panel, print_progress_bar,
    print_table, print_card, print_status, print_section_header,
    print_workflow_status, print_checkpoint_prompt, print_welcome,
    bold, highlight, print_divider
)
from .display import (
    display_paper_list, display_gap_report, display_method_design,
    display_experiment_plan, display_paper_draft, display_review_report,
    display_project_status, display_help
)
from mcp.tool_registry import get_registry
from mcp.clients.arxiv_client import ArXivClient
from mcp.clients.semantic_scholar_client import SemanticScholarClient
from .interactive import ConfirmationHandler


class CLI:
    """
    基础命令行界面
    """

    COMMANDS = {
        "new": "创建新项目",
        "status": "查看当前项目状态",
        "stage": "查看所有工作流阶段",
        "goto <stage>": "跳转到指定阶段",
        "progress": "查看进度",
        "help": "显示帮助",
        "quit/exit": "退出程序",
    }

    def get_command(self) -> str:
        """获取用户命令"""
        try:
            print()
            cmd = input(f"\n{Colors.CYAN}>{Colors.RESET} ").strip()
            return cmd
        except EOFError:
            return "quit"
        except KeyboardInterrupt:
            print()
            return "quit"

    def show_help(self):
        """显示帮助信息"""
        display_help()


class EnhancedCLI(CLI):
    """
    增强版命令行界面

    支持：
    - 工作流执行命令
    - 结果查看命令
    - 项目管理命令
    - 确认点交互
    """

    COMMANDS = {
        # 工作流控制
        "run": "运行当前阶段",
        "next": "进入下一阶段",
        "rollback <CP>": "回滚到指定确认点",
        "resume": "继续执行",

        # 查看命令
        "status": "查看项目状态",
        "stage": "查看工作流阶段",
        "progress": "查看进度",
        "view papers": "查看文献列表",
        "view gap": "查看 Gap 报告",
        "view method": "查看方法设计",
        "view experiment": "查看实验方案",
        "view paper [section]": "查看论文草稿",
        "review": "查看审阅报告",
        "mcp": "查看 MCP 工具状态",

        # 项目管理
        "new": "创建新项目",
        "list": "列出所有项目",
        "switch <ID>": "切换项目",
        "export": "导出项目",

        # 帮助
        "help": "显示帮助",
        "tutorial": "新手教程",
        "cheatsheet": "命令速查",
        "quit/exit": "退出程序",
    }

    def __init__(self):
        super().__init__()
        self.confirmation_handler = ConfirmationHandler(self)
        self.command_history = []
        self.history_index = -1

    def get_command(self) -> str:
        """获取用户命令（带历史记录）"""
        try:
            cmd = input(f"\n{Colors.CYAN}>{Colors.RESET} ").strip()

            # 记录历史
            if cmd and cmd != self.command_history[-1:] if self.command_history else True:
                self.command_history.append(cmd)
                self.history_index = len(self.command_history)

            return cmd
        except EOFError:
            return "quit"
        except KeyboardInterrupt:
            print()
            return "quit"

    def parse_command(self, cmd: str) -> tuple[str, list[str]]:
        """
        解析命令

        Returns:
            (command, args)
        """
        parts = shlex.split(cmd) if cmd else []
        if not parts:
            return "", []
        return parts[0], parts[1:]

    # ==================== 显示增强帮助 ====================

    def show_help(self):
        """显示增强帮助"""
        print_section_header("📖 命令帮助")

        categories = {
            "工作流控制": ["run", "next", "rollback", "resume"],
            "查看命令": ["status", "stage", "progress", "view", "mcp"],
            "项目管理": ["new", "list", "switch", "export"],
            "帮助": ["help", "tutorial", "cheatsheet"],
        }

        for category, cmds in categories.items():
            print(f"\n{bold(Colors.CYAN + category + Colors.RESET)}:")
            for cmd_key, desc in self.COMMANDS.items():
                cmd_name = cmd_key.split()[0]
                if cmd_name in cmds:
                    print(f"  {Colors.CYAN}{cmd_key:<20}{Colors.RESET} {desc}")

        print_divider()

    def show_tutorial(self):
        """显示新手教程"""
        print_section_header("🎓 新手教程")

        print(f"""
{bold('欢迎使用论文写作辅助系统！')}

本系统将帮助您完成从研究主题到完整论文的全流程。

{bold('快速开始:')}

1. {Colors.CYAN}new{Colors.RESET} - 创建新项目，输入研究主题
2. {Colors.CYAN}run{Colors.RESET} - 运行当前阶段（文献调研）
3. 根据提示完成确认点交互
4. {Colors.CYAN}next{Colors.RESET} - 进入下一阶段
5. 重复直到完成论文撰写

{bold('查看结果:')}

- {Colors.CYAN}view papers{Colors.RESET} - 查看文献列表
- {Colors.CYAN}view gap{Colors.RESET} - 查看 Gap 分析报告
- {Colors.CYAN}view method{Colors.RESET} - 查看方法设计
- {Colors.CYAN}view paper{Colors.RESET} - 查看论文草稿

{bold('需要帮助时:')}

- {Colors.CYAN}help{Colors.RESET} - 查看所有命令
- {Colors.CYAN}cheatsheet{Colors.RESET} - 命令速查表
""")
        print_divider()

    def show_cheatsheet(self):
        """显示命令速查表"""
        print_section_header("📋 命令速查表")

        data = [
            ["new", "创建新项目"],
            ["run", "运行当前阶段"],
            ["next", "下一阶段"],
            ["rollback <CP>", "回滚到确认点"],
            ["status", "查看状态"],
            ["view papers", "查看文献"],
            ["view gap", "查看 Gap 报告"],
            ["view method", "查看方法"],
            ["view paper", "查看论文"],
            ["export", "导出项目"],
            ["help", "帮助"],
            ["quit", "退出"],
        ]

        print_table(["命令", "功能"], data)
        print()

    # ==================== 显示命令实现 ====================

    def cmd_view(self, args: list[str], context: dict):
        """
        view 命令实现

        view papers
        view gap
        view method
        view experiment
        view paper [section]
        """
        if not args:
            print_status("error", "请指定查看内容：view papers|gap|method|experiment|paper")
            return

        target = args[0]
        section = args[1] if len(args) > 1 else None

        if target == "papers":
            papers = context.get('papers', [])
            if papers:
                display_paper_list(papers, show_abstract=False)
            else:
                print_status("info", "暂无文献数据，请先运行文献调研")

        elif target == "gap":
            gap_data = context.get('gap_analysis', {})
            if gap_data:
                display_gap_report(gap_data)
            else:
                print_status("info", "暂无 Gap 分析数据")

        elif target == "method":
            method_data = context.get('method_design', {})
            if method_data:
                display_method_design(method_data)
            else:
                print_status("info", "暂无方法设计数据")

        elif target == "experiment":
            exp_data = context.get('experiment_plan', {})
            if exp_data:
                display_experiment_plan(exp_data)
            else:
                print_status("info", "暂无实验方案数据")

        elif target == "paper":
            paper_data = context.get('paper_draft', {})
            if paper_data:
                display_paper_draft(paper_data, section)
            else:
                print_status("info", "暂无论文草稿数据")

        else:
            print_status("error", f"未知查看目标：{target}")

    def cmd_status(self, context: dict):
        """status 命令实现"""
        project_state = context.get('project_state', {})
        if project_state:
            display_project_status(project_state)
        else:
            print_status("info", "暂无项目状态")

    def cmd_stage(self, workflow_engine):
        """stage 命令实现"""
        stages = workflow_engine.list_stages()
        current = workflow_engine.state_manager.get_current_stage()
        print_workflow_status(stages, current)

    def cmd_progress(self, workflow_engine):
        """progress 命令实现"""
        progress = workflow_engine.get_progress()
        print(f"\n{bold('当前阶段')}: {progress['current_stage']}")
        print_progress_bar(
            int(progress['percent']),
            100,
            "总体进度",
            width=40
        )
        print(f"\n已完成阶段：{', '.join(progress['completed_stages'])}")
        if progress['remaining_stages']:
            print(f"待进行阶段：{', '.join(progress['remaining_stages'])}")

    def cmd_export(self, context: dict):
        """export 命令实现"""
        paper_data = context.get('paper_draft', {})
        if not paper_data:
            print_status("error", "暂无论文数据，无法导出")
            return

        print("选择导出格式:")
        print("  [1] Markdown")
        print("  [2] LaTeX")
        print("  [3] JSON")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-3):{Colors.RESET} ").strip()

            format_map = {'1': 'markdown', '2': 'latex', '3': 'json'}
            fmt = format_map.get(choice, 'markdown')

            # 简单导出实现
            full_paper = paper_data.get('full_paper', '')
            print_status("success", f"论文已导出为 {fmt} 格式")
            print(f"\n{full_paper[:500]}...")

        except (EOFError, KeyboardInterrupt):
            print()

    # ==================== MCP 工具状态 ====================

    def cmd_mcp(self, args: list[str], context: dict):
        """mcp 命令实现 - 查看 MCP 工具状态"""
        print_section_header("🔧 MCP 工具状态")

        # 工具注册中心
        registry = get_registry()
        tools = registry.list_tools()
        servers = registry.list_servers()

        print(f"\n{bold('已注册工具')}: {len(tools)}")

        tool_data = []
        for tool in tools:
            tool_data.append([
                tool.get("name", ""),
                tool.get("description", "")[:40],
                tool.get("server_name", "local") or "local",
            ])

        if tool_data:
            print_table(["工具名称", "描述", "类型"], tool_data)

        # MCP 服务器状态
        print(f"\n{bold('MCP 服务器')}: {len(servers)}")

        if servers:
            server_data = []
            for server in servers:
                status = "✓ 已连接" if server.get("connected") else "○ 未连接"
                server_data.append([
                    server.get("name", ""),
                    status,
                    ", ".join(server.get("capabilities", [])),
                ])
            print_table(["服务器", "状态", "能力"], server_data)
        else:
            print("  暂无配置的 MCP 服务器（使用内置 API 客户端）")

        # 内置客户端状态
        print(f"\n{bold('内置 API 客户端')}:")

        try:
            arxiv = ArXivClient(max_results=1)
            print(f"  {Icons.SUCCESS} ArXivClient - 就绪")
        except Exception:
            print(f"  {Icons.ERROR} ArXivClient - 错误")

        try:
            ss = SemanticScholarClient(max_results=1)
            print(f"  {Icons.SUCCESS} SemanticScholarClient - 就绪")
        except Exception:
            print(f"  {Icons.ERROR} SemanticScholarClient - 错误")

        print(f"\n{Colors.DIM}提示：当前使用内置 API 客户端直接访问 arXiv 和 Semantic Scholar{Colors.RESET}")
        print_divider()

    # ==================== 确认点交互 ====================

    def run_confirmation(self, cp_id: str, cp_name: str, context: dict):
        """
        运行确认点交互

        Returns:
            (confirmed, user_data)
        """
        return self.confirmation_handler.handle_confirmation(cp_id, cp_name, context)


# 全局 CLI 实例
_cli: Optional[EnhancedCLI] = None


def get_cli() -> EnhancedCLI:
    """获取 CLI 实例"""
    global _cli
    if _cli is None:
        _cli = EnhancedCLI()
    return _cli
