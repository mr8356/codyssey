from __future__ import annotations

import sys

from quiz_game import QuizGame


def main() -> None:
    game = QuizGame()

    try:
        while True:
            game.show_menu()
            menu_choice = game.get_int_input("선택: ", min_val=1, max_val=5)

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
    except (KeyboardInterrupt, EOFError):
        # "비정상 종료"하지 않고, 가능한 범위에서 저장 후 안전 종료
        print("\n\n⚠️ 입력이 중단되었습니다. 현재 상태를 저장하고 종료합니다.")
        game.save()
    finally:
        # VSCode/터미널에서 실행할 때 프로세스가 깔끔히 종료되도록 안내
        sys.exit(0)


if __name__ == "__main__":
    main()

