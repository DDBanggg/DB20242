from fastapi import APIRouter, HTTPException
from ..db_connection import execute_query

router = APIRouter()

@router.get("/bao-cao/hom-nay")
async def get_bao_cao_nhanh_hom_nay():
    """
    Báo cáo nhanh Doanh thu & Lợi nhuận trong ngày (Hôm nay).
    Logic:
    - Lọc đơn hàng có ngày tạo = Hôm nay (CURRENT_DATE).
    - Trạng thái = 'Hoàn tất'.
    - Doanh thu = SUM(ChiTiet.tong_gia_ban).
    - Lợi nhuận gộp = Doanh thu - SUM(ChiTiet.tong_gia_von).
    """
    try:
        # Query tính toán trực tiếp từ DB để đảm bảo tốc độ
        sql = """
            SELECT
                COUNT(DISTINCT dh.id) as so_don_hang,
                COALESCE(SUM(ct.tong_gia_ban), 0) as doanh_thu,
                COALESCE(SUM(ct.tong_gia_von), 0) as tong_gia_von
            FROM DonHangBan dh
            JOIN ChiTietDonHangBan ct ON dh.id = ct.id_don_hang_ban
            WHERE DATE(dh.ngay_dat_hang) = CURRENT_DATE
              AND dh.trang_thai_don_hang = 'Hoàn tất'
        """

        result = execute_query(sql)
        data = result[0] if result else {}

        # Xử lý số liệu
        doanh_thu = float(data.get('doanh_thu', 0))
        gia_von = float(data.get('tong_gia_von', 0))
        loi_nhuan = doanh_thu - gia_von
        so_don = data.get('so_don_hang', 0)

        return {
            "status": "success",
            "date": "Hôm nay",
            "data": {
                "so_don_hang": so_don,
                "doanh_thu": doanh_thu,
                "loi_nhuan": loi_nhuan,
                "ty_suat_loi_nhuan": round((loi_nhuan/doanh_thu * 100), 1) if doanh_thu > 0 else 0
            }
        }

    except Exception as e:
        print(f"Lỗi báo cáo: {e}")
        raise HTTPException(status_code=500, detail=str(e))