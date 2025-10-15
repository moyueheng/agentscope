# -*- coding: utf-8 -*-
"""评估报告生成器。"""

from typing import Any


class ReportGenerator:
    """生成评估报告。"""

    def __init__(self, statistics: dict[str, Any]) -> None:
        """初始化报告生成器。

        Args:
            statistics: 统计信息字典
        """
        self.statistics = statistics

    def generate_text_report(self) -> str:
        """生成文本格式报告。

        Returns:
            文本报告字符串
        """
        win_rates = self.statistics["win_rates"]
        avg_rounds = self.statistics["avg_rounds"]
        role_stats = self.statistics["role_stats"]

        report = []
        report.append("=" * 50)
        report.append("狼人杀游戏评估报告")
        report.append("=" * 50)
        report.append("")

        # 基本统计
        report.append("📊 基本统计")
        report.append(f"  总局数: {win_rates['total_games']}")
        if win_rates["failed_games"] > 0:
            report.append(f"  失败局数: {win_rates['failed_games']}")
        report.append(f"  平均轮数: {avg_rounds:.1f}")
        report.append("")

        # 胜率统计
        report.append("🏆 胜率统计")
        report.append(
            f"  村民阵营胜率: {win_rates['villagers_win_rate']:.1f}% ({win_rates['villagers_wins']}/{win_rates['total_games']})"
        )
        report.append(
            f"  狼人阵营胜率: {win_rates['werewolves_win_rate']:.1f}% ({win_rates['werewolves_wins']}/{win_rates['total_games']})"
        )
        report.append("")

        # 角色统计
        if role_stats:
            report.append("👥 角色统计")
            role_names = {
                "villager": "村民",
                "werewolf": "狼人",
                "seer": "预言家",
                "witch": "女巫",
                "hunter": "猎人",
            }
            for role, stats in role_stats.items():
                role_name = role_names.get(role, role)
                report.append(f"  {role_name}:")
                report.append(f"    胜率: {stats['win_rate']:.1f}%")
                report.append(f"    存活率: {stats['survival_rate']:.1f}%")
            report.append("")

        report.append("=" * 50)
        return "\n".join(report)

    def generate_comparison_report(
        self,
        baseline_stats: dict[str, Any],
        custom_stats: dict[str, Any],
    ) -> str:
        """生成对比报告。

        Args:
            baseline_stats: 基线统计
            custom_stats: 自定义 Agent 统计

        Returns:
            对比报告字符串
        """
        report = []
        report.append("=" * 50)
        report.append("基线 vs 自定义 Agent 对比报告")
        report.append("=" * 50)
        report.append("")

        baseline_win = baseline_stats["win_rates"]
        custom_win = custom_stats["win_rates"]

        # 村民胜率对比
        villagers_diff = (
            custom_win["villagers_win_rate"] - baseline_win["villagers_win_rate"]
        )
        werewolves_diff = (
            custom_win["werewolves_win_rate"] - baseline_win["werewolves_win_rate"]
        )

        report.append("🔄 胜率对比")
        report.append(f"  基线 - 村民胜率: {baseline_win['villagers_win_rate']:.1f}%")
        report.append(f"  自定义 - 村民胜率: {custom_win['villagers_win_rate']:.1f}%")
        report.append(
            f"  差异: {villagers_diff:+.1f}% {'⬆️' if villagers_diff > 0 else '⬇️' if villagers_diff < 0 else '➡️'}"
        )
        report.append("")
        report.append(f"  基线 - 狼人胜率: {baseline_win['werewolves_win_rate']:.1f}%")
        report.append(f"  自定义 - 狼人胜率: {custom_win['werewolves_win_rate']:.1f}%")
        report.append(
            f"  差异: {werewolves_diff:+.1f}% {'⬆️' if werewolves_diff > 0 else '⬇️' if werewolves_diff < 0 else '➡️'}"
        )
        report.append("")

        # 平均轮数对比
        baseline_rounds = baseline_stats["avg_rounds"]
        custom_rounds = custom_stats["avg_rounds"]
        rounds_diff = custom_rounds - baseline_rounds

        report.append("⏱️ 平均轮数对比")
        report.append(f"  基线: {baseline_rounds:.1f} 轮")
        report.append(f"  自定义: {custom_rounds:.1f} 轮")
        report.append(f"  差异: {rounds_diff:+.1f} 轮")
        report.append("")

        report.append("=" * 50)
        return "\n".join(report)

    def print_report(self) -> None:
        """打印报告到终端。"""
        print(self.generate_text_report())
