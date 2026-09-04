from fastapi import APIRouter
from datetime import datetime
from api.models.schemas import HealthResponse
from api.services.predictor import get_predictor
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


@router.get('/health', response_model=HealthResponse)
def health_check():
    predictor = get_predictor()
    data_mode = os.getenv('MODE', 'DEMO')
    return HealthResponse(
        status='ok',
        models_loaded=predictor.get_loaded_stocks(),
        timestamp=datetime.now().isoformat(),
        version='1.0.0',
        data_mode=data_mode
    )
