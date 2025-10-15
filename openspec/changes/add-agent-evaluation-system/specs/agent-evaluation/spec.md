# Agent 评估系统规范

## ADDED Requirements

### Requirement: 批量游戏运行

系统 SHALL 支持批量运行多局狼人杀游戏，以便评估 Agent 性能。

#### Scenario: 运行 10 局基线游戏
- **WHEN** 用户执行 `python evaluate.py --num-games 10 --mode baseline`
- **THEN** 系统应运行 10 局游戏，所有玩家使用默认的 ReActAgent
- **AND** 系统应显示进度信息（如 "Running game 3/10..."）
- **AND** 系统应记录每局游戏的结果

#### Scenario: 运行 10 局自定义 Agent 游戏
- **WHEN** 用户执行 `python evaluate.py --num-games 10 --mode custom --custom-agent examples/agent_werewolves/enhanced_agent.py`
- **THEN** 系统应运行 10 局游戏，指定角色使用自定义 Agent，其他角色使用默认 Agent
- **AND** 系统应记录每局游戏的结果

#### Scenario: 处理游戏运行失败
- **WHEN** 某局游戏因异常而失败（如 API 错误）
- **THEN** 系统应记录失败信息
- **AND** 系统应继续运行后续游戏
- **AND** 最终报告中应标注失败的局数

### Requirement: 游戏结果记录

系统 SHALL 记录每局游戏的详细结果，包括胜负、角色分配、存活情况等。

#### Scenario: 记录游戏胜负
- **WHEN** 一局游戏结束
- **THEN** 系统应记录胜利方（"werewolves" 或 "villagers"）
- **AND** 系统应记录游戏总轮数

#### Scenario: 记录玩家信息
- **WHEN** 一局游戏结束
- **THEN** 系统应记录每个玩家的姓名、角色、是否存活、存活轮数
- **AND** 记录数据应使用结构化格式（Pydantic BaseModel）

#### Scenario: 保存结果到文件
- **WHEN** 所有游戏运行完成
- **THEN** 系统应将结果保存为 JSON 文件
- **AND** 文件路径应可通过 `--output` 参数配置
- **AND** 默认路径为 `evaluation_results_<timestamp>.json`

### Requirement: 统计分析

系统 SHALL 提供统计分析功能，计算胜率和其他关键指标。

#### Scenario: 计算总体胜率
- **WHEN** 用户查看评估报告
- **THEN** 报告应显示好人阵营的胜率（百分比）
- **AND** 报告应显示狼人阵营的胜率（百分比）
- **AND** 报告应显示总局数和有效局数

#### Scenario: 计算特定 Agent 的胜率
- **WHEN** 使用自定义 Agent 运行游戏
- **THEN** 报告应显示使用该 Agent 的玩家的胜率
- **AND** 报告应区分不同角色（如"自定义狼人 Agent 的胜率"）

#### Scenario: 对比基线和自定义 Agent
- **WHEN** 用户分别运行基线和自定义 Agent 评估
- **THEN** 系统应提供对比功能
- **AND** 报告应显示胜率提升百分点（如 "+5%"）
- **AND** 报告应显示统计显著性提示（如样本量是否足够）

### Requirement: 评估报告生成

系统 SHALL 生成可读的评估报告，展示统计结果。

#### Scenario: 生成文本格式报告
- **WHEN** 评估完成
- **THEN** 系统应在终端输出文本格式报告
- **AND** 报告应包含：总局数、胜率统计、角色统计、对比结果（如有）
- **AND** 报告应使用表格格式，易于阅读

#### Scenario: 生成 JSON 格式报告
- **WHEN** 用户指定 `--output report.json`
- **THEN** 系统应生成 JSON 格式的详细报告
- **AND** JSON 应包含所有原始数据和统计结果
- **AND** JSON 格式应遵循定义的 schema

#### Scenario: 显示关键指标
- **WHEN** 用户查看报告
- **THEN** 报告 MUST 包含以下指标：
  - 总局数（total_games）
  - 好人胜率（villagers_win_rate）
  - 狼人胜率（werewolves_win_rate）
  - 平均游戏轮数（avg_rounds）
  - 失败局数（failed_games，如有）

### Requirement: Agent 工厂接口

系统 SHALL 支持通过 Agent 工厂函数注入自定义 Agent 实现。

#### Scenario: 使用默认 Agent 工厂
- **WHEN** 未指定自定义 Agent
- **THEN** 系统应使用默认的 `create_player` 函数创建所有玩家
- **AND** 所有玩家应为 ReActAgent 实例

#### Scenario: 注入自定义 Agent 工厂
- **WHEN** 用户提供自定义 Agent 模块路径
- **THEN** 系统应动态加载该模块
- **AND** 系统应调用模块中的 `custom_agent_factory(role: str)` 函数
- **AND** 自定义工厂应返回符合接口要求的 Agent 实例

#### Scenario: 验证自定义 Agent 接口
- **WHEN** 加载自定义 Agent
- **THEN** 系统应验证 Agent 实现了必需的方法：
  - `observe(msg)` 方法
  - `__call__(msg)` 或 `__call__()` 方法
  - `state_dict()` 和 `load_state_dict()` 方法
- **AND** 如果接口不完整，应给出清晰的错误提示

### Requirement: 游戏逻辑封装

系统 SHALL 将现有游戏逻辑封装为可复用的类，同时保持向后兼容。

#### Scenario: 单局游戏运行保持不变
- **WHEN** 用户执行 `python examples/game/werewolves/main.py`
- **THEN** 游戏应按原有方式运行一局
- **AND** 游戏行为应与重构前完全一致

#### Scenario: 游戏类实例化
- **WHEN** 评估系统创建 `WerewolfGame` 实例
- **THEN** 应支持传入可选的 `agent_factory` 参数
- **AND** 应支持传入可选的随机种子参数

#### Scenario: 游戏结果返回
- **WHEN** 调用 `game.run()` 方法
- **THEN** 方法应返回 `GameResult` 对象
- **AND** `GameResult` 应包含胜利方、玩家信息、轮数等完整数据

### Requirement: 示例自定义 Agent

系统 SHALL 提供一个示例自定义 Agent 实现，展示如何继承和改进基线 Agent。

#### Scenario: 示例 Agent 满足比赛要求
- **WHEN** 用户查看示例 Agent 代码
- **THEN** 示例应实现所有必需的接口：
  - `observe(msg)` 方法
  - `__call__(msg)` 和 `__call__()` 重载
  - 支持结构化输出 `agent(msg, structured_model=Model)`
  - 实现 `state_dict()` 和 `load_state_dict()` 方法

#### Scenario: 示例 Agent 展示改进策略
- **WHEN** 用户阅读示例 Agent 实现
- **THEN** 代码应包含注释，说明改进点（如增强的系统提示词、记忆管理等）
- **AND** 应提供使用文档，说明如何基于示例创建自己的 Agent

#### Scenario: 示例 Agent 可直接用于评估
- **WHEN** 用户执行 `python evaluate.py --custom-agent examples/agent_werewolves/enhanced_agent.py`
- **THEN** 系统应成功加载并使用示例 Agent
- **AND** 评估应正常运行完成

### Requirement: 命令行接口

系统 SHALL 提供用户友好的命令行接口配置评估参数。

#### Scenario: 基本参数配置
- **WHEN** 用户执行 `python evaluate.py --help`
- **THEN** 系统应显示所有可用参数的帮助信息
- **AND** 应包含参数说明和默认值

#### Scenario: 必需参数和可选参数
- **WHEN** 用户执行 `python evaluate.py`（无参数）
- **THEN** 系统应使用默认值运行：
  - `--num-games`: 10
  - `--mode`: baseline
  - `--output`: `evaluation_results_<timestamp>.json`
  - `--seed`: None（随机）

#### Scenario: 参数验证
- **WHEN** 用户提供无效参数（如 `--num-games -5`）
- **THEN** 系统应显示错误信息
- **AND** 系统应退出并提示正确用法

### Requirement: 错误处理和日志

系统 SHALL 提供完善的错误处理和日志记录功能。

#### Scenario: 记录运行日志
- **WHEN** 评估运行时
- **THEN** 系统应输出进度信息到终端
- **AND** 应记录关键事件（如游戏开始、结束、失败）
- **AND** 日志级别应可配置（INFO, DEBUG）

#### Scenario: 处理 API 错误
- **WHEN** 大模型 API 调用失败（如网络错误）
- **THEN** 系统应捕获异常
- **AND** 系统应记录错误信息
- **AND** 系统应标记该局游戏为失败
- **AND** 系统应继续运行后续游戏（不中断整体评估）

#### Scenario: 处理 Agent 接口错误
- **WHEN** 自定义 Agent 缺少必需方法
- **THEN** 系统应在加载时检测并报错
- **AND** 错误信息应明确指出缺少哪个方法
- **AND** 系统应退出（不运行游戏）

### Requirement: 可复现性

系统 SHALL 支持通过随机种子确保评估结果可复现。

#### Scenario: 设置随机种子
- **WHEN** 用户执行 `python evaluate.py --seed 42`
- **THEN** 系统应使用种子 42 初始化随机数生成器
- **AND** 角色分配应可复现
- **AND** 相同种子应产生相同的游戏序列

#### Scenario: 未设置随机种子
- **WHEN** 用户未指定 `--seed` 参数
- **THEN** 系统应使用随机种子
- **AND** 每次运行应产生不同的游戏序列

