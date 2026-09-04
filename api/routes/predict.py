from fastapi import APIRouter, HTTPException
from api.models.schemas import SignalResponse, AllSignalsResponse, StockSignalSummary
from api.services.predictor import get_predictor
from api.services.live_data import get_current_price
from datetime import datetime

router = APIRouter()


@router.get('/signal/{stock}', response_model=SignalResponse)
def get_signal(stock: str):
    stock = stock.upper().strip()
    predictor = get_predictor()

    try:
        current_price = get_current_price(stock)
        data_mode = 'LIVE'
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market data connection error for {stock}: {str(e)}")

    try:
        result = predictor.predict(stock, current_price=current_price)
        result['data_mode'] = data_mode
        return SignalResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Inference error for {stock}: {str(e)}")


@router.get('/signals', response_model=AllSignalsResponse)
def get_all_signals():
    """Return BUY/HOLD/SELL signals for popular stocks at once."""
    predictor = get_predictor()
    summaries = []
    
    featured = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'TATAMOTORS', 'SBIN', 'ZOMATO']

    for stock in featured:
        try:
            current_price = get_current_price(stock)
            result = predictor.predict(stock, current_price=current_price)
            summaries.append(StockSignalSummary(
                stock=result['stock'],
                action=result['action'],
                confidence=result['confidence'],
                price=result['price'],
                portfolio_value=result['portfolio_value'],
                timestamp=result['timestamp']
            ))
        except Exception:
            pass

    return AllSignalsResponse(
        signals=summaries,
        count=len(summaries),
        timestamp=datetime.now().isoformat(),
        supported_universe_size=7000
    )
