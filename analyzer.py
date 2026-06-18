import io
import chess
import chess.pgn

from models import MoveAnalysis
from engine_service import EngineService
from annotator import classify_move, detect_missed_chance, build_comment


def moves_to_san_list(board: chess.Board, moves: list[chess.Move], max_len: int = 8) -> list[str]:
    
    temp_board = board.copy()
    san_moves = []

    for mv in moves[:max_len]:
        try:
            san_moves.append(temp_board.san(mv))
            temp_board.push(mv)
        except Exception:
            break

    return san_moves


def analyze_pgn(pgn_text: str, engine: EngineService) -> list[MoveAnalysis]:
    
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("Invalid PGN.")

    board = game.board()
    analyses: list[MoveAnalysis] = []

    for idx, move in enumerate(game.mainline_moves()):
        fen_before = board.fen()
        fullmove_number = board.fullmove_number
        side = "white" if board.turn == chess.WHITE else "black"

        san = board.san(move)
        uci = move.uci()

        eval_before, best_move, pv, cp_loss, eval_after_cp = engine.evaluate_move_loss(board, move)

        best_move_san = None
        best_move_uci = None

        if best_move is not None:
            try:
                best_move_san = board.san(best_move)
                best_move_uci = best_move.uci()
            except Exception:
                best_move_san = None
                best_move_uci = None

        pv_san = moves_to_san_list(board, pv)

        board.push(move)
        fen_after = board.fen()

        symbol, classification = classify_move(cp_loss, eval_before, eval_after_cp)
        missed_chance = detect_missed_chance(eval_before, cp_loss)

        if missed_chance and symbol == "":
            symbol = "?!"

        is_critical = (
            symbol != ""
            or missed_chance
            or classification in {"inaccuracy", "mistake", "blunder"}
        )

        analysis = MoveAnalysis(
            move_index=idx,
            fullmove_number=fullmove_number,
            side=side,
            san=san,
            uci=uci,
            fen_before=fen_before,
            fen_after=fen_after,
            best_move_san=best_move_san,
            best_move_uci=best_move_uci,
            eval_before_cp=eval_before,
            eval_after_cp=eval_after_cp,
            cp_loss=cp_loss,
            symbol=symbol,
            classification=classification,
            comment="",
            principal_variation_san=pv_san,
            is_critical=is_critical,
            missed_chance=missed_chance,
        )

        analysis.comment = build_comment(analysis)
        analyses.append(analysis)

    return analyses
