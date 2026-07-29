import logging
import time

from fastapi import FastAPI, Request

from router import router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-api")

app = FastAPI(title="Task API")
app.include_router(router)


@app.middleware("http")
async def request_log(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)

    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - start) * 1000,
    )

    return response