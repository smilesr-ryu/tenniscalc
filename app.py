import math
import streamlit as st
import requests
import json

st.set_page_config(page_title="Tennis Calculator", page_icon="🎾", layout="centered")

st.markdown(
    """
    <style>
    .block-container {
        max-width: 420px;
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }
    .calc-wrap {
        background: #0e1117;
        border-radius: 18px;
        padding: 14px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .display-box {
        background: #151a24;
        border-radius: 14px;
        min-height: 90px;
        padding: 14px;
        border: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: end;
        justify-content: end;
        font-size: 2.2rem;
        font-weight: 700;
        color: #f5f7fb;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .menu-note {
        text-align: right;
        color: #a3acb9;
        font-size: 0.8rem;
        margin-bottom: 6px;
    }
    .stButton > button {
        width: 100%;
        height: 58px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.09);
        background: #1b2130;
        color: #ffffff !important;
        font-size: 1.15rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #ffffff;
        color: #1b2130 !important;
        border-color: rgba(255,255,255,0.5);
    }
    .stButton > button:hover span, 
    .stButton > button:hover div,
    .stButton > button:hover p {
        color: #1b2130 !important;
    }
    button {
        color: #ffffff !important;
    }
    .stButton > button span, .stButton > button div {
        color: #ffffff !important;
    }
    .stButton > button p {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "display" not in st.session_state:
    st.session_state.display = "0"
if "reset_next" not in st.session_state:
    st.session_state.reset_next = False
if "digit_count" not in st.session_state:
    st.session_state.digit_count = {str(i): 0 for i in range(10)}
if "lotto_result" not in st.session_state:
    st.session_state.lotto_result = None


def format_result(value: float) -> str:
    if math.isinf(value) or math.isnan(value):
        return "Error"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.10g}"


def safe_eval(expr: str) -> str:
    try:
        normalized = expr.replace("x", "*").replace("÷", "/")
        result = eval(normalized, {"__builtins__": {}}, {})
        return format_result(float(result))
    except Exception:
        return "Error"


def append_value(token: str) -> None:
    display = st.session_state.display

    if st.session_state.reset_next and token not in {"+", "-", "x", "÷"}:
        display = "0"
        st.session_state.reset_next = False

    if token in {"+", "-", "x", "÷"}:
        if display[-1:] in "+-x÷":
            st.session_state.display = display[:-1] + token
        else:
            st.session_state.display = display + token
        st.session_state.reset_next = False
        return

    if token == ".":
        parts = display.replace("+", " ").replace("-", " ").replace("x", " ").replace("÷", " ").split()
        current = parts[-1] if parts else display
        if "." not in current:
            st.session_state.display = display + token
        return

    # 숫자 입력 시 카운트 증가
    if token in st.session_state.digit_count:
        st.session_state.digit_count[token] += 1
    
    if display == "0":
        st.session_state.display = token
    else:
        st.session_state.display = display + token



def apply_action(action: str) -> None:
    if action == "AC":
        st.session_state.display = "0"
        st.session_state.reset_next = False
        return

    if action == "DEL":
        current = st.session_state.display
        st.session_state.display = current[:-1] if len(current) > 1 else "0"
        return

    if action == "±":
        current = st.session_state.display
        if current == "0":
            return
        if current.startswith("-"):
            st.session_state.display = current[1:]
        else:
            st.session_state.display = "-" + current
        return

    if action == "%":
        result = safe_eval(st.session_state.display)
        if result != "Error":
            st.session_state.display = format_result(float(result) / 100)
            st.session_state.reset_next = True
        else:
            st.session_state.display = "Error"
        return

    if action == "=":
        st.session_state.display = safe_eval(st.session_state.display)
        st.session_state.reset_next = True
        return

    append_value(action)


def call_lotto_api() -> None:
    """API를 호출하여 로또 번호 생성"""
    try:
        max_digit = max(st.session_state.digit_count, key=st.session_state.digit_count.get)
        max_count = st.session_state.digit_count[max_digit]
        
        if max_count == 0:
            st.error("먼저 숫자를 누른 후 로또 번호를 생성해주세요!")
            return
        
        # API 요청
        response = requests.post(
            "http://127.0.0.1:8000/api/lotto",
            json={"most_digit": max_digit, "count": max_count},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.lotto_result = {
                "main_numbers": data["main_numbers"],
                "bonus_number": data["bonus_number"],
                "most_digit": data["most_digit"],
                "count": data["count"]
            }
        else:
            st.error(f"API 오류: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요!")
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")


st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
st.markdown('<div class="menu-note">▦ 메뉴(테마/날짜)는 옵션으로 추후 확장 가능</div>', unsafe_allow_html=True)

# Display 영역
display_placeholder = st.empty()
with display_placeholder.container():
    st.markdown(f'<div class="display-box">{st.session_state.display}</div>', unsafe_allow_html=True)

st.write("")

rows = [
    ["AC", "±", "%", "DEL"],
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "x"],
    ["1", "2", "3", "-"],
    ["0", "00", ".", "+"],
]

for row in rows:
    cols = st.columns(4, gap="small")
    for index, key in enumerate(row):
        with cols[index]:
            st.button(key, key=f"btn_{key}_{index}", on_click=apply_action, args=(key,), use_container_width=True)

eq_cols = st.columns([1, 1, 1, 1], gap="small")
with eq_cols[3]:
    st.button("=", key="btn_equal", on_click=apply_action, args=("=",), use_container_width=True)

# 가장 많이 누른 숫자 표시
max_digit = max(st.session_state.digit_count, key=st.session_state.digit_count.get)
max_count = st.session_state.digit_count[max_digit]

st.write("")
if max_count > 0:
    st.markdown(
        f'<div style="text-align: center; color: #a3acb9; font-size: 0.9rem; margin-top: 12px;">'
        f'가장 많이 누른 숫자: <span style="color: #4CAF50; font-weight: 700; font-size: 1.1rem;">{max_digit}</span> '
        f'({max_count}회)</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div style="text-align: center; color: #a3acb9; font-size: 0.9rem; margin-top: 12px;">'
        '아직 숫자를 누르지 않음</div>',
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# 로또 번호 생성 영역
st.write("")
st.divider()
st.write("")

# 로또 생성 버튼
if st.button("🎰 로또 번호 생성", use_container_width=True, key="lotto_button"):
    call_lotto_api()

# 로또 결과 표시
if st.session_state.lotto_result:
    result = st.session_state.lotto_result
    st.markdown(
        f'<div style="background: #1b2130; border-radius: 12px; padding: 16px; border: 1px solid #4CAF50; margin-top: 12px;">'
        f'<div style="text-align: center; color: #a3acb9; font-size: 0.85rem; margin-bottom: 8px;">'
        f'입력: {result["most_digit"]} ({result["count"]}회) 기반 생성</div>'
        f'<div style="text-align: center; font-size: 1.3rem; font-weight: 700; color: #ffffff; margin: 12px 0;">'
        f'{"&nbsp;&nbsp;".join([f"<span style=\"background: #FFD700; color: #000000; padding: 6px 10px; border-radius: 6px; margin: 0 4px;\">{n}</span>" for n in result["main_numbers"]])}'
        f'</div>'
        f'<div style="text-align: center; font-size: 1rem; color: #FF6B6B; font-weight: 600; margin-top: 8px;">'
        f'보너스: <span style="background: #FF6B6B; color: #ffffff; padding: 4px 8px; border-radius: 4px;">{result["bonus_number"]}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

