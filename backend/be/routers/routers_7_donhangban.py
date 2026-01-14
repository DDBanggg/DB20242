# File: backend/be/routers/routers_7_donhangban.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..db_connection import execute_query, execute_non_query

router = APIRouter()

# --- MODELS ---
class ChiTietDonHangInput(BaseModel):
    MaSP: int
    SoLuong: int
    DonGia: float

class DonHangInput(BaseModel):
    MaKH: int
    MaNV: int
    ChiTiet: List[ChiTietDonHangInput]

@router.post("/don-hang-ban/tao-moi")
async def create_don_hang_ban(don_hang: DonHangInput):
    """
    Tạo đơn hàng bán mới (POS).
    - Tự động tính Thuế VAT (10%).
    - Tự động set trạng thái 'Hoàn tất' (để kích hoạt trigger trừ kho nếu có).
    """
    try:
        # 1. Tính toán tổng tiền
        tong_tien_hang = 0
        for item in don_hang.ChiTiet:
            tong_tien_hang += item.SoLuong * item.DonGia
            
        THUE_VAT_RATE = 0.10
        tien_thue = tong_tien_hang * THUE_VAT_RATE
        tong_thanh_toan = tong_tien_hang + tien_thue
        
        # 2. Insert vào DonHangBan
        # Lưu ý: DB dùng snake_case và thiếu cột TongTien, nên ta chỉ lưu các trường có thật.
        # Hardcode: dia_chi_giao_hang, phuong_thuc_thanh_toan để thỏa mãn NOT NULL
        sql_don_hang = """
            INSERT INTO DonHangBan (
                id_khach_hang, id_nhan_vien, ngay_dat_hang, 
                trang_thai_don_hang, trang_thai_thanh_toan,
                dia_chi_giao_hang, phuong_thuc_thanh_toan
            )
            VALUES (%s, %s, NOW(), 'Hoàn tất', 'Đã thanh toán', 'Tại quầy', 'Tiền mặt')
            RETURNING id
        """
        
        ma_dh_moi = execute_non_query(
            sql_don_hang, 
            (don_hang.MaKH, don_hang.MaNV), 
            return_id=True
        )
        
        if not ma_dh_moi:
             raise HTTPException(status_code=500, detail="Lỗi DB: Không thể tạo đơn hàng.")

        # 3. Insert ChiTietDonHangBan
        for item in don_hang.ChiTiet:
            # Tính toán các giá trị cho bảng ChiTiet
            thanh_tien = item.SoLuong * item.DonGia
            
            sql_chi_tiet = """
                INSERT INTO ChiTietDonHangBan (
                    id_don_hang_ban, id_san_pham, so_luong, 
                    gia_ban_niem_yet_don_vi, gia_ban_cuoi_cung_don_vi,
                    giam_gia, tong_gia_ban
                )
                VALUES (%s, %s, %s, %s, %s, 0, %s)
            """
            execute_non_query(sql_chi_tiet, (
                ma_dh_moi, item.MaSP, item.SoLuong, 
                item.DonGia, item.DonGia, 
                thanh_tien
            ))

        # 4. Trả về kết quả đầy đủ để Frontend in hóa đơn
        return {
            "status": "success",
            "message": "Tạo đơn hàng thành công",
            "data": {
                "MaDH": ma_dh_moi,
                "MaKH": don_hang.MaKH,
                "MaNV": don_hang.MaNV,
                "TongTienHang": tong_tien_hang,
                "ThueVAT": tien_thue,
                "TongThanhToan": tong_thanh_toan,
                "TrangThai": "Hoàn tất"
            }
        }

    except Exception as e:
        print(f"Lỗi tạo đơn hàng: {e}")
        raise HTTPException(status_code=500, detail=str(e))