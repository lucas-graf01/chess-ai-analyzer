import chess
import chess.engine
from typing import List, Tuple, Optional


class EngineService:
    def __init__(self, stockfish_path: str, depth: int = 15):
        self.stockfish_path = stockfish_path
        self.depth = depth
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    def close(self):
        if self.engine:
            self.engine.quit()

    def evaluate_position(self, board: chess.Board):
        info = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))

        score = info["score"].pov(board.turn)

        if score.is_mate():
            mate = score.mate()
            cp = 100000 if mate and mate > 0 else -100000
        else:
            cp = score.score()

        best_move = info.get("pv", [None])[0]
        pv = info.get("pv", [])

        return cp, best_move, pv

    def evaluate_move_loss(self, board_before: chess.Board, played_move: chess.Move):
        eval_before, best_move, pv = self.evaluate_position(board_before)

        board_after = board_before.copy()
        board_after.push(played_move)

        eval_after_next, _, _ = self.evaluate_position(board_after)

        eval_after = None
        if eval_after_next is not None:
            eval_after = -eval_after_next

        cp_loss = None
        if eval_before is not None and eval_after is not None:
            cp_loss = eval_before - eval_after

        return eval_before, best_move, pv, cp_loss, eval_after

