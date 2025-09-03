-- #####################################################################
-- # TỔNG HỢP TOÀN BỘ TRIGGER VÀ HÀM TRIGGER CỦA DỰ ÁN
-- #####################################################################


-- =====================================================================
-- SECTION 1: CÁC HÀM CHUNG VÀ TRIGGER CƠ BẢN
-- =====================================================================

-- 1.1. Hàm tự động cập nhật "ngay_cap_nhat_ban_ghi"
-- Mục đích: Ghi nhận lại thời điểm một bản ghi được sửa đổi.
CREATE OR REPLACE FUNCTION fn_cap_nhat_ngay_gio_sua()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ngay_cap_nhat_ban_ghi = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng DonHangNhap
CREATE TRIGGER trg_donhangnhap_cap_nhat_ngay_gio_sua
BEFORE UPDATE ON DonHangNhap
FOR EACH ROW
EXECUTE FUNCTION fn_cap_nhat_ngay_gio_sua();

-- Trigger áp dụng cho bảng DonHangBan
CREATE TRIGGER trg_donhangban_cap_nhat_ngay_gio_sua
BEFORE UPDATE ON DonHangBan
FOR EACH ROW
EXECUTE FUNCTION fn_cap_nhat_ngay_gio_sua();


-- 1.2. Hàm tự động cập nhật trạng thái Sản phẩm dựa trên tồn kho
-- Mục đích: Tự động đổi trạng thái sản phẩm sang "Còn hàng" hoặc "Hết hàng".
CREATE OR REPLACE FUNCTION func_cap_nhat_trang_thai_san_pham()
RETURNS TRIGGER AS $$
BEGIN
    -- Chỉ thay đổi trạng thái nếu sản phẩm không phải là "Ngừng kinh doanh"
    IF NEW.trang_thai != 'Ngừng kinh doanh' THEN
        IF NEW.so_luong_ton_kho > 0 THEN
            NEW.trang_thai = 'Đang kinh doanh - Còn hàng';
        ELSE
            NEW.trang_thai = 'Đang kinh doanh - Hết hàng';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng SanPham khi tồn kho thay đổi
CREATE TRIGGER trg_cap_nhat_trang_thai_san_pham
BEFORE UPDATE OF so_luong_ton_kho ON SanPham
FOR EACH ROW
EXECUTE FUNCTION func_cap_nhat_trang_thai_san_pham();


-- =====================================================================
-- SECTION 2: TRIGGER CHO NGHIỆP VỤ NHẬP HÀNG (DonHangNhap)
-- =====================================================================

-- 2.1. Hàm cập nhật tồn kho khi đơn hàng nhập hoàn tất
-- Mục đích: Tăng số lượng tồn kho của sản phẩm khi đơn nhập được xác nhận hoàn tất.
CREATE OR REPLACE FUNCTION func_cap_nhat_ton_kho_khi_nhap_hang()
RETURNS TRIGGER AS $$
BEGIN
    -- Chỉ thực thi khi trạng thái chuyển thành 'Hoàn tất'
    IF NEW.trang_thai = 'Hoàn tất' AND OLD.trang_thai IS DISTINCT FROM NEW.trang_thai THEN
        UPDATE SanPham sp
        SET so_luong_ton_kho = sp.so_luong_ton_kho + ctdhn.so_luong
        FROM ChiTietDonHangNhap ctdhn
        WHERE ctdhn.id_don_hang_nhap = NEW.id AND sp.id = ctdhn.id_san_pham;
        
        RAISE NOTICE 'Đã cập nhật số lượng tồn kho cho các sản phẩm của Đơn Hàng Nhập ID %.', NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng DonHangNhap
CREATE TRIGGER trg_after_update_donhangnhap_hoantat
AFTER UPDATE ON DonHangNhap
FOR EACH ROW
WHEN (OLD.trang_thai IS DISTINCT FROM NEW.trang_thai AND NEW.trang_thai = 'Hoàn tất')
EXECUTE FUNCTION func_cap_nhat_ton_kho_khi_nhap_hang();


-- 2.2. Hàm khởi tạo giá trị cho ChiTietDonHangNhap
-- Mục đích: Tự động gán so_luong_con_lai và tong_gia_nhap khi thêm mới chi tiết.
CREATE OR REPLACE FUNCTION func_khoi_tao_chitiet_nhap()
RETURNS TRIGGER AS $$
BEGIN
    -- Tự động gán so_luong_con_lai bằng so_luong
    NEW.so_luong_con_lai = NEW.so_luong;
    -- Tự động tính tong_gia_nhap
    NEW.tong_gia_nhap = NEW.gia_nhap_don_vi * NEW.so_luong;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng ChiTietDonHangNhap khi INSERT
CREATE TRIGGER trg_before_insert_chitietnhap
BEFORE INSERT ON ChiTietDonHangNhap
FOR EACH ROW
EXECUTE FUNCTION func_khoi_tao_chitiet_nhap();


-- =====================================================================
-- SECTION 3: TRIGGER CHO NGHIỆP VỤ BÁN HÀNG (DonHangBan)
-- =====================================================================

-- 3.1. Hàm cập nhật tồn kho khi đơn hàng bán hoàn tất
-- Mục đích: Giảm số lượng tồn kho của sản phẩm khi đơn bán được giao thành công.
CREATE OR REPLACE FUNCTION func_cap_nhat_ton_kho_khi_ban_hang()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trang_thai_don_hang = 'Hoàn tất' AND OLD.trang_thai_don_hang IS DISTINCT FROM NEW.trang_thai_don_hang THEN
        UPDATE SanPham sp
        SET so_luong_ton_kho = sp.so_luong_ton_kho - ctdhb.so_luong
        FROM ChiTietDonHangBan ctdhb
        WHERE ctdhb.id_don_hang_ban = NEW.id AND sp.id = ctdhb.id_san_pham;
        
        RAISE NOTICE 'Đã cập nhật số lượng tồn kho cho các sản phẩm của Đơn Hàng Bán ID %.', NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng DonHangBan
CREATE TRIGGER trg_after_update_donhangban_hoantat
AFTER UPDATE ON DonHangBan
FOR EACH ROW
WHEN (OLD.trang_thai_don_hang IS DISTINCT FROM NEW.trang_thai_don_hang AND NEW.trang_thai_don_hang = 'Hoàn tất')
EXECUTE FUNCTION func_cap_nhat_ton_kho_khi_ban_hang();


-- 3.2. Hàm cập nhật số lần mua hàng của Khách hàng
-- Mục đích: Tăng số lần mua hàng của khách hàng lên 1 khi họ có một đơn hàng hoàn tất.
CREATE OR REPLACE FUNCTION func_cap_nhat_so_lan_mua_hang()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trang_thai_don_hang = 'Hoàn tất' AND OLD.trang_thai_don_hang IS DISTINCT FROM NEW.trang_thai_don_hang THEN
        UPDATE KhachHang
        SET so_lan_mua_hang = so_lan_mua_hang + 1
        WHERE id = NEW.id_khach_hang;
        
        RAISE NOTICE 'Đã cập nhật số lần mua hàng cho khách hàng ID %.', NEW.id_khach_hang;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng DonHangBan
CREATE TRIGGER trg_after_update_so_lan_mua_hang
AFTER UPDATE ON DonHangBan
FOR EACH ROW
WHEN (OLD.trang_thai_don_hang IS DISTINCT FROM NEW.trang_thai_don_hang AND NEW.trang_thai_don_hang = 'Hoàn tất' AND NEW.id_khach_hang IS NOT NULL)
EXECUTE FUNCTION func_cap_nhat_so_lan_mua_hang();


-- 3.3. Hàm tính toán tự động cho ChiTietDonHangBan
-- Mục đích: Tính giá bán cuối cùng và tổng giá bán cho mỗi chi tiết.
CREATE OR REPLACE FUNCTION func_tinh_toan_chitiet_ban()
RETURNS TRIGGER AS $$
BEGIN
    -- Tính giá bán cuối cùng sau khi đã trừ giảm giá
    NEW.gia_ban_cuoi_cung_don_vi = NEW.gia_ban_niem_yet_don_vi * (1 - NEW.giam_gia);
    -- Tính tổng giá bán cho dòng chi tiết này
    NEW.tong_gia_ban = NEW.gia_ban_cuoi_cung_don_vi * NEW.so_luong;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng ChiTietDonHangBan
CREATE TRIGGER trg_before_insert_update_chitietban
BEFORE INSERT OR UPDATE ON ChiTietDonHangBan
FOR EACH ROW
EXECUTE FUNCTION func_tinh_toan_chitiet_ban();


-- 3.4. Hàm tính giá vốn hàng bán (FIFO)
-- Mục đích: Tính giá vốn cho mỗi sản phẩm được bán ra dựa trên các lô hàng nhập trước.
CREATE OR REPLACE FUNCTION func_tinh_tong_gia_von_ban_fifo()
RETURNS TRIGGER AS $$
DECLARE
    v_so_luong_can_xuat NUMERIC;
    v_tong_gia_von NUMERIC := 0;
    v_gia_nhap NUMERIC;
    v_sl_con_lai_trong_lo NUMERIC;
    v_sl_xuat_tu_lo_nay NUMERIC;
    rec RECORD;
BEGIN
    v_so_luong_can_xuat := NEW.so_luong;

    FOR rec IN (
        SELECT ctdhn.id, ctdhn.gia_nhap_don_vi, ctdhn.so_luong_con_lai
        FROM ChiTietDonHangNhap ctdhn
        JOIN DonHangNhap dhn ON ctdhn.id_don_hang_nhap = dhn.id
        WHERE ctdhn.id_san_pham = NEW.id_san_pham
          AND ctdhn.so_luong_con_lai > 0
          AND dhn.trang_thai = 'Hoàn tất'
        ORDER BY dhn.ngay_nhan_hang_thuc_te ASC, ctdhn.id ASC
    )
    LOOP
        IF v_so_luong_can_xuat <= 0 THEN
            EXIT;
        END IF;

        v_gia_nhap := rec.gia_nhap_don_vi;
        v_sl_con_lai_trong_lo := rec.so_luong_con_lai;

        IF v_so_luong_can_xuat <= v_sl_con_lai_trong_lo THEN
            v_sl_xuat_tu_lo_nay := v_so_luong_can_xuat;
            v_tong_gia_von := v_tong_gia_von + (v_sl_xuat_tu_lo_nay * v_gia_nhap);
            UPDATE ChiTietDonHangNhap SET so_luong_con_lai = so_luong_con_lai - v_sl_xuat_tu_lo_nay WHERE id = rec.id;
            v_so_luong_can_xuat := 0;
        ELSE
            v_sl_xuat_tu_lo_nay := v_sl_con_lai_trong_lo;
            v_tong_gia_von := v_tong_gia_von + (v_sl_xuat_tu_lo_nay * v_gia_nhap);
            UPDATE ChiTietDonHangNhap SET so_luong_con_lai = 0 WHERE id = rec.id;
            v_so_luong_can_xuat := v_so_luong_can_xuat - v_sl_xuat_tu_lo_nay;
        END IF;
    END LOOP;

    NEW.tong_gia_von := v_tong_gia_von;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng ChiTietDonHangBan
CREATE TRIGGER trg_tinh_tong_gia_von_ban
BEFORE INSERT ON ChiTietDonHangBan
FOR EACH ROW
EXECUTE FUNCTION func_tinh_tong_gia_von_ban_fifo();


-- =====================================================================
-- SECTION 4: TRIGGER CHO QUẢN LÝ GIÁ (LichSuGiaNiemYet)
-- =====================================================================

-- 4.1. Hàm cập nhật ngày kết thúc của giá cũ khi có giá mới
-- Mục đích: Đảm bảo không có các khoảng giá bị chồng chéo.
CREATE OR REPLACE FUNCTION func_cap_nhat_ngay_ket_thuc_gia()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE LichSuGiaNiemYet
    SET ngay_ket_thuc = NEW.ngay_ap_dung - INTERVAL '1 day'
    WHERE id_san_pham = NEW.id_san_pham
      AND ngay_ap_dung < NEW.ngay_ap_dung
      AND (ngay_ket_thuc IS NULL OR ngay_ket_thuc >= NEW.ngay_ap_dung);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger áp dụng cho bảng LichSuGiaNiemYet
CREATE TRIGGER trg_cap_nhat_ngay_ket_thuc_gia
BEFORE INSERT ON LichSuGiaNiemYet
FOR EACH ROW
EXECUTE FUNCTION func_cap_nhat_ngay_ket_thuc_gia();