# 🐺⚔️👨‍🌾 九人狼人杀游戏

这是一个使用 AgentScope 构建的九人狼人杀示例，展示了**多智能体交互**、**基于角色的玩法**以及**结构化输出处理**。
游戏共包含以下角色：

- 三名村民 👨‍🌾，
- 三名狼人 🐺，
- 一名预言家 🔮，
- 一名女巫 🧙‍♀️，
- 一名猎人 🏹。

## 快速开始

运行以下命令即可启动游戏。请确保已将 DashScope 的 API Key 设置为环境变量。

```bash
python main.py
```

> 注意：
> - 你可以在 `main.py` 中调整语言、模型和其他参数；
> - 不同模型可能会带来不同的游戏体验。

使用 AgentScope Studio 运行该示例可以获得更加互动的体验。

- 中文演示视频（点击播放）：

[![Werewolf Game in Chinese](https://img.alicdn.com/imgextra/i3/6000000007235/O1CN011pK6Be23JgcdLWmLX_!!6000000007235-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/KxyR66_CWaWwu76OPTvOV2Ye1Gas3i5p4molJtzhn_s.mp4)

- 英文演示视频（点击播放）：

[![Werewolf Game in English](https://img.alicdn.com/imgextra/i3/6000000007389/O1CN011alyGK24SDcFBzHea_!!6000000007389-0-tbvideo.jpg)](https://cloud.video.taobao.com/vod/bMiRTfxPg2vm76wEoaIP2eJfkCi8CUExHRas-1LyK1I.mp4)

## 详情

本游戏基于 AgentScope 的 ``ReActAgent`` 构建，利用其生成结构化输出的能力来控制游戏流程与交互。
我们还使用 AgentScope 的 ``MsgHub`` 与管道（pipelines）来管理讨论、投票等复杂交互。
观察不同角色与目标的智能体如何进行狼人杀对局，十分有趣。

此外，你可以使用 ``UserAgent`` 替换其中一个智能体，亲自与 AI 智能体一起游戏！

## 延伸阅读

- [结构化输出](https://doc.agentscope.io/tutorial/task_agent.html#structured-output)
- [MsgHub 与管道](https://doc.agentscope.io/tutorial/task_pipeline.html)
- [提示词格式化](https://doc.agentscope.io/tutorial/task_prompt.html)
- [AgentScope Studio](https://doc.agentscope.io/tutorial/task_studio.html)
