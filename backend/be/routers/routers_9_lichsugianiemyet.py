# be/routers/routers_9_lichsugianiemyet.py

from fastapi import APIRouter, HTTPException, status, Response, Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

# Import các hàm nghiệp vụ
from be.operation import operation_9_lichsugianiemyet as lsg_ops

# Khởi tạo router mới
router = APIRouter(
    tags=["Lịch sử giá"],
)


# --- Pydantic Models ---
class PriceHistoryBase(BaseModel):
    gia_niem_yet: Decimal = Field(..., ge=0, description="Mức giá niêm yết mới")
    ghi_chu: Optional[str] = None


class PriceHistoryCreate(PriceHistoryBase):
    ngay_ap_dung: date


class PriceHistoryUpdate(BaseModel):
    gia_niem_yet: Optional[Decimal] = Field(None, ge=0, description="Mức giá niêm yết mới")
    ghi_chu: Optional[str] = None


class PriceHistoryOut(BaseModel):
    id: int
    id_san_pham: int
    gia_niem_yet: Decimal
    ngay_ap_dung: date
    ngay_ket_thuc: Optional[date] = None
    ghi_chu: Optional[str] = None
    ngay_tao_ban_ghi: datetime
    ten_san_pham: str
    ma_san_pham: str

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.post("/products/{product_id}/price-history", response_model=PriceHistoryOut,
             status_code=status.HTTP_201_CREATED, summary="Thêm một mức giá mới cho sản phẩm")
def create_price_history_for_product(
        product_id: int = Path(..., gt=0, description="ID của sản phẩm cần cập nhật giá"),
        price_history: PriceHistoryCreate = ...
):
    """
    Tạo một bản ghi lịch sử giá mới cho một sản phẩm cụ thể.
    """
    new_id = lsg_ops.add_lichsugianiemyet(
        id_san_pham=product_id,
        gia_niem_yet=price_history.gia_niem_yet,
        ngay_ap_dung_str=price_history.ngay_ap_dung.isoformat(),
        ghi_chu=price_history.ghi_chu
    )
    if new_id is None:
        raise HTTPException(status_code=400, detail="Không thể thêm lịch sử giá.")

    created_history = lsg_ops.get_lichsugianiemyet_by_id(new_id)
    return created_history


@router.get("/products/{product_id}/price-history", response_model=List[PriceHistoryOut],
            summary="Lấy lịch sử giá của một sản phẩm")
def get_price_history_for_product(
        product_id: int = Path(..., gt=0, description="ID của sản phẩm cần xem lịch sử giá")
):
    """
    Lấy toàn bộ lịch sử giá của một sản phẩm.
    """
    history = lsg_ops.get_lichsugianiemyet_for_sanpham(product_id)
    if history is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ.")
    return history


@router.put("/price-history/{history_id}", response_model=PriceHistoryOut, summary="Cập nhật một bản ghi lịch sử giá")
def update_price_history(
        history_id: int,
        price_update: PriceHistoryUpdate
):
    """
    Cập nhật giá niêm yết hoặc ghi chú của một bản ghi lịch sử giá đã có.
    Không cho phép thay đổi ngày áp dụng để đảm bảo logic.
    """
    update_data = price_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không có dữ liệu để cập nhật.")

    success = lsg_ops.update_lichsugianiemyet(history_id, **update_data)
    if not success:
        raise HTTPException(status_code=404,
                            detail=f"Không tìm thấy lịch sử giá với ID {history_id} hoặc cập nhật thất bại.")

    return lsg_ops.get_lichsugianiemyet_by_id(history_id)
