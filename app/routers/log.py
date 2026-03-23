from fastapi import APIRouter
from app.schemas.request_response import LogRequest, LogResponse
from app.services.fake_db import logs_db

router = APIRouter()


@router.post("/", response_model=LogResponse)
def save_log(request: LogRequest):
    log_item = request.model_dump()
    logs_db.append(log_item)

    return LogResponse(
        message="운동 로그가 저장되었습니다.",
        saved_log=log_item
    )