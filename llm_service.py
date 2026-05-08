
import os
from openai import OpenAI


def _get_client():
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY is not set.")

    base_url = os.getenv("LLM_BASE_URL")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)

    return OpenAI(api_key=api_key)


def _get_model():
    return os.getenv("LLM_MODEL", "gpt-4.1-mini")


def build_context(move):
    return f"""
Current move: {move.san}{move.symbol}
Side: {move.side}
Classification: {move.classification}
Missed chance: {"yes" if move.missed_chance else "no"}
Best move: {move.best_move_san or "-"}
Evaluation before: {move.eval_before_cp if move.eval_before_cp is not None else "-"} cp
Evaluation after: {move.eval_after_cp if move.eval_after_cp is not None else "-"} cp
Centipawn loss: {move.cp_loss if move.cp_loss is not None else "-"}
FEN before move: {move.fen_before}
FEN after move: {move.fen_after}
Principal variation: {" ".join(move.principal_variation_san) if move.principal_variation_san else "-"}
Existing comment: {move.comment or "-"}
""".strip()


def explain_move(question, move):
    client = _get_client()
    model = _get_model()

    system_prompt = """
You are a chess analysis coach.

Rules:
- Explain positions clearly and accurately.
- Use only the provided engine data and position context.
- Do not invent evaluations or lines.
- If the user asks why a move is bad, explain the strategic or tactical reason.
- If the user asks about the best move, explain why it is stronger.
- If the user asks for a beginner explanation, simplify the language.
- Be concise but useful.
""".strip()

    user_prompt = f"""
Here is the current chess analysis context:

{build_context(move)}

User question:
{question}
""".strip()

    response = client.chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


