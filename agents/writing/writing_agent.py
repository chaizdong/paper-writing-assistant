"""
论文撰写 Agent

生成论文各章节内容（LaTeX/Markdown 格式）
"""

import logging
from typing import Any, Optional

from agents.base import BaseAgent, TaskRequest, TaskResponse

logger = logging.getLogger(__name__)


class WritingAgent(BaseAgent):
    """
    论文撰写 Agent

    职责:
    - 生成论文各章节（LaTeX/Markdown）
    - 管理引用和参考文献
    - 保持章节间逻辑连贯
    """

    def __init__(self, agent_id: str = "writing_agent", output_format: str = "latex"):
        super().__init__(
            agent_id=agent_id,
            name="WritingAgent",
            description="论文撰写 Agent - 生成论文各章节内容"
        )
        self.output_format = output_format

    def get_capabilities(self) -> list[str]:
        return [
            "write_abstract - 撰写摘要",
            "write_introduction - 撰写引言",
            "write_related_work - 撰写相关工作",
            "write_method - 撰写方法",
            "write_experiments - 撰写实验",
            "write_conclusion - 撰写结论",
            "generate_bibtex - 生成参考文献",
        ]

    def execute(self, task_request: TaskRequest) -> TaskResponse:
        """
        执行论文撰写任务

        Args:
            task_request: 任务请求，包含所有前期 Agent 的输出

        Returns:
            TaskResponse: 包含完整论文
        """
        try:
            # 解析输入
            input_data = task_request.input_data or {}

            # 提取各阶段数据
            literature_review = input_data.get("literature_review", {})
            gap_analysis = input_data.get("gap_analysis", {})
            method_design = input_data.get("method_design", {})
            experiment_plan = input_data.get("experiment_plan", {})

            # 提取具体字段
            papers = literature_review.get("papers", [])
            method = method_design.get("method", {})
            method_name = method.get("name", "Our Method")

            logger.info(f"开始论文撰写：方法={method_name}")

            # 发送进度更新
            self.send_progress(1, 7, "正在撰写摘要...")

            # 撰写各章节
            abstract = self._write_abstract(method_name, method_design)

            self.send_progress(2, 7, "正在撰写引言...")

            introduction = self._write_introduction(
                method_name, method_design, gap_analysis
            )

            self.send_progress(3, 7, "正在撰写相关工作...")

            related_work = self._write_related_work(literature_review)

            self.send_progress(4, 7, "正在撰写方法...")

            method = self._write_method(method_design)

            self.send_progress(5, 7, "正在撰写实验...")

            experiments = self._write_experiments(experiment_plan)

            self.send_progress(6, 7, "正在撰写结论...")

            conclusion = self._write_conclusion(method_name, method_design)

            self.send_progress(7, 7, "正在生成参考文献...")

            # 生成参考文献
            references = self._generate_references(papers)

            # 组合完整论文
            full_paper = self._assemble_paper(
                abstract=abstract,
                introduction=introduction,
                related_work=related_work,
                method=method,
                experiments=experiments,
                conclusion=conclusion,
                references=references,
            )

            logger.info("论文撰写完成")

            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": True,
                    "result": {
                        "sections": {
                            "abstract": {"content": abstract},
                            "introduction": {"content": introduction},
                            "related_work": {"content": related_work},
                            "method": {"content": method},
                            "experiments": {"content": experiments},
                            "conclusion": {"content": conclusion},
                        },
                        "references": references,
                        "full_paper": full_paper,
                        "format": self.output_format,
                    }
                }
            )

        except Exception as e:
            logger.exception(f"论文撰写失败：{e}")
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": False,
                    "error_message": str(e),
                }
            )

    def _write_abstract(self, method_name: str, method_design: dict) -> str:
        """撰写摘要"""
        contributions = method_design.get("contributions", [])

        if self.output_format == "latex":
            return f"""\\begin{{abstract}}
近年来，XX 领域的研究取得了显著进展，但现有方法在 XX 方面仍存在局限性。
针对这一问题，本文提出了{method_name}，一种新颖的 XX 方法。

本文的主要贡献包括：
(1) {contributions[0] if contributions else '提出了新方法'}；
(2) {contributions[1] if len(contributions) > 1 else '设计了关键模块'}；
(3) {contributions[2] if len(contributions) > 2 else '验证了方法有效性'}。

在多个基准数据集上的实验结果表明，{method_name} 优于现有 SOTA 方法，
在主要评价指标上提升了 X.X%。
\\end{{abstract}}"""
        else:
            return f"""## 摘要

近年来，XX 领域的研究取得了显著进展，但现有方法在 XX 方面仍存在局限性。
针对这一问题，本文提出了{method_name}，一种新颖的 XX 方法。

本文的主要贡献包括：
1. {contributions[0] if contributions else '提出了新方法'}
2. {contributions[1] if len(contributions) > 1 else '设计了关键模块'}
3. {contributions[2] if len(contributions) > 2 else '验证了方法有效性'}

在多个基准数据集上的实验结果表明，{method_name} 优于现有 SOTA 方法，
在主要评价指标上提升了 X.X%。

**关键词**: {method_name}, XX 任务，深度学习，SOTA
"""

    def _write_introduction(
        self,
        method_name: str,
        method_design: dict,
        gap_analysis: dict
    ) -> str:
        """撰写引言"""
        core_idea = method_design.get("method", {}).get("core_idea", "")
        limitations = gap_analysis.get("limitations", [])

        if self.output_format == "latex":
            return f"""\\section{{Introduction}}
\\label{{sec:intro}}

\\paragraph{背景}
XX 任务是 XX 领域的核心问题之一，在 XX 场景中具有重要应用价值。
近年来，深度学习的快速发展为该任务带来了革命性进展。

\\paragraph{问题与挑战}
然而，现有方法仍面临以下挑战：
{chr(10).join(f'- {lim}' for lim in limitations[:3])}

这些问题的根本原因在于 XX，这给现有方法带来了本质性限制。

\\paragraph{本文方法}
针对上述问题，本文提出了{method_name}。
核心思想是：{core_idea[:100]}...

\\paragraph{本文贡献}
本文的主要贡献总结如下：
\\begin{{itemize}}
    \\item {method_design.get('contributions', ['贡献 1'])[0]}
    \\item {method_design.get('contributions', ['贡献 2'])[1] if len(method_design.get('contributions', [])) > 1 else '设计了关键模块'}
    \\item {method_design.get('contributions', ['贡献 3'])[2] if len(method_design.get('contributions', [])) > 2 else '实验验证有效性'}
\\end{{itemize}}
"""
        else:
            return f"""## 引言

### 背景

XX 任务是 XX 领域的核心问题之一，在 XX 场景中具有重要应用价值。
近年来，深度学习的快速发展为该任务带来了革命性进展。

### 问题与挑战

然而，现有方法仍面临以下挑战：
{chr(10).join(f'- {lim}' for lim in limitations[:3])}

这些问题的根本原因在于 XX，这给现有方法带来了本质性限制。

### 本文方法

针对上述问题，本文提出了{method_name}。
核心思想是：{core_idea[:100]}...

### 本文贡献

本文的主要贡献总结如下：
1. {method_design.get('contributions', ['贡献 1'])[0]}
2. {method_design.get('contributions', ['贡献 2'])[1] if len(method_design.get('contributions', [])) > 1 else '设计了关键模块'}
3. {method_design.get('contributions', ['贡献 3'])[2] if len(method_design.get('contributions', [])) > 2 else '实验验证有效性'}
"""

    def _write_related_work(self, literature_review: dict) -> str:
        """撰写相关工作"""
        papers = literature_review.get("papers", [])
        summary = literature_review.get("summary", "")

        if self.output_format == "latex":
            content = """\\section{Related Work}
\label{sec:related}

"""
            # 按方法分组讨论
            content += "\\paragraph{基于 XX 的方法}\n"
            content += "早期工作主要采用 XX 方法，代表性工作包括...\n\n"

            for i, paper in enumerate(papers[:5], 1):
                content += f"Paper {i}: {paper.get('title', 'N/A')}\\cite{{{paper.get('id', 'ref')}}}...\n"

            content += """
\\paragraph{基于深度学习的方法}
随着深度学习的发展，XX 方法被广泛应用于该任务...

\\paragraph{基于 Transformer 的方法}
近年来，Transformer 架构在该任务上取得了 SOTA 结果...

\\paragraph{总结}
综上所述，现有方法虽然取得了一定进展，但在 XX 方面仍存在局限性。
本文提出的方法针对这些局限性进行改进。
"""
            return content
        else:
            return f"""## 相关工作

### 基于 XX 的方法

早期工作主要采用 XX 方法，代表性工作包括...

{chr(10).join(f"- Paper {i}: {p.get('title', 'N/A')}" for i, p in enumerate(papers[:5], 1))}

### 基于深度学习的方法

随着深度学习的发展，XX 方法被广泛应用于该任务...

### 基于 Transformer 的方法

近年来，Transformer 架构在该任务上取得了 SOTA 结果...

### 总结

综上所述，现有方法虽然取得了一定进展，但在 XX 方面仍存在局限性。
本文提出的方法针对这些局限性进行改进。
"""

    def _write_method(self, method_design: dict) -> str:
        """撰写方法"""
        method = method_design.get("method", {})
        technical_route = method_design.get("technical_route", [])
        method_description = method_design.get("method_description", "")

        if self.output_format == "latex":
            method_name = method.get('name', 'Our Method')
            return f"""\\section{{Method}}
\\label{{sec:method}}

\\section{{Overview}}
如图\\ref{{fig:framework}}所示，{method_name} 包含以下核心组件...

\\begin{{figure}}[t]
    \\centering
    \\includegraphics[width=\\linewidth]{{figures/framework.pdf}}
    \\caption{{{method_name} 框架图}}
    \\label{{fig:framework}}
\\end{{figure}}

\\subsection{{核心组件}}
{method_description}

\\subsection{{技术路线}}
{chr(10).join(f'\\paragraph{{Step {step["step"]}: {step["name"]}}}' + chr(10) + f'{step["description"]}' for step in technical_route)}
"""
        else:
            return f"""## 方法

### 总览

如图所示，{method.get('name', 'Our Method')} 包含以下核心组件...

### 核心组件

{method_description}

### 技术路线

{chr(10).join(f'#### Step {step["step"]}: {step["name"]}' + chr(10) + f'{step["description"]}' for step in technical_route)}
"""

    def _write_experiments(self, experiment_plan: dict) -> str:
        """撰写实验"""
        datasets = experiment_plan.get("datasets", [])
        baselines = experiment_plan.get("baselines", [])
        metrics = experiment_plan.get("metrics", [])
        ablation_studies = experiment_plan.get("ablation_studies", [])

        if self.output_format == "latex":
            content = """\\section{Experiments}
\label{sec:experiments}

\\subsection{Experimental Setup}

\\paragraph{Datasets}
我们使用以下数据集进行实验：
"""
            for ds in datasets:
                content += f"\\item \\textbf{{{ds['name']}}}: {ds['description']}\n"

            content += """
\\paragraph{Baselines}
对比方法包括：
"""
            for bl in baselines:
                content += f"\\item \\textbf{{{bl['name']}}} ({bl['citation']})\n"

            content += """
\\paragraph{Evaluation Metrics}
评价指标：
"""
            for m in metrics:
                content += f"\\item \\textbf{{{m['name']}}}: {m['description']}\n"

            content += """
\\subsection{Main Results}
表\\ref{tab:main} 展示了主要实验结果...

\\begin{table}[t]
    \centering
    \begin{tabular}{l|ccc}
        \hline
        Method & Metric1 & Metric2 & Metric3 \\
        \hline
        Baseline1 & XX.X & XX.X & XX.X \\
        Baseline2 & XX.X & XX.X & XX.X \\
        \hline
        \textbf{Ours} & \textbf{XX.X} & \textbf{XX.X} & \textbf{XX.X} \\
        \hline
    \end{tabular}
    \caption{主要实验结果}
    \label{tab:main}
\end{table}

\\subsection{Ablation Study}
为验证各模块的有效性，我们进行了消融实验...

\\subsection{Qualitative Analysis}
图\\ref{fig:vis} 展示了可视化结果...
"""
            return content
        else:
            return f"""## 实验

### 实验设置

**数据集**:
{chr(10).join(f'- {ds["name"]}: {ds["description"]}' for ds in datasets)}

**Baseline 方法**:
{chr(10).join(f'- {bl["name"]} ({bl["citation"]})' for bl in baselines)}

**评价指标**:
{chr(10).join(f'- {m["name"]}: {m["description"]}' for m in metrics)}

### 主要结果

| Method | Metric1 | Metric2 | Metric3 |
|--------|---------|---------|---------|
| Baseline1 | XX.X | XX.X | XX.X |
| Baseline2 | XX.X | XX.X | XX.X |
| **Ours** | **XX.X** | **XX.X** | **XX.X** |

### 消融实验

{chr(10).join(f'- {ab["variant"]}: {ab["purpose"]}' for ab in ablation_studies)}

### 可视化分析

(此处添加可视化结果图)
"""

    def _write_conclusion(self, method_name: str, method_design: dict) -> str:
        """撰写结论"""
        if self.output_format == "latex":
            return f"""\\section{{Conclusion}}
\label{{sec:conclusion}}

本文提出了{method_name}，一种针对 XX 问题的新方法。
通过{method_design.get('method', {}).get('design_principle', '创新设计')}，
我们的方法在多个基准数据集上取得了 SOTA 结果。

未来工作将探索：
(1) 将方法扩展到其他相关任务；
(2) 进一步优化计算效率；
(3) 探索在实际应用场景中的部署。
"""
        else:
            return f"""## 结论

本文提出了{method_name}，一种针对 XX 问题的新方法。
通过{method_design.get('method', {}).get('design_principle', '创新设计')}，
我们的方法在多个基准数据集上取得了 SOTA 结果。

未来工作将探索：
1. 将方法扩展到其他相关任务
2. 进一步优化计算效率
3. 探索在实际应用场景中的部署
"""

    def _generate_references(self, papers: list[dict]) -> list[dict]:
        """生成参考文献"""
        references = []
        for i, paper in enumerate(papers[:20], 1):
            references.append({
                "id": f"ref{i}",
                "title": paper.get("title", "N/A"),
                "authors": paper.get("authors", []),
                "venue": paper.get("venue", "N/A"),
                "year": paper.get("year", "2024"),
            })
        return references

    def _assemble_paper(
        self,
        abstract: str,
        introduction: str,
        related_work: str,
        method: str,
        experiments: str,
        conclusion: str,
        references: list[dict],
    ) -> str:
        """组装完整论文"""
        if self.output_format == "latex":
            return f"""\\documentclass{{article}}
\\usepackage{{graphicx}}
\\usepackage{{amsmath}}
\\usepackage{{booktabs}}

\\title{{XX Paper Title}}
\\author{{Anonymous}}
\\date{{2024}}

\\begin{{document}}

\\maketitle

{abstract}

{introduction}

{related_work}

{method}

{experiments}

{conclusion}

\\bibliographystyle{{plain}}
\\begin{{thebibliography}}{{99}}
{chr(10).join(f'\\bibitem{{{ref["id"]}}} {ref["authors"][0] if ref["authors"] else "Unknown"}. {ref["title"]}. {ref["venue"]}, {ref["year"]}.' for ref in references)}
\\end{{thebibliography}}

\\end{{document}}
"""
        else:
            return f"""# Paper Title

{abstract}

---

{introduction}

---

{related_work}

---

{method}

---

{experiments}

---

{conclusion}

---

## References

{chr(10).join(f'{i}. {ref["authors"][0] if ref["authors"] else "Unknown"}. {ref["title"]}. {ref["venue"]}, {ref["year"]}.' for i, ref in enumerate(references, 1))}
"""
