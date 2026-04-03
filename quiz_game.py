from __future__ import annotations

import os
import random
from datetime import datetime

from typing import Any

from quiz import Quiz
from storage import load_state, save_state


class QuizGame:
    def __init__(self, filename: str = "state.json"):
        self.filename = filename
        self.quizzes: list[Quiz] = []
        self.best_score: int = 0
        self.score_history: list[dict[str, Any]] = []

        existed_before = os.path.exists(self.filename)
        default_quizzes = self._build_default_quizzes()
        (
            self.quizzes,
            self.best_score,
            self.score_history,
            did_recover,
        ) = load_state(self.filename, default_quizzes)
        if did_recover:
            if existed_before:
                print("⚠️ 데이터 파일이 손상되었거나 스키마가 올바르지 않습니다. 기본 퀴즈로 복구합니다.")
            # 복구/초기화 후 바로 파일을 다시 생성해 "다음 실행도 동일"하게 맞춤
            save_state(self.filename, self.quizzes, self.best_score, self.score_history)

    @staticmethod
    def _build_default_quizzes() -> list[Quiz]:
        # 과제 주제 예시: Linux + Git + 네트워크/모니터링 기반
        raw = [
            {
                "question": "Linux에서 현재 디렉토리의 파일 목록을 보는 명령어는?",
                "choices": ["cd", "ls", "pwd", "mkdir"],
                "answer": 2,
                "hint": "파일을 '목록'으로 볼 때 자주 쓰는 명령어입니다. (ls)",
            },
            {
                "question": "Python에서 리스트에 요소를 추가하는 메서드는?",
                "choices": ["add()", "push()", "append()", "insert()"],
                "answer": 3,
                "hint": "리스트에 마지막에 붙일 때 흔히 쓰는 메서드입니다. (append)",
            },
            {
                "question": "AWS의 객체 스토리지 서비스 이름은?",
                "choices": ["EC2", "RDS", "S3", "Lambda"],
                "answer": 3,
                "hint": "오브젝트(객체) 스토리지는 'S3'입니다.",
            },
            {
                "question": "Git에서 변경 사항을 로컬 저장소에 기록하는 명령어는?",
                "choices": ["add", "push", "commit", "fetch"],
                "answer": 3,
                "hint": "로컬에 '기록'을 남길 때는 commit 입니다.",
            },
            {
                "question": "Prometheus가 주로 사용하는 데이터 저장 방식은?",
                "choices": ["RDBMS", "NoSQL", "TSDB", "GraphDB"],
                "answer": 3,
                "hint": "메트릭을 시간 순으로 다루는 시계열 DB는 TSDB입니다.",
            },
        ]
        return [Quiz.from_dict(item) for item in raw]

    def save(self) -> None:
        save_state(self.filename, self.quizzes, self.best_score, self.score_history)

    def get_int_input(self, prompt: str, *, min_val: int, max_val: int) -> int:
        while True:
            try:
                user_input = input(prompt).strip()
            except Exception:
                # KeyboardInterrupt/EOFError 등은 main에서 처리하도록 전달
                raise

            if not user_input:
                print("⚠️ 빈 입력입니다. 숫자를 입력해주세요.")
                continue

            try:
                val = int(user_input)
            except ValueError:
                print("⚠️ 숫자를 입력해야 합니다.")
                continue

            if val < min_val or val > max_val:
                print(f"⚠️ {min_val}~{max_val} 사이의 숫자를 입력해주세요.")
                continue

            return val

    def show_menu(self) -> None:
        print("\n" + "=" * 40)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def get_answer_with_optional_hint(self, quiz: Quiz) -> tuple[int, bool]:
        """
        Returns:
          (user_answer, hint_used)
        """
        hint_used = False
        while True:
            raw = input("정답 입력 (1-4) 또는 h(힌트): ").strip().lower()

            if raw in {"h", "hint"}:
                if not quiz.hint:
                    print("⚠️ 이 문제에는 힌트가 없습니다.")
                    continue

                print(f"💡 힌트: {quiz.hint}")
                if not hint_used:
                    hint_used = True
                    print("힌트를 사용하면, 정답이어도 점수가 50% 감점됩니다.")
                else:
                    print("이미 힌트를 확인하셨습니다.")
                continue

            if not raw:
                print("⚠️ 입력이 비어있습니다.")
                continue

            try:
                val = int(raw)
            except ValueError:
                print("⚠️ 숫자 또는 'h'를 입력해주세요.")
                continue

            if val < 1 or val > 4:
                print("⚠️ 1~4 사이의 숫자를 입력해주세요.")
                continue

            return val, hint_used

    def play(self) -> None:
        if not self.quizzes:
            print("📋 등록된 퀴즈가 없습니다.")
            return

        n = self.get_int_input(
            f"\n몇 문제를 풀까요? (1-{len(self.quizzes)}): ",
            min_val=1,
            max_val=len(self.quizzes),
        )

        game_quizzes = list(self.quizzes)
        random.shuffle(game_quizzes)  # 랜덤 출제(문제 순서 섞기)
        game_quizzes = game_quizzes[:n]

        print(f"\n📝 퀴즈를 시작합니다! (총 {n}문제 / 랜덤 출제)")

        hint_penalty_points = 0.5  # 힌트 사용 후 정답이면 50% 점수
        points_sum = 0.0
        max_points = float(n)
        correct_count = 0

        for i, quiz in enumerate(game_quizzes, 1):
            quiz.display(i)
            user_answer, hint_used = self.get_answer_with_optional_hint(quiz)

            if quiz.is_correct(user_answer):
                correct_count += 1
                if hint_used:
                    points_sum += hint_penalty_points
                    print("✅ 정답입니다! (힌트 사용으로 점수가 감점되었습니다.)")
                else:
                    points_sum += 1.0
                    print("✅ 정답입니다!")
            else:
                print(f"❌ 틀렸습니다. 정답은 {quiz.answer}번입니다.")

        score_percentage = int((points_sum / max_points) * 100) if max_points > 0 else 0
        print("\n" + "=" * 40)
        print(
            f"🏆 결과: {n}문제 중 {correct_count}문제 정답! ({score_percentage}점)"
        )

        # 점수 히스토리 기록
        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "played_questions": n,
            "score": score_percentage,
        }
        self.score_history.append(record)

        previous_best = self.best_score
        if score_percentage > self.best_score:
            self.best_score = score_percentage

        self.save()

        if score_percentage > previous_best:
            if previous_best <= 0:
                print("🎉 첫 최고 점수입니다! (최고 기록 갱신)")
            else:
                print("🎉 새로운 최고 점수입니다!")
        else:
            print(f"현재 최고 점수: {self.best_score}점")

        print("=" * 40)

    def add_quiz(self) -> None:
        print("\n📌 새로운 퀴즈를 추가합니다.")
        question = input("문제를 입력하세요: ").strip()
        while not question:
            question = input("문제를 입력하세요 (필수): ").strip()

        choices: list[str] = []
        for i in range(1, 5):
            choice = input(f"선택지 {i}: ").strip()
            while not choice:
                choice = input(f"선택지 {i} (필수): ").strip()
            choices.append(choice)

        answer = self.get_int_input("정답 번호 (1-4): ", min_val=1, max_val=4)
        hint = input("힌트(선택, Enter로 생략): ").strip()
        self.quizzes.append(
            Quiz(question=question, choices=choices, answer=answer, hint=hint)
        )
        self.save()
        print("\n✅ 퀴즈가 추가되었습니다!")

    def show_list(self) -> None:
        if not self.quizzes:
            print("\n📋 등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for i, quiz in enumerate(self.quizzes, 1):
            print(f"[{i}] {quiz.question}")
        print("-" * 40)

        raw = input("🗑️ 퀴즈를 삭제할까요? (y/N): ").strip().lower()
        if raw not in {"y", "yes"}:
            return

        idx = self.get_int_input(
            f"삭제할 퀴즈 번호를 입력해주세요 (1-{len(self.quizzes)}): ",
            min_val=1,
            max_val=len(self.quizzes),
        )
        removed = self.quizzes.pop(idx - 1)
        self.save()
        print(f"\n✅ 삭제 완료: {removed.question}")

    def show_score(self) -> None:
        if self.best_score <= 0 and not self.score_history:
            print("\n🏆 최고 점수가 없습니다. 먼저 '퀴즈 풀기'를 해보세요!")
            return

        print(f"\n🏆 최고 점수: {self.best_score}점")

        if not self.score_history:
            return

        print(f"🗂️ 게임 기록: 총 {len(self.score_history)}개")
        print("-" * 40)
        for rec in self.score_history[-5:]:
            ts = rec.get("timestamp", "")
            played = rec.get("played_questions", 0)
            score = rec.get("score", 0)
            print(f"{ts} | {played}문제 | {score}점")
        print("-" * 40)

