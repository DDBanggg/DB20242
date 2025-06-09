# be/routers/routers_12_phantichkhachhang.py

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from enum import Enum

# Import các hàm nghiệp vụ
from be.reports import operation_12_phantichkhachhang as customer_ops

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


class TopN(int, Enum):
    top_3 = 3
    top_5 = 5
    top_10 = 10


# --- Pydantic Models ---
class CustomerAcquisitionDetail(BaseModel):
    ky_bao_cao: date
    so_khach_hang_moi: int
    so_khach_hang_quay_lai: int


class CustomerAcquisitionSummary(BaseModel):
    so_khach_hang_moi: int
    so_khach_hang_quay_lai: int


class CustomerAcquisitionReportOut(BaseModel):
    summary: CustomerAcquisitionSummary
    details: List[CustomerAcquisitionDetail]


class TopSpenderOut(BaseModel):
    id_khach_hang: int
    ten_khach_hang: str
    tong_chi_tieu: Decimal
    tong_so_don_hang: int
    ngay_mua_cuoi_cung: date

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.get("/customer-acquisition", response_model=CustomerAcquisitionReportOut,
            summary="Lấy báo cáo khách hàng mới/quay lại")
def get_customer_acquisition_report(
        period: ReportPeriod = Query(..., description="Kỳ báo cáo"),
        start_date: Optional[date] = Query(None, description="Ngày bắt đầu cho kỳ 'custom'"),
        end_date: Optional[date] = Query(None, description="Ngày kết thúc cho kỳ 'custom'")
):
    """
    Tạo báo cáo phân tích khách hàng mới và khách hàng quay lại.
    - **Khách hàng mới**: Là những người có đơn hàng 'Hoàn tất' đầu tiên trong kỳ báo cáo.
    - **Khách hàng quay lại**: Là những người có đơn hàng 'Hoàn tất' trong kỳ nhưng đã có đơn hàng hoàn tất trước đó.
    """
    report = customer_ops.get_customer_acquisition_report(
        period.value,
        start_date.isoformat() if start_date else None,
        end_date.isoformat() if end_date else None
    )
    if report is None:
        raise HTTPException(status_code=400, detail="Không thể tạo báo cáo.")

    # Đảm bảo summary không rỗng
    if not report.get("summary"):
        report["summary"] = {"so_khach_hang_moi": 0, "so_khach_hang_quay_lai": 0}

    return report


@router.get("/top-spending-customers", response_model=List[TopSpenderOut],
            summary="Lấy báo cáo top khách hàng chi tiêu")
def get_top_spending_customers_report(
        period: ReportPeriod = Query(..., description="Kỳ báo cáo"),
        top_n: TopN = Query(..., description="Số lượng khách hàng top cần lấy (3, 5, hoặc 10)"),
        start_date: Optional[date] = Query(None, description="Ngày bắt đầu cho kỳ 'custom'"),
        end_date: Optional[date] = Query(None, description="Ngày kết thúc cho kỳ 'custom'")
):
    """
    Tạo báo cáo về các khách hàng có tổng chi tiêu cao nhất trong một khoảng thời gian.
    """
    report = customer_ops.get_top_spending_customers_report(
        period.value,
        top_n.value,
        start_date.isoformat() if start_date else None,
        end_date.isoformat() if end_date else None
    )
    if report is None:
        raise HTTPException(status_code=400, detail="Không thể tạo báo cáo.")
    return report
