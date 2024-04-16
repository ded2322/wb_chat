from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from sqladmin import Admin

from core.chat.chat_websoket.router import router as chat_router
from core.chat.users.router import router_auth as auth_router
from core.chat.users.router import router_user as user_router
from core.chat.chat_websoket.router_wb import router as wb_router
from core.chat.image.router import router as image_router
from core.database import engine
from core.admin.views import UserAdmin, MessagesAdmin
from core.admin.auth import authentication_backend

app = FastAPI(
    title="Real-time chat",
    version="1.2"
)

app.mount("/static",StaticFiles(directory="core/static"), "static")

# todo роли
# todo переделать админку
# todo картинка удаленного пользователя, картинка на вкладку

# celery -A core.tasks.celery_config:celery worker --loglevel=INFO --pool=solo
# alembic revision --autogenerate -m "init"  alembic upgrade head
'''
DB_USER=postgres
DB_PASS=postgres
DB_NAME=chat_db
DB_HOST=db
DB_PORT=5432
'''

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(image_router)
app.include_router(wb_router)

origins = ['http://localhost:3000', 'http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(MessagesAdmin)
