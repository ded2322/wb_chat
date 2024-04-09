from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.chat.chat_websoket.router import router as chat_router
from core.chat.users.router import router_auth as auth_router
from core.chat.users.router import router_user as user_router
from core.chat.chat_websoket.router_wb import router as wb_router
from core.chat.image.router import router as image_router


app = FastAPI()

app.mount("/static",StaticFiles(directory="core/static"), "static")


# todo сделать логи
# todo админку

# celery -A core.tasks.celery_config:celery worker --loglevel=INFO --pool=solo
# alembic revision --autogenerate -m "init"  alembic upgrade head
'''

'''

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(image_router)


origins = ['http://localhost:3000', 'http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)


app.include_router(wb_router)
