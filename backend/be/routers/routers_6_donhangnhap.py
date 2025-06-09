# be/routers/routers_6_donhangnhap.py

from fastapi import APIRouter, HTTPException, status, Query, Response
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date, datetime
from decimal import Decimal

# Import các hàm nghiệp vụ
from be.operation import operation_6_donhangnhap as dhn_ops

# Khởi tạo router mới
router = APIRouter(
    prefix="/purchase-orders",
    tags=["Đơn hàng nhập"],
)

# --- Định nghĩa các giá trị Enum để validation ---
PurchaseOrderStatus = Literal['Chờ xác nhận', 'Đã đặt hàng', 'Đang giao hàng', 'Hoàn tất', 'Đã hủy']


# --- Pydantic Models ---
class PurchaseOrderItemBase(BaseModel):
    id_san_pham: int = Field(..., gt=0)
    so_luong: int = Field(..., gt=0)
    gia_nhap_don_vi: Decimal = Field(..., ge=0)
    ghi_chu: Optional[str] = None


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemOut(PurchaseOrderItemBase):
    id: int
    tong_gia_nhap: Decimal
    ten_san_pham: str
    ma_san_pham: str
    don_vi_tinh: str

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    id_nha_cung_cap: int = Field(..., gt=0)
    id_nhan_vien: int = Field(..., gt=0)
    ngay_dat_hang: Optional[date] = None
    ngay_du_kien_nhan_hang: Optional[date] = None
    trang_thai: PurchaseOrderStatus = 'Chờ xác nhận'
    ghi_chu: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    chi_tiet_san_pham: Optional[List[PurchaseOrderItemCreate]] = []


class PurchaseOrderStatusUpdate(BaseModel):
    trang_thai: PurchaseOrderStatus
    ngay_nhan_hang_thuc_te: Optional[date] = None


class PurchaseOrderOut(PurchaseOrderBase):
    id: int
    ngay_tao_ban_ghi: datetime
    ngay_cap_nhat_ban_ghi: datetime
    ten_nha_cung_cap: str
    ten_nhan_vien: str
    # tong_gia_tri sẽ được tính bởi trigger CSDL
    # tong_gia_tri: Decimal


class PurchaseOrderDetailOut(PurchaseOrderOut):
    chi_tiet_san_pham: List[PurchaseOrderItemOut] = []


# --- API Endpoints ---

@router.post("/", response_model=PurchaseOrderDetailOut, status_code=status.HTTP_201_CREATED,
             summary="Tạo đơn hàng nhập mới")
def create_purchase_order(order: PurchaseOrderCreate):
    """
    Tạo một đơn hàng nhập mới, có thể kèm theo danh sách sản phẩm ban đầu.
    """
    order_dict = order.model_dump(exclude={"chi_tiet_san_pham"})
    # Chuyển đổi date object thành string để hàm operation xử lý
    for key in ['ngay_dat_hang', 'ngay_du_kien_nhan_hang']:
        if order_dict[key]:
            order_dict[f"{key}_str"] = order_dict.pop(key).isoformat()

    new_id = dhn_ops.create_donhangnhap(**order_dict)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Không thể tạo đơn hàng nhập.")

    # Thêm các chi tiết sản phẩm nếu có
    if order.chi_tiet_san_pham:
        for item in order.chi_tiet_san_pham:
            dhn_ops.add_item_to_donhangnhap(new_id, **item.model_dump())

    created_order = dhn_ops.get_chitietdonhangnhap(new_id)
    return created_order


@router.get("/", response_model=List[PurchaseOrderOut], summary="Lấy danh sách đơn hàng nhập")
def get_all_purchase_orders(
        supplier_id: Optional[int] = Query(None, description="Lọc theo ID nhà cung cấp"),
        status: Optional[PurchaseOrderStatus] = Query(None, description="Lọc theo trạng thái đơn hàng")
):
    """
    Lấy danh sách tất cả các đơn hàng nhập, có thể lọc theo nhà cung cấp hoặc trạng thái.
    """
    orders = dhn_ops.get_all_donhangnhap(supplier_id=supplier_id, status=status)
    if orders is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ.")
    return orders


@router.get("/{order_id}", response_model=PurchaseOrderDetailOut, summary="Lấy chi tiết một đơn hàng nhập")
def get_purchase_order_details(order_id: int):
    """
    Lấy thông tin chi tiết của một đơn hàng nhập, bao gồm danh sách sản phẩm.
    """
    order = dhn_ops.get_chitietdonhangnhap(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng nhập với ID {order_id}")
    return order


@router.post("/{order_id}/items", response_model=PurchaseOrderDetailOut, summary="Thêm sản phẩm vào đơn hàng nhập")
def add_item_to_purchase_order(order_id: int, item: PurchaseOrderItemCreate):
    """
    Thêm một sản phẩm vào đơn hàng nhập đã tồn tại.
    """
    item_id = dhn_ops.add_item_to_donhangnhap(order_id, **item.model_dump())
    if item_id is None:
        raise HTTPException(status_code=400,
                            detail="Không thể thêm sản phẩm, vui lòng kiểm tra ID đơn hàng và ID sản phẩm.")
    return dhn_ops.get_chitietdonhangnhap(order_id)


@router.patch("/{order_id}/status", response_model=PurchaseOrderDetailOut, summary="Cập nhật trạng thái đơn hàng nhập")
def update_purchase_order_status(order_id: int, status_update: PurchaseOrderStatusUpdate):
    """
    Cập nhật trạng thái của đơn hàng nhập.
    - Khi trạng thái được cập nhật thành 'Hoàn tất', trigger trong CSDL sẽ tự động cập nhật tồn kho.
    """
    ngay_nhan_hang_str = status_update.ngay_nhan_hang_thuc_te.isoformat() if status_update.ngay_nhan_hang_thuc_te else None

    success = dhn_ops.update_donhangnhap_status(order_id, status_update.trang_thai, ngay_nhan_hang_str)
    if not success:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng ID {order_id} hoặc cập nhật thất bại.")

    return dhn_ops.get_chitietdonhangnhap(order_id)