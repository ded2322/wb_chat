from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from sqladmin import Admin

from core.admin.auth import authentication_backend
from core.admin.views import MessagesAdmin, UserAdmin
from core.routers.message_router import router as chat_router
from core.routers.wb_router import router as wb_router
from core.routers.image_router import router as image_router
from core.routers.user_router import router_auth as auth_router
from core.routers.user_router import router_user as user_router
from core.database import engine

app = FastAPI(title="Real-time routers", version="1.3")

app.mount("/static", StaticFiles(directory="/core/static"), "static")

# todo картинка удаленного пользователя

# alembic revision --autogenerate -m "init"  alembic upgrade head
"""
DB_USER=postgres
DB_PASS=root
DB_NAME=App
DB_HOST=localhost
DB_PORT=5432
"""

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(image_router)
app.include_router(wb_router)

origins = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(MessagesAdmin)
