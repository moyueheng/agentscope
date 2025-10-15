# 技术设计文档

## Context

当前狼人杀游戏实现 (`examples/game/werewolves/main.py`) 是一个完整的单局游戏流程，包含 345 行代码，使用全局变量管理游戏状态。为了支持批量评估和 Agent 对比，需要：
1. 不破坏现有游戏逻辑
2. 支持灵活注入不同的 Agent 实现
3. 提供可靠的统计和评估能力

**约束条件**:
- 必须保持现有 `python main.py` 运行方式不变（向后兼容）
- 必须支持自定义 Agent 遵循比赛要求（observe、state_dict、结构化输出等）
- 需要处理异步执行（AgentScope 1.0 全异步）
- 需要考虑大量局数时的性能和内存

## Goals / Non-Goals

**Goals**:
- ✅ 支持批量运行 N 局游戏（N 可配置，如 10、100）
- ✅ 记录每局游戏的完整结果（胜负、角色、存活情况）
- ✅ 统计和对比不同 Agent 的胜率
- ✅ 生成可读的评估报告
- ✅ 提供示例自定义 Agent 实现
- ✅ 保持代码简洁，避免过度设计

**Non-Goals**:
- ❌ 不实现 GUI 界面（命令行即可）
- ❌ 不实现实时可视化（文本报告即可）
- ❌ 不实现分布式并行（单机运行即可）
- ❌ 不实现复杂的策略分析（胜率统计足够）
- ❌ 不修改 AgentScope 框架本身

## Decisions

### 1. 游戏逻辑重构方案

**决策**: 将游戏逻辑封装为 `WerewolfGame` 类，保持原有 `main()` 函数作为入口

**理由**:
- 最小化改动，降低引入 Bug 风险
- 原有 `python main.py` 方式完全兼容
- 新的评估系统可以实例化 `WerewolfGame` 多次运行

**实现方式**:
```python
# main.py 重构后
class WerewolfGame:
    def __init__(self, agent_factory=None):
        """agent_factory: 可选的 Agent 工厂函数"""
        self.agent_factory = agent_factory or default_agent_factory
        # ... 初始化游戏状态
    
    async def run(self) -> GameResult:
        """运行一局游戏，返回结果"""
        # ... 原有游戏逻辑
        return GameResult(
            winner="werewolves",  # or "villagers"
            players={...},
            rounds=5,
            # ...
        )

async def main():
    """原有入口保持不变"""
    game = WerewolfGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Agent 工厂模式

**决策**: 使用工厂函数而非类继承来支持自定义 Agent

**理由**:
- 灵活性高，用户可以自由组合 Agent
- 符合 Python 函数式编程风格
- 避免深层继承，符合项目代码规范

**接口定义**:
```python
from typing import Callable, Awaitable
from agentscope.agent import ReActAgent

AgentFactory = Callable[[str], Awaitable[ReActAgent]]
# str: role (villager, werewolf, seer, witch, hunter)
# 返回: 该角色的 Agent 实例

async def custom_agent_factory(role: str) -> ReActAgent:
    """用户自定义的 Agent 工厂"""
    name = get_player_name()
    if role == "werewolf":
        # 使用自定义的增强版 Agent
        return EnhancedWerewolfAgent(name=name, ...)
    else:
        # 其他角色使用默认 Agent
        return await create_player(role)
```

### 3. 评估框架架构

**决策**: 采用职责分离的模块化设计

```
evaluation/
├── __init__.py
├── game_runner.py       # GameRunner: 批量运行游戏
├── result_recorder.py   # ResultRecorder: 记录结果
├── statistics.py        # StatisticsAnalyzer: 统计分析
├── report.py           # ReportGenerator: 生成报告
└── models.py           # GameResult, PlayerInfo 等数据模型
```

**理由**:
- 单一职责原则，每个模块功能明确
- 易于测试和维护
- 符合项目"模块职责单一"的规范

### 4. 结果数据结构

**决策**: 使用 Pydantic BaseModel 定义数据结构

```python
from pydantic import BaseModel

class PlayerInfo(BaseModel):
    name: str
    role: str
    survived: bool
    rounds_survived: int

class GameResult(BaseModel):
    game_id: int
    winner: str  # "werewolves" or "villagers"
    total_rounds: int
    players: list[PlayerInfo]
    timestamp: str
```

**理由**:
- 符合 AgentScope 结构化输出要求
- 自动类型验证
- 易于序列化为 JSON
- 符合项目类型标注规范

### 5. 对比评估模式

**决策**: 支持"替换式"对比，而非"混合式"对比

**"替换式"**: 一局游戏中，某个角色（如狼人）全部使用自定义 Agent，其他角色使用基线
**"混合式"**: 一局游戏中，同一角色既有基线又有自定义（不采用）

**理由**:
- 替换式更简单，易于理解和实现
- 结果更清晰：可以明确对比"使用自定义狼人 Agent"vs"使用基线狼人 Agent"的胜率
- 避免混合模式下的公平性问题

**使用方式**:
```bash
# 运行 20 局，其中 10 局全用基线，10 局狼人用自定义 Agent
python evaluate.py --num-games 10 --mode baseline
python evaluate.py --num-games 10 --mode custom --custom-agent myagent.py
```

### 6. 进度显示和日志

**决策**: 使用 Python 标准库，避免引入额外依赖

```python
# 简单的进度显示
import sys
for i in range(total_games):
    print(f"Running game {i+1}/{total_games}...", end="\r")
    # ...
print()  # 换行
```

**理由**:
- 简单实用，满足需求
- 避免增加依赖（如 tqdm）
- 符合"简单优先"原则

## Alternatives Considered

### 备选方案 1: 完全重写游戏逻辑
- ❌ **不采用**: 风险大，工作量大，可能引入新 Bug

### 备选方案 2: 使用配置文件而非命令行参数
- ⚖️ **暂不采用**: 命令行参数足够，配置文件作为后续优化项

### 备选方案 3: 实现并行运行多局游戏
- ⚖️ **暂不采用**: 增加复杂度，当前单线程顺序运行足够（10-100 局可接受）
- 💡 **后续优化**: 如果需要运行上千局，可以考虑使用 asyncio.gather 并行运行

### 备选方案 4: 使用数据库存储结果
- ❌ **不采用**: JSON 文件足够，避免增加依赖和复杂度

## Risks / Trade-offs

### 风险 1: 重构可能破坏原有游戏逻辑
- **缓解**: 
  - 重构前后都要测试单局游戏运行
  - 保持原有 `main()` 函数不变
  - 小步重构，每步都验证

### 风险 2: 异步执行可能导致状态混乱
- **缓解**:
  - 每局游戏使用独立的 `WerewolfGame` 实例
  - 避免全局变量（或在类中封装）
  - 清理每局游戏后的状态

### 风险 3: 大量局数可能内存溢出
- **缓解**:
  - 不在内存中保留所有游戏的完整记录
  - 增量写入结果到文件
  - 只保留统计数据在内存

### 权衡 1: 单线程顺序 vs 并行运行
- **选择**: 单线程顺序
- **理由**: 实现简单，10-100 局可接受（预计 10-30 分钟）
- **后续**: 如需更高性能再优化

### 权衡 2: 简单文本报告 vs 可视化图表
- **选择**: 简单文本报告
- **理由**: 满足比赛需求，避免额外依赖（如 matplotlib）
- **后续**: 可以输出 JSON，用户自行可视化

## Migration Plan

### 步骤 1: 重构游戏逻辑（不改变行为）
1. 创建 `WerewolfGame` 类
2. 将 `main()` 中的逻辑移至 `WerewolfGame.run()`
3. 测试 `python main.py` 仍正常运行

### 步骤 2: 实现评估框架（独立模块）
1. 创建 `evaluation/` 目录
2. 实现各个模块
3. 单元测试各模块

### 步骤 3: 集成评估入口
1. 创建 `evaluate.py`
2. 连接游戏逻辑和评估框架
3. 端到端测试

### 步骤 4: 提供示例 Agent
1. 创建示例自定义 Agent
2. 测试评估对比功能

### 回滚计划
- 保持 Git 分支隔离
- 如果重构出现问题，可以回退到原始 `main.py`
- 评估框架是独立模块，可以单独移除

## Open Questions

1. **Q**: 是否需要支持中途暂停和恢复评估？
   - **A**: 暂不需要，10-100 局可以一次性运行完

2. **Q**: 是否需要支持多种自定义 Agent 同时对比（A vs B vs C）？
   - **A**: 暂不需要，先实现基线 vs 单个自定义，后续可扩展

3. **Q**: 统计指标是否需要更复杂的分析（如置信区间）？
   - **A**: 暂不需要，胜率百分比足够，比赛主要看胜率提升

4. **Q**: 是否需要记录游戏过程的详细日志（每轮发言内容）？
   - **A**: 暂不需要，只记录结果即可，避免存储过大

