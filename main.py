from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import postRoutes, patchRoutes, getRoutes


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=postRoutes.router)
app.include_router(router=patchRoutes.router)
app.include_router(router=getRoutes.router)
