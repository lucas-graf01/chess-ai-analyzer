import streamlit as st
import pandas as pd
import chess
import chess.svg

from analyzer import analyze_pgn
from engine_service import EngineService
from llm_service import explain_move


def render_move_list(analyses):
    move_line = ""
    annotations = {}

    for m in analyses:
        move_text = m.san
        if m.is_critical:
            move_text += m.symbol
            annotations[f"{m.fullmove_number}{m.side}{m.move_index}"] = m

        if m.side == "white":
            move_line += f"{m.fullmove_number}. {move_text} "
        else:
            move_line += f"{move_text} "

    return move_line, annotations


def board_from_fen(fen: str, size: int = 420):
    board = chess.Board(fen)
    svg = chess.svg.board(board=board, size=size)
    return svg


st.set_page_config(page_title="Chess Analyzer", layout="wide")
st.title("Chess Analyzer")

if "analyses" not in st.session_state:
    st.session_state["analyses"] = None

if "current_move_index" not in st.session_state:
    st.session_state["current_move_index"] = 0

stockfish_path = st.text_input("Stockfish path", value="/usr/games/stockfish")
pgn_text = st.text_area("Paste PGN here")

if st.button("Analyze"):
    try:
        engine = EngineService(stockfish_path)
        analyses = analyze_pgn(pgn_text, engine)
        engine.close()
        st.session_state["analyses"] = analyses
        st.session_state["current_move_index"] = 0
    except Exception as e:
        st.error(f"Analysis error: {e}")

analyses = st.session_state.get("analyses", None)

if analyses:
    # ---------------------------
    # NAVIGATION FIRST
    # ---------------------------
    st.subheader("Game Navigation")

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    with nav_col1:
        if st.button("⏮ Start"):
            st.session_state["current_move_index"] = 0

    with nav_col2:
        if st.button("◀ Previous"):
            st.session_state["current_move_index"] = max(
                0, st.session_state["current_move_index"] - 1
            )

    with nav_col3:
        if st.button("Next ▶"):
            st.session_state["current_move_index"] = min(
                len(analyses), st.session_state["current_move_index"] + 1
            )

    with nav_col4:
        if st.button("End ⏭"):
            st.session_state["current_move_index"] = len(analyses)

    move_options = ["Start position"]
    for m in analyses:
        label = (
            f"{m.fullmove_number}. {m.san}"
            if m.side == "white"
            else f"{m.fullmove_number}... {m.san}"
        )
        move_options.append(label)

    selected_from_dropdown = st.selectbox(
        "Select move to inspect",
        move_options,
        index=st.session_state["current_move_index"]
    )

    selected_index = move_options.index(selected_from_dropdown)
    st.session_state["current_move_index"] = selected_index

    if st.session_state["current_move_index"] == 0:
        selected_fen = analyses[0].fen_before
        selected_move_obj = None
    else:
        selected_move_obj = analyses[st.session_state["current_move_index"] - 1]
        selected_fen = selected_move_obj.fen_after

    # ---------------------------
    # BOARD + POSITION INFO HIGH UP
    # ---------------------------
    board_col, info_col = st.columns([1, 1])

    with board_col:
        st.subheader("Board")
        svg = board_from_fen(selected_fen, size=450)
        st.components.v1.html(svg, height=500)

    with info_col:
        st.subheader("Position Info")
        st.code(selected_fen, language="text")

        if selected_move_obj:
            selected_label = (
                f"{selected_move_obj.fullmove_number}. {selected_move_obj.san}"
                if selected_move_obj.side == "white"
                else f"{selected_move_obj.fullmove_number}... {selected_move_obj.san}"
            )

            st.write(f"**Move:** {selected_label}")
            st.write(f"**Side:** {selected_move_obj.side}")
            st.write(f"**Classification:** {selected_move_obj.classification}")
            st.write(f"**Symbol:** {selected_move_obj.symbol or '-'}")
            st.write(
                f"**Missed chance:** {'Yes' if selected_move_obj.missed_chance else 'No'}"
            )
            st.write(f"**Best move:** {selected_move_obj.best_move_san or '-'}")
            st.write(
                f"**Eval before:** "
                f"{selected_move_obj.eval_before_cp if selected_move_obj.eval_before_cp is not None else '-'}"
            )
            st.write(
                f"**Eval after:** "
                f"{selected_move_obj.eval_after_cp if selected_move_obj.eval_after_cp is not None else '-'}"
            )
            st.write(
                f"**Centipawn loss:** "
                f"{selected_move_obj.cp_loss if selected_move_obj.cp_loss is not None else '-'}"
            )

            if selected_move_obj.comment:
                st.info(selected_move_obj.comment)

            if selected_move_obj.principal_variation_san:
                st.write(
                    "**Principal variation:** "
                    + " ".join(selected_move_obj.principal_variation_san[:8])
                )
        else:
            st.write("Start position")

    # ---------------------------
    # CRITICAL MOVES TABLE
    # ---------------------------
    st.subheader("Critical Moves")

    rows = []
    for m in analyses:
        if not m.is_critical:
            continue

        label = (
            f"{m.fullmove_number}. {m.san}"
            if m.side == "white"
            else f"{m.fullmove_number}... {m.san}"
        )

        rows.append({
            "Move": label,
            "Symbol": m.symbol,
            "Classification": m.classification,
            "Missed Chance": "Yes" if m.missed_chance else "No",
            "Best Move": m.best_move_san or "-",
            "Comment": m.comment or "-"
        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No critical moves were found in this game.")

    # ---------------------------
    # ANNOTATED GAME
    # ---------------------------
    st.subheader("Annotated Game")

    move_line, annotations = render_move_list(analyses)

    st.markdown("### Game Moves")
    st.write(move_line)

    st.markdown("### Critical Moments")
    for _key, m in annotations.items():
        label = (
            f"{m.fullmove_number}. {m.san}"
            if m.side == "white"
            else f"{m.fullmove_number}... {m.san}"
        )

        st.markdown(f"#### {label}{m.symbol}")
        if m.comment:
            st.write(m.comment)

        if m.best_move_san:
            st.write(f"**Best move:** {m.best_move_san}")

        if m.principal_variation_san:
            st.caption("Better line: " + " ".join(m.principal_variation_san[:8]))

        if m.missed_chance:
            st.warning("Missed chance detected.")

        st.divider()

    # ---------------------------
    # MOVE DETAILS + CHAT
    # ---------------------------
    critical_moves = [m for m in analyses if m.is_critical]

    if critical_moves:
        st.subheader("Move Details")

        selected_critical = st.selectbox(
            "Select critical move",
            [
                f"{m.fullmove_number}. {m.san}"
                if m.side == "white"
                else f"{m.fullmove_number}... {m.san}"
                for m in critical_moves
            ]
        )

        move_obj = next(
            m for m in critical_moves
            if (
                f"{m.fullmove_number}. {m.san}"
                if m.side == "white"
                else f"{m.fullmove_number}... {m.san}"
            ) == selected_critical
        )

        st.markdown(f"### {selected_critical}{move_obj.symbol}")
        st.write(f"**Classification:** {move_obj.classification}")
        st.write(f"**Missed chance:** {'Yes' if move_obj.missed_chance else 'No'}")
        st.write(f"**Comment:** {move_obj.comment or '-'}")
        st.write(f"**Best move:** {move_obj.best_move_san or '-'}")
        st.write(
            f"**Centipawn loss:** "
            f"{move_obj.cp_loss if move_obj.cp_loss is not None else '-'}"
        )

        if move_obj.principal_variation_san:
            st.write(
                "**Principal variation:** "
                + " ".join(move_obj.principal_variation_san[:8])
            )

        st.subheader("Ask about this move")
        question = st.text_input(
            "Your question",
            value="Why is this move inaccurate?"
        )

        if st.button("Explain"):
            try:
                answer = explain_move(question, move_obj)
                st.write(answer)
            except Exception as e:
                st.error(f"LLM error: {e}")
