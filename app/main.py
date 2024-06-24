from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app import models
from app.database import engine, get_db
from app.api import document_endpoints
from app.api import projects_endpoints
from app.api import user_endpoints


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# register the rate limit exceeded handler
app.state.limiter = user_endpoints.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(document_endpoints.router)
app.include_router(projects_endpoints.router)
app.include_router(user_endpoints.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
