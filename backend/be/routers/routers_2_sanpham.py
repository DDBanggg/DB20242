# be/routers/routers_2_sanpham.py

from fastapi import APIRouter, HTTPException, status, Response, Query
from pydantic import BaseModel, Field
from typing import List, Optional

# Import các hàm nghiệp vụ từ module operation
from be.operation import operation_2_sanpham as sp_ops

# Khởi tạo một router mới
router = APIRouter(
    prefix="/products",
    tags=["Sản phẩm"],
)


# --- Pydantic Models ---
# Model cho dữ liệu đầu vào khi tạo sản phẩm
class ProductCreate(BaseModel):
    ma_san_pham: str = Field(..., max_length=20, description="Mã sản phẩm (duy nhất)")
    ten_san_pham: str = Field(..., max_length=255, description="Tên sản phẩm (duy nhất)")
    id_danh_muc: int = Field(..., gt=0, description="ID của danh mục sản phẩm")
    so_luong_ton_kho: int = Field(0, ge=0, description="Số lượng tồn kho ban đầu")
    don_vi_tinh: str = Field(..., max_length=50, description="Đơn vị tính (Cái, Hộp, v.v.)")
    mo_ta_chi_tiet: Optional[str] = None
    duong_dan_hinh_anh_chinh: Optional[str] = None
    trang_thai: Optional[str] = 'Đang kinh doanh - Còn hàng'


# Model cho dữ liệu đầu vào khi cập nhật thông tin cơ bản
class ProductInfoUpdate(BaseModel):
    ma_san_pham: Optional[str] = Field(None, max_length=20)
    ten_san_pham: Optional[str] = Field(None, max_length=255)
    id_danh_muc: Optional[int] = Field(None, gt=0)
    don_vi_tinh: Optional[str] = Field(None, max_length=50)
    mo_ta_chi_tiet: Optional[str] = None


# Model cho dữ liệu đầu vào khi cập nhật trạng thái
class ProductStatusUpdate(BaseModel):
    trang_thai: str = Field(..., description="Trạng thái mới của sản phẩm")


# Model cho dữ liệu đầu ra, có thêm tên danh mục
class ProductOut(BaseModel):
    id: int
    ma_san_pham: str
    ten_san_pham: str
    id_danh_muc: int
    so_luong_ton_kho: int
    don_vi_tinh: str
    mo_ta_chi_tiet: Optional[str] = None
    duong_dan_hinh_anh_chinh: Optional[str] = None
    trang_thai: str
    ten_danh_muc: str

    class Config:
        from_attributes = True


# --- Hàm helper để lấy sản phẩm và kiểm tra ---
def get_product_or_404(product_id: int):
    # (Hàm get_sanpham_by_id cần được thêm vào file operation của bạn)
    # Giả định bạn sẽ thêm hàm này:
    # product = sp_ops.get_sanpham_by_id(product_id)
    # Tạm thời, chúng ta sẽ tìm trong danh sách đầy đủ
    all_products = sp_ops.get_all_sanpham_with_danhmuc()
    product = next((p for p in all_products if p['id'] == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Không tìm thấy sản phẩm với ID {product_id}")
    return product


# --- API Endpoints ---

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="Tạo một sản phẩm mới")
def create_product(product: ProductCreate):
    """
    Tạo một sản phẩm mới trong cơ sở dữ liệu.
    """
    new_id = sp_ops.add_sanpham(**product.model_dump())
    if new_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tạo sản phẩm. Mã, tên sản phẩm hoặc ID danh mục không hợp lệ/đã tồn tại."
        )
    return get_product_or_404(new_id)


@router.get("/", response_model=List[ProductOut], summary="Lấy danh sách sản phẩm và lọc")
def get_products(
        category_id: Optional[int] = Query(None, description="Lọc sản phẩm theo ID danh mục"),
        name_search: Optional[str] = Query(None, description="Tìm kiếm sản phẩm theo tên"),
        low_stock_threshold: Optional[int] = Query(None, description="Lọc sản phẩm có tồn kho <= ngưỡng này")
):
    """
    Lấy danh sách sản phẩm với các bộ lọc tùy chọn.
    - Nếu không có tham số nào, trả về tất cả sản phẩm.
    - Các bộ lọc có thể được kết hợp.
    """
    if category_id:
        products = sp_ops.filter_sanpham_by_danhmuc(category_id)
    elif name_search:
        products = sp_ops.search_sanpham_by_name(name_search)
    elif low_stock_threshold is not None:
        products = sp_ops.get_low_stock_sanpham(low_stock_threshold)
    else:
        products = sp_ops.get_all_sanpham_with_danhmuc()

    if products is None:
        raise HTTPException(status_code=500, detail="Lỗi máy chủ nội bộ khi truy vấn sản phẩm.")
    return products


@router.get("/{product_id}", response_model=ProductOut, summary="Lấy thông tin một sản phẩm theo ID")
def get_product_by_id(product_id: int):
    """
    Lấy thông tin chi tiết của một sản phẩm dựa trên ID của nó.
    """
    return get_product_or_404(product_id)


@router.put("/{product_id}", response_model=ProductOut, summary="Cập nhật thông tin cơ bản của sản phẩm")
def update_product_info(product_id: int, product_update: ProductInfoUpdate):
    """
    Cập nhật các thông tin mô tả của một sản phẩm.
    Tồn kho và trạng thái kinh doanh không được cập nhật qua endpoint này.
    """
    update_data = product_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không có dữ liệu nào để cập nhật.")

    success = sp_ops.update_sanpham_info(product_id, **update_data)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Không tìm thấy sản phẩm ID {product_id} hoặc cập nhật thất bại.")

    return get_product_or_404(product_id)


@router.patch("/{product_id}/status", response_model=ProductOut, summary="Cập nhật trạng thái sản phẩm")
def update_product_status(product_id: int, status_update: ProductStatusUpdate):
    """
    Cập nhật trạng thái kinh doanh của một sản phẩm (ví dụ: 'Ngừng kinh doanh').
    """
    success = sp_ops.update_sanpham_status(product_id, status_update.trang_thai)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Không tìm thấy sản phẩm ID {product_id} hoặc trạng thái không hợp lệ.")

    return get_product_or_404(product_id)
