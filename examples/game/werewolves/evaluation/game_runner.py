# -*- coding: utf-8 -*-
"""游戏批量运行器。"""

from game_result import GameResult
from main import AgentFactory, WerewolfGame


class GameRunner:
    """批量运行游戏的运行器。"""

    def __init__(
        self,
        num_games: int = 10,
        agent_factory: AgentFactory | None = None,
        show_progress: bool = True,
    ) -> None:
        """初始化游戏运行器。

        Args:
            num_games: 要运行的游戏局数
            agent_factory: 可选的 Agent 工厂函数
            show_progress: 是否显示进度信息
        """
        self.num_games = num_games
        self.agent_factory = agent_factory
        self.show_progress = show_progress
        self.results: list[GameResult] = []

    async def run_single_game(self, game_id: int) -> GameResult:
        """运行单局游戏。

        Args:
            game_id: 游戏 ID

        Returns:
            游戏结果
        """
        try:
            game = WerewolfGame(game_id=game_id, agent_factory=self.agent_factory)
            result = await game.run()
            return result
        except Exception as e:
            # 如果游戏运行失败，返回失败结果
            from datetime import datetime

            from game_result import GameResult

            return GameResult(
                game_id=game_id,
                winner="unknown",
                total_rounds=0,
                players=[],
                timestamp=datetime.now().isoformat(),
                failed=True,
                error_message=str(e),
            )

    async def run_all_games(self) -> list[GameResult]:
        """批量运行所有游戏。

        Returns:
            所有游戏结果列表
        """
        self.results = []
        for i in range(self.num_games):
            if self.show_progress:
                print(f"\r运行游戏 {i + 1}/{self.num_games}...", end="", flush=True)

            result = await self.run_single_game(i + 1)
            self.results.append(result)

        if self.show_progress:
            print()  # 换行

        return self.results

    def get_results(self) -> list[GameResult]:
        """获取游戏结果。

        Returns:
            游戏结果列表
        """
        return self.results
