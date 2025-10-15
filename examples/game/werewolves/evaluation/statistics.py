# -*- coding: utf-8 -*-
"""统计分析模块。"""

from typing import Any

from game_result import GameResult


class StatisticsAnalyzer:
    """统计分析游戏结果。"""

    def __init__(self, results: list[GameResult]) -> None:
        """初始化统计分析器。

        Args:
            results: 游戏结果列表
        """
        self.results = results
        self.valid_results = [r for r in results if not r.failed]
        self.failed_count = len(results) - len(self.valid_results)

    def calculate_win_rates(self) -> dict[str, Any]:
        """计算胜率统计。

        Returns:
            胜率统计字典
        """
        if not self.valid_results:
            return {
                "total_games": 0,
                "failed_games": self.failed_count,
                "villagers_wins": 0,
                "werewolves_wins": 0,
                "villagers_win_rate": 0.0,
                "werewolves_win_rate": 0.0,
            }

        villagers_wins = sum(1 for r in self.valid_results if r.winner == "villagers")
        werewolves_wins = sum(1 for r in self.valid_results if r.winner == "werewolves")
        total = len(self.valid_results)

        return {
            "total_games": total,
            "failed_games": self.failed_count,
            "villagers_wins": villagers_wins,
            "werewolves_wins": werewolves_wins,
            "villagers_win_rate": villagers_wins / total * 100 if total > 0 else 0.0,
            "werewolves_win_rate": werewolves_wins / total * 100 if total > 0 else 0.0,
        }

    def calculate_avg_rounds(self) -> float:
        """计算平均游戏轮数。

        Returns:
            平均轮数
        """
        if not self.valid_results:
            return 0.0

        total_rounds = sum(r.total_rounds for r in self.valid_results)
        return total_rounds / len(self.valid_results)

    def calculate_role_stats(self) -> dict[str, Any]:
        """计算各角色统计。

        Returns:
            角色统计字典
        """
        role_stats: dict[str, dict[str, int]] = {}

        for result in self.valid_results:
            for player in result.players:
                if player.role not in role_stats:
                    role_stats[player.role] = {
                        "total": 0,
                        "survived": 0,
                        "wins": 0,
                    }

                role_stats[player.role]["total"] += 1
                if player.survived:
                    role_stats[player.role]["survived"] += 1

                # 判断是否胜利
                is_werewolf = player.role == "werewolf"
                if (is_werewolf and result.winner == "werewolves") or (
                    not is_werewolf and result.winner == "villagers"
                ):
                    role_stats[player.role]["wins"] += 1

        # 计算胜率和存活率
        for role, stats in role_stats.items():
            total = stats["total"]
            stats["win_rate"] = stats["wins"] / total * 100 if total > 0 else 0.0
            stats["survival_rate"] = (
                stats["survived"] / total * 100 if total > 0 else 0.0
            )

        return role_stats

    def get_full_statistics(self) -> dict[str, Any]:
        """获取完整统计信息。

        Returns:
            完整统计字典
        """
        return {
            "win_rates": self.calculate_win_rates(),
            "avg_rounds": self.calculate_avg_rounds(),
            "role_stats": self.calculate_role_stats(),
        }
