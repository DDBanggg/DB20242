# backend/be/routers/routers_10_doanhthuloinhuan.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import be.reports.operation_10_doanhthuloinhuan as operation_10

router = APIRouter(
    prefix="/baocao/taichinh",
    tags=["Báo cáo Tài chính (Doanh thu & Lợi nhuận)"]
)

@router.get("/", description="Lấy báo cáo tài chính (Doanh thu, Lợi nhuận ròng, Chi phí, Thuế)")
def get_financial_report(
    period: str = Query(..., description="Kỳ báo cáo. Các giá trị hợp lệ: 'yesterday', 'last_week', 'last_month', 'custom'"),
    start_date: Optional[str] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD). Chỉ dùng khi period='custom'."),
    end_date: Optional[str] = Query(None, description="Ngày kết thúc (YYYY-MM-DD). Chỉ dùng khi period='custom'.")
) -> Dict[str, Any]:
    """
    API trả về báo cáo tài chính.
    
    Lưu ý:
    - **Lợi nhuận** trả về ở đây là lợi nhuận ròng (đã trừ giá vốn FIFO, chi phí vận hành và các loại thuế VAT/HKD).
    - Không sử dụng 'response_model' cứng để đảm bảo các trường dữ liệu tính toán động (dynamic) được trả về đầy đủ.
    """
    
    # Gọi hàm operation để lấy số liệu (đã bao gồm logic trừ thuế 11.5%)
    report_data = operation_10.get_financial_report(period, start_date, end_date)
    
    if report_data is None:
        raise HTTPException(
            status_code=400, 
            detail="Không thể tạo báo cáo. Vui lòng kiểm tra lại tham số ngày tháng (start_date <= end_date) hoặc định dạng ngày (YYYY-MM-DD)."
        )
        
    return report_data