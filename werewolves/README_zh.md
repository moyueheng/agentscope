# 🐺⚔️👨‍🌾 九人狼人杀游戏

这是一个使用AgentScope构建的九人狼人杀游戏示例，展示了**多智能体交互**、**基于角色的游戏玩法**和**结构化输出处理**。
具体来说，这个游戏由以下角色组成：

- 三名村民 👨‍🌾，
- 三名狼人 🐺，
- 一名预言家 🔮，
- 一名女巫 🧙‍♀️ 以及
- 一名猎人 🏹。

## ✨更新日志

- 2025-10：我们更新了示例以支持更多功能：
    - 允许死亡玩家留言。
    - 现在支持中文。
    - 通过加载和保存会话状态支持**连续游戏**，使相同的智能体可以进行多场游戏并不断学习和优化他们的策略。

## 快速开始

运行以下命令启动游戏，确保您已将DashScope API密钥设置为环境变量。

```bash
python main.py
```

> 注意：
> - 您可以在`main.py`中调整语言、模型和其他参数。
> - 不同的模型可能会带来不同的游戏体验。

使用AgentScope Studio运行示例可以提供更加交互式的体验。

- 中文演示视频（点击播放）：

[![中文狼人杀游戏](https://img.alicdn.com/imgextra/i3/6000000007235/O1CN011pK6Be23JgcdLWmLX_!!6000000007235-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/KxyR66_CWaWwu76OPTvOV2Ye1Gas3i5p4molJtzhn_s.mp4)

- 英文演示视频（点击播放）：

[![英文狼人杀游戏](https://img.alicdn.com/imgextra/i3/6000000007389/O1CN011alyGK24SDcFBzHea_!!6000000007389-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/bMiRTfxPg2vm76wEoaIP2eJfkCi8CUExHRas-1LyK1I.mp4)

## 详细信息

该游戏是使用AgentScope中的`ReActAgent`构建的，利用其生成结构化输出的能力来控制游戏流程和交互。
我们还使用AgentScope中的`MsgHub`和管道来管理复杂的交互，如讨论和投票。
看到智能体如何以不同的角色和目标玩狼人杀游戏是非常有趣的。

# 高级用法

## 更改语言

游戏默认使用英语进行。只需在`game.py`中取消注释以下行即可切换到中文。

```python
# from prompt import ChinesePrompts as Prompts
```

## 与智能体一起游戏

您可以用`UserAgent`替换其中一个智能体，与AI智能体一起游戏。

## 更改模型

只需修改`main.py`中的`model`参数即可尝试不同的模型。请注意，您需要同时更改格式化器以匹配模型的输出格式。

## 进一步阅读

- [结构化输出](https://doc.agentscope.io/tutorial/task_agent.html#structured-output)
- [MsgHub和管道](https://doc.agentscope.io/tutorial/task_pipeline.html)
- [提示词格式化器](https://doc.agentscope.io/tutorial/task_prompt.html)
- [AgentScope Studio](https://doc.agentscope.io/tutorial/task_studio.html)