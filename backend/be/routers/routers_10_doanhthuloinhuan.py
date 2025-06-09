# be/routers/routers_10_doanhthuloinhuan.py

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from enum import Enum

# Import các hàm nghiệp vụ
from be.reports import operation_10_doanhthuloinhuan as report_ops

# Khởi tạo router mới
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


# --- Pydantic Models ---
class FinancialReportDetail(BaseModel):
    ky_bao_cao: date
    tong_doanh_thu: Decimal
    loi_nhuan: Decimal


class FinancialReportSummary(BaseModel):
    ky_bao_cao: str
    tong_doanh_thu: Decimal
    loi_nhuan: Decimal


class FinancialReportOut(BaseModel):
    summary: FinancialReportSummary
    details: List[FinancialReportDetail]


# --- API Endpoint ---

@router.get("/financial", response_model=FinancialReportOut, summary="Lấy báo cáo doanh thu và lợi nhuận")
def get_financial_report(
        period: ReportPeriod = Query(..., description="Kỳ báo cáo: 'yesterday', 'last_week', 'last_month', 'custom'"),
        start_date: Optional[date] = Query(None, description="Ngày bắt đầu cho kỳ 'custom' (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="Ngày kết thúc cho kỳ 'custom' (YYYY-MM-DD)")
):
    """
    Tạo báo cáo tài chính tổng hợp về doanh thu và lợi nhuận.
    - **period**: Chọn một kỳ báo cáo được định sẵn.
    - **start_date / end_date**: Bắt buộc nếu `period` là `custom`.
    """
    start_date_str = start_date.isoformat() if start_date else None
    end_date_str = end_date.isoformat() if end_date else None

    report = report_ops.get_financial_report(
        period=period.value,
        start_date_str=start_date_str,
        end_date_str=end_date_str
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tạo báo cáo. Vui lòng kiểm tra lại các tham số."
        )

    # Đảm bảo summary không rỗng
    if not report.get("summary"):
        report["summary"] = {
            "ky_bao_cao": "Không có dữ liệu",
            "tong_doanh_thu": 0,
            "loi_nhuan": 0
        }

    return report
