# be/routers/routers_11_thongkebanhang.py

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from enum import Enum

# Import các hàm nghiệp vụ
from be.reports import operation_11_thongkebanhang as stats_ops

# Khởi tạo router mới, gộp chung vào tag "Báo cáo"
router = APIRouter(
    prefix="/reports",
    tags=["Báo cáo"],
)


# --- Định nghĩa các giá trị Enum để validation ---
class ReportPeriod(str, Enum):
    yesterday = "yesterday"
    last_week = "last_week"
    last_month = "last_month"
    custom = "custom"


class BestSellingSortBy(str, Enum):
    quantity = "quantity"
    revenue = "revenue"


class TopN(int, Enum):
    top_3 = 3
    top_5 = 5
    top_10 = 10


class InventoryStatus(str, Enum):
    low_stock = "low_stock"
    high_stock = "high_stock"


# --- Pydantic Models ---
class OrderCountDetail(BaseModel):
    ky_bao_cao: date
    so_luong_don_hang: int


class BestSellingProductOut(BaseModel):
    id_san_pham: int
    ten_san_pham: str
    ma_san_pham: str
    tong_so_luong_ban: int
    tong_doanh_thu: Decimal

    class Config:
        from_attributes = True


class InventoryReportOut(BaseModel):
    id_san_pham: int
    ten_san_pham: str
    ma_san_pham: str
    so_luong_ton_kho: int
    ten_danh_muc: str

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.get("/order-count", response_model=List[OrderCountDetail], summary="Lấy báo cáo số lượng đơn hàng đã bán")
def get_order_count_report(
        period: ReportPeriod = Query(..., description="Kỳ báo cáo"),
        start_date: Optional[date] = Query(None, description="Ngày bắt đầu cho kỳ 'custom'"),
        end_date: Optional[date] = Query(None, description="Ngày kết thúc cho kỳ 'custom'")
):
    """
    Tạo báo cáo thống kê số lượng đơn hàng đã 'Hoàn tất' theo từng ngày.
    """
    report = stats_ops.get_order_count_report(
        period.value,
        start_date.isoformat() if start_date else None,
        end_date.isoformat() if end_date else None
    )
    if report is None:
        raise HTTPException(status_code=400, detail="Không thể tạo báo cáo.")
    return report


@router.get("/best-selling-products", response_model=List[BestSellingProductOut],
            summary="Lấy báo cáo sản phẩm bán chạy nhất")
def get_best_selling_products_report(
        period: ReportPeriod = Query(..., description="Kỳ báo cáo"),
        sort_by: BestSellingSortBy = Query(...,
                                           description="Sắp xếp theo 'quantity' (số lượng) hoặc 'revenue' (doanh thu)"),
        top_n: TopN = Query(..., description="Số lượng sản phẩm top cần lấy (3, 5, hoặc 10)"),
        start_date: Optional[date] = Query(None, description="Ngày bắt đầu cho kỳ 'custom'"),
        end_date: Optional[date] = Query(None, description="Ngày kết thúc cho kỳ 'custom'")
):
    """
    Tạo báo cáo về các sản phẩm bán chạy nhất trong một khoảng thời gian.
    """
    report = stats_ops.get_best_selling_products_report(
        period.value,
        sort_by.value,
        top_n.value,
        start_date.isoformat() if start_date else None,
        end_date.isoformat() if end_date else None
    )
    if report is None:
        raise HTTPException(status_code=400, detail="Không thể tạo báo cáo.")
    return report


@router.get("/inventory-status", response_model=List[InventoryReportOut], summary="Lấy báo cáo tình trạng tồn kho")
def get_inventory_report(
        status: InventoryStatus = Query(...,
                                        description="Trạng thái tồn kho cần xem: 'low_stock' (<10) hoặc 'high_stock' (>100)"),
        category_id: Optional[int] = Query(None, description="Lọc theo một ID danh mục cụ thể")
):
    """
    Tạo báo cáo về các sản phẩm có tồn kho thấp (<10) hoặc tồn kho cao (>100).
    """
    report = stats_ops.get_inventory_report(status.value, category_id)
    if report is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ khi tạo báo cáo tồn kho.")
    return report
