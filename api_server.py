from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI(title="Lotto API")

class DigitRequest(BaseModel):
    """가장 많이 누른 숫자를 받는 요청"""
    most_digit: str
    count: int

class LottoResponse(BaseModel):
    """로또 번호 응답"""
    main_numbers: list[int]
    bonus_number: int
    most_digit: str
    count: int

@app.post("/api/lotto")
def generate_lotto(request: DigitRequest) -> LottoResponse:
    """
    가장 많이 누른 숫자를 받아서 로또 번호를 생성하여 반환
    가장 많이 사용된 숫자는 반드시 로또 번호에 포함됨
    
    Args:
        request: 가장 많이 누른 숫자와 횟수
    
    Returns:
        로또 번호 6개 + 보너스 번호 1개
    """
    try:
        # 입력 검증
        if not request.most_digit.isdigit() or int(request.most_digit) > 9:
            raise ValueError("가장 많이 누른 숫자는 0-9 범위여야 합니다")
        
        # 계산기 숫자(0-9)를 로또 번호 범위(1-45)로 매핑
        most_digit_int = int(request.most_digit)
        if most_digit_int == 0:
            guaranteed_number = 10  # 0 → 10
        else:
            guaranteed_number = most_digit_int  # 1-9 → 1-9
        
        # 로또 번호 생성: 가장 많이 사용된 숫자는 반드시 포함
        available = [n for n in range(1, 46) if n != guaranteed_number]
        other_numbers = random.sample(available, 5)
        main_numbers = sorted([guaranteed_number] + other_numbers)
        
        # 보너스 번호 생성 (메인 번호와 다름)
        bonus_candidates = [n for n in range(1, 46) if n not in main_numbers]
        bonus_number = random.choice(bonus_candidates)
        
        return LottoResponse(
            main_numbers=main_numbers,
            bonus_number=bonus_number,
            most_digit=request.most_digit,
            count=request.count
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
