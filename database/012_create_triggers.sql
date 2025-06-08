-- Script to create triggers for inventory management database

-- 1. Create or Replace trigger function for auto-updating "ngay_cap_nhat_ban_ghi"
CREATE OR REPLACE FUNCTION fn_cap_nhat_ngay_gio_sua()
RETURNS TRIGGER AS $$
BEGIN
   NEW.ngay_cap_nhat_ban_ghi = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    -- 1.1. Create trigger for DonHangNhap table
    CREATE TRIGGER trg_donhangnhap_cap_nhat_ngay_gio_sua
    BEFORE UPDATE ON DonHangNhap
    FOR EACH ROW
    EXECUTE FUNCTION fn_cap_nhat_ngay_gio_sua();

    -- 1.2. Create trigger for DonHangBan table
    CREATE TRIGGER trg_donhangban_cap_nhat_ngay_gio_sua
    BEFORE UPDATE ON DonHangBan
    FOR EACH ROW
    EXECUTE FUNCTION fn_cap_nhat_ngay_gio_sua();

-- 2. Create or Replace trigger function for auto-updating "so_luong_ton_kho" when a new DonHangNhap is completed
CREATE OR REPLACE FUNCTION func_cap_nhat_ton_kho_khi_nhap_hang()
RETURNS TRIGGER AS $$
BEGIN
    -- Kiểm tra xem trạng thái mới có phải là 'Hoàn tất'
    -- và trạng thái cũ có khác trạng thái mới không (để tránh chạy lại khi không cần thiết)
    IF NEW.trang_thai = 'Hoàn tất' AND OLD.trang_thai IS DISTINCT FROM NEW.trang_thai THEN
        -- Cập nhật số lượng tồn kho cho từng sản phẩm trong chi tiết đơn hàng nhập
        UPDATE SanPham sp
        SET so_luong_ton_kho = sp.so_luong_ton_kho + ctdhn.so_luong -- Giả sử cột số lượng trong ChiTietDonHangNhap là 'so_luong' [cite: 63]
        FROM ChiTietDonHangNhap ctdhn
        WHERE ctdhn.id_don_hang_nhap = NEW.id AND sp.id = ctdhn.id_san_pham;
        
        RAISE NOTICE 'Đã cập nhật số lượng tồn kho cho các sản phẩm của Đơn Hàng Nhập ID %.', NEW.id;
    END IF;

    RETURN NEW; -- Đối với AFTER trigger, giá trị trả về thường không quan trọng, nhưng trả về NEW là một thực hành tốt.
END;
$$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_after_update_donhangnhap_hoantat
    AFTER UPDATE ON DonHangNhap
    FOR EACH ROW
    WHEN (OLD.trang_thai IS DISTINCT FROM NEW.trang_thai AND NEW.trang_thai = 'Hoàn tất')
    EXECUTE FUNCTION func_cap_nhat_ton_kho_khi_nhap_hang();

-- 3. Create or Replace trigger function for auto-updating "so_luong_con_lai" in ChiTietDonHangNhap
CREATE OR REPLACE FUNCTION set_so_luong_con_lai()
RETURNS TRIGGER AS $$
BEGIN
    -- Gán so_luong_con_lai bằng so_luong cho bản ghi mới
    NEW.so_luong_con_lai = NEW.so_luong;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    -- Tạo trigger
    CREATE TRIGGER trigger_set_so_luong_con_lai
    BEFORE INSERT ON ChiTietDonHangNhap
    FOR EACH ROW
    EXECUTE FUNCTION set_so_luong_con_lai();

-- 4. Trigger to reduce so_luong_ton_kho in SanPham after DonHangBan reaches 'Hoàn tất'
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

    CREATE TRIGGER trg_after_update_donhangban_hoantat
    AFTER UPDATE ON DonHangBan
    FOR EACH ROW
    WHEN (OLD.trang_thai_don_hang IS DISTINCT FROM NEW.trang_thai_don_hang AND NEW.trang_thai_don_hang = 'Hoàn tất')
    EXECUTE FUNCTION func_cap_nhat_ton_kho_khi_ban_hang();

-- 5. Trigger to calculate gia_ban_cuoi_cung_don_vi in ChiTietDonHangBan
CREATE OR REPLACE FUNCTION func_tinh_gia_ban_cuoi_cung()
RETURNS TRIGGER AS $$
BEGIN
    NEW.gia_ban_cuoi_cung_don_vi = NEW.gia_ban_niem_yet_don_vi * (1 - NEW.giam_gia);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_tinh_gia_ban_cuoi_cung
    BEFORE INSERT OR UPDATE ON ChiTietDonHangBan
    FOR EACH ROW
    EXECUTE FUNCTION func_tinh_gia_ban_cuoi_cung();

-- 6. Trigger to calculate tong_doanh_thu in DonHangBan
CREATE OR REPLACE FUNCTION func_cap_nhat_tong_doanh_thu()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE DonHangBan
    SET tong_doanh_thu = (
        SELECT COALESCE(SUM(so_luong * gia_ban_cuoi_cung_don_vi), 0)
        FROM ChiTietDonHangBan
        WHERE id_don_hang_ban = 
            CASE 
                WHEN TG_OP = 'DELETE' THEN OLD.id_don_hang_ban 
                ELSE NEW.id_don_hang_ban 
            END
    )
    WHERE id = 
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.id_don_hang_ban 
            ELSE NEW.id_don_hang_ban 
        END;
    RETURN NULL; -- AFTER trigger does not need to return a row
END;
$$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_cap_nhat_tong_doanh_thu
    AFTER INSERT OR UPDATE OR DELETE ON ChiTietDonHangBan
    FOR EACH ROW
    EXECUTE FUNCTION func_cap_nhat_tong_doanh_thu();

-- 7. Trigger to update so_lan_mua_hang in KhachHang after DonHangBan reaches 'Hoàn tất'
CREATE OR REPLACE FUNCTION func_cap_nhat_so_lan_mua_hang()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trang_thai_don_hang = 'Hoàn tất' AND OLD.trang_thai_don_hang IS DISTINCT FROM NEW.trang_thai_don_hang THEN
        UPDATE KhachHang
        SET so_lan_mua_hang = so_lan_mua_hang + 1
        WHERE id = NEW.id_khach_hang;
        
        RAISE NOTICE 'Đã cập nhật số lần mua hàng cho khách hàng ID % của Đơn Hàng Bán ID %.', NEW.id_khach_hang, NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_after_update_so_lan_mua_hang
    AFTER UPDATE ON DonHangBan
    FOR EACH ROW
    WHEN (OLD.trang_thai_don_hang IS DISTINCT FROM NEW.trang_thai_don_hang AND NEW.trang_thai_don_hang = 'Hoàn tất')
    EXECUTE FUNCTION func_cap_nhat_so_lan_mua_hang();

-- 8. Trigger to update ngay_ket_thuc in LichSuGiaNiemYet
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

    CREATE TRIGGER trg_cap_nhat_ngay_ket_thuc_gia
    BEFORE INSERT ON LichSuGiaNiemYet
    FOR EACH ROW
    EXECUTE FUNCTION func_cap_nhat_ngay_ket_thuc_gia();

-- 9. Trigger to update trang_thai in SanPham based on so_luong_ton_kho
CREATE OR REPLACE FUNCTION func_cap_nhat_trang_thai_san_pham()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.so_luong_ton_kho > 0 AND NEW.trang_thai != 'Ngừng kinh doanh' THEN
        NEW.trang_thai = 'Đang kinh doanh - Còn hàng';
    ELSIF NEW.so_luong_ton_kho = 0 AND NEW.trang_thai != 'Ngừng kinh doanh' THEN
        NEW.trang_thai = 'Đang kinh doanh - Hết hàng';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_cap_nhat_trang_thai_san_pham
    BEFORE UPDATE OF so_luong_ton_kho ON SanPham
    FOR EACH ROW
    EXECUTE FUNCTION func_cap_nhat_trang_thai_san_pham();

-- 10. Trigger to calculate tong_gia_nhap in ChiTietDonHangNhap
CREATE OR REPLACE FUNCTION func_tinh_tong_gia_nhap()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tong_gia_nhap = NEW.gia_nhap_don_vi * NEW.so_luong;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    -- Trigger for tong_gia_nhap
    CREATE TRIGGER trg_tinh_tong_gia_nhap
    BEFORE INSERT OR UPDATE OF gia_nhap_don_vi, so_luong
    ON ChiTietDonHangNhap
    FOR EACH ROW
    EXECUTE FUNCTION func_tinh_tong_gia_nhap();

-- 11. Trigger to calculate tong_gia_tri in DonHangNhap
CREATE OR REPLACE FUNCTION func_cap_nhat_tong_gia_tri_nhap()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE DonHangNhap
    SET tong_gia_tri = (
        SELECT COALESCE(SUM(tong_gia_nhap), 0)
        FROM ChiTietDonHangNhap
        WHERE id_don_hang_nhap = NEW.id_don_hang_nhap
    )
    WHERE id = NEW.id_don_hang_nhap;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

    -- Trigger for tong_gia_tri
    CREATE TRIGGER trg_cap_nhat_tong_gia_tri_nhap
    AFTER INSERT OR UPDATE
    ON ChiTietDonHangNhap
    FOR EACH ROW
    EXECUTE FUNCTION func_cap_nhat_tong_gia_tri_nhap();

-- 12. Trigger to calculate tong_gia_ban in ChiTietDonHangBan
CREATE OR REPLACE FUNCTION func_tinh_tong_gia_ban_ban()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tong_gia_ban = NEW.gia_ban_cuoi_cung_don_vi * NEW.so_luong;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    -- Trigger for tong_gia_ban
    CREATE TRIGGER trg_tinh_tong_gia_ban_ban
    BEFORE INSERT OR UPDATE OF gia_ban_cuoi_cung_don_vi, so_luong
    ON ChiTietDonHangBan
    FOR EACH ROW
    EXECUTE FUNCTION func_tinh_tong_gia_ban_ban();

-- 13. Trigger to calculate tong_gia_von in ChiTietDonHangBan using FIFO
CREATE OR REPLACE FUNCTION func_tinh_tong_gia_von_ban()
RETURNS TRIGGER AS $$
DECLARE
    v_so_luong_can_xuat NUMERIC; -- Đổi tên cho rõ ràng hơn
    v_tong_gia_von NUMERIC := 0;
    v_gia_nhap NUMERIC;
    v_sl_con_lai_trong_lo NUMERIC; -- Số lượng còn lại trong lô nhập cụ thể
    v_sl_xuat_tu_lo_nay NUMERIC; -- Số lượng thực tế xuất từ lô này
    rec RECORD;
BEGIN
    v_so_luong_can_xuat := NEW.so_luong;
    -- Nếu là UPDATE, và số lượng không đổi hoặc sản phẩm không đổi,
    -- có thể không cần tính lại nếu logic nghiệp vụ cho phép.
    -- Tuy nhiên, để đơn giản, ta luôn tính lại.
    -- Nếu bạn muốn tối ưu, cần thêm điều kiện kiểm tra OLD.so_luong != NEW.so_luong OR OLD.id_san_pham != NEW.id_san_pham

    FOR rec IN (
        SELECT id, gia_nhap_don_vi, so_luong_con_lai, id_don_hang_nhap -- Thêm id_don_hang_nhap để debug nếu cần
        FROM ChiTietDonHangNhap
        WHERE id_san_pham = NEW.id_san_pham
        AND so_luong_con_lai > 0
        AND id_don_hang_nhap IN (
            SELECT id FROM DonHangNhap WHERE trang_thai = 'Hoàn tất'
        )
        ORDER BY ngay_tao_ban_ghi ASC -- Giả sử ngay_tao_ban_ghi của ChiTietDonHangNhap phản ánh FIFO
                                      -- Hoặc ORDER BY DonHangNhap.ngay_nhap ASC, ChiTietDonHangNhap.id ASC nếu cần
    )
    LOOP
        IF v_so_luong_can_xuat <= 0 THEN
            EXIT; -- Đã đủ số lượng, thoát vòng lặp
        END IF;

        v_gia_nhap := rec.gia_nhap_don_vi;
        v_sl_con_lai_trong_lo := rec.so_luong_con_lai;

        IF v_so_luong_can_xuat <= v_sl_con_lai_trong_lo THEN
            -- Lô này đủ hàng cho phần còn lại
            v_sl_xuat_tu_lo_nay := v_so_luong_can_xuat;
            v_tong_gia_von := v_tong_gia_von + (v_sl_xuat_tu_lo_nay * v_gia_nhap);
            
            -- CẬP NHẬT SỐ LƯỢNG CÒN LẠI TRONG ChiTietDonHangNhap
            UPDATE ChiTietDonHangNhap
            SET so_luong_con_lai = so_luong_con_lai - v_sl_xuat_tu_lo_nay
            WHERE id = rec.id; -- Giả sử 'id' là khóa chính của ChiTietDonHangNhap

            v_so_luong_can_xuat := 0; -- Đã xuất đủ
        ELSE
            -- Lô này không đủ, lấy hết số lượng còn lại trong lô này
            v_sl_xuat_tu_lo_nay := v_sl_con_lai_trong_lo;
            v_tong_gia_von := v_tong_gia_von + (v_sl_xuat_tu_lo_nay * v_gia_nhap);
            
            -- CẬP NHẬT SỐ LƯỢNG CÒN LẠI TRONG ChiTietDonHangNhap
            UPDATE ChiTietDonHangNhap
            SET so_luong_con_lai = 0 -- Hoặc so_luong_con_lai - v_sl_xuat_tu_lo_nay
            WHERE id = rec.id;

            v_so_luong_can_xuat := v_so_luong_can_xuat - v_sl_xuat_tu_lo_nay;
        END IF;
    END LOOP;

    NEW.tong_gia_von := v_tong_gia_von;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_tinh_tong_gia_von_ban
    BEFORE INSERT OR UPDATE OF so_luong, id_san_pham
    ON ChiTietDonHangBan
    FOR EACH ROW
    EXECUTE FUNCTION func_tinh_tong_gia_von_ban();