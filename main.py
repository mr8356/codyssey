from __future__ import annotations

import sys

from quiz_game import QuizGame


def main() -> None:
    game = QuizGame()

    try:
        while True:
            game.show_menu()
            choice = input("선택: ").strip()

            # 공통 입력 규칙: 빈 입력이면 안내 후 재입력
            if not choice:
                print("⚠️ 입력이 비어 있습니다. 번호를 입력해주세요.")
                continue

            try:
                menu_choice = int(choice)
            except ValueError:
                print("⚠️ 숫자만 입력 가능합니다. 번호를 다시 입력해주세요.")
                continue

            if menu_choice == 1:
                game.play()
            elif menu_choice == 2:
                game.add_quiz()
            elif menu_choice == 3:
                game.show_list()
            elif menu_choice == 4:
                game.show_score()
            elif menu_choice == 5:
                print("프로그램을 종료합니다.")
                break
            else:
                print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")
    except (KeyboardInterrupt, EOFError):
        # "비정상 종료"하지 않고, 가능한 범위에서 저장 후 안전 종료
        print("\n\n⚠️ 입력이 중단되었습니다. 현재 상태를 저장하고 종료합니다.")
        game.save()
    finally:
        # VSCode/터미널에서 실행할 때 프로세스가 깔끔히 종료되도록 안내
        sys.exit(0)


if __name__ == "__main__":
    main()

