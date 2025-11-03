import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from flxo.routers import auth, presence, user
from flxo.services import database
from flxo.services.settings import get_settings

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=get_settings().app.secret_key)


@app.on_event("startup")
def on_startup():
    database.create_db_and_tables()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(presence.router)


def main():
    uvicorn.run(
    "flxo.core.main:app",
        host=get_settings().app.bind,
        port=get_settings().app.port,
        reload=True
    )
