# -*- coding: utf-8 -*-
"""游戏结果记录器。"""

import json
from pathlib import Path

from game_result import GameResult


class ResultRecorder:
    """记录游戏结果到文件。"""

    def __init__(self, output_path: str | Path) -> None:
        """初始化结果记录器。

        Args:
            output_path: 输出文件路径
        """
        self.output_path = Path(output_path)

    def save_results(self, results: list[GameResult]) -> None:
        """保存游戏结果到文件。

        Args:
            results: 游戏结果列表
        """
        # 确保输出目录存在
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # 转换为字典列表
        results_dict = [result.model_dump() for result in results]

        # 写入 JSON 文件
        with self.output_path.open("w", encoding="utf-8") as f:
            json.dump(results_dict, f, ensure_ascii=False, indent=2)

    def load_results(self) -> list[GameResult]:
        """从文件加载游戏结果。

        Returns:
            游戏结果列表
        """
        if not self.output_path.exists():
            return []

        with self.output_path.open("r", encoding="utf-8") as f:
            results_dict = json.load(f)

        return [GameResult(**result) for result in results_dict]
