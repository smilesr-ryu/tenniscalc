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
    
    Args:
        request: 가장 많이 누른 숫자와 횟수
    
    Returns:
        로또 번호 6개 + 보너스 번호 1개
    """
    try:
        # 입력 검증
        if not request.most_digit.isdigit() or int(request.most_digit) > 9:
            raise ValueError("가장 많이 누른 숫자는 0-9 범위여야 합니다")
        
        # 로또 번호 생성 (1-45 범위에서 6개, 중복 없음)
        main_numbers = sorted(random.sample(range(1, 46), 6))
        
        # 보너스 번호 생성 (1-45 범위, 메인 번호와 다름)
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
