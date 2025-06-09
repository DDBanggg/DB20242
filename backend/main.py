# main.py
# File này nằm ở thư mục gốc của backend.

from fastapi import FastAPI
import uvicorn

# 1. Import tất cả các router
from be.routers import routers_1_danhmuc
from be.routers import routers_2_sanpham
from be.routers import routers_3_nhacungcap
from be.routers import routers_4_khachhang
from be.routers import routers_5_nhanvien
from be.routers import routers_6_donhangnhap
from be.routers import routers_7_donhangban
from be.routers import routers_8_chiphi
from be.routers import routers_9_lichsugianiemyet
from be.routers import routers_10_doanhthuloinhuan
from be.routers import routers_11_thongkebanhang
from be.routers import routers_12_phantichkhachhang
from be.routers import routers_13_congno

# 2. Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="API Quản Lý Bán Hàng",
    description="Đây là API backend cho dự án quản lý bán hàng sử dụng FastAPI và PostgreSQL.",
    version="1.0.0"
)

# 3. Thêm các router vào ứng dụng chính
# Tiền tố /api sẽ được áp dụng cho tất cả các endpoint trong các router này
app.include_router(routers_1_danhmuc.router, prefix="/api")
app.include_router(routers_2_sanpham.router, prefix="/api")
app.include_router(routers_3_nhacungcap.router, prefix="/api")
app.include_router(routers_4_khachhang.router, prefix="/api")
app.include_router(routers_5_nhanvien.router, prefix="/api")
app.include_router(routers_6_donhangnhap.router, prefix="/api")
app.include_router(routers_7_donhangban.router, prefix="/api")
app.include_router(routers_8_chiphi.router, prefix="/api")
app.include_router(routers_9_lichsugianiemyet.router, prefix="/api")
app.include_router(routers_10_doanhthuloinhuan.router, prefix="/api")
app.include_router(routers_11_thongkebanhang.router, prefix="/api")
app.include_router(routers_12_phantichkhachhang.router, prefix="/api")
app.include_router(routers_13_congno.router, prefix="/api")


@app.get("/")
def read_root():
    """
    Endpoint gốc để kiểm tra xem API có hoạt động không.
    """
    return {"message": "Chào mừng đến với API Quản Lý Bán Hàng!"}

# Cách chạy chuẩn là dùng lệnh trong terminal: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
