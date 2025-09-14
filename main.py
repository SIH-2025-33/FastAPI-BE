from fastapi import FastAPI

from routers import postRoutes

app = FastAPI()

app.include_router(router=postRoutes.router)
