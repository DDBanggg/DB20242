# be/routers/routers_5_nhanvien.py

from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
from datetime import datetime

# Import các hàm nghiệp vụ
from be.operation import operation_5_nhanvien as nv_ops

# Khởi tạo router mới
router = APIRouter(
    prefix="/staff",
    tags=["Nhân viên"],
)

# --- Định nghĩa các giá trị Enum để validation ---
Role = Literal['Nhân viên', 'Quản lý']
Status = Literal['Đang làm việc', 'Đã nghỉ việc']


# --- Pydantic Models ---
class StaffBase(BaseModel):
    ten_nhan_vien: str = Field(..., max_length=255)
    ten_dang_nhap: str = Field(..., max_length=50)
    email: EmailStr
    so_dien_thoai: str = Field(..., max_length=20)
    vai_tro: Role = 'Nhân viên'
    trang_thai: Status = 'Đang làm việc'


class StaffCreate(StaffBase):
    mat_khau: str = Field(..., min_length=6, description="Mật khẩu của nhân viên")


class StaffUpdate(BaseModel):
    ten_nhan_vien: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    so_dien_thoai: Optional[str] = Field(None, max_length=20)
    vai_tro: Optional[Role] = None
    trang_thai: Optional[Status] = None
    mat_khau: Optional[str] = Field(None, min_length=6, description="Mật khẩu mới nếu muốn thay đổi")


class StaffOut(StaffBase):
    id: int
    ngay_tao_ban_ghi: datetime

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.post("/", response_model=StaffOut, status_code=status.HTTP_201_CREATED, summary="Tạo nhân viên mới")
def create_staff(staff: StaffCreate):
    """
    Tạo một nhân viên mới.
    - **ten_dang_nhap** và **email** phải là duy nhất.
    """
    new_id = nv_ops.add_nhanvien(**staff.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400,
                            detail="Không thể tạo nhân viên. Tên đăng nhập hoặc email có thể đã tồn tại.")
    created_staff = nv_ops.get_nhanvien_by_id(new_id)
    return created_staff


@router.get("/", response_model=List[StaffOut], summary="Lấy danh sách nhân viên")
def get_all_staff():
    """
    Lấy danh sách tất cả nhân viên trong hệ thống.
    """
    staff_list = nv_ops.get_all_nhanvien()
    if staff_list is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ khi truy vấn nhân viên.")
    return staff_list


@router.get("/{staff_id}", response_model=StaffOut, summary="Lấy thông tin một nhân viên")
def get_staff_by_id(staff_id: int):
    """
    Lấy thông tin chi tiết của một nhân viên theo ID.
    """
    staff = nv_ops.get_nhanvien_by_id(staff_id)
    if staff is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhân viên với ID {staff_id}")
    return staff


@router.put("/{staff_id}", response_model=StaffOut, summary="Cập nhật thông tin nhân viên")
def update_staff(staff_id: int, staff_update: StaffUpdate):
    """
    Cập nhật thông tin cho một nhân viên đã tồn tại.
    """
    update_data = staff_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu nào được cung cấp để cập nhật.")

    success = nv_ops.update_nhanvien(staff_id, **update_data)
    if not success:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhân viên ID {staff_id} hoặc cập nhật thất bại.")

    return nv_ops.get_nhanvien_by_id(staff_id)

