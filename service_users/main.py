from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from config import settings
from database import engine
from errors import ApiException
from models import Base
from routers import auth, users
from schemas import ApiResponse, ErrorDetail

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users Service")


# Обработчик ошибки валидации с Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    first_error = exc.errors()[0]
    return JSONResponse(
        status_code=400,
        content=ApiResponse(
            success=False,
            data=None,
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message='.'.join(map(str, first_error['loc'][1:])) + ": " + first_error['msg'],
            )
        ).model_dump(mode='json')
    )

# Обработчик кастомной ошибки
@app.exception_handler(ApiException)
async def api_exception_handler(_, exc: ApiException):
    return JSONResponse(
        status_code=400,
        content=ApiResponse(
            success=False,
            data=None,
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
            )
        ).model_dump(mode='json'),
    )

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

v1_prefix = "/v1"
app.include_router(auth.router, prefix=v1_prefix)
app.include_router(users.router, prefix=v1_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )
