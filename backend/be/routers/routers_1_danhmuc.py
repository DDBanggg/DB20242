# be/routers/routers_1_danhmuc.py

from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Import các hàm nghiệp vụ từ module operation
from be.operation import operation_1_danhmuc as dm_ops

# Khởi tạo một router mới.
router = APIRouter(
    prefix="/categories",
    tags=["Danh mục"],
)


# --- Pydantic Models ---
# Model cho dữ liệu đầu vào khi tạo danh mục
class CategoryCreate(BaseModel):
    ma_danh_muc: str = Field(..., max_length=10, description="Mã danh mục (duy nhất, <= 10 ký tự)")
    ten_danh_muc: str = Field(..., max_length=100, description="Tên danh mục (duy nhất)")
    mo_ta: Optional[str] = None


# Model cho dữ liệu đầu vào khi cập nhật (tất cả các trường đều không bắt buộc)
class CategoryUpdate(BaseModel):
    ma_danh_muc: Optional[str] = Field(None, max_length=10)
    ten_danh_muc: Optional[str] = Field(None, max_length=100)
    mo_ta: Optional[str] = None


# Model cho dữ liệu đầu ra
class CategoryOut(BaseModel):
    id: int
    ma_danh_muc: str
    ten_danh_muc: str
    mo_ta: Optional[str] = None
    ngay_tao: datetime

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED,
             summary="Tạo một danh mục mới")
def create_category(category: CategoryCreate):
    """
    Tạo một danh mục sản phẩm mới.
    - **ma_danh_muc**: Mã danh mục, phải là duy nhất và không quá 10 ký tự.
    - **ten_danh_muc**: Tên danh mục, phải là duy nhất.
    """
    new_id = dm_ops.add_danhmuc(category.ma_danh_muc, category.ten_danh_muc, category.mo_ta)
    if new_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tạo danh mục. Mã hoặc tên danh mục có thể đã tồn tại."
        )
    # Lấy lại thông tin đầy đủ của danh mục vừa tạo để trả về
    created_category = dm_ops.get_danhmuc_by_id(new_id)
    return created_category


@router.get("/", response_model=List[CategoryOut], summary="Lấy danh sách tất cả danh mục")
def get_all_categories():
    """
    Trả về một danh sách tất cả các danh mục có trong hệ thống,
    sắp xếp theo mã danh mục.
    """
    categories = dm_ops.get_all_danhmuc()
    if categories is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ khi truy vấn danh mục.")
    return categories


@router.put("/{category_id}", response_model=CategoryOut, summary="Cập nhật thông tin danh mục")
def update_category(category_id: int, category_update: CategoryUpdate):
    """
    Cập nhật thông tin cho một danh mục đã tồn tại.
    Chỉ những trường được cung cấp trong body của request mới được cập nhật.
    """
    # Chuyển model thành dict, loại bỏ các giá trị None để không cập nhật chúng
    update_data = category_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không có dữ liệu nào được cung cấp để cập nhật."
        )

    success = dm_ops.update_danhmuc(category_id, **update_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy danh mục với ID {category_id} hoặc cập nhật thất bại (dữ liệu có thể bị trùng lặp)."
        )

    updated_category = dm_ops.get_danhmuc_by_id(category_id)
    return updated_category




