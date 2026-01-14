# backend/be/routers/routers_7_donhangban.py

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
import be.operation.operation_7_donhangban as operation_7

router = APIRouter(
    prefix="/donhangban",
    tags=["Quản lý Đơn Hàng Bán"]
)

# ---------------------------------------------------------
# 1. CÁC PYDANTIC MODEL (SCHEMA) CHO INPUT
# ---------------------------------------------------------

class CreateDonHangBan(BaseModel):
    id_nhan_vien: int
    id_khach_hang: int
    dia_chi_giao_hang: str
    ngay_dat_hang_str: Optional[str] = None  # Định dạng YYYY-MM-DD
    phuong_thuc_thanh_toan: Optional[str] = "Tiền mặt"
    trang_thai_don_hang: Optional[str] = "Chờ xác nhận"
    trang_thai_thanh_toan: Optional[str] = "Chưa thanh toán"
    ghi_chu_don_hang: Optional[str] = None

class AddItemDonHangBan(BaseModel):
    id_don_hang_ban: int
    id_san_pham: int
    so_luong: float
    gia_ban_niem_yet_don_vi: float
    giam_gia: float = 0.0  # Từ 0.0 đến 1.0 (VD: 0.1 là giảm 10%)
    ghi_chu_item: Optional[str] = None

class UpdateStatusDonHangBan(BaseModel):
    trang_thai_don_hang: str
    trang_thai_thanh_toan: Optional[str] = None
    ngay_giao_hang_thuc_te_str: Optional[str] = None

# ---------------------------------------------------------
# 2. CÁC API ENDPOINT
# ---------------------------------------------------------

@router.post("/", description="Tạo một đơn hàng bán mới")
def create_don_hang(order_data: CreateDonHangBan):
    new_id = operation_7.create_donhangban(
        id_nhan_vien=order_data.id_nhan_vien,
        id_khach_hang=order_data.id_khach_hang,
        dia_chi_giao_hang=order_data.dia_chi_giao_hang,
        ngay_dat_hang_str=order_data.ngay_dat_hang_str,
        phuong_thuc_thanh_toan=order_data.phuong_thuc_thanh_toan,
        trang_thai_don_hang=order_data.trang_thai_don_hang,
        trang_thai_thanh_toan=order_data.trang_thai_thanh_toan,
        ghi_chu_don_hang=order_data.ghi_chu_don_hang
    )
    
    if not new_id:
        raise HTTPException(status_code=400, detail="Không thể tạo đơn hàng. Vui lòng kiểm tra lại thông tin (ID nhân viên, Khách hàng...).")
    
    return {"message": "Tạo đơn hàng thành công", "id_don_hang": new_id}


@router.post("/add-item", description="Thêm sản phẩm vào đơn hàng (Kiểm tra tồn kho & Tính giá vốn)")
def add_item_to_order(item_data: AddItemDonHangBan):
    new_item_id = operation_7.add_item_to_donhangban(
        id_don_hang_ban=item_data.id_don_hang_ban,
        id_san_pham=item_data.id_san_pham,
        so_luong=item_data.so_luong,
        gia_ban_niem_yet_don_vi=item_data.gia_ban_niem_yet_don_vi,
        giam_gia=item_data.giam_gia,
        ghi_chu_item=item_data.ghi_chu_item
    )
    
    if not new_item_id:
        raise HTTPException(status_code=400, detail="Lỗi khi thêm sản phẩm (Có thể do hết tồn kho hoặc ID không hợp lệ).")
        
    return {"message": "Thêm sản phẩm thành công", "id_chi_tiet": new_item_id}


@router.get("/chitiet/{id_don_hang}", description="Lấy chi tiết đơn hàng + Tính toán thuế phí (Financial Calc)")
def get_chitiet_donhang(id_don_hang: int):
    # LƯU Ý: Không sử dụng response_model để trả về đầy đủ dictionary bao gồm cả 'financial_calc'
    result = operation_7.get_chitietdonhangban(id_don_hang)
    
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng này.")
        
    return result


@router.get("/", description="Lấy danh sách đơn hàng (Có lọc theo khách, nhân viên, trạng thái)")
def get_all_donhang(
    customer_id: Optional[int] = None, 
    staff_id: Optional[int] = None, 
    status: Optional[str] = None
):
    # LƯU Ý: Không sử dụng response_model để trả về được trường 'tong_thanh_toan_du_kien' tính toán từ operation
    results = operation_7.get_all_donhangban(customer_id, staff_id, status)
    
    if results is None:
        raise HTTPException(status_code=500, detail="Lỗi Server khi lấy danh sách đơn hàng.")
        
    return results


@router.put("/update-status/{id_don_hang}", description="Cập nhật trạng thái đơn hàng (Duyệt đơn, Hoàn tất, Hủy...)")
def update_status(id_don_hang: int, status_data: UpdateStatusDonHangBan):
    success = operation_7.update_donhangban_status(
        id_don_hang_ban=id_don_hang,
        new_trang_thai_don_hang=status_data.trang_thai_don_hang,
        new_trang_thai_thanh_toan=status_data.trang_thai_thanh_toan,
        ngay_giao_hang_thuc_te_str=status_data.ngay_giao_hang_thuc_te_str
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Không thể cập nhật trạng thái đơn hàng.")
        
    return {"message": f"Đã cập nhật trạng thái đơn hàng {id_don_hang} thành công."}