import math

def safe_eval(expr: str) -> str:
    try:
        normalized = expr.replace("x", "*").replace("÷", "/")
        result = eval(normalized, {"__builtins__": {}}, {})
        if math.isinf(result) or math.isnan(result):
            return "Error"
        if float(result).is_integer():
            return str(int(result))
        return f"{result:.10g}"
    except Exception as e:
        return "Error"


# 테스트 케이스
test_cases = [
    ("5+3", "8"),              # 덧셈
    ("10-4", "6"),             # 뺄셈
    ("7x8", "56"),             # 곱셈 (x 기호)
    ("20÷4", "5"),             # 나눗셈 (÷ 기호)
    ("100÷3", "33.33333333"),  # 나눗셈 (소수점)
    ("0.5+0.3", "0.8"),        # 소수 덧셈
    ("-5+3", "-2"),            # 음수 시작
    ("10-20", "-10"),          # 음수 결과
    ("100x2", "200"),          # 큰 수 곱셈
    ("1÷0", "Error"),          # Division by zero
    ("5++3", "Error"),         # 잘못된 문법
]

print("=== 계산기 사칙 연산 테스트 ===\n")
print(f"{'테스트':<20} {'입력식':<15} {'결과':<15} {'기대값':<15} {'상태':<5}")
print("-" * 70)

passed = 0
failed = 0

for test_name, expr in [
    ("덧셈", "5+3"),
    ("뺄셈", "10-4"),
    ("곱셈", "7x8"),
    ("나눗셈", "20÷4"),
    ("소수 나눗셈", "100÷3"),
    ("소수 덧셈", "0.5+0.3"),
    ("음수 시작", "-5+3"),
    ("음수 결과", "10-20"),
    ("큰 수", "100x2"),
    ("0 나누기", "1÷0"),
    ("에러 케이스", "5++3"),
]:
    expected = None
    for case_expr, case_expected in test_cases:
        if case_expr == expr:
            expected = case_expected
            break
    
    result = safe_eval(expr)
    
    # 부동소수점 오차 허용도 확인
    match = str(result) == expected
    if not match and expected != "Error":
        try:
            r = float(result)
            e = float(expected)
            match = abs(r - e) < 0.0001
        except:
            match = False
    
    status = "✓ 통과" if match else "✗ 실패"
    if match:
        passed += 1
    else:
        failed += 1
    
    print(f"{test_name:<20} {expr:<15} {result:<15} {expected:<15} {status:<5}")

print("-" * 70)
print(f"\n결과: {passed} 통과, {failed} 실패\n")

# append_value 로직 테스트
print("=== 입력 조립 로직 테스트 ===\n")

class MockState:
    def __init__(self):
        self.display = "0"
        self.reset_next = False

def append_value(state, token: str) -> None:
    display = state.display

    if state.reset_next and token not in {"+", "-", "x", "÷"}:
        display = "0"
        state.reset_next = False

    if token in {"+", "-", "x", "÷"}:
        if display[-1:] in "+-x÷":
            state.display = display[:-1] + token
        else:
            state.display = display + token
        state.reset_next = False
        return

    if token == ".":
        parts = display.replace("+", " ").replace("-", " ").replace("x", " ").replace("÷", " ").split()
        current = parts[-1] if parts else display
        if "." not in current:
            state.display = display + token
        return

    if display == "0":
        state.display = token
    else:
        state.display = display + token


# 입력 시나리오 테스트
scenarios = [
    ("초기 상태", ["0"], "0"),
    ("숫자 입력: 5 누르기", ["5"], "5"),
    ("계속: 3 누르기", ["5", "3"], "53"),
    ("+누르기", ["5", "3", "+"], "53+"),
    ("2 누르기", ["5", "3", "+", "2"], "53+2"),
    ("0 상태에서 00 누르기", ["0", "0", "0"], "0"),
    ("소수점: 5.3", ["5", ".", "3"], "5.3"),
]

print(f"{'시나리오':<25} {'입력':<20} {'결과':<15} {'기대값':<15} {'상태':<5}")
print("-" * 80)

scenario_passed = 0
scenario_failed = 0

for scenario, inputs, expected in scenarios:
    state = MockState()
    for token in inputs:
        append_value(state, token)
    
    match = state.display == expected
    status = "✓ 통과" if match else "✗ 실패"
    if match:
        scenario_passed += 1
    else:
        scenario_failed += 1
    
    input_str = ", ".join(inputs)
    print(f"{scenario:<25} {input_str:<20} {state.display:<15} {expected:<15} {status:<5}")

print("-" * 80)
print(f"\n입력 조립 결과: {scenario_passed} 통과, {scenario_failed} 실패\n")
