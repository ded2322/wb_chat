import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.chat.router import router as chat_router
from core.chat.users.router import router_auth as auth_router
from core.chat.users.router import router_user as user_router
from core.chat.router_wb import router as wb_router

app = FastAPI()




app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chat_router)


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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
