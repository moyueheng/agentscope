# 狼人杀 Agent 评估系统使用指南

本指南介绍如何使用评估系统来量化和对比不同 Agent 的性能。

## 🎯 系统概述

评估系统允许你：
- ✅ 批量运行多局游戏（10 局、100 局等）
- ✅ 记录每局游戏的详细结果
- ✅ 统计和对比不同 Agent 的胜率
- ✅ 生成评估报告（文本/JSON 格式）

## 📋 快速开始

### 1. 运行基线测试

首先，运行基线 Agent（普通 ReActAgent）的测试：

```bash
cd examples/game/werewolves
python evaluate.py --num-games 10 --mode baseline
```

**输出示例**：
```
==================================================
狼人杀游戏 Agent 评估系统
==================================================
模式: baseline
游戏局数: 10
输出路径: evaluation_results_baseline_20250115_143022.json
==================================================

开始运行游戏...

运行游戏 10/10...
✅ 结果已保存到: evaluation_results_baseline_20250115_143022.json

==================================================
狼人杀游戏评估报告
==================================================

📊 基本统计
  总局数: 10
  平均轮数: 4.2

🏆 胜率统计
  村民阵营胜率: 60.0% (6/10)
  狼人阵营胜率: 40.0% (4/10)

👥 角色统计
  村民:
    胜率: 60.0%
    存活率: 45.0%
  狼人:
    胜率: 40.0%
    存活率: 25.0%
  ...

==================================================
```

### 2. 开发自定义 Agent

参考 `examples/agent_werewolves/enhanced_agent.py` 创建你的自定义 Agent。

关键要求：
```python
# 你的 Agent 模块必须包含 agent_factory 函数
async def agent_factory(role: str) -> ReActAgent:
    """创建自定义 Agent。
    
    Args:
        role: 角色类型 (villager, werewolf, seer, witch, hunter)
        
    Returns:
        符合要求的 Agent 实例
    """
    # 实现代码
    pass
```

### 3. 运行自定义 Agent 测试

```bash
python evaluate.py --num-games 10 --mode custom \
  --custom-agent ../../agent_werewolves/enhanced_agent.py
```

### 4. 对比结果

比较两次运行的结果文件（baseline 和 custom）：

- 查看胜率提升
- 分析角色表现
- 评估策略有效性

## 🔧 命令行参数

### 基本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--num-games` | 运行的游戏局数 | 10 |
| `--mode` | 评估模式：`baseline` 或 `custom` | baseline |
| `--custom-agent` | 自定义 Agent 模块路径 | - |
| `--output` | 输出报告路径 | evaluation_results_<mode>_<timestamp>.json |
| `--no-progress` | 不显示进度信息 | False |

### 使用示例

#### 示例 1：快速测试（3 局）

```bash
python evaluate.py --num-games 3 --mode custom \
  --custom-agent ../../agent_werewolves/my_agent.py
```

#### 示例 2：大规模评估（100 局）

```bash
python evaluate.py --num-games 100 --mode custom \
  --custom-agent ../../agent_werewolves/my_agent.py \
  --output my_agent_100games.json
```

#### 示例 3：无进度输出（适合后台运行）

```bash
python evaluate.py --num-games 50 --mode custom \
  --custom-agent ../../agent_werewolves/my_agent.py \
  --no-progress > output.log 2>&1 &
```

## 📊 评估指标说明

### 1. 基本统计

- **总局数**: 成功运行的游戏局数
- **失败局数**: 因异常而失败的游戏局数
- **平均轮数**: 游戏平均持续轮数

### 2. 胜率统计

- **村民阵营胜率**: 村民方获胜的比例
- **狼人阵营胜率**: 狼人方获胜的比例

**注意**: 两个阵营的胜率之和应为 100%

### 3. 角色统计

每个角色的详细统计：

- **胜率**: 该角色所在阵营获胜的比例
- **存活率**: 该角色在游戏结束时仍存活的比例

### 4. 对比分析

当你运行基线和自定义 Agent 后，可以对比：

- **胜率提升**: 自定义 Agent 相对基线的胜率变化
- **策略有效性**: 判断改进是否有效
- **统计显著性**: 样本量越大，结果越可靠

**建议样本量**：
- 初步验证：10-20 局
- 可靠评估：50-100 局
- 充分验证：200+ 局

## 📁 输出文件格式

评估系统会生成 JSON 格式的结果文件：

```json
[
  {
    "game_id": 1,
    "winner": "villagers",
    "total_rounds": 5,
    "players": [
      {
        "name": "张伟",
        "role": "werewolf",
        "survived": false,
        "rounds_survived": 3
      },
      ...
    ],
    "timestamp": "2025-01-15T14:30:22.123456",
    "failed": false,
    "error_message": null
  },
  ...
]
```

### 字段说明

- `game_id`: 游戏编号
- `winner`: 胜利方（"werewolves" 或 "villagers"）
- `total_rounds`: 游戏总轮数
- `players`: 玩家信息列表
  - `name`: 玩家姓名
  - `role`: 角色（villager/werewolf/seer/witch/hunter）
  - `survived`: 是否存活
  - `rounds_survived`: 存活轮数
- `failed`: 游戏是否失败
- `error_message`: 错误信息（如果有）

## 🧪 测试验证

### 验证游戏逻辑重构

重构后，原有游戏运行方式应保持不变：

```bash
# 测试单局游戏
python main.py
```

应该能正常运行一局完整的狼人杀游戏。

### 验证评估系统

```bash
# 1. 测试基线模式
python evaluate.py --num-games 3 --mode baseline

# 2. 测试自定义 Agent 模式
python evaluate.py --num-games 3 --mode custom \
  --custom-agent ../../agent_werewolves/enhanced_agent.py

# 3. 检查输出文件
cat evaluation_results_*.json | head -20
```

### 常见问题排查

#### 问题 1：模块加载失败

```
❌ 加载自定义 Agent 失败: Agent 模块文件不存在
```

**解决方案**: 检查文件路径是否正确，使用绝对路径或相对路径。

#### 问题 2：缺少 agent_factory 函数

```
❌ 加载自定义 Agent 失败: 模块中未找到 'agent_factory' 函数
```

**解决方案**: 确保模块中定义了 `async def agent_factory(role: str) -> ReActAgent` 函数。

#### 问题 3：游戏运行失败

```
⚠️  警告: 3 局游戏运行失败
```

**解决方案**: 
- 检查 API 配置是否正确
- 查看输出文件中的 `error_message` 字段
- 确保网络连接正常

#### 问题 4：进度卡住

**解决方案**:
- 游戏可能需要较长时间（每局 5-10 分钟）
- 使用 `--no-progress` 参数并检查日志文件
- 减少 `--num-games` 数量进行测试

## 💡 最佳实践

### 1. 迭代开发流程

```
1. 快速验证（3-5 局）
   └─> 调试 Agent 逻辑
2. 小规模测试（10-20 局）
   └─> 初步评估效果
3. 中等规模（50 局）
   └─> 确认策略有效性
4. 大规模验证（100+ 局）
   └─> 充分验证稳定性
```

### 2. 对比测试

```bash
# Step 1: 运行基线
python evaluate.py --num-games 50 --mode baseline \
  --output baseline_50.json

# Step 2: 运行自定义 Agent v1
python evaluate.py --num-games 50 --mode custom \
  --custom-agent my_agent_v1.py \
  --output custom_v1_50.json

# Step 3: 改进策略后运行 v2
python evaluate.py --num-games 50 --mode custom \
  --custom-agent my_agent_v2.py \
  --output custom_v2_50.json

# Step 4: 对比三次结果
# 手动查看三个 JSON 文件的统计数据
```

### 3. 性能优化建议

- **减少模型调用**: 优化 Agent 逻辑，减少不必要的推理
- **批量运行**: 使用 `--num-games` 一次性运行所需局数
- **后台运行**: 大规模评估使用后台运行，避免中断

### 4. 结果分析技巧

- **查看胜率变化**: 自定义 Agent 胜率是否提升
- **分析角色表现**: 特定角色的改进效果
- **关注存活率**: 关键角色（预言家、女巫）的存活率
- **游戏轮数**: 更短的游戏可能意味着更高效的策略

## 📚 参考资源

- 示例 Agent: `examples/agent_werewolves/enhanced_agent.py`
- Agent 开发指南: `examples/agent_werewolves/README.md`
- 游戏主逻辑: `examples/game/werewolves/main.py`
- 评估框架源码: `examples/game/werewolves/evaluation/`

## 🤝 比赛提交

准备比赛提交时：

1. 确保你的 Agent 符合所有要求
2. 运行充分的评估测试（建议 100+ 局）
3. 记录你的策略改进和效果
4. 准备展示你的评估结果

祝你在比赛中取得好成绩！🏆

