from app.utils import lifespan
from fastapi import FastAPI
from app.endpoints import router
import uvicorn


app = FastAPI(
    lifespan=lifespan,
    docs_url="/"
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)