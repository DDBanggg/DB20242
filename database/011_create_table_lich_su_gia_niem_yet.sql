CREATE TABLE LichSuGiaNiemYet (
    id SERIAL PRIMARY KEY,                          -- ID tự tăng, khóa chính của bảng
    id_san_pham INTEGER NOT NULL,                   -- Khóa ngoại tham chiếu đến sản phẩm
    gia_niem_yet NUMERIC(12, 0) NOT NULL,           -- Giá niêm yết của sản phẩm
    ngay_ap_dung DATE NOT NULL,                     -- Ngày giá này bắt đầu có hiệu lực
    ngay_ket_thuc DATE NULL,                        -- Ngày giá này kết thúc hiệu lực (NULL nếu chưa xác định)
    ghi_chu TEXT NULL,                              -- Ghi chú thêm về lần thay đổi giá này
    ngay_tao_ban_ghi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Ngày giờ bản ghi giá được tạo

    CONSTRAINT fk_san_pham_gia
        FOREIGN KEY (id_san_pham)
        REFERENCES SanPham(id)
        ON DELETE CASCADE  -- Nếu sản phẩm bị xóa, lịch sử giá của nó cũng sẽ bị xóa
        ON UPDATE CASCADE, -- Nếu ID sản phẩm thay đổi (ít khi xảy ra với SERIAL), ở đây cũng cập nhật

    CONSTRAINT chk_gia_niem_yet_duong
        CHECK (gia_niem_yet >= 0),                  -- Đảm bảo giá niêm yết không âm

    CONSTRAINT chk_ngay_hieu_luc_gia
        CHECK (ngay_ket_thuc IS NULL OR ngay_ket_thuc > ngay_ap_dung) -- Đảm bảo ngày kết thúc (nếu có) phải sau ngày áp dụng
);

-- Tạo index để tăng tốc độ truy vấn lịch sử giá theo sản phẩm và ngày áp dụng
--CREATE INDEX idx_lichsugia_sanpham_ngayapdung ON LichSuGiaNiemYet (id_san_pham, ngay_ap_dung DESC);