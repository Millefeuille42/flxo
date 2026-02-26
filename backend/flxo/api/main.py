from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from flxo.api.routers import auth, office, presence, property, seat, user
from flxo.services.settings import get_settings


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=get_settings().app.secret_key)  # type: ignore

origins = get_settings().app.allowed_origins

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(presence.router)
app.include_router(office.router)
app.include_router(property.router)
app.include_router(seat.router)


def main() -> None:
    uvicorn.run(
        "flxo.core.main:app",
        host=get_settings().app.bind,  # type: ignore
        port=get_settings().app.port,  # type: ignore
        reload=True,
    )
