from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..db_connection import execute_query

router = APIRouter()

@router.get("/san-pham/danh-sach")
async def get_danh_sach_san_pham(tu_khoa: Optional[str] = None):
    """
    Lấy danh sách sản phẩm cho POS.
    - JOIN ngầm với bảng LichSuGiaNiemYet để lấy giá bán hiện tại.
    - Tìm kiếm theo Tên hoặc Mã sản phẩm.
    - Cảnh báo nếu tồn kho <= 5.
    """
    try:
        # Câu query thông minh: Lấy thông tin SP + Giá hiệu lực mới nhất
        sql = """
            SELECT 
                sp.id, 
                sp.ma_san_pham, 
                sp.ten_san_pham, 
                sp.don_vi_tinh, 
                sp.so_luong_ton_kho,
                sp.duong_dan_hinh_anh_chinh,
                -- Subquery: Lấy giá niêm yết mới nhất có hiệu lực tính đến hôm nay
                COALESCE(
                    (SELECT gia_niem_yet 
                     FROM LichSuGiaNiemYet ls 
                     WHERE ls.id_san_pham = sp.id 
                       AND ls.ngay_ap_dung <= CURRENT_DATE 
                     ORDER BY ls.ngay_ap_dung DESC 
                     LIMIT 1), 
                    0
                ) as gia_ban_hien_tai
            FROM SanPham sp
            WHERE sp.trang_thai IN ('Đang kinh doanh - Còn hàng', 'Đang kinh doanh - Hết hàng')
        """
        
        params = []
        if tu_khoa:
            # Tìm kiếm cả Mã SP và Tên SP (ILIKE không phân biệt hoa thường)
            sql += " AND (sp.ten_san_pham ILIKE %s OR sp.ma_san_pham ILIKE %s)"
            search_term = f"%{tu_khoa}%"
            params.extend([search_term, search_term])
            
        sql += " ORDER BY sp.id DESC"
        
        # Thực thi query
        products = execute_query(sql, tuple(params) if params else None)
        
        # --- LOGIC XỬ LÝ PYTHON (Cảnh báo tồn kho) ---
        NGUONG_CANH_BAO = 5
        
        for p in products:
            # Xử lý tồn kho
            ton_kho = p.get('so_luong_ton_kho') or 0
            
            # Gắn cờ cảnh báo
            if ton_kho <= NGUONG_CANH_BAO:
                p['canh_bao'] = True
                p['trang_thai_kho'] = 'Sắp hết hàng'
            else:
                p['canh_bao'] = False
                p['trang_thai_kho'] = 'Còn hàng'
                
            # Ép kiểu giá về float cho Frontend dễ tính toán
            p['gia_ban_hien_tai'] = float(p.get('gia_ban_hien_tai') or 0)

        return {
            "status": "success",
            "count": len(products),
            "data": products
        }

    except Exception as e:
        print(f"Lỗi lấy danh sách sản phẩm: {e}")
        raise HTTPException(status_code=500, detail=str(e))