# be/routers/routers_4_khachhang.py

from fastapi import APIRouter, HTTPException, status, Response, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
from datetime import date, datetime

# Import các hàm nghiệp vụ
from be.operation import operation_4_khachhang as kh_ops

# Khởi tạo router mới
router = APIRouter(
    prefix="/customers",
    tags=["Khách hàng"],
)

# Định nghĩa các giá trị cho giới tính để validation
Gender = Literal['Nam', 'Nữ', 'Khác']


# --- Pydantic Models ---
class CustomerBase(BaseModel):
    ten_khach_hang: str = Field(..., max_length=255)
    so_dien_thoai: str = Field(..., max_length=20)
    email: EmailStr
    dia_chi: Optional[str] = None
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[Gender] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    ten_khach_hang: Optional[str] = Field(None, max_length=255)
    so_dien_thoai: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    dia_chi: Optional[str] = None
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[Gender] = None


class CustomerOut(CustomerBase):
    id: int
    so_lan_mua_hang: int
    ngay_tao_ban_ghi: datetime

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED, summary="Tạo khách hàng mới")
def create_customer(customer: CustomerCreate):
    """
    Tạo một khách hàng mới.
    - **email**: Phải là một địa chỉ email hợp lệ.
    - **so_dien_thoai**: Số điện thoại, thường là duy nhất.
    """
    new_id = kh_ops.add_khachhang(**customer.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400, detail="Không thể tạo khách hàng. Email hoặc SĐT có thể đã tồn tại.")
    created_customer = kh_ops.get_khachhang_by_id(new_id)
    return created_customer


@router.get("/", response_model=List[CustomerOut], summary="Lấy danh sách khách hàng và tìm kiếm")
def get_customers(
        name: Optional[str] = Query(None, description="Tìm theo tên khách hàng"),
        phone: Optional[str] = Query(None, description="Tìm theo số điện thoại"),
        email: Optional[str] = Query(None, description="Tìm theo email")
):
    """
    Lấy danh sách khách hàng. Có thể tìm kiếm theo tên, SĐT, hoặc email.
    """
    customers = kh_ops.get_khachhang(name_filter=name, phone_filter=phone, email_filter=email)
    if customers is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ khi truy vấn khách hàng.")
    return customers


@router.get("/{customer_id}", response_model=CustomerOut, summary="Lấy thông tin một khách hàng")
def get_customer_by_id(customer_id: int):
    """
    Lấy thông tin chi tiết của một khách hàng theo ID.
    """
    customer = kh_ops.get_khachhang_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy khách hàng với ID {customer_id}")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut, summary="Cập nhật thông tin khách hàng")
def update_customer(customer_id: int, customer_update: CustomerUpdate):
    """
    Cập nhật thông tin cho một khách hàng đã tồn tại.
    """
    update_data = customer_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu nào được cung cấp để cập nhật.")

    success = kh_ops.update_khachhang(customer_id, **update_data)
    if not success:
        raise HTTPException(status_code=404,
                            detail=f"Không tìm thấy khách hàng ID {customer_id} hoặc cập nhật thất bại.")

    return kh_ops.get_khachhang_by_id(customer_id)
