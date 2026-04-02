# 퀴즈 게임 (Python Console) - 제출본

## 제출 체크리스트
- GitHub 저장소 URL
- 환경 설정 스크린샷: `python --version`, `git --version`
- 실행 결과 스크린샷: 메뉴/퀴즈 추가/퀴즈 풀기(결과)/점수 확인
- 데이터 영속성 증거: `state.json`에 추가한 퀴즈와 최고점수가 종료 후에도 유지됨 확인
- Git 히스토리 스크린샷: `git log --oneline --graph`

## 프로젝트 개요
Python 콘솔에서 동작하는 퀴즈 게임입니다. 메뉴를 통해 퀴즈를 풀고, 새로운 퀴즈를 추가하며, `state.json`에 데이터를 저장해 종료 후에도 최고 점수와 퀴즈가 유지됩니다.

## 퀴즈 주제 선정 이유
Linux / Git 기본 개념을 중심으로 구성해, 터미널과 데이터 저장 흐름을 학습/검증할 수 있도록 했습니다.

## 실행 방법
```bash
python main.py
```

## 기능 목록
- 퀴즈 풀기: 정답 입력 후 결과와 점수(정답률 %) 출력
- 퀴즈 추가: 문제/선택지 4개/정답(1~4) 입력 후 즉시 저장
- 퀴즈 목록: 저장된 퀴즈 제목 나열
- 점수 확인: 최고 점수 확인(기록 전이면 안내)
- 데이터 영속성: 종료 후에도 `state.json` 기반으로 복구

## 파일 구조
- `main.py`: 메뉴 루프 및 실행 진입점(KeyboardInterrupt/EOF 안전 종료)
- `quiz.py`: `Quiz` 클래스(표시/정답 판정/직렬화)
- `quiz_game.py`: `QuizGame` 클래스(입력 검증/플레이/추가/목록/점수/저장)
- `storage.py`: `state.json` 로드/세이브(UTF-8, 손상 시 기본값 복구)
- `state.example.json`: `state.json` 스키마 예시
- `.gitignore`: 실행 중 생성/갱신되는 `state.json` 제외

## 데이터 파일 설명 (`state.json`)
- 인코딩: UTF-8
- 파일이 없으면: 기본 퀴즈로 시작(첫 실행 시 자동 생성)
- 파일이 손상되면: 안내 메시지 출력 후 기본 퀴즈로 복구

스키마 예시:
```json
{
  "quizzes": [
    { "question": "...", "choices": ["...", "...", "...", "..."], "answer": 1 }
  ],
  "best_score": 0
}
```

## 제출 시 스크린샷 가이드(예시 경로)
- `docs/screenshots/menu.png` (메뉴 출력 화면)
- `docs/screenshots/add_quiz.png` (퀴즈 추가 화면)
- `docs/screenshots/play.png` (퀴즈 플레이/결과 화면)
- `docs/screenshots/score.png` (`점수 확인` 화면)

## 7. 스피드런(권장 실행 순서)
1. `python main.py` 실행 후 메뉴가 정상 출력되는지 확인합니다. (`menu.png`)
2. `2` 선택 → 퀴즈 1개 추가 후 저장 메시지가 뜨는지 확인합니다. (`add_quiz.png`)
3. `3` 선택 → 방금 추가한 퀴즈가 목록에 보이는지 확인합니다.
4. `1` 선택 → 퀴즈를 풀고 결과/점수(정답률 %) 및 최고 점수 갱신 여부를 확인합니다. (`play.png`)
5. `4` 선택 → 최고 점수를 확인합니다. (`score.png`)
6. `5`로 종료 후, 다시 실행했을 때 추가한 퀴즈/최고 점수가 유지되는지 확인합니다.

7. `git log --oneline --graph` 실행 후 결과를 스크린샷으로 남기세요.
