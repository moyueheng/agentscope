# -*- coding: utf-8 -*-
"""狼人杀游戏评估入口脚本。"""

import argparse
import asyncio
import importlib.util
import sys
from datetime import datetime
from pathlib import Path

from evaluation import GameRunner, ReportGenerator, ResultRecorder, StatisticsAnalyzer
from main import AgentFactory


def load_custom_agent_factory(module_path: str) -> AgentFactory:
    """动态加载自定义 Agent 工厂函数。

    Args:
        module_path: Agent 模块路径

    Returns:
        Agent 工厂函数

    Raises:
        ValueError: 如果模块或工厂函数不存在
    """
    path = Path(module_path)
    if not path.exists():
        raise ValueError(f"Agent 模块文件不存在: {module_path}")

    # 动态加载模块
    spec = importlib.util.spec_from_file_location("custom_agent", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法加载模块: {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["custom_agent"] = module
    spec.loader.exec_module(module)

    # 查找 agent_factory 函数
    if not hasattr(module, "agent_factory"):
        raise ValueError(
            f"模块 {module_path} 中未找到 'agent_factory' 函数。\n"
            "请确保模块中定义了 async def agent_factory(role: str) -> ReActAgent 函数。"
        )

    return module.agent_factory


async def main() -> None:
    """评估入口函数。"""
    parser = argparse.ArgumentParser(description="狼人杀游戏 Agent 评估系统")
    parser.add_argument(
        "--num-games",
        type=int,
        default=10,
        help="运行的游戏局数 (默认: 10)",
    )
    parser.add_argument(
        "--mode",
        choices=["baseline", "custom"],
        default="baseline",
        help="评估模式: baseline(基线) 或 custom(自定义 Agent) (默认: baseline)",
    )
    parser.add_argument(
        "--custom-agent",
        type=str,
        help="自定义 Agent 模块路径 (仅在 mode=custom 时需要)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出报告路径 (默认: evaluation_results_<timestamp>.json)",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="不显示进度信息",
    )

    args = parser.parse_args()

    # 验证参数
    if args.mode == "custom" and not args.custom_agent:
        parser.error("使用 custom 模式时必须指定 --custom-agent 参数")

    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode_suffix = "custom" if args.mode == "custom" else "baseline"
        output_path = f"evaluation_results_{mode_suffix}_{timestamp}.json"

    print("=" * 50)
    print("狼人杀游戏 Agent 评估系统")
    print("=" * 50)
    print(f"模式: {args.mode}")
    print(f"游戏局数: {args.num_games}")
    if args.mode == "custom":
        print(f"自定义 Agent: {args.custom_agent}")
    print(f"输出路径: {output_path}")
    print("=" * 50)
    print()

    # 加载自定义 Agent 工厂（如果需要）
    agent_factory = None
    if args.mode == "custom":
        try:
            print(f"正在加载自定义 Agent: {args.custom_agent}")
            agent_factory = load_custom_agent_factory(args.custom_agent)
            print("✅ 自定义 Agent 加载成功")
            print()
        except Exception as e:
            print(f"❌ 加载自定义 Agent 失败: {e}")
            sys.exit(1)

    # 创建游戏运行器
    runner = GameRunner(
        num_games=args.num_games,
        agent_factory=agent_factory,
        show_progress=not args.no_progress,
    )

    # 运行游戏
    print("开始运行游戏...")
    print()
    results = await runner.run_all_games()

    # 保存结果
    recorder = ResultRecorder(output_path)
    recorder.save_results(results)
    print(f"✅ 结果已保存到: {output_path}")
    print()

    # 统计分析
    analyzer = StatisticsAnalyzer(results)
    statistics = analyzer.get_full_statistics()

    # 生成报告
    report_gen = ReportGenerator(statistics)
    report_gen.print_report()

    # 如果有失败的游戏，显示警告
    if statistics["win_rates"]["failed_games"] > 0:
        print()
        print(f"⚠️  警告: {statistics['win_rates']['failed_games']} 局游戏运行失败")


if __name__ == "__main__":
    asyncio.run(main())
