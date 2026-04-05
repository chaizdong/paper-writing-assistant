#!/usr/bin/env python3
"""
核心 Agents 测试脚本

测试所有 6 个核心 Agent 的功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_literature_agent():
    """测试 LiteratureAgent"""
    print("\n" + "=" * 50)
    print("  测试 LiteratureAgent (文献调研)")
    print("=" * 50)

    from agents.research import LiteratureAgent

    # 创建 Agent
    agent = LiteratureAgent(max_papers=5)
    print(f"\n[1] Agent 创建：{agent.name}")
    print(f"    能力：{agent.get_capabilities()}")

    # 测试执行
    from agents.base import TaskRequest
    task = TaskRequest(
        sender="test",
        receiver="literature_agent",
        payload={
            "task_type": "literature_review",
            "input_data": {
                "search_query": "Transformer for Time Series Forecasting",
                "keywords": ["Transformer", "Time Series"],
                "limit": 5,
            }
        }
    )

    print("\n[2] 执行文献调研...")
    response = agent.handle_message(task)

    assert response.payload["success"] == True
    result = response.payload["result"]
    print(f"    找到论文数：{result['total_found']}")
    print(f"    摘要长度：{len(result['summary'])} 字符")

    print("\n✓ LiteratureAgent 测试通过")
    return True


def test_gap_analysis_agent():
    """测试 GapAnalysisAgent"""
    print("\n" + "=" * 50)
    print("  测试 GapAnalysisAgent (Gap 分析)")
    print("=" * 50)

    from agents.research import GapAnalysisAgent

    # 创建 Agent
    agent = GapAnalysisAgent()
    print(f"\n[1] Agent 创建：{agent.name}")
    print(f"    能力：{agent.get_capabilities()}")

    # 准备模拟输入
    from agents.base import TaskRequest
    task = TaskRequest(
        sender="test",
        receiver="gap_analysis_agent",
        payload={
            "task_type": "gap_analysis",
            "input_data": {
                "papers": [
                    {
                        "id": "paper1",
                        "title": "Paper 1",
                        "abstract": "However, this method has limitations in efficiency.",
                        "methods": ["Transformer"],
                    },
                    {
                        "id": "paper2",
                        "title": "Paper 2",
                        "abstract": "The main challenge is the requirement for large datasets.",
                        "methods": ["Attention"],
                    },
                ],
                "summary": "文献总结...",
            }
        }
    )

    print("\n[2] 执行 Gap 分析...")
    response = agent.handle_message(task)

    assert response.payload["success"] == True
    result = response.payload["result"]
    print(f"    识别方法数：{len(result['existing_methods'])}")
    print(f"    局限性数：{len(result['limitations'])}")
    print(f"    研究空白数：{len(result['research_gaps'])}")

    print("\n✓ GapAnalysisAgent 测试通过")
    return True


def test_method_agent():
    """测试 MethodAgent"""
    print("\n" + "=" * 50)
    print("  测试 MethodAgent (方法设计)")
    print("=" * 50)

    from agents.design import MethodAgent

    # 创建 Agent
    agent = MethodAgent()
    print(f"\n[1] Agent 创建：{agent.name}")
    print(f"    能力：{agent.get_capabilities()}")

    # 准备模拟输入
    from agents.base import TaskRequest
    task = TaskRequest(
        sender="test",
        receiver="method_agent",
        payload={
            "task_type": "method_design",
            "input_data": {
                "gap_analysis": {
                    "research_gaps": [
                        {
                            "gap": "现有方法计算复杂度高",
                            "opportunity": "设计高效轻量级方法",
                        }
                    ],
                    "recommendation": "建议设计高效方法",
                }
            }
        }
    )

    print("\n[2] 执行方法设计...")
    response = agent.handle_message(task)

    assert response.payload["success"] == True
    result = response.payload["result"]
    print(f"    方法名称：{result['method']['name']}")
    print(f"    贡献点数：{len(result['contributions'])}")
    print(f"    技术路线步骤：{len(result['technical_route'])}")

    print("\n✓ MethodAgent 测试通过")
    return True


def test_experiment_agent():
    """测试 ExperimentAgent"""
    print("\n" + "=" * 50)
    print("  测试 ExperimentAgent (实验规划)")
    print("=" * 50)

    from agents.experiment import ExperimentAgent

    # 创建 Agent
    agent = ExperimentAgent()
    print(f"\n[1] Agent 创建：{agent.name}")
    print(f"    能力：{agent.get_capabilities()}")

    # 准备模拟输入
    from agents.base import TaskRequest
    task = TaskRequest(
        sender="test",
        receiver="experiment_agent",
        payload={
            "task_type": "experiment_planning",
            "input_data": {
                "method": {
                    "name": "EfficientNet",
                    "keywords": ["高效", "轻量级"],
                    "design_principle": "设计轻量级高效率方法",
                    "components": [
                        {"name": "Module A"},
                        {"name": "Module B"},
                    ],
                }
            }
        }
    )

    print("\n[2] 执行实验规划...")
    response = agent.handle_message(task)

    assert response.payload["success"] == True
    result = response.payload["result"]
    print(f"    任务类型：{result['task_type']}")
    print(f"    数据集数：{len(result['datasets'])}")
    print(f"    Baseline 数：{len(result['baselines'])}")
    print(f"    评价指标数：{len(result['metrics'])}")
    print(f"    消融实验数：{len(result['ablation_studies'])}")

    print("\n✓ ExperimentAgent 测试通过")
    return True


def test_writing_agent():
    """测试 WritingAgent"""
    print("\n" + "=" * 50)
    print("  测试 WritingAgent (论文撰写)")
    print("=" * 50)

    from agents.writing import WritingAgent

    # 创建 Agent
    agent = WritingAgent(output_format="markdown")
    print(f"\n[1] Agent 创建：{agent.name}")
    print(f"    输出格式：{agent.output_format}")
    print(f"    能力：{agent.get_capabilities()}")

    # 准备模拟输入
    from agents.base import TaskRequest
    task = TaskRequest(
        sender="test",
        receiver="writing_agent",
        payload={
            "task_type": "writing",
            "input_data": {
                "literature_review": {
                    "papers": [
                        {"title": "Paper 1", "authors": ["A"], "venue": "CVPR", "year": 2023},
                    ],
                    "summary": "文献总结",
                },
                "gap_analysis": {
                    "limitations": ["局限性 1"],
                },
                "method_design": {
                    "method": {
                        "name": "OurMethod",
                        "core_idea": "核心思想",
                        "design_principle": "设计原则",
                    },
                    "contributions": ["贡献 1", "贡献 2", "贡献 3"],
                },
                "experiment_plan": {
                    "datasets": [{"name": "Dataset1", "description": "D1"}],
                    "baselines": [{"name": "Baseline1", "citation": "C1"}],
                    "metrics": [{"name": "Accuracy", "description": "ACC"}],
                    "ablation_studies": [{"variant": "w/o A", "purpose": "验证 A"}],
                },
            }
        }
    )

    print("\n[2] 执行论文撰写...")
    response = agent.handle_message(task)

    assert response.payload["success"] == True
    result = response.payload["result"]
    print(f"    章节数：{len(result['sections'])}")
    print(f"    参考文献数：{len(result['references'])}")
    print(f"    完整论文长度：{len(result['full_paper'])} 字符")

    print("\n✓ WritingAgent 测试通过")
    return True


def test_review_agent():
    """测试 ReviewAgent"""
    print("\n" + "=" * 50)
    print("  测试 ReviewAgent (审阅润色)")
    print("=" * 50)

    from agents.writing import ReviewAgent

    # 创建 Agent
    agent = ReviewAgent()
    print(f"\n[1] Agent 创建：{agent.name}")
    print(f"    能力：{agent.get_capabilities()}")

    # 准备模拟输入
    from agents.base import TaskRequest
    task = TaskRequest(
        sender="test",
        receiver="review_agent",
        payload={
            "task_type": "review",
            "input_data": {
                "paper": {
                    "sections": {
                        "abstract": {"content": "Abstract content..."},
                        "introduction": {"content": "Introduction content... " * 50},
                        "method": {"content": "Method content..."},
                        "experiments": {"content": "Experiments content..."},
                    },
                    "references": [
                        {"id": "ref1", "title": "Ref 1", "authors": ["A"], "venue": "V", "year": 2023},
                    ],
                },
                "target_venue": "general",
            }
        }
    )

    print("\n[2] 执行审阅...")
    response = agent.handle_message(task)

    assert response.payload["success"] == True
    result = response.payload["result"]
    print(f"    总体评分：{result['overall_score']}/100")
    print(f"    语法问题数：{len(result['grammar_issues'])}")
    print(f"    逻辑问题数：{len(result['logic_issues'])}")
    print(f"    引用问题数：{len(result['citation_issues'])}")
    print(f"    格式问题数：{len(result['format_issues'])}")
    print(f"    修改建议数：{len(result['suggestions'])}")
    print(f"    可提交状态：{result['ready_for_submission']}")

    print("\n✓ ReviewAgent 测试通过")
    return True


def test_full_pipeline():
    """测试完整流程"""
    print("\n" + "=" * 50)
    print("  测试完整论文写作流程")
    print("=" * 50)

    from agents.base import get_orchestrator
    from agents.research import LiteratureAgent, GapAnalysisAgent
    from agents.design import MethodAgent
    from agents.experiment import ExperimentAgent
    from agents.writing import WritingAgent, ReviewAgent

    # 初始化编排器
    orch = get_orchestrator()

    # 注册所有 Agent
    agents = [
        LiteratureAgent(agent_id="literature", max_papers=3),
        GapAnalysisAgent(agent_id="gap"),
        MethodAgent(agent_id="method"),
        ExperimentAgent(agent_id="experiment"),
        WritingAgent(agent_id="writing", output_format="markdown"),
        ReviewAgent(agent_id="review"),
    ]

    for agent in agents:
        orch.register_agent(agent)

    print(f"\n[1] 已注册 {len(agents)} 个 Agent")

    # 执行流程
    print("\n[2] 执行文献调研...")
    lit_response = orch.execute_task(
        agent_id="literature",
        task_type="literature_review",
        input_data={"search_query": "Deep Learning", "limit": 3}
    )
    # 检查响应
    if not lit_response.payload.get("success"):
        print(f"    文献调研失败：{lit_response.payload.get('error_message', 'Unknown')}")
        return False
    print(f"    找到 {len(lit_response.payload['result']['papers'])} 篇论文")

    print("[3] 执行 Gap 分析...")
    gap_response = orch.execute_task(
        agent_id="gap",
        task_type="gap_analysis",
        input_data={
            "papers": lit_response.payload["result"]["papers"],
            "summary": lit_response.payload["result"]["summary"],
        }
    )
    if not gap_response.payload.get("success"):
        print(f"    Gap 分析失败：{gap_response.payload.get('error_message', 'Unknown')}")
        return False

    print("[4] 执行方法设计...")
    method_response = orch.execute_task(
        agent_id="method",
        task_type="method_design",
        input_data={"gap_analysis": gap_response.payload["result"]}
    )
    if not method_response.payload.get("success"):
        print(f"    方法设计失败：{method_response.payload.get('error_message', 'Unknown')}")
        return False

    print("[5] 执行实验规划...")
    exp_response = orch.execute_task(
        agent_id="experiment",
        task_type="experiment_planning",
        input_data={"method": method_response.payload["result"]["method"]}
    )
    if not exp_response.payload.get("success"):
        print(f"    实验规划失败：{exp_response.payload.get('error_message', 'Unknown')}")
        return False

    print("[6] 执行论文撰写...")
    write_response = orch.execute_task(
        agent_id="writing",
        task_type="writing",
        input_data={
            "literature_review": lit_response.payload["result"],
            "gap_analysis": gap_response.payload["result"],
            "method_design": method_response.payload["result"],
            "experiment_plan": exp_response.payload["result"],
        }
    )
    if not write_response.payload.get("success"):
        print(f"    论文撰写失败：{write_response.payload.get('error_message', 'Unknown')}")
        return False

    print("[7] 执行审阅...")
    review_response = orch.execute_task(
        agent_id="review",
        task_type="review",
        input_data={
            "paper": write_response.payload["result"],
            "target_venue": "general",
        }
    )
    if not review_response.payload.get("success"):
        print(f"    审阅失败：{review_response.payload.get('error_message', 'Unknown')}")
        return False

    print(f"\n    最终评分：{review_response.payload['result']['overall_score']}/100")
    print(f"    可提交：{review_response.payload['result']['ready_for_submission']}")

    print("\n✓ 完整流程测试通过")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  论文写作 Agent 系统 - 核心 Agents 测试")
    print("=" * 60)

    results = []
    tests = [
        ("LiteratureAgent", test_literature_agent),
        ("GapAnalysisAgent", test_gap_analysis_agent),
        ("MethodAgent", test_method_agent),
        ("ExperimentAgent", test_experiment_agent),
        ("WritingAgent", test_writing_agent),
        ("ReviewAgent", test_review_agent),
        ("完整流程", test_full_pipeline),
    ]

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

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
        print("\n  ✓ 所有 Agents 测试通过！系统可以正常运行")
        return 0
    else:
        print(f"\n  ✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
