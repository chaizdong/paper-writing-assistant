# 论文写作辅助系统

一个基于 Agent 的论文写作辅助工具，通过人机协作的方式帮助用户完成从主题到完整论文的全流程。

## 系统特点

- **人机协作**：10 个确认点确保方向可控
- **6 个核心 Agent**：文献调研、Gap 分析、方法设计、实验规划、论文撰写、审阅润色
- **增强 CLI**：富文本输出、友好交互、工作流控制
- **检查点机制**：支持保存/恢复进度，可回滚到任意阶段
- **Claude 生态**：基于 Claude Code + MCP 工具链构建

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

### 常用命令

```
# 项目管理
new                 创建新项目
list                列出所有项目
switch <ID>         切换项目
export              导出论文

# 工作流控制
run                 运行当前阶段
next                进入下一阶段
rollback <CP>       回滚到确认点

# 查看结果
status              查看项目状态
view papers         查看文献列表
view gap            查看 Gap 报告
view method         查看方法设计
view experiment     查看实验方案
view paper          查看论文草稿
review              查看审阅报告

# 帮助
help                显示所有命令
tutorial            新手教程
cheatsheet          命令速查
```

## 完整工作流

```
1. 输入 new 创建项目
   ↓
2. CP1: 确认研究主题
   ↓
3. 输入 run 执行文献调研
   ↓
4. CP2: 确认文献筛选
   ↓
5. 输入 run 执行 Gap 分析
   ↓
6. CP3: 确认 Gap 报告
   ↓
7. 输入 run 执行方法设计
   ↓
8. CP4/CP5: 确认技术方案和创新性
   ↓
9. 输入 run 执行实验规划
   ↓
10. CP6/CP7: 确认实验设计
    ↓
11. 输入 run 执行论文撰写
    ↓
12. CP8/CP9: 确认大纲和章节
    ↓
13. CP10: 最终审阅 → export 导出
```

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    增强 CLI (v0.2.0)                         │
│  工作流控制 | 结果查看 | 确认点交互 | 项目管理                │
├─────────────────────────────────────────────────────────────┤
│                       工作流引擎                              │
│     文献调研 → Gap 分析 → 方法设计 → 实验规划 → 论文撰写       │
├─────────────────────────────────────────────────────────────┤
│                        6 个核心 Agent                         │
│  Literature  │  Gap   │  Method │ Experiment │ Writing │Review│
├─────────────────────────────────────────────────────────────┤
│                      基础设施                                 │
│   状态管理器 (SQLite)  |  编排器  |  MCP 工具注册中心          │
└─────────────────────────────────────────────────────────────┘
```

## UI 组件

- **widgets.py** - 进度条、表格、卡片、状态图标
- **display.py** - 文献列表、Gap 报告、论文草稿显示
- **interactive.py** - 10 个确认点的交互逻辑
- **cli.py** - EnhancedCLI 增强命令行界面

## 开发路线图

### 阶段 1：基础框架 ✅ 完成
- [x] 创建目录结构
- [x] 实现 Agent 基类
- [x] 实现消息类型
- [x] 实现编排器
- [x] 实现 MCP 工具注册中心
- [x] 实现状态管理器
- [x] 实现工作流引擎
- [x] 配置文件和入口程序

### 阶段 2：核心 Agents ✅ 完成
- [x] LiteratureAgent - 文献调研
- [x] GapAnalysisAgent - Gap 分析
- [x] MethodAgent - 方法设计
- [x] ExperimentAgent - 实验规划
- [x] WritingAgent - 论文撰写
- [x] ReviewAgent - 审阅润色

### 阶段 3：CLI 增强 ✅ 完成
- [x] UI 组件模块（widgets.py）
- [x] 确认点交互（interactive.py）
- [x] 富文本显示（display.py）
- [x] 增强 CLI（cli.py）
- [x] 工作流集成（main.py）

### 阶段 4：MCP 工具集成（待开发）
- [ ] arXiv MCP 客户端
- [ ] Semantic Scholar MCP 客户端
- [ ] 真实 API 对接

## 技术栈

- Python 3.10+
- PyYAML
- SQLite3（内置）
- Claude Code（推荐运行环境）
- MCP 工具链（待集成）

## License

MIT
