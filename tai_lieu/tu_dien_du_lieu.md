# Từ điển dữ liệu

Tài liệu mô tả ba tầng dữ liệu của đề tài: tệp thô trong `data/raw` và `data/external`, bảng thô do khâu nạp trả về, và bảng sạch dùng cho phân tích; cuối cùng là các tệp trong `ket_qua/`. Tên cột, mã chuỗi và mã sự kiện viết không dấu, đúng như trong mã nguồn và `cau_hinh.yaml`. Miền giá trị ghi trong tài liệu là miền thực tế của bộ dữ liệu tải ngày 10/11/2026 (quan sát giá từ 2/1/2018 đến 5/11/2026).

## 1. Dữ liệu thô

`data/raw` chứa dữ liệu tải qua API và trang tin bằng `python chay.py --giai-doan nap`; `data/external` chứa tệp tải nguyên vẹn từ bên thứ ba. Cả hai chỉ đọc: không bước nào sửa tệp đã có.

| Mã nguồn | Tệp | Định dạng | Trường được dùng | Ý nghĩa và đơn vị | Phạm vi |
|---|---|---|---|---|---|
| `eia` | `raw/eia/gia_giao_ngay_trang_NNN.json` | JSON, mỗi tệp một trang 5.000 bản ghi của API | `period`, `series`, `value`, `units` | Giá giao ngay (spot, FOB) theo phiên của một chuỗi; `value` là chuỗi ký tự; `units` là `$/BBL` (USD/thùng) hoặc `$/GAL` (USD/gallon) | 32.760 bản ghi, 11 chuỗi, 2/1/2015 - 3/11/2026 |
| `moit` | `raw/moit/bai_viet.jsonl`; `raw/moit/tim_kiem_trang_NNN.json` (trang kết quả tìm kiếm) | JSON Lines, mỗi dòng một bài; JSON | `content` (HTML thân bài); ngoài ra lưu `id`, `type`, `title`, `brief`, `publishTime`, `createdTime`, `lastUpdateTime`, `categories`, `rewriteURL` | Thông báo điều hành giá: giá bán lẻ tối đa (đồng/lít; dầu mazut đồng/kg) và giá thành phẩm Singapore bình quân kỳ (USD/thùng; dầu mazut USD/tấn) nằm trong câu văn; ngày lấy từ câu "Áp dụng từ ... giờ ... ngày ... tháng ... năm ..." | 306 bài, tách được 2.696 câu nêu giá |
| `bcp` | `raw/bcp/bai_viet.jsonl`; `raw/bcp/tim_kiem_KK_trang_NNN.html` (trang tìm kiếm của từ khoá thứ KK) | JSON Lines; HTML | `content` (HTML thân bài), `publishTime` (ISO 8601, múi giờ +07:00); ngoài ra lưu `id` (đường dẫn bài), `title` | Bài báo đưa lại giá bán lẻ tối đa của kỳ điều hành; ngày của quan sát là thời điểm đăng bài | 346 bài, tách được 1.044 câu nêu giá |
| `ty_gia` | `raw/ty_gia/ty_gia_trang_NNN.json` | JSON, mỗi tệp một trang của API | `effective_date`, `country_currency_desc`, `exchange_rate` | Tỷ giá báo cáo cuối quý của Bộ Tài chính Hoa Kỳ: số đồng Việt Nam đổi một USD | 103 bản ghi, 31/3/2001 - 30/9/2026, mỗi quý một giá trị |
| `gpr` | `external/gpr/data_gpr_daily_recent.xls` | Excel `.xls`, một trang tính | `DAY` (số dạng yyyymmdd), `GPRD` | Chỉ số rủi ro địa chính trị theo ngày của Caldara và Iacoviello, tính từ tỷ lệ bài báo nói về căng thẳng địa chính trị; điểm chỉ số, không có đơn vị | 15.281 ngày, 1/1/1985 - 2/11/2026 |
| `oxcgrt` | `external/oxcgrt/OxCGRT_compact_national_v1.csv` | CSV 43,8 MB, đọc theo khối | `Date` (số dạng yyyymmdd), `CountryCode`, `Jurisdiction`, `StringencyIndex_Average` | Chỉ số mức độ nghiêm ngặt của biện pháp chống dịch COVID-19 của một nước trong một ngày, thang 0 - 100; chỉ lấy dòng cấp quốc gia (`Jurisdiction = NAT_TOTAL`) | 202.760 dòng, 185 nước, 1/1/2020 - 31/12/2022 |

Hai tệp `bai_viet.jsonl` không có trường tác giả hay người đăng. Thân bài là văn bản đã công bố nên có thể còn bút danh phóng viên ở cuối bài; chương trình không trích phần này.

## 2. Bảng thô

Kết quả của `nap_du_lieu`, lưu tại `data/interim/bang_tho.csv`: 254.644 dòng, 7 cột. Mọi nguồn được đưa về cùng bảy cột và **mọi ô đều là chuỗi** đúng như trong tệp gốc; việc đổi kiểu thuộc về khâu làm sạch.

| Cột | Kiểu | Ý nghĩa | Miền giá trị (dạng gốc) |
|---|---|---|---|
| `nguon` | chuỗi | Mã nguồn của dòng | `bcp`, `eia`, `gpr`, `moit`, `oxcgrt`, `ty_gia` |
| `tep` | chuỗi | Tên tệp gốc chứa dòng | ví dụ `gia_giao_ngay_trang_001.json` |
| `ngay` | chuỗi | Ngày ở dạng gốc của nguồn | bốn kiểu viết: `2020-01-15`; `20200115`; `2026-11-05T14:50:00+07:00`; "15 giờ 30 ngày 15 tháng 01 năm 2020" |
| `chuoi` | chuỗi | Nhãn chuỗi số liệu ở dạng gốc | mã chuỗi EIA (`RBRTE`); tên mặt hàng trong bài viết ("Xăng E5RON92"); mã nước (`VNM`); tên cặp tiền (`Vietnam-Dong`); `GPRD` |
| `gia_tri` | chuỗi | Giá trị ở dạng gốc | `66.25`; `.593`; `19.845` (kiểu Việt Nam, nghĩa là 19845); `81,252` (nghĩa là 81 phẩy 252) |
| `don_vi` | chuỗi | Đơn vị ở dạng gốc | `$/BBL`, `$/GAL`, `USD/thùng`, `USD/tấn`, `VND/USD`, `chi so`, `chi so 0-100`, `đồng/kg`, `đồng/lít` |
| `van_ban` | chuỗi | Câu văn chứa giá (chỉ có ở `moit`, `bcp`); dùng để đọc mức tăng giảm của kỳ điều hành | tối đa 160 ký tự sau chỗ nêu giá; rỗng ở các nguồn khác |

## 3. Bảng sạch

Kết quả của `lam_sach`, lưu tại `data/processed/gia_xang_dau.csv`: 25.083 dòng, 20 cột, 19 chuỗi giá. Mỗi dòng là **một quan sát giá của một chuỗi trong một ngày**; khoá chính là (`ngay`, `ma_chuoi`), không trùng.

| Cột | Kiểu | Đơn vị | Miền giá trị | Ý nghĩa |
|---|---|---|---|---|
| `ngay` | ngày |  | 2/1/2018 đến 5/11/2026; không thiếu | Ngày của quan sát. Giá giao ngay: ngày của phiên giao dịch. Giá bán lẻ và giá Singapore lấy từ `moit`: ngày bắt đầu áp dụng; lấy từ `bcp`: ngày đăng bài (có thể lệch một ngày so với ngày áp dụng). Dòng suy ra: ngày liền trước ngày điều chỉnh |
| `nam` | số nguyên |  | 2018 đến 2026 | Năm của `ngay` |
| `thang` | số nguyên |  | 1 đến 12 | Tháng của `ngay` |
| `ma_chuoi` | chuỗi |  | 19 mã, xem mục 4 | Mã chuỗi chuẩn |
| `ten_chuoi` | chuỗi |  | một tên cho mỗi mã chuỗi | Tên hiển thị có dấu của chuỗi |
| `thi_truong` | chuỗi |  | `singapore`, `the_gioi`, `viet_nam` | `the_gioi`: giá giao ngay của EIA; `singapore`: giá thành phẩm bình quân kỳ do Bộ Công Thương công bố; `viet_nam`: giá bán lẻ tối đa |
| `nhom_hang` | chuỗi |  | `dau_hoa`, `dau_tho`, `diesel`, `xang` | Nhóm hàng của chuỗi |
| `nguon` | chuỗi |  | `bcp`, `eia`, `moit` | Nguồn của dòng được giữ sau khi bỏ bản ghi trùng |
| `suy_ra` | đúng/sai |  | `True` ở 853 dòng, `False` ở 24.230 dòng | `True`: giá của ngày liền trước kỳ điều chỉnh, tính bằng giá mới trừ mức tăng giảm nêu trong câu; `False`: giá nguồn công bố trực tiếp |
| `gia_goc` | số thực | theo `don_vi` | -36,98 đến 44.788; không thiếu; giá trị âm duy nhất là dầu WTI ngày 20/4/2020 | Giá theo đơn vị gốc của chuỗi |
| `don_vi` | chuỗi |  | `usd_gallon`, `usd_thung`, `vnd_lit` | Đơn vị chuẩn của `gia_goc`: USD/thùng, USD/gallon, đồng/lít |
| `ty_gia` | số thực | đồng/USD | 22.709,9 đến 26.425,0; không thiếu | Tỷ giá của ngày, nội suy tuyến tính theo thời gian giữa hai mốc cuối quý; sau mốc cuối của nguồn thì giữ giá trị cuối (tối đa 120 ngày) |
| `gia_usd_thung` | số thực | USD/thùng | -36,98 đến 270,57; không thiếu | Giá quy về USD một thùng (1 thùng = 42 gallon = 158,987 lít); giá tính bằng đồng thì chia cho `ty_gia` |
| `gia_vnd_lit` | số thực | đồng/lít | -5.472 đến 44.788; không thiếu | Giá quy về đồng một lít theo `ty_gia` |
| `thay_doi_pct` | số thực | % | -49,2 đến 121,9; thiếu 21 ô | Thay đổi của `gia_goc` so với quan sát liền trước của cùng chuỗi; thiếu ở quan sát đầu của mỗi chuỗi và khi một trong hai giá không dương |
| `gpr` | số thực | điểm chỉ số | 9,5 đến 540,8; không thiếu | Chỉ số rủi ro địa chính trị của ngày; ngày sau mốc cuối của nguồn (tối đa 7 ngày) nhận giá trị cuối |
| `phong_toa_tg` | số thực | điểm, thang 0 - 100 | 0,0 đến 79,8; thiếu 11.237 ô | Trung bình chỉ số nghiêm ngặt của mọi nước trong ngày; bằng 0 trước 1/1/2020; thiếu sau 31/12/2022 vì nguồn ngừng cập nhật |
| `phong_toa_vn` | số thực | điểm, thang 0 - 100 | 0,0 đến 96,3; thiếu 11.237 ô | Chỉ số nghiêm ngặt của Việt Nam; quy tắc như cột trên |
| `su_kien` | chuỗi |  | `binh_thuong`, `covid_2020`, `iran_hormuz_2026`, `israel_hamas_2023`, `israel_iran_2025`, `nga_ukraina_2022` | Mã sự kiện (bối cảnh) chứa ngày đó, xem mục 5 |
| `loai_boi_canh` | chuỗi |  | `binh_thuong`, `dich_benh`, `xung_dot` | Loại bối cảnh của sự kiện |

## 4. Mã chuỗi

Quy tắc đưa nhãn gốc về mã chuỗi nằm ở mục `danh_muc` của `cau_hinh.yaml`. Cột "Giá gốc" là giá nhỏ nhất và lớn nhất theo đơn vị gốc; cột "Quan sát" ghi tổng số dòng và, với giá bán lẻ, số dòng suy ra trong đó.

| `ma_chuoi` | `thi_truong` | Nội dung | Đơn vị gốc | Nhãn chuẩn trong nguồn | Khoảng ngày | Quan sát | Giá gốc |
|---|---|---|---|---|---|---|---|
| `brent` | `the_gioi` | Dầu thô Brent | USD/thùng | `RBRTE` | 2/1/2018 - 3/11/2026 | 2.240 | 9,12 - 138,21 |
| `wti` | `the_gioi` | Dầu thô WTI | USD/thùng | `RWTC` | 2/1/2018 - 3/11/2026 | 2.215 | -36,98 - 123,64 |
| `xang_nyh` | `the_gioi` | Xăng (cảng New York) | USD/gallon | `EER_EPMRU_PF4_Y35NY_DPG` | 2/1/2018 - 3/11/2026 | 2.217 | 0,43 - 4,51 |
| `xang_gc` | `the_gioi` | Xăng (Bờ Vịnh Mỹ) | USD/gallon | `EER_EPMRU_PF4_RGC_DPG` | 2/1/2018 - 3/11/2026 | 2.217 | 0,36 - 4,34 |
| `xang_la` | `the_gioi` | Xăng RBOB (Los Angeles) | USD/gallon | `EER_EPMRR_PF4_Y05LA_DPG` | 2/1/2018 - 3/11/2026 | 2.217 | 0,29 - 4,97 |
| `diesel_nyh` | `the_gioi` | Diesel (cảng New York) | USD/gallon | `EER_EPD2DXL0_PF4_Y35NY_DPG` | 2/1/2018 - 3/11/2026 | 2.217 | 0,60 - 5,37 |
| `diesel_gc` | `the_gioi` | Diesel (Bờ Vịnh Mỹ) | USD/gallon | `EER_EPD2DXL0_PF4_RGC_DPG` | 2/1/2018 - 3/11/2026 | 2.217 | 0,54 - 5,30 |
| `diesel_la` | `the_gioi` | Diesel CARB (Los Angeles) | USD/gallon | `EER_EPD2DC_PF4_Y05LA_DPG` | 2/1/2018 - 3/11/2026 | 2.213 | 0,57 - 5,53 |
| `nl_bay_gc` | `the_gioi` | Nhiên liệu bay (Bờ Vịnh Mỹ) | USD/gallon | `EER_EPJK_PF4_RGC_DPG` | 2/1/2018 - 3/11/2026 | 2.217 | 0,41 - 5,07 |
| `dau_dot_nyh` | `the_gioi` | Dầu đốt số 2 (cảng New York) | USD/gallon | `EER_EPD2F_PF4_Y35NY_DPG` | 2/1/2018 - 3/11/2026 | 2.217 | 0,56 - 5,16 |
| `sg_ron92` | `singapore` | Xăng RON92 (Singapore, bình quân kỳ) | USD/thùng | "xăng RON92 dùng để pha chế xăng E5RON92" | 3/2/2018 - 5/11/2026 | 223 | 18,48 - 149,59 |
| `sg_ron95` | `singapore` | Xăng RON95 (Singapore, bình quân kỳ) | USD/thùng | "xăng RON95" | 23/4/2018 - 5/11/2026 | 219 | 19,73 - 156,21 |
| `sg_diesel` | `singapore` | Dầu diesel 0.05S (Singapore, bình quân kỳ) | USD/thùng | "dầu diesel 0.05S" | 3/2/2018 - 5/11/2026 | 223 | 27,15 - 249,50 |
| `sg_dau_hoa` | `singapore` | Dầu hỏa (Singapore, bình quân kỳ) | USD/thùng | "dầu hỏa" | 3/2/2018 - 11/3/2026 | 205 | 19,75 - 188,20 |
| `vn_e5ron92` | `viet_nam` | Xăng E5 RON92 (bán lẻ Việt Nam) | đồng/lít | "Xăng E5RON92" | 4/1/2018 - 5/11/2026 | 520 (218 suy ra) | 10.942 - 31.302 |
| `vn_ron95` | `viet_nam` | Xăng RON95-III (bán lẻ Việt Nam) | đồng/lít | "Xăng RON95-III" | 23/4/2018 - 28/5/2026 | 466 (196 suy ra) | 11.631 - 33.840 |
| `vn_e10ron95` | `viet_nam` | Xăng E10 RON95-III (bán lẻ Việt Nam) | đồng/lít | "Xăng E10RON95-III" | 18/6/2026 - 5/11/2026 | 47 (22 suy ra) | 19.916 - 28.254 |
| `vn_diesel` | `viet_nam` | Dầu diesel 0.05S (bán lẻ Việt Nam) | đồng/lít | "Dầu diesel 0.05S" | 4/1/2018 - 5/11/2026 | 527 (222 suy ra) | 9.857 - 44.788 |
| `vn_dau_hoa` | `viet_nam` | Dầu hỏa (bán lẻ Việt Nam) | đồng/lít | "Dầu hỏa" | 4/1/2018 - 27/3/2026 | 466 (195 suy ra) | 7.882 - 40.455 |

Ghi chú: giá `the_gioi` là giá giao ngay tại thị trường Mỹ và châu Âu (Brent) do EIA công bố; giá `singapore` là giá thành phẩm bình quân giữa hai kỳ điều hành, nêu trong thông báo của Bộ Công Thương; giá `viet_nam` là giá bán lẻ tối đa (giá trần) của kỳ điều hành. Trong dữ liệu, xăng RON95-III có quan sát cuối ngày 28/5/2026; xăng E10 RON95-III xuất hiện từ 18/6/2026 và là một sản phẩm khác nên được giữ thành chuỗi riêng; dầu hỏa có quan sát cuối ngày 27/3/2026. Nhãn không có quy tắc (propan của EIA; dầu mazut tính theo đồng/kg và USD/tấn) bị loại ở bước chuẩn hoá danh mục và được đếm trong nhật ký.

## 5. Mã sự kiện (bối cảnh)

| `su_kien` | `loai_boi_canh` | Khoảng thời gian | Mốc bắt đầu lấy theo | Số dòng của bảng sạch |
|---|---|---|---|---|
| `covid_2020` | `dich_benh` | 30/1/2020 - 30/6/2020 | WHO tuyên bố tình trạng khẩn cấp y tế công cộng gây quan ngại quốc tế | 1.147 |
| `nga_ukraina_2022` | `xung_dot` | 24/2/2022 - 31/8/2022 | Nga mở chiến dịch quân sự tại Ukraine | 1.516 |
| `israel_hamas_2023` | `xung_dot` | 7/10/2023 - 31/12/2023 | Hamas tấn công Israel | 662 |
| `israel_iran_2025` | `xung_dot` | 13/6/2025 - 24/6/2025 | Israel không kích Iran | 79 |
| `iran_hormuz_2026` | `xung_dot` | 28/2/2026 - hết dữ liệu | Mỹ và Israel không kích Iran; vận tải qua eo biển Hormuz gián đoạn | 2.023 |
| `binh_thuong` | `binh_thuong` | các ngày còn lại |  | 19.656 |

Ngày kết thúc của bốn sự kiện đầu là mốc do nhóm chọn để so sánh, không phải mốc chính thức. Đường dẫn tài liệu làm căn cứ cho từng mốc bắt đầu nằm ở mục `su_kien` của `cau_hinh.yaml`.

## 6. Tệp kết quả

Mọi tệp trong `ket_qua/` do mã sinh ra. Bảng csv mã hoá UTF-8 (có BOM để mở được bằng Excel), số thực ghi bốn chữ số thập phân.

| Tệp | Mỗi dòng là | Cột và đơn vị |
|---|---|---|
| `tom_tat.json` | một lần chạy | 13 khoá theo mục 5.4 của đề bài; `ket_qua` gồm các chỉ tiêu trả lời câu hỏi: độ biến động (% một năm), số lần so với bình thường, mức thay đổi (%), tỷ lệ truyền dẫn, giá (đồng/lít), tỷ trọng (%), hệ số tương quan, số kỳ |
| `nhat_ky.log` | một thông điệp | thời điểm, mức, mô-đun, nội dung; mỗi bước làm sạch ghi số dòng vào, ra, loại, thêm và lý do |
| `bang/a1_cac_buoc_lam_sach.csv` | một bước làm sạch | `thu_tu`, `buoc`, `khoa_thong_ke`, `so_dong_vao`, `so_dong_ra`, `so_dong_loai`, `so_dong_them`, `so_o_xu_ly` (ô hoặc dòng), `ly_do`, `chi_tiet` (đếm theo nguồn hoặc theo nhãn) |
| `bang/a2_mau_doi_chieu.csv` | một giá tách từ bài viết, rút ngẫu nhiên theo seed | `ngay`, `ma_chuoi`, `ten_chuoi`, `gia_goc` (theo `don_vi`), `don_vi`, `nguon` |
| `bang/b1_bien_dong_theo_boi_canh.csv` | một cặp (chuỗi giá thế giới, bối cảnh) | `so_phien` (phiên), `bien_dong_nam_pct` (% một năm), `gap_lan_binh_thuong` (lần) |
| `bang/b2_cu_soc_gia_theo_su_kien.csv` | một cặp (sự kiện, chuỗi) | `huong` (`tang`/`giam`), `gia_truoc`, `gia_cuc_tri`, `thay_doi_dong_lit` (đồng/lít), `ngay_cuc_tri`, `thay_doi_pct` (%), `ty_le_truyen_dan` (lần; bằng 1 với Brent) |
| `bang/b3_ty_trong_gia_the_gioi_trong_gia_ban_le.csv` | một cặp (mặt hàng bán lẻ, bối cảnh) | `so_ky` (kỳ điều hành có cả hai giá), `ty_trong_tb_pct` (%), `chenh_lech_tb_dong_lit` (đồng/lít) |
| `bang/b4_tuong_quan_theo_thang.csv` | một cặp biến | `chi_tieu`, `he_so_tuong_quan` (Pearson, từ -1 đến 1), `so_thang` (tháng) |
| `bang/b5_do_phu_gia_ban_le.csv` | một cặp (chuỗi bán lẻ, năm) | `so_ky_quan_sat`, `so_dong_suy_ra`, `so_khoang_thieu_ky` (số chỗ giữa hai quan sát còn thiếu ít nhất một kỳ), `khoang_cach_lon_nhat_ngay` (ngày) |
| `bang/b6_tong_hop_theo_chuoi_va_nam.csv` | một cặp (chuỗi, năm) | với `gia_vnd_lit` (đồng/lít) và `thay_doi_pct` (%): số quan sát, trung bình, trung vị, độ lệch chuẩn, nhỏ nhất, lớn nhất |
| `bang/b7_tong_hop_theo_thi_truong_va_boi_canh.csv` | một bộ (thị trường, nhóm hàng, bối cảnh) | các cột thống kê như `b6` |
| `hinh/h1_dien_bien_gia_va_su_kien.png` |  | đường: giá Brent và giá bán lẻ xăng E5 RON92, dầu diesel (đồng/lít) theo ngày, tô nền các sự kiện |
| `hinh/h2_bien_dong_theo_boi_canh.png` |  | cột ghép: độ biến động quy năm (%) của bốn chuỗi giá thế giới theo bối cảnh |
| `hinh/h3_cu_soc_gia_va_truyen_dan.png` |  | cột ghép: mức thay đổi lớn nhất (%) của Brent và giá bán lẻ trong ba sự kiện chính |
| `hinh/h4_ty_trong_gia_the_gioi_trong_gia_ban_le.png` |  | đường: tỷ trọng giá Singapore trong giá bán lẻ (%) theo kỳ điều hành |
| `hinh/h5_rui_ro_dia_chinh_tri_va_bien_dong.png` |  | phân tán: chỉ số GPR bình quân tháng và độ biến động của Brent trong tháng (%) |
