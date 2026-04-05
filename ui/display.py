"""
富文本显示模块

用于显示论文、文献列表、报告等内容的格式化输出
"""

from .widgets import (
    Colors, Icons, print_panel, print_table, print_card,
    print_status, print_section_header, print_divider,
    bold, highlight, truncate, print_workflow_status
)


def display_paper_list(papers: list[dict], show_abstract: bool = False):
    """
    显示论文列表

    Args:
        papers: 论文列表
        show_abstract: 是否显示摘要
    """
    print_section_header(f"📚 文献列表 ({len(papers)} 篇)")

    for i, paper in enumerate(papers, 1):
        print(f"\n{Colors.CYAN}{Colors.BOLD}[{i}] {paper.get('title', 'N/A')}{Colors.RESET}")

        authors = paper.get('authors', [])
        if authors:
            author_str = ', '.join(authors[:3])
            if len(authors) > 3:
                author_str += ' et al.'
            print(f"   {Colors.DIM}作者：{author_str}{Colors.RESET}")

        venue = paper.get('venue', '')
        year = paper.get('year', '')
        if venue or year:
            print(f"   {Colors.DIM}发表：{venue} ({year}){Colors.RESET}")

        if show_abstract and paper.get('abstract'):
            abstract = truncate(paper['abstract'], 200)
            print(f"   {Colors.DIM}摘要：{abstract}{Colors.RESET}")

        print(f"   {Colors.DIM}链接：{paper.get('url', 'N/A')}{Colors.RESET}")


def display_gap_report(gap_data: dict):
    """
    显示 Gap 分析报告

    Args:
        gap_data: Gap 分析结果
    """
    print_section_header("🔍 Gap 分析报告")

    # 现有方法
    print(f"\n{bold('现有方法总结')}:\n")
    methods = gap_data.get('existing_methods', [])
    for i, method in enumerate(methods[:5], 1):
        print(f"  {Colors.CYAN}{i}.{Colors.RESET} {method.get('name', 'N/A')}")
        print(f"      {Colors.DIM}{method.get('description', '')}{Colors.RESET}")
        if method.get('papers'):
            print(f"      {Colors.DIM}相关论文：{len(method['papers'])} 篇{Colors.RESET}")

    # 局限性
    print(f"\n{bold('现有方法局限性')}:\n")
    limitations = gap_data.get('limitations', [])
    for i, lim in enumerate(limitations, 1):
        print(f"  {Colors.YELLOW}{Icons.WARNING}{Colors.RESET} {lim}")

    # 研究空白
    print(f"\n{bold('研究空白')}:\n")
    gaps = gap_data.get('research_gaps', [])
    for i, gap in enumerate(gaps, 1):
        print(f"  {Colors.CYAN}{i}.{Colors.RESET} {gap.get('gap', 'N/A')}")
        print(f"      {Colors.GREEN}→ {gap.get('opportunity', '')}{Colors.RESET}")

    # 推荐方向
    print(f"\n{bold('推荐研究方向')}:\n")
    recommendation = gap_data.get('recommendation', '')
    print_panel(recommendation, "💡 建议")


def display_method_design(method_data: dict):
    """
    显示方法设计结果

    Args:
        method_data: 方法设计结果
    """
    print_section_header("💡 方法设计")

    method = method_data.get('method', {})

    # 方法名称和核心思想
    print(f"\n{Colors.BOLD}{Colors.CYAN}方法名称：{method.get('name', 'N/A')}{Colors.RESET}\n")

    print(f"{bold('核心思想')}:\n")
    print_panel(method.get('core_idea', 'N/A'))

    # 贡献点
    print(f"\n{bold('主要贡献')}:\n")
    contributions = method_data.get('contributions', [])
    for i, cont in enumerate(contributions, 1):
        print(f"  {Colors.GREEN}{Icons.SUCCESS}{Colors.RESET} {cont}")

    # 技术路线
    print(f"\n{bold('技术路线')}:\n")
    route = method_data.get('technical_route', [])
    for step in route:
        print(f"  {Colors.CYAN}Step {step.get('step', '?')}: {step.get('name', 'N/A')}{Colors.RESET}")
        print(f"      {Colors.DIM}{step.get('description', '')}{Colors.RESET}")
        print(f"      {Colors.DIM}输出：{step.get('output', 'N/A')}{Colors.RESET}")
        if step != route[-1]:
            print(f"      {Colors.DIM}{Icons.ARROW_DOWN}{Colors.RESET}")


def display_experiment_plan(exp_data: dict):
    """
    显示实验设计方案

    Args:
        exp_data: 实验规划结果
    """
    print_section_header("📊 实验设计方案")

    # 数据集
    print(f"\n{bold('数据集')}:\n")
    datasets = exp_data.get('datasets', [])
    for ds in datasets:
        print(f"  {Colors.CYAN}▸ {ds.get('name', 'N/A')}{Colors.RESET}")
        print(f"    {Colors.DIM}{ds.get('description', '')}{Colors.RESET}")
        print(f"    {Colors.DIM}理由：{ds.get('reason', '')}{Colors.RESET}")

    # Baselines
    print(f"\n{bold('Baseline 方法')}:\n")
    baselines = exp_data.get('baselines', [])
    for bl in baselines:
        print(f"  {Colors.CYAN}▸ {bl.get('name', 'N/A')}{Colors.RESET}")
        print(f"    {Colors.DIM}{bl.get('citation', '')}{Colors.RESET}")
        print(f"    {Colors.DIM}理由：{bl.get('reason', '')}{Colors.RESET}")

    # 评价指标
    print(f"\n{bold('评价指标')}:\n")
    metrics = exp_data.get('metrics', [])
    table_data = [[m.get('name', ''), m.get('description', ''), m.get('type', '')]
                  for m in metrics]
    if table_data:
        print_table(["指标名称", "描述", "类型"], table_data)

    # 消融实验
    print(f"\n{bold('消融实验')}:\n")
    ablations = exp_data.get('ablation_studies', [])
    for ab in ablations:
        print(f"  {Colors.YELLOW}▸ {ab.get('variant', 'N/A')}{Colors.RESET}")
        print(f"    {Colors.DIM}目的：{ab.get('purpose', '')}{Colors.RESET}")


def display_paper_draft(paper_data: dict, section: str = None):
    """
    显示论文草稿

    Args:
        paper_data: 论文数据
        section: 指定章节（None 显示全部）
    """
    sections = paper_data.get('sections', {})

    if section:
        # 显示指定章节
        if section in sections:
            content = sections[section].get('content', '')
            section_titles = {
                'abstract': '摘要',
                'introduction': '引言',
                'related_work': '相关工作',
                'method': '方法',
                'experiments': '实验',
                'conclusion': '结论',
            }
            title = section_titles.get(section, section)
            print_section_header(f"📄 {title}")
            print_panel(content, title)
        else:
            print_status("error", f"未知章节：{section}")
    else:
        # 显示全部
        print_section_header("📄 论文草稿")

        section_order = ['abstract', 'introduction', 'related_work',
                         'method', 'experiments', 'conclusion']
        section_titles = {
            'abstract': '摘要',
            'introduction': '引言',
            'related_work': '相关工作',
            'method': '方法',
            'experiments': '实验',
            'conclusion': '结论',
        }

        for sec in section_order:
            if sec in sections:
                title = section_titles.get(sec, sec)
                content = sections[sec].get('content', '')
                word_count = len(content.split())
                print(f"\n{Colors.BOLD}{Colors.CYAN}══ {title} ══{Colors.RESET} ({word_count} 字)")
                print_divider("─", 40)
                # 显示前 500 字符
                preview = truncate(content, 500)
                print(preview)
                if len(content) > 500:
                    print(f"\n{Colors.DIM}... (完整内容请使用 view paper {sec}){Colors.RESET}")

        # 参考文献
        references = paper_data.get('references', [])
        print(f"\n{bold('参考文献')} ({len(references)} 篇):\n")
        for i, ref in enumerate(references[:10], 1):
            print(f"  [{i}] {ref.get('title', 'N/A')}")
            if ref.get('venue'):
                print(f"      {Colors.DIM}{ref.get('venue', '')}, {ref.get('year', '')}{Colors.RESET}")


def display_review_report(review_data: dict):
    """
    显示审阅报告

    Args:
        review_data: 审阅结果
    """
    print_section_header("📋 审阅报告")

    # 总体评分
    score = review_data.get('overall_score', 0)
    ready = review_data.get('ready_for_submission', False)

    if score >= 80:
        score_color = Colors.GREEN
        status = "✓ 可以提交"
    elif score >= 60:
        score_color = Colors.YELLOW
        status = "⚠ 建议修改后再提交"
    else:
        score_color = Colors.RED
        status = "✗ 需要大幅修改"

    print(f"\n{bold('总体评分')}: {score_color}{score}/100{Colors.RESET}")
    print(f"{bold('提交状态')}: {status}\n")

    # 问题统计
    print(f"{bold('问题统计')}:\n")
    issues = {
        '语法': len(review_data.get('grammar_issues', [])),
        '逻辑': len(review_data.get('logic_issues', [])),
        '引用': len(review_data.get('citation_issues', [])),
        '格式': len(review_data.get('format_issues', [])),
    }
    total = sum(issues.values())

    table_data = [[k, str(v)] for k, v in issues.items()]
    table_data.append(['总计', str(total)])
    print_table(["类型", "数量"], table_data)

    # 修改建议
    print(f"\n{bold('修改建议')}:\n")
    suggestions = review_data.get('suggestions', [])
    for i, sug in enumerate(suggestions[:10], 1):
        print(f"  {Colors.CYAN}{i}.{Colors.RESET} {sug}")


def display_project_status(project_state: dict):
    """
    显示项目状态

    Args:
        project_state: 项目状态数据
    """
    print_section_header("📁 项目状态")

    print(f"\n{bold('项目名称')}: {project_state.get('title', 'N/A')}")
    print(f"{bold('研究领域')}: {project_state.get('domain', 'N/A')}")
    print(f"{bold('当前阶段')}: {project_state.get('current_stage', 'N/A')}")

    # 检查点历史
    checkpoints = project_state.get('checkpoint_history', [])
    if checkpoints:
        print(f"\n{bold('已完成的确认点')}:\n")
        for cp in checkpoints:
            print(f"  {Colors.GREEN}{Icons.SUCCESS}{Colors.RESET} {cp.get('checkpoint_id', '')}: {cp.get('name', '')}")
    else:
        print(f"\n{Colors.DIM}暂无已完成的确认点{Colors.RESET}")


def display_help():
    """显示帮助信息"""
    print_section_header("📖 帮助")

    print(f"""
{bold('工作流控制命令:')}
  {Colors.CYAN}run{Colors.RESET}          运行当前阶段
  {Colors.CYAN}next{Colors.RESET}         进入下一阶段
  {Colors.CYAN}rollback <CP>{Colors.RESET}  回滚到指定确认点
  {Colors.CYAN}resume{Colors.RESET}       继续执行

{bold('查看命令:')}
  {Colors.CYAN}status{Colors.RESET}       查看项目状态
  {Colors.CYAN}stage{Colors.RESET}        查看工作流阶段
  {Colors.CYAN}progress{Colors.RESET}     查看进度
  {Colors.CYAN}view papers{Colors.RESET}  查看文献列表
  {Colors.CYAN}view gap{Colors.RESET}     查看 Gap 报告
  {Colors.CYAN}view method{Colors.RESET}  查看方法设计
  {Colors.CYAN}view experiment{Colors.RESET} 查看实验方案
  {Colors.CYAN}view paper{Colors.RESET}   查看论文草稿

{bold('项目管理命令:')}
  {Colors.CYAN}new{Colors.RESET}          创建新项目
  {Colors.CYAN}list{Colors.RESET}         列出所有项目
  {Colors.CYAN}switch <ID>{Colors.RESET}  切换项目

{bold('其他命令:')}
  {Colors.CYAN}export{Colors.RESET}       导出项目
  {Colors.CYAN}help{Colors.RESET}         显示帮助
  {Colors.CYAN}quit{Colors.RESET}         退出程序
""")


def print_divider(char: str = "─", width: int = 50):
    """打印分隔线（本地定义）"""
    from .widgets import Colors
    print(f"{Colors.DIM}{char * width}{Colors.RESET}")
