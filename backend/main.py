from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- Thêm dòng này
import uvicorn

# Import các router
from be.routers import (
    routers_1_danhmuc, 
    routers_2_sanpham, 
    routers_7_donhangban, 
    routers_10_doanhthuloinhuan
)

app = FastAPI()

# --- CẤU HÌNH CORS (QUAN TRỌNG) ---
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500", # Port mặc định của Live Server
    "*" # Cho phép tất cả (Dùng cho MVP demo cho tiện)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------------

# Include Routers
app.include_router(routers_1_danhmuc.router)
app.include_router(routers_2_sanpham.router)
app.include_router(routers_7_donhangban.router)
app.include_router(routers_10_doanhthuloinhuan.router)

@app.get("/")
def read_root():
    return {"Hello": "OmniPocket Backend is Running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)