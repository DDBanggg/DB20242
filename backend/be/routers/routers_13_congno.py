# be/routers/routers_13_congno.py

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

# Import các hàm nghiệp vụ
from be.reports import operation_13_congno as receivables_ops

# Khởi tạo router mới, gộp chung vào tag "Báo cáo"
router = APIRouter(
    prefix="/reports",
    tags=["Báo cáo"],
)


# --- Pydantic Models ---
class ReceivablesSummaryOut(BaseModel):
    tong_cong_no_phai_thu: Decimal
    tong_cong_no_qua_han: Decimal


class ReceivablesDetailOut(BaseModel):
    id_khach_hang: int
    ten_khach_hang: str
    tong_cong_no: Decimal
    cong_no_qua_han: Decimal


class ReceivablesReportOut(BaseModel):
    summary: ReceivablesSummaryOut
    details: List[ReceivablesDetailOut]


# --- API Endpoint ---

@router.get("/receivables", response_model=ReceivablesReportOut, summary="Lấy báo cáo công nợ phải thu")
def get_receivables_report(
        overdue_only: bool = Query(False, description="Nếu True, chỉ hiển thị chi tiết các khách hàng có nợ quá hạn")
):
    """
    Tạo báo cáo về công nợ phải thu từ khách hàng.
    - **Công nợ**: Được tính từ các đơn hàng có trạng thái 'Đã giao' hoặc 'Hoàn tất' nhưng 'Chưa thanh toán'.
    - **Nợ quá hạn**: Các khoản nợ có ngày giao hàng thực tế đã qua hơn 30 ngày.
    """
    report = receivables_ops.get_receivables_report(overdue_only=overdue_only)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo báo cáo công nợ."
        )

    # Đảm bảo summary không rỗng
    if not report.get("summary"):
        report["summary"] = {"tong_cong_no_phai_thu": 0, "tong_cong_no_qua_han": 0}

    return report
