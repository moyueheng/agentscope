# 变更提案：添加 Agent 评估系统

## Why

在狼人杀比赛中，需要客观量化不同 Agent 策略的性能表现。目前的游戏主逻辑只支持单局游戏，无法批量测试和对比不同 Agent 的胜率。为了验证自定义 Agent 相比基线 ReActAgent 的改进效果，需要一个可以：
1. 批量运行多局游戏（如 10 局、100 局）
2. 记录每局游戏的详细结果
3. 统计和对比不同 Agent 的胜率
4. 生成评估报告的系统

这对于比赛优化迭代至关重要。

## What Changes

- 新增评估框架模块 (`examples/game/werewolves/evaluation/`)
  - 批量游戏运行器：支持配置游戏局数和 Agent 组合
  - 结果记录器：记录每局游戏的胜负、存活情况、角色分配等
  - 统计分析器：计算胜率、角色胜率、平均存活时间等指标
  - 报告生成器：生成可视化的评估报告（文本/JSON 格式）

- 重构游戏主逻辑 (`examples/game/werewolves/main.py`)
  - 将游戏逻辑封装为可复用的 `WerewolfGame` 类
  - 支持注入自定义 Agent 工厂函数
  - 保持原有单局游戏运行方式不变（向后兼容）

- 新增评估入口脚本 (`examples/game/werewolves/evaluate.py`)
  - 提供命令行接口配置评估参数
  - 支持对比模式：基线 Agent vs 自定义 Agent

- 新增示例自定义 Agent (`examples/agent_werewolves/`)
  - 提供一个示例自定义 Agent 实现
  - 展示如何继承和改进 ReActAgent

## Impact

- **Affected specs**: 
  - 新增 `agent-evaluation` capability（评估系统核心功能）
  - 新增 `game-refactoring` capability（游戏逻辑重构）

- **Affected code**:
  - `examples/game/werewolves/main.py` - 需要重构但保持向后兼容
  - 新增 `examples/game/werewolves/evaluation/` - 评估框架目录
  - 新增 `examples/game/werewolves/evaluate.py` - 评估入口
  - 新增 `examples/agent_werewolves/` - 自定义 Agent 示例目录

- **Breaking changes**: 无 - 原有游戏运行方式完全兼容

- **Performance considerations**: 
  - 批量运行可能较耗时，需要支持进度显示
  - 考虑后续支持并行运行多局游戏

