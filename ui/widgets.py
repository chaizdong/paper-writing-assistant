"""
UI 组件模块

提供丰富的 UI 组件：进度条、表格、卡片、面板等
"""

import sys
from typing import Any, Optional


class Colors:
    """ANSI 颜色代码"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # 前景色
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # 背景色
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_BLACK = "\033[40m"

    @classmethod
    def color(cls, text: str, color: str) -> str:
        """给文本上色"""
        return f"{color}{text}{cls.RESET}"


class Icons:
    """Unicode 图标"""
    # 状态
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    PENDING = "○"
    RUNNING = "⟳"

    # 箭头
    ARROW_RIGHT = "→"
    ARROW_DOWN = "↓"
    ARROW_LEFT = "←"
    ARROW_UP = "↑"

    # 文档
    DOCUMENT = "📄"
    FOLDER = "📁"
    BOOK = "📚"
    CHART = "📊"

    # 其他
    STAR = "★"
    BULLET = "•"
    CHECKBOX = "☐"
    CHECKBOX_CHECKED = "☑"
    LIGHTBULB = "💡"
    TARGET = "🎯"
    ROCKET = "🚀"


def print_header(title: str, subtitle: str = "", width: int = 50):
    """
    打印标题头

    ╔══════════════════════════════════════════╗
    ║   论文写作辅助系统 v0.2.0                ║
    ╠══════════════════════════════════════════╣
    ║  副标题                                   ║
    ╚══════════════════════════════════════════╝
    """
    inner_width = width - 4

    # 顶行
    print(f"╔{'═' * width}╗")

    # 主标题
    title_line = f"║  {Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}"
    padding = inner_width - len(title) - 2
    print(f"{title_line}{' ' * padding}║")

    if subtitle:
        # 分隔线
        print(f"╠{'═' * width}╣")

        # 副标题
        subtitle_line = f"║  {subtitle}"
        padding = inner_width - len(subtitle) - 2
        print(f"{subtitle_line}{' ' * padding}║")

    # 底行
    print(f"╚{'═' * width}╝")


def print_panel(content: str, title: str = "", color: str = Colors.WHITE):
    """
    打印面板

    ┌─────────────────────┐
    │  标题               │
    ├─────────────────────┤
    │  内容               │
    │  多行内容...        │
    └─────────────────────┘
    """
    lines = content.split("\n")
    max_line_len = max(len(line) for line in lines)
    width = max(max_line_len + 4, len(title) + 4 if title else 20)

    # 顶行
    if title:
        print(f"┌{'─' * (width - 2)}┐")
        title_line = f"│  {Colors.BOLD}{title}{Colors.RESET}"
        padding = width - len(title) - 4
        print(f"{title_line}{' ' * padding}│")
        print(f"├{'─' * (width - 2)}┤")
    else:
        print(f"┌{'─' * (width - 2)}┐")

    # 内容行
    for line in lines:
        content_line = f"│  {line}"
        padding = width - len(line) - 4
        print(f"{content_line}{' ' * padding}│")

    # 底行
    print(f"└{'─' * (width - 2)}┘")


def print_progress_bar(current: int, total: int, label: str = "", width: int = 30):
    """
    打印进度条

    进度：████████████░░░░░░░░ 66.7%
    """
    percent = (current / total) * 100 if total > 0 else 0
    filled = int(width * current / total) if total > 0 else 0

    bar = f"{Colors.GREEN}{'█' * filled}{Colors.DIM}{'░' * (width - filled)}{Colors.RESET}"
    percent_str = f"{percent:5.1f}%"

    if label:
        print(f"{label}: {bar} {percent_str}")
    else:
        print(f"进度：{bar} {percent_str}")


def print_step_progress(current: int, total: int, description: str):
    """
    打印步骤进度

    [3/5] 正在执行实验规划...
    """
    step_str = f"[{Colors.CYAN}{current}{Colors.RESET}/{total}]"
    print(f"  {step_str} {description}")


def print_table(headers: list[str], rows: list[list[str]], max_width: int = 40):
    """
    打印表格

    | 标题 1 | 标题 2 | 标题 3 |
    |--------|--------|--------|
    | 数据 1 | 数据 2 | 数据 3 |
    """
    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell)[:max_width]
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell_str))

    # 打印表头
    header_line = "|"
    for i, header in enumerate(headers):
        header_line += f" {Colors.BOLD}{header}{Colors.RESET}"
        padding = col_widths[i] - len(header)
        header_line += f"{' ' * padding} |"
    print(header_line)

    # 打印分隔线
    sep_line = "|"
    for width in col_widths:
        sep_line += f"{'-' * (width + 1)}|"
    print(sep_line)

    # 打印数据行
    for row in rows:
        row_line = "|"
        for i, cell in enumerate(row):
            cell_str = str(cell)[:max_width]
            if i < len(col_widths):
                padding = col_widths[i] - len(cell_str)
                row_line += f" {cell_str}{' ' * padding} |"
        print(row_line)


def print_card(title: str, items: list[dict], numbered: bool = True):
    """
    打印卡片列表

    ┌─ 文献列表 ─────────────────────┐
    │ 1. 论文标题 1                   │
    │    作者，会议 2024              │
    │                                 │
    │ 2. 论文标题 2                   │
    │    作者，会议 2023              │
    └─────────────────────────────────┘
    """
    print(f"┌─ {Colors.BOLD}{title}{Colors.RESET} " + "─" * 30)

    for i, item in enumerate(items):
        if numbered:
            print(f"│ {Colors.CYAN}{i + 1}.{Colors.RESET} {item.get('title', 'N/A')}")
        else:
            print(f"│ {Colors.CYAN}•{Colors.RESET} {item.get('title', 'N/A')}")

        # 副信息
        if 'authors' in item:
            authors = ', '.join(item['authors'][:3])
            if len(item['authors']) > 3:
                authors += ' et al.'
            print(f"│   {Colors.DIM}{authors}, {item.get('venue', 'N/A')}{Colors.RESET}")
        elif 'description' in item:
            print(f"│   {Colors.DIM}{item['description']}{Colors.RESET}")

        print("│")

    print(f"└{'─' * 40}")


def print_status(status: str, message: str, indent: int = 0):
    """
    打印状态消息

    ✓ 操作成功
    ✗ 操作失败
    ⚠ 警告信息
    ℹ 提示信息
    """
    icons = {
        "success": f"{Colors.GREEN}{Icons.SUCCESS}{Colors.RESET}",
        "error": f"{Colors.RED}{Icons.ERROR}{Colors.RESET}",
        "warning": f"{Colors.YELLOW}{Icons.WARNING}{Colors.RESET}",
        "info": f"{Colors.BLUE}{Icons.INFO}{Colors.RESET}",
        "running": f"{Colors.CYAN}{Icons.RUNNING}{Colors.RESET}",
    }

    icon = icons.get(status, f"{Colors.WHITE}•{Colors.RESET}")
    prefix = " " * indent
    print(f"{prefix}{icon} {message}")


def print_section_header(text: str):
    """打印章节标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ {text} ═══{Colors.RESET}\n")


def print_divider(char: str = "─", width: int = 50):
    """打印分隔线"""
    print(f"{Colors.DIM}{char * width}{Colors.RESET}")


def highlight(text: str, color: str = Colors.YELLOW) -> str:
    """高亮文本"""
    return f"{color}{text}{Colors.RESET}"


def bold(text: str) -> str:
    """粗体文本"""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def print_workflow_status(stages: list[dict], current_stage: str):
    """
    打印工作流状态

    工作流进度:
    ✓ 文献调研        (已完成)
    ▶ Gap 分析        (进行中)
    ○ 方法设计        (待开始)
    ○ 实验规划        (待开始)
    ○ 论文撰写        (待开始)
    """
    print(f"\n{bold('工作流进度')}:")

    for i, stage in enumerate(stages):
        stage_name = stage.get('name', f'Stage {i+1}')
        stage_id = stage.get('stage_id', '')

        if stage_id == current_stage:
            icon = f"{Colors.CYAN}▶{Colors.RESET}"
            status = f"{Colors.CYAN}(进行中){Colors.RESET}"
        elif i < stages.index(next((s for s in stages if s['stage_id'] == current_stage), stages[-1])):
            icon = f"{Colors.GREEN}{Icons.SUCCESS}{Colors.RESET}"
            status = f"{Colors.DIM}(已完成){Colors.RESET}"
        else:
            icon = f"{Colors.DIM}{Icons.PENDING}{Colors.RESET}"
            status = f"{Colors.DIM}(待开始){Colors.RESET}"

        print(f"  {icon} {stage_name:<15} {status}")


def print_divider(char: str = "─", width: int = 50):
    """打印分隔线"""
    print(f"{Colors.DIM}{char * width}{Colors.RESET}")


def print_welcome():
    """打印欢迎界面"""
    clear_screen()
    print_header("论文写作辅助系统", "v0.2.0 - 基于 Agent 的智能写作")

    print(f"""
{Colors.BOLD}快速开始:{Colors.RESET}
  {Colors.CYAN}new{Colors.RESET}         创建新项目
  {Colors.CYAN}run{Colors.RESET}         执行当前阶段
  {Colors.CYAN}help{Colors.RESET}        查看所有命令

{Colors.BOLD}当前状态:{Colors.RESET}
  暂无活动项目，输入 {Colors.CYAN}new{Colors.RESET} 创建新项目
""")
    print_divider()


def print_checkpoint_prompt(cp_info: dict, options: list[str] = None):
    """
    打印确认点提示

    ══ 确认点 CP1: 确认研究主题 ══

    请确认以下研究关键词：
      [1] Transformer + Time Series
      [2] Efficient Deep Learning
      [3] Few-shot Learning

    请选择 (输入编号或自定义):
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 {cp_info['id']}: {cp_info['name']} ═══{Colors.RESET}\n")

    if cp_info.get('description'):
        print(f"{cp_info['description']}\n")

    if options:
        print("请选择：")
        for i, option in enumerate(options, 1):
            print(f"  [{Colors.CYAN}{i}{Colors.RESET}] {option}")
        print()


def clear_screen():
    """清屏"""
    # ANSI 转义码清屏
    print("\033[2J\033[H", end="")


def print_welcome():
    """打印欢迎界面"""
    clear_screen()
    print_header("论文写作辅助系统", "v0.2.0 - 基于 Agent 的智能写作")

    print(f"""
{Colors.BOLD}快速开始:{Colors.RESET}
  {Colors.CYAN}new{Colors.RESET}         创建新项目
  {Colors.CYAN}run{Colors.RESET}         执行当前阶段
  {Colors.CYAN}help{Colors.RESET}        查看所有命令

{Colors.BOLD}当前状态:{Colors.RESET}
  暂无活动项目，输入 {Colors.CYAN}new{Colors.RESET} 创建新项目
""")
    print_divider()
