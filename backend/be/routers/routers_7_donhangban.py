# be/routers/routers_7_donhangban.py

from fastapi import APIRouter, HTTPException, status, Query, Response
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date, datetime
from decimal import Decimal

# Import các hàm nghiệp vụ
from be.operation import operation_7_donhangban as dhb_ops

# Khởi tạo router mới
router = APIRouter(
    prefix="/sales-orders",
    tags=["Đơn hàng bán"],
)

# --- Định nghĩa các giá trị Enum để validation ---
PaymentMethod = Literal['Tiền mặt', 'Chuyển khoản', 'Thẻ tín dụng', 'COD']
OrderStatus = Literal['Chờ xác nhận', 'Đã xác nhận', 'Đang giao hàng', 'Đã giao', 'Hoàn tất', 'Đã hủy', 'Trả hàng']
PaymentStatus = Literal['Chưa thanh toán', 'Đã thanh toán']


# --- Pydantic Models ---
class SalesOrderItemBase(BaseModel):
    id_san_pham: int = Field(..., gt=0)
    so_luong: int = Field(..., gt=0)
    gia_ban_niem_yet_don_vi: Decimal = Field(..., ge=0)
    giam_gia: Decimal = Field(..., ge=0, le=1)
    ghi_chu: Optional[str] = None


class SalesOrderItemCreate(SalesOrderItemBase):
    pass


class SalesOrderItemOut(SalesOrderItemBase):
    id: int
    gia_ban_cuoi_cung_don_vi: Decimal
    tong_gia_von: Decimal
    tong_gia_ban: Decimal
    ten_san_pham: str
    ma_san_pham: str
    don_vi_tinh: str

    class Config:
        from_attributes = True


class SalesOrderBase(BaseModel):
    id_khach_hang: int = Field(..., gt=0)
    id_nhan_vien: int = Field(..., gt=0)
    dia_chi_giao_hang: str
    ngay_dat_hang: Optional[date] = None
    phuong_thuc_thanh_toan: PaymentMethod
    trang_thai_don_hang: OrderStatus = 'Chờ xác nhận'
    trang_thai_thanh_toan: PaymentStatus = 'Chưa thanh toán'
    ghi_chu_don_hang: Optional[str] = None


class SalesOrderCreate(SalesOrderBase):
    chi_tiet_san_pham: List[SalesOrderItemCreate]


class SalesOrderStatusUpdate(BaseModel):
    trang_thai_don_hang: OrderStatus
    trang_thai_thanh_toan: Optional[PaymentStatus] = None
    ngay_giao_hang_thuc_te: Optional[date] = None


class SalesOrderOut(SalesOrderBase):
    id: int
    ngay_tao_ban_ghi: datetime
    ngay_cap_nhat_ban_ghi: datetime
    ten_khach_hang: str
    ten_nhan_vien: str


class SalesOrderDetailOut(SalesOrderOut):
    chi_tiet_san_pham: List[SalesOrderItemOut] = []


# --- API Endpoints ---

@router.post("/", response_model=SalesOrderDetailOut, status_code=status.HTTP_201_CREATED,
             summary="Tạo đơn hàng bán mới")
def create_sales_order(order: SalesOrderCreate):
    order_dict = order.model_dump(exclude={"chi_tiet_san_pham"})
    ngay_dat_hang_str = order_dict.pop('ngay_dat_hang').isoformat() if order_dict.get('ngay_dat_hang') else None

    new_id = dhb_ops.create_donhangban(ngay_dat_hang_str=ngay_dat_hang_str, **order_dict)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Không thể tạo đơn hàng bán.")

    for item in order.chi_tiet_san_pham:
        item_id = dhb_ops.add_item_to_donhangban(new_id, **item.model_dump())
        if item_id is None:
            # Nếu một item không thêm được, có thể xóa đơn hàng vừa tạo và báo lỗi
            dhb_ops.delete_donhangban_by_id(new_id)
            raise HTTPException(status_code=400,
                                detail=f"Không thể thêm sản phẩm ID {item.id_san_pham} (có thể hết hàng). Đơn hàng đã được hủy.")

    return dhb_ops.get_chitietdonhangban(new_id)


@router.get("/", response_model=List[SalesOrderOut], summary="Lấy danh sách đơn hàng bán")
def get_all_sales_orders(
        customer_id: Optional[int] = Query(None, description="Lọc theo ID khách hàng"),
        staff_id: Optional[int] = Query(None, description="Lọc theo ID nhân viên"),
        status: Optional[OrderStatus] = Query(None, description="Lọc theo trạng thái đơn hàng")
):
    orders = dhb_ops.get_all_donhangban(customer_id=customer_id, staff_id=staff_id, status=status)
    if orders is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ.")
    return orders


@router.get("/{order_id}", response_model=SalesOrderDetailOut, summary="Lấy chi tiết một đơn hàng bán")
def get_sales_order_details(order_id: int):
    order = dhb_ops.get_chitietdonhangban(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng bán với ID {order_id}")
    return order


@router.post("/{order_id}/items", response_model=SalesOrderDetailOut, summary="Thêm sản phẩm vào đơn hàng bán")
def add_item_to_sales_order(order_id: int, item: SalesOrderItemCreate):
    item_id = dhb_ops.add_item_to_donhangban(order_id, **item.model_dump())
    if item_id is None:
        raise HTTPException(status_code=400,
                            detail="Không thể thêm sản phẩm, vui lòng kiểm tra ID đơn hàng, ID sản phẩm và tồn kho.")
    return dhb_ops.get_chitietdonhangban(order_id)


@router.patch("/{order_id}/status", response_model=SalesOrderDetailOut, summary="Cập nhật trạng thái đơn hàng bán")
def update_sales_order_status(order_id: int, status_update: SalesOrderStatusUpdate):
    ngay_giao_hang_str = status_update.ngay_giao_hang_thuc_te.isoformat() if status_update.ngay_giao_hang_thuc_te else None
    success = dhb_ops.update_donhangban_status(
        order_id,
        status_update.trang_thai_don_hang,
        status_update.trang_thai_thanh_toan,
        ngay_giao_hang_str
    )
    if not success:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng ID {order_id} hoặc cập nhật thất bại.")
    return dhb_ops.get_chitietdonhangban(order_id)
