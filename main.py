from fastapi import FastAPI

from routers import postRoutes, patchRoutes

app = FastAPI()

app.include_router(router=postRoutes.router)
app.include_router(router=patchRoutes.router)
