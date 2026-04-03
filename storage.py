from __future__ import annotations

import json
import os
from typing import Any

from quiz import Quiz


def load_state(
    filename: str,
    default_quizzes: list[Quiz],
) -> tuple[list[Quiz], int, list[dict[str, Any]], bool]:
    """
    Returns:
      (quizzes, best_score, score_history, did_recover)
    """
    if not os.path.exists(filename):
        return list(default_quizzes), 0, [], True

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        quizzes_raw = data.get("quizzes", [])
        best_score = int(data.get("best_score", 0))
        score_history_raw = data.get("score_history", [])

        quizzes: list[Quiz] = []
        for q in quizzes_raw:
            if isinstance(q, dict):
                quiz = Quiz.from_dict(q)
                # 스키마 손상/변형 방지(최소한의 검증)
                if not quiz.question:
                    continue
                if len(quiz.choices) != 4:
                    continue
                if quiz.answer < 1 or quiz.answer > 4:
                    continue
                quizzes.append(quiz)

        score_history: list[dict[str, Any]] = []
        if isinstance(score_history_raw, list):
            for rec in score_history_raw:
                if not isinstance(rec, dict):
                    continue

                ts = rec.get("timestamp")
                played_questions = rec.get("played_questions")
                score = rec.get("score")

                if not isinstance(ts, str) or not ts.strip():
                    continue

                try:
                    played_questions_int = int(played_questions)
                    score_int = int(score)
                except Exception:
                    continue

                if played_questions_int < 1 or score_int < 0:
                    continue

                score_history.append(
                    {
                        "timestamp": ts.strip(),
                        "played_questions": played_questions_int,
                        "score": score_int,
                    }
                )

        best_from_history = max((r["score"] for r in score_history), default=0)

        if not quizzes:
            # 손상/스키마 변경으로 인해 quizzes가 비어있으면 기본 데이터로 복구
            best = max(best_score if best_score > 0 else 0, best_from_history)
            return list(default_quizzes), best, [], True

        # best_score와 히스토리를 함께 사용할 수 있게 보정
        best = max(best_score if best_score > 0 else 0, best_from_history)
        return quizzes, best, score_history, False
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return list(default_quizzes), 0, [], True


def save_state(
    filename: str,
    quizzes: list[Quiz],
    best_score: int,
    score_history: list[dict[str, Any]],
) -> None:
    data: dict[str, Any] = {
        "quizzes": [q.to_dict() for q in quizzes],
        "best_score": int(best_score),
        "score_history": score_history,
    }
    # UTF-8 + ensure_ascii=False로 한글 깨짐 방지
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

