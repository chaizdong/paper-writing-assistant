"""
确认点交互模块

实现 10 个确认点的用户交互逻辑
"""

from typing import Any, Optional
from .widgets import (
    Colors, print_panel, print_status, print_checkpoint_prompt,
    print_divider, bold
)


class ConfirmationHandler:
    """
    确认点处理器

    处理所有确认点的用户交互
    """

    def __init__(self, cli=None):
        self.cli = cli
        self.confirmation_data = {}

    def handle_confirmation(self, cp_id: str, cp_name: str, context: dict) -> tuple[bool, Any]:
        """
        处理确认点交互

        Args:
            cp_id: 确认点 ID (cp1, cp2, ...)
            cp_name: 确认点名称
            context: 上下文数据

        Returns:
            (confirmed, user_data) - 是否确认，用户输入的数据
        """
        handler = getattr(self, f'_handle_{cp_id}', self._handle_default)
        return handler(cp_name, context)

    def _handle_cp1(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP1: 确认研究主题
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP1: 确认研究主题 ═══{Colors.RESET}\n")

        print("请输入您的研究主题或方向：")
        print("(例如：'Transformer 在时间序列预测中的应用'、'高效的深度学习模型')\n")

        try:
            topic = input(f"{Colors.CYAN}>{Colors.RESET} ").strip()

            if not topic:
                print_status("warning", "研究主题不能为空")
                return False, {}

            # 确认
            print(f"\n确认研究主题：{Colors.BOLD}{topic}{Colors.RESET}")
            confirm = self._ask_confirm("开始文献调研")

            if confirm:
                return True, {"topic": topic, "keywords": self._extract_keywords(topic)}
            return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp2(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP2: 确认文献筛选结果
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP2: 确认文献筛选结果 ═══{Colors.RESET}\n")

        papers = context.get('papers', [])
        print(f"找到 {len(papers)} 篇相关论文：\n")

        for i, paper in enumerate(papers[:10], 1):
            title = paper.get('title', 'N/A')
            venue = paper.get('venue', '')
            year = paper.get('year', '')
            print(f"  [{Colors.CYAN}{i}{Colors.RESET}] {title} ({venue}, {year})")

        if len(papers) > 10:
            print(f"\n  ... 还有 {len(papers) - 10} 篇")

        print(f"\n请选择要保留的论文编号（空格分隔，或输入 a 全选）：")

        try:
            selection = input(f"{Colors.CYAN}>{Colors.RESET} ").strip().lower()

            if selection == 'a':
                selected_ids = list(range(len(papers)))
            else:
                selected_ids = []
                for s in selection.split():
                    try:
                        idx = int(s) - 1
                        if 0 <= idx < len(papers):
                            selected_ids.append(idx)
                    except ValueError:
                        pass

            if not selected_ids:
                print_status("warning", "请至少选择一篇论文")
                return False, {}

            selected_papers = [papers[i] for i in selected_ids]
            print_status("success", f"已选择 {len(selected_papers)} 篇论文")

            # 确认
            confirm = self._ask_confirm("开始 Gap 分析")
            if confirm:
                return True, {"selected_papers": selected_papers}
            return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp3(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP3: 确认 Gap 分析报告
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP3: 确认 Gap 分析报告 ═══{Colors.RESET}\n")

        gap_report = context.get('gap_report', '')
        print(gap_report)

        print(f"\n{bold('确认')}:\n")
        print("  [1] 确认 Gap 分析，继续方法设计")
        print("  [2] 重新进行 Gap 分析")
        print("  [3] 返回修改文献选择")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-3):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"confirmed": True}
            elif choice == '2':
                return False, {"retry": True}
            elif choice == '3':
                return False, {"backtrack": "cp2"}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp4(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP4: 确认技术方案
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP4: 确认技术方案 ═══{Colors.RESET}\n")

        method = context.get('method', {})
        print(f"方法名称：{Colors.BOLD}{method.get('name', 'N/A')}{Colors.RESET}\n")

        print(f"{bold('核心思想')}:\n")
        print_panel(method.get('core_idea', 'N/A'))

        contributions = context.get('contributions', [])
        print(f"\n{bold('主要贡献')}:\n")
        for i, cont in enumerate(contributions, 1):
            print(f"  {i}. {cont}")

        print(f"\n{bold('确认')}:\n")
        print("  [1] 确认技术方案，继续实验设计")
        print("  [2] 重新设计方法")
        print("  [3] 返回修改 Gap 分析")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-3):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"confirmed": True}
            elif choice == '2':
                return False, {"retry": True}
            elif choice == '3':
                return False, {"backtrack": "cp3"}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp5(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP5: 确认创新性评估
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP5: 确认创新性评估 ═══{Colors.RESET}\n")

        novelty_score = context.get('novelty_score', 'N/A')
        print(f"创新性评分：{Colors.BOLD}{novelty_score}{Colors.RESET}\n")

        print(context.get('novelty_report', 'N/A'))

        print(f"\n{bold('确认')}:\n")
        print("  [1] 创新性充分，继续实验设计")
        print("  [2] 需要增强创新性（重新设计方法）")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-2):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"confirmed": True}
            elif choice == '2':
                return False, {"retry": True, "backtrack": "cp4"}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp6(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP6: 确认实验设计
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP6: 确认实验设计 ═══{Colors.RESET}\n")

        exp_data = context.get('experiment_plan', {})

        print(f"{bold('数据集')}:\n")
        for ds in exp_data.get('datasets', []):
            print(f"  • {ds.get('name', 'N/A')}: {ds.get('description', '')}")

        print(f"\n{bold('Baseline 方法')}:\n")
        for bl in exp_data.get('baselines', []):
            print(f"  • {bl.get('name', 'N/A')}")

        print(f"\n{bold('评价指标')}:\n")
        for m in exp_data.get('metrics', []):
            print(f"  • {m.get('name', 'N/A')}: {m.get('description', '')}")

        print(f"\n{bold('确认')}:\n")
        print("  [1] 确认实验设计，开始论文撰写")
        print("  [2] 修改实验设计")
        print("  [3] 返回修改方法")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-3):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"confirmed": True}
            elif choice == '2':
                return False, {"retry": True}
            elif choice == '3':
                return False, {"backtrack": "cp4"}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp7(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP7: 确认评价指标
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP7: 确认评价指标 ═══{Colors.RESET}\n")

        metrics = context.get('metrics', [])

        print(f"{bold('主要指标')}:\n")
        for m in metrics:
            if m.get('type') == 'main':
                print(f"  ★ {m.get('name', 'N/A')}: {m.get('description', '')}")

        print(f"\n{bold('次要指标')}:\n")
        for m in metrics:
            if m.get('type') != 'main':
                print(f"  ○ {m.get('name', 'N/A')}: {m.get('description', '')}")

        print(f"\n{bold('确认')}:\n")
        print("  [1] 确认评价指标")
        print("  [2] 添加/修改指标")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-2):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"confirmed": True}
            elif choice == '2':
                # 简单实现：让用户输入新指标
                new_metric = input("输入新指标名称（或回车跳过）: ").strip()
                if new_metric:
                    desc = input("描述：").strip()
                    return True, {"new_metric": {"name": new_metric, "description": desc}}
                return False, {}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp8(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP8: 确认论文大纲
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP8: 确认论文大纲 ═══{Colors.RESET}\n")

        outline = context.get('outline', [])

        print(f"{bold('论文大纲')}:\n")
        for i, section in enumerate(outline, 1):
            print(f"  {i}. {section}")

        print(f"\n{bold('确认')}:\n")
        print("  [1] 确认大纲，开始撰写")
        print("  [2] 修改大纲")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-2):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"confirmed": True}
            elif choice == '2':
                print("请输入要修改的章节编号和新内容（格式：编号.新内容）：")
                edit = input("> ").strip()
                return False, {"edit": edit}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp9(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP9: 逐章确认
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP9: 逐章确认 ═══{Colors.RESET}\n")

        section = context.get('current_section', 'N/A')
        content = context.get('section_content', '')

        print(f"{bold('章节')}: {section}\n")
        print_panel(content[:500] + "..." if len(content) > 500 else content, section)

        print(f"\n{bold('操作')}:\n")
        print("  [1] 确认本章")
        print("  [2] 修改本章")
        print("  [3] 重新生成")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-3):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"confirmed": True}
            elif choice == '2':
                print("请输入修改意见：")
                feedback = input("> ").strip()
                return False, {"feedback": feedback}
            elif choice == '3':
                return False, {"regenerate": True}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_cp10(self, name: str, context: dict) -> tuple[bool, Any]:
        """
        CP10: 最终审阅
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ 确认点 CP10: 最终审阅 ═══{Colors.RESET}\n")

        review_data = context.get('review_report', {})
        score = review_data.get('overall_score', 0)

        print(f"{bold('总体评分')}: {score}/100\n")

        # 问题统计
        issues = review_data.get('issues', {})
        print(f"{bold('问题统计')}:\n")
        for issue_type, count in issues.items():
            print(f"  {issue_type}: {count}")

        print(f"\n{bold('确认')}:\n")
        print("  [1] 确认提交，导出论文")
        print("  [2] 需要进一步修改")
        print("  [3] 返回修改特定章节")

        try:
            choice = input(f"\n{Colors.CYAN}请选择 (1-3):{Colors.RESET} ").strip()

            if choice == '1':
                return True, {"ready_for_submission": True}
            elif choice == '2':
                return False, {"needs_revision": True}
            elif choice == '3':
                section = input("输入要修改的章节名称：").strip()
                return False, {"revise_section": section}
            else:
                print_status("warning", "无效选择")
                return False, {}

        except (EOFError, KeyboardInterrupt):
            print()
            return False, {}

    def _handle_default(self, name: str, context: dict) -> tuple[bool, Any]:
        """默认处理器"""
        print(f"\n确认点：{name}")
        return self._ask_confirm("继续")

    def _ask_confirm(self, action: str) -> bool:
        """简单的确认询问"""
        try:
            response = input(f"\n{Colors.CYAN}确认{action}？[Y/n]:{Colors.RESET} ").strip().lower()
            return response in ('', 'y', 'yes')
        except (EOFError, KeyboardInterrupt):
            print()
            return False

    def _extract_keywords(self, topic: str) -> list[str]:
        """从主题中提取关键词（简单实现）"""
        # 可以接入 NLP 工具进行更智能的提取
        return [topic.split()[0]] if topic.split() else [topic]
