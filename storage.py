from __future__ import annotations

import json
import os
from typing import Any

from quiz import Quiz


def load_state(filename: str, default_quizzes: list[Quiz]) -> tuple[list[Quiz], int, bool]:
    """
    Returns:
      (quizzes, best_score, did_recover)
    """
    if not os.path.exists(filename):
        return list(default_quizzes), 0, True

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        quizzes_raw = data.get("quizzes", [])
        best_score = int(data.get("best_score", 0))

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

        if not quizzes:
            # 손상/스키마 변경으로 인해 quizzes가 비어있으면 기본 데이터로 복구
            return list(default_quizzes), best_score if best_score > 0 else 0, True

        return quizzes, best_score, False
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return list(default_quizzes), 0, True


def save_state(filename: str, quizzes: list[Quiz], best_score: int) -> None:
    data: dict[str, Any] = {
        "quizzes": [q.to_dict() for q in quizzes],
        "best_score": int(best_score),
    }
    # UTF-8 + ensure_ascii=False로 한글 깨짐 방지
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

