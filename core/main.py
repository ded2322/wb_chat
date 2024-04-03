import uvicorn
from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.chat.router import router as chat_router
from core.chat.users.router import router_auth as auth_router
from core.chat.users.router import router_user as user_router
from core.chat.router_wb import router as wb_router

app = FastAPI()




app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)


app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
    description="Это основная версия, находящиеся здесь ручки сделаны или почти сделаны ",
    #middleware=[
    #    Middleware(SessionMiddleware, secret_key='mysecretkey')
    #]
)




app.include_router(wb_router)