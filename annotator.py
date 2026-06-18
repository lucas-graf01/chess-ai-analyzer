def classify_move(cp_loss, eval_before=None, eval_after=None):
   

    if cp_loss is None:
        return "", "normal"

    if cp_loss >= 300:
        return "??", "blunder"
    elif cp_loss >= 150:
        return "?", "mistake"
    elif cp_loss >= 50:
        return "?!", "inaccuracy"
    elif cp_loss <= 15:
        return "", "good move"
    else:
        return "", "normal"


def detect_missed_chance(eval_before, cp_loss):
   
    if eval_before is None or cp_loss is None:
        return False

    return eval_before > 150 and cp_loss >= 80


def side_label(side):
    return "White" if side == "white" else "Black"


def build_comment(move):
  
    player = side_label(move.side)
    san_text = move.san if move.side == "white" else f"...{move.san}"

    best_part = f" Better was {move.best_move_san}." if move.best_move_san else ""
    line_part = ""
    if move.principal_variation_san:
        line_part = " Line: " + " ".join(move.principal_variation_san[:6])

    if move.missed_chance:
        return f"{player} misses a stronger continuation with {san_text}.{best_part}{line_part}"

    if move.classification == "blunder":
        return f"{player}'s {san_text} is a blunder.{best_part}{line_part}"

    if move.classification == "mistake":
        return f"{player}'s {san_text} is a mistake.{best_part}{line_part}"

    if move.classification == "inaccuracy":
        return f"{player}'s {san_text} is inaccurate.{best_part}{line_part}"

    if move.classification == "good move":
        return f"{player}'s {san_text} is a solid move.{line_part}"

    return ""
