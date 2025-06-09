# be/routers/routers_8_chiphi.py

from fastapi import APIRouter, HTTPException, status, Query, Response
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

# Import các hàm nghiệp vụ
from be.operation import operation_8_chiphi as cp_ops

# Khởi tạo router mới
router = APIRouter(
    prefix="/expenses",
    tags=["Chi phí"],
)


# --- Pydantic Models ---
class ExpenseBase(BaseModel):
    loai_chi_phi: str = Field(..., max_length=255)
    so_tien: Decimal = Field(..., gt=0)
    ngay_chi_phi: date
    mo_ta: Optional[str] = None
    id_nhan_vien: Optional[int] = Field(None, gt=0)


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    loai_chi_phi: Optional[str] = Field(None, max_length=255)
    so_tien: Optional[Decimal] = Field(None, gt=0)
    ngay_chi_phi: Optional[date] = None
    mo_ta: Optional[str] = None
    id_nhan_vien: Optional[int] = Field(None, gt=0)


class ExpenseOut(ExpenseBase):
    id: int
    ten_nhan_vien: Optional[str] = None
    ngay_tao_ban_ghi: datetime

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED, summary="Tạo một khoản chi phí mới")
def create_expense(expense: ExpenseCreate):
    """
    Tạo một khoản chi phí mới.
    """
    expense_data = expense.model_dump()
    expense_data['ngay_chi_phi_str'] = expense_data.pop('ngay_chi_phi').isoformat()

    new_id = cp_ops.add_chiphi(**expense_data)
    if new_id is None:
        raise HTTPException(status_code=400, detail="Không thể tạo chi phí. Dữ liệu có thể không hợp lệ.")
    created_expense = cp_ops.get_chiphi_by_id(new_id)
    return created_expense


@router.get("/", response_model=List[ExpenseOut], summary="Lấy danh sách chi phí")
def get_expenses(
        type_filter: Optional[str] = Query(None, description="Tìm theo loại chi phí"),
        date_from: Optional[date] = Query(None, description="Lọc chi phí từ ngày (YYYY-MM-DD)"),
        date_to: Optional[date] = Query(None, description="Lọc chi phí đến ngày (YYYY-MM-DD)")
):
    """
    Lấy danh sách tất cả các khoản chi phí, có thể lọc theo loại và khoảng ngày.
    """
    date_from_str = date_from.isoformat() if date_from else None
    date_to_str = date_to.isoformat() if date_to else None

    expenses = cp_ops.get_chiphi(loai_filter=type_filter, date_from_str=date_from_str, date_to_str=date_to_str)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ khi truy vấn chi phí.")
    return expenses


@router.get("/{expense_id}", response_model=ExpenseOut, summary="Lấy thông tin một khoản chi phí")
def get_expense_by_id(expense_id: int):
    """
    Lấy thông tin chi tiết của một khoản chi phí theo ID.
    """
    expense = cp_ops.get_chiphi_by_id(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chi phí với ID {expense_id}")
    return expense


@router.put("/{expense_id}", response_model=ExpenseOut, summary="Cập nhật một khoản chi phí")
def update_expense(expense_id: int, expense_update: ExpenseUpdate):
    """
    Cập nhật thông tin cho một khoản chi phí đã tồn tại.
    """
    update_data = expense_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu nào được cung cấp để cập nhật.")

    success = cp_ops.update_chiphi(expense_id, **update_data)
    if not success:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chi phí ID {expense_id} hoặc cập nhật thất bại.")

    return cp_ops.get_chiphi_by_id(expense_id)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa một khoản chi phí")
def delete_expense(expense_id: int):
    """
    Xóa một khoản chi phí khỏi hệ thống.
    """
    success = cp_ops.delete_chiphi(expense_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chi phí ID {expense_id} để xóa.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
