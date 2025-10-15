# -*- coding: utf-8 -*-
"""游戏结果数据模型。"""

from pydantic import BaseModel


class PlayerInfo(BaseModel):
    """玩家信息。"""

    name: str
    role: str
    survived: bool
    rounds_survived: int


class GameResult(BaseModel):
    """游戏结果。"""

    game_id: int
    winner: str  # "werewolves" or "villagers"
    total_rounds: int
    players: list[PlayerInfo]
    timestamp: str
    failed: bool = False
    error_message: str | None = None
