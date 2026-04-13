import json
import time
import os

# --- 1. 유틸리티 함수 ---

def normalize_label(label):
    """입력된 라벨을 표준 라벨(Cross, X)로 정규화"""
    label_upper = label.strip().upper()
    if label_upper in ['+', 'CROSS']:
        return 'Cross'
    elif label_upper in ['X', 'x']:
        return 'X'
    return 'UNDECIDED'

def mac_operation(pattern, filter_matrix):
    """N x N 패턴과 필터 간의 MAC 연산 (외부 라이브러리 금지)"""
    n = len(pattern)
    score = 0.0
    for i in range(n):
        for j in range(n):
            score += pattern[i][j] * filter_matrix[i][j]
    return score

def decide_pattern(score_cross, score_x, epsilon=1e-9):
    """부동소수점 오차를 고려한(epsilon) 점수 비교 및 판정"""
    if abs(score_cross - score_x) < epsilon:
        return 'UNDECIDED'
    elif score_cross > score_x:
        return 'Cross'
    else:
        return 'X'

def measure_performance(pattern, filter_matrix, iterations=10):
    """MAC 연산 소요 시간 측정 (ms 단위, 10회 반복 평균)"""
    start_time = time.perf_counter()
    for _ in range(iterations):
        mac_operation(pattern, filter_matrix)
    end_time = time.perf_counter()
    
    avg_time_sec = (end_time - start_time) / iterations
    return avg_time_sec * 1000  # ms로 변환

def input_matrix(size, name):
    """콘솔에서 N x N 행렬 입력 받기 (검증 포함)"""
    print(f"[{name}] {size}x{size} 행렬을 한 줄씩 입력하세요 (숫자는 공백으로 구분):")
    matrix = []
    while len(matrix) < size:
        line = input(f"행 {len(matrix) + 1}/{size}: ")
        try:
            row = [float(x) for x in line.split()]
            if len(row) != size:
                print(f"입력 형식 오류: {size}개의 숫자를 공백으로 구분해 입력하세요.")
                continue
            matrix.append(row)
        except ValueError:
            print("입력 형식 오류: 숫자가 아닌 값이 포함되어 있습니다. 다시 입력하세요.")
    return matrix


# --- 2. 코어 비즈니스 로직 ---

def run_mode_1_user_input():
    """모드 1: 사용자 입력 (3x3)"""
    print("\n--- 모드 1: 사용자 입력 (3x3) ---")
    size = 3
    filter_a = input_matrix(size, "필터 A (Cross)")
    filter_b = input_matrix(size, "필터 B (X)")
    pattern = input_matrix(size, "입력 패턴")

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)
    
    decision = decide_pattern(score_a, score_b)
    avg_time_ms = measure_performance(pattern, filter_a)

    print("\n[결과]")
    print(f"필터 A 점수: {score_a}")
    print(f"필터 B 점수: {score_b}")
    print(f"판정 결과: {decision}")
    print(f"MAC 연산 평균 시간: {avg_time_ms:.6f} ms")


def run_mode_2_json_analysis():
    """모드 2: JSON 로드 및 스키마 검증"""
    print("\n--- 모드 2: JSON 데이터 분석 ---")
    
    if not os.path.exists('data.json'):
        print("오류: data.json 파일을 찾을 수 없습니다.")
        return

    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("오류: data.json 파일의 형식이 올바르지 않습니다.")
        return

    filters = data.get('filters', {})
    patterns = data.get('patterns', {})
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    fail_cases = []
    performance_data = {} # 크기별 성능 데이터 저장

    for key, pattern_data in patterns.items():
        total_tests += 1
        
        # 키에서 N 추출 (예: size_5_01 -> 5)
        try:
            size_n = int(key.split('_')[1])
        except (IndexError, ValueError):
            fail_cases.append((key, "키 형식 오류 (N 추출 실패)"))
            failed_tests += 1
            continue

        filter_key = f"size_{size_n}"
        if filter_key not in filters:
            fail_cases.append((key, f"매칭되는 필터 누락 ({filter_key})"))
            failed_tests += 1
            continue

        target_filters = filters[filter_key]
        cross_filter = target_filters.get('cross')
        x_filter = target_filters.get('x')
        input_matrix = pattern_data.get('input')
        expected_raw = pattern_data.get('expected')

        # 스키마(크기) 검증
        if not (len(input_matrix) == size_n and all(len(row) == size_n for row in input_matrix)):
            fail_cases.append((key, f"패턴 크기 불일치 (예상: {size_n}x{size_n})"))
            failed_tests += 1
            continue
            
        # 라벨 정규화
        expected_normalized = normalize_label(expected_raw)

        # MAC 연산 및 판정
        score_cross = mac_operation(input_matrix, cross_filter)
        score_x = mac_operation(input_matrix, x_filter)
        decision = decide_pattern(score_cross, score_x)

        # 성능 측정 (크기별 1회씩만 기록)
        if size_n not in performance_data:
            perf_time = measure_performance(input_matrix, cross_filter)
            performance_data[size_n] = perf_time

        # PASS / FAIL 판정
        is_pass = (decision == expected_normalized)
        if is_pass:
            passed_tests += 1
            result_str = "PASS"
        else:
            failed_tests += 1
            result_str = "FAIL"
            fail_cases.append((key, f"판정 실패 (예상: {expected_normalized}, 실제: {decision})"))

        print(f"[{key}] Cross점수: {score_cross:<5.1f} | X점수: {score_x:<5.1f} | 판정: {decision:<6} | 예상: {expected_normalized:<6} -> {result_str}")

    # 성능 테이블 출력
    print("\n--- 성능 분석 ---")
    print(f"{'크기 (NxN)':<15} | {'평균 연산 시간 (ms)':<20} | {'연산 횟수 (N²)':<15}")
    print("-" * 55)
    for size, time_ms in sorted(performance_data.items()):
        print(f"{f'{size}x{size}':<15} | {time_ms:<20.6f} | {size**2:<15}")

    # 결과 리포트 출력
    print("\n--- 결과 요약 ---")
    print(f"전체 테스트: {total_tests} | 통과: {passed_tests} | 실패: {failed_tests}")
    if failed_tests > 0:
        print("실패 케이스 목록:")
        for fc in fail_cases:
            print(f" - {fc[0]}: {fc[1]}")


# --- 메인 실행부 ---
if __name__ == "__main__":
    while True:
        print("\n=== Mini NPU 시뮬레이터 ===")
        print("1. 사용자 입력 모드 (3x3)")
        print("2. JSON 데이터 분석 모드")
        print("3. 종료")
        choice = input("모드를 선택하세요: ")

        if choice == '1':
            run_mode_1_user_input()
        elif choice == '2':
            run_mode_2_json_analysis()
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 1, 2, 3 중 하나를 선택하세요.")