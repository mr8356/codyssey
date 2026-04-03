from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Quiz:
    question: str
    choices: list[str]  # 4개
    answer: int  # 1~4
    hint: str = ""

    def display(self, index: int) -> None:
        print(f"\n[{index}] {self.question}")
        for i, choice in enumerate(self.choices, 1):
            print(f"{i}. {choice}")

    def is_correct(self, user_answer: int) -> bool:
        return user_answer == self.answer

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Quiz":
        question = str(data.get("question", "")).strip()
        choices = data.get("choices", [])
        answer = int(data.get("answer", 0))
        hint = str(data.get("hint", "")).strip()
        return Quiz(question=question, choices=list(choices), answer=answer, hint=hint)

