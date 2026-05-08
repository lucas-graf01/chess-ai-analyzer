from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MoveAnalysis:
    move_index: int
    fullmove_number: int
    side: str
    san: str
    uci: str

    fen_before: str
    fen_after: str

    best_move_san: Optional[str] = None
    eval_before_cp: Optional[int] = None
    eval_after_cp: Optional[int] = None
    cp_loss: Optional[int] = None
    best_move_uci: str | None = None

    symbol: str = ""
    classification: str = "normal"
    comment: str = ""

    principal_variation_san: List[str] = field(default_factory=list)

    is_critical: bool = False
    missed_chance: bool = False
