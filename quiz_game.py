from __future__ import annotations

import os

from typing import Callable

from quiz import Quiz
from storage import load_state, save_state


class QuizGame:
    def __init__(self, filename: str = "state.json"):
        self.filename = filename
        self.quizzes: list[Quiz] = []
        self.best_score: int = 0

        existed_before = os.path.exists(self.filename)
        default_quizzes = self._build_default_quizzes()
        self.quizzes, self.best_score, did_recover = load_state(self.filename, default_quizzes)
        if did_recover:
            if existed_before:
                print("⚠️ 데이터 파일이 손상되었거나 스키마가 올바르지 않습니다. 기본 퀴즈로 복구합니다.")
            # 복구/초기화 후 바로 파일을 다시 생성해 "다음 실행도 동일"하게 맞춤
            save_state(self.filename, self.quizzes, self.best_score)

    @staticmethod
    def _build_default_quizzes() -> list[Quiz]:
        # 과제 주제 예시: Linux + Git + 네트워크/모니터링 기반
        raw = [
            {
                "question": "Linux에서 현재 디렉토리의 파일 목록을 보는 명령어는?",
                "choices": ["cd", "ls", "pwd", "mkdir"],
                "answer": 2,
            },
            {
                "question": "Python에서 리스트에 요소를 추가하는 메서드는?",
                "choices": ["add()", "push()", "append()", "insert()"],
                "answer": 3,
            },
            {
                "question": "AWS의 객체 스토리지 서비스 이름은?",
                "choices": ["EC2", "RDS", "S3", "Lambda"],
                "answer": 3,
            },
            {
                "question": "Git에서 변경 사항을 로컬 저장소에 기록하는 명령어는?",
                "choices": ["add", "push", "commit", "fetch"],
                "answer": 3,
            },
            {
                "question": "Prometheus가 주로 사용하는 데이터 저장 방식은?",
                "choices": ["RDBMS", "NoSQL", "TSDB", "GraphDB"],
                "answer": 3,
            },
        ]
        return [Quiz.from_dict(item) for item in raw]

    def save(self) -> None:
        save_state(self.filename, self.quizzes, self.best_score)

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

    def play(self) -> None:
        if not self.quizzes:
            print("📋 등록된 퀴즈가 없습니다.")
            return

        print(f"\n📝 퀴즈를 시작합니다! (총 {len(self.quizzes)}문제)")
        current_score = 0

        for i, quiz in enumerate(self.quizzes, 1):
            quiz.display(i)
            user_answer = self.get_int_input("정답 입력 (1-4): ", min_val=1, max_val=4)
            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                current_score += 1
            else:
                print(f"❌ 틀렸습니다. 정답은 {quiz.answer}번입니다.")

        score_percentage = int((current_score / len(self.quizzes)) * 100)
        print("\n" + "=" * 40)
        print(f"🏆 결과: {len(self.quizzes)}문제 중 {current_score}문제 정답! ({score_percentage}점)")

        if score_percentage > self.best_score:
            previous_best = self.best_score
            self.best_score = score_percentage
            self.save()
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
        self.quizzes.append(Quiz(question=question, choices=choices, answer=answer))
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

    def show_score(self) -> None:
        if self.best_score <= 0:
            print("\n🏆 최고 점수가 없습니다. 먼저 '퀴즈 풀기'를 해보세요!")
            return
        print(f"\n🏆 최고 점수: {self.best_score}점")

