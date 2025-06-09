# be/routers/routers_3_nhacungcap.py

from fastapi import APIRouter, HTTPException, status, Response, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# Import các hàm nghiệp vụ
from be.operation import operation_3_nhacungcap as ncc_ops

# Khởi tạo router mới
router = APIRouter(
    prefix="/suppliers",
    tags=["Nhà cung cấp"],
)


# --- Pydantic Models ---
class SupplierBase(BaseModel):
    ten_nha_cung_cap: str = Field(..., max_length=255)
    email: EmailStr
    dia_chi: str
    ma_so_thue: Optional[str] = Field(None, max_length=20)
    so_dien_thoai: Optional[str] = Field(None, max_length=20)
    nguoi_lien_he_chinh: Optional[str] = Field(None, max_length=100)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    ten_nha_cung_cap: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    dia_chi: Optional[str] = None
    ma_so_thue: Optional[str] = Field(None, max_length=20)
    so_dien_thoai: Optional[str] = Field(None, max_length=20)
    nguoi_lien_he_chinh: Optional[str] = Field(None, max_length=100)


class SupplierOut(SupplierBase):
    id: int
    ngay_tao_ban_ghi: datetime

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.post("/", response_model=SupplierOut, status_code=status.HTTP_201_CREATED, summary="Tạo nhà cung cấp mới")
def create_supplier(supplier: SupplierCreate):
    """
    Tạo một nhà cung cấp mới.
    - **email**: Phải là một địa chỉ email hợp lệ.
    - **ten_nha_cung_cap**: Tên nhà cung cấp, thường là duy nhất.
    """
    new_id = ncc_ops.add_nhacungcap(**supplier.model_dump())
    if new_id is None:
        raise HTTPException(status_code=400,
                            detail="Không thể tạo nhà cung cấp. Dữ liệu có thể không hợp lệ hoặc bị trùng.")
    created_supplier = ncc_ops.get_nhacungcap_by_id(new_id)
    return created_supplier


@router.get("/", response_model=List[SupplierOut], summary="Lấy danh sách nhà cung cấp và tìm kiếm")
def get_suppliers(
        name: Optional[str] = Query(None, description="Tìm theo tên nhà cung cấp"),
        phone: Optional[str] = Query(None, description="Tìm theo số điện thoại"),
        email: Optional[str] = Query(None, description="Tìm theo email")
):
    """
    Lấy danh sách nhà cung cấp. Có thể tìm kiếm theo tên, SĐT, hoặc email.
    """
    suppliers = ncc_ops.get_nhacungcap(name_filter=name, phone_filter=phone, email_filter=email)
    if suppliers is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ khi truy vấn nhà cung cấp.")
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierOut, summary="Lấy thông tin một nhà cung cấp")
def get_supplier_by_id(supplier_id: int):
    """
    Lấy thông tin chi tiết của một nhà cung cấp theo ID.
    """
    supplier = ncc_ops.get_nhacungcap_by_id(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy nhà cung cấp với ID {supplier_id}")
    return supplier


@router.put("/{supplier_id}", response_model=SupplierOut, summary="Cập nhật thông tin nhà cung cấp")
def update_supplier(supplier_id: int, supplier_update: SupplierUpdate):
    """
    Cập nhật thông tin cho một nhà cung cấp đã tồn tại.
    """
    update_data = supplier_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu nào được cung cấp để cập nhật.")

    success = ncc_ops.update_nhacungcap(supplier_id, **update_data)
    if not success:
        raise HTTPException(status_code=404,
                            detail=f"Không tìm thấy nhà cung cấp ID {supplier_id} hoặc cập nhật thất bại.")

    return ncc_ops.get_nhacungcap_by_id(supplier_id)

