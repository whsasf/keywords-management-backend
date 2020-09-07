from typing import Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from myrouters import projects,categories,account
from database.db_advanced import dbinit

import uvicorn

app = FastAPI()

# 引入子路由
app.include_router(projects.router, prefix="/Projects")
# app.include_router(categories.router, prefix="/Categories")
app.include_router(account.router, prefix="/Account")

# 设定静态目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 允许的跨域来源
origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://192.168.1.3:8080",
    "http://192.168.20.160:8080"
]
# CSRF攻击防范
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000, log_level="debug", reload=True)