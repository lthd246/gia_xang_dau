# Biến động giá xăng dầu Việt Nam và thế giới qua các cú sốc 2018 - 2026

Đồ án cuối kỳ học phần MTH10605 - Python cho Khoa học Dữ liệu, hướng đề tài 3.2 (giá cả và chỉ số thị trường). Nhóm NN; tên gói mã nguồn: `gia_xang_dau`.

Chương trình tải giá xăng dầu thế giới và giá bán lẻ ở Việt Nam từ sáu nguồn công khai, làm sạch, ghép theo khoá ngày rồi đo mức biến động của giá trong các giai đoạn dịch bệnh và xung đột vũ trang. Đây là một chương trình phân tích mô tả: không huấn luyện mô hình, không dự báo, không kiểm định giả thuyết (các nội dung ngoài phạm vi ở mục 2.2 của đề bài).

Mọi con số trong tệp này lấy từ lần chạy trên bộ dữ liệu thô tải ngày 10/11/2026 (quan sát giá từ 2/1/2018 đến 5/11/2026) và trùng với `ket_qua/tom_tat.json`.

## Cau hoi phan tich

> Giai đoạn 2018 - 11/2026, trong ba cú sốc lớn (đại dịch COVID-19 năm 2020, chiến sự Nga - Ukraine năm 2022, chiến sự Iran - eo biển Hormuz năm 2026), giá dầu thế giới biến động mạnh gấp mấy lần lúc bình thường, và giá bán lẻ xăng E5 RON92, dầu diesel ở Việt Nam tăng giảm bằng bao nhiêu phần so với mức tăng giảm của giá dầu thế giới khi cùng quy về đồng/lít?

Câu hỏi có hai vế, mỗi vế trả lời bằng một nhóm con số; hai phép đo bổ trợ giúp giải thích kết quả. Tất cả đều là thống kê mô tả.

| Phần của câu hỏi | Thước đo | Cách tính | Bảng và hình |
|---|---|---|---|
| Vế 1: giá thế giới biến động mạnh gấp mấy lần | Độ biến động quy năm của dầu thô Brent trong từng bối cảnh | Độ lệch chuẩn của lợi suất log theo phiên ln(P_t / P_(t-1)), nhân căn bậc hai của 252 phiên/năm; tính riêng cho từng bối cảnh rồi chia cho mức của các ngày bình thường | `b1`, hình `h2` |
| Vế 2: giá bán lẻ tăng giảm bằng bao nhiêu phần | Tỷ lệ truyền dẫn trong từng sự kiện | Mức thay đổi (%) lớn nhất của giá bán lẻ trong sự kiện chia cho mức thay đổi (%) lớn nhất của giá Brent, cả hai cùng so với giá của ngày ngay trước sự kiện và cùng tính bằng đồng/lít; giá Brent lấy bình quân trượt 7 ngày | `b2`, hình `h1`, `h3` |
| Bổ trợ: giá thế giới chiếm bao nhiêu trong giá bán lẻ | Tỷ trọng giá thành phẩm Singapore trong giá bán lẻ | Giá thành phẩm Singapore bình quân kỳ (USD/thùng, quy ra đồng/lít) chia cho giá bán lẻ tối đa của cùng kỳ điều hành | `b3`, hình `h4` |
| Bổ trợ: bối cảnh đi cùng biến động thế nào | Hệ số tương quan Pearson theo tháng | Giữa chỉ số rủi ro địa chính trị (GPR), chỉ số phong toả chống dịch và giá, độ biến động của Brent; giữa mức thay đổi theo tháng của giá Brent và giá bán lẻ | `b4`, hình `h5` |

**Bối cảnh.** Mỗi ngày thuộc một trong năm sự kiện dưới đây hoặc là ngày "bình thường". Mốc thời gian khai báo ở mục `su_kien` của `cau_hinh.yaml`; ba sự kiện in đậm là ba cú sốc nêu trong câu hỏi. Ngày kết thúc của bốn sự kiện đầu là mốc do nhóm chọn để so sánh, không phải mốc chính thức.

| Mã | Sự kiện | Loại bối cảnh | Khoảng thời gian | Căn cứ của mốc bắt đầu |
|---|---|---|---|---|
| `covid_2020` | **COVID-19 (2020)** | dịch bệnh | 30/1/2020 - 30/6/2020 | https://www.who.int/news/item/29-06-2020-covidtimeline |
| `nga_ukraina_2022` | **Nga - Ukraine (2022)** | xung đột vũ trang | 24/2/2022 - 31/8/2022 | https://digitallibrary.un.org/record/3965290 |
| `israel_hamas_2023` | Israel - Hamas (2023) | xung đột vũ trang | 7/10/2023 - 31/12/2023 | https://press.un.org/en/2023/sgsm21981.doc.htm |
| `israel_iran_2025` | Israel - Iran (2025) | xung đột vũ trang | 13/6/2025 - 24/6/2025 | https://www.eia.gov/todayinenergy/detail.php?id=65884 |
| `iran_hormuz_2026` | **Iran - Hormuz (2026)** | xung đột vũ trang | 28/2/2026 - hết dữ liệu | https://www.everycrsreport.com/reports/R48887.html |

**Vì sao chọn câu hỏi này.** (1) Thời sự: chiến sự Iran và việc gián đoạn vận tải qua eo biển Hormuz từ 28/2/2026 vẫn đang diễn ra khi lấy dữ liệu, và giá bán lẻ dầu diesel trong nước đã lập mức cao nhất của cả giai đoạn. (2) Trả lời được bằng con số và so sánh được giữa ba cú sốc khác bản chất: một cú sốc cầu (đại dịch) và hai cú sốc cung (xung đột). (3) Không trả lời được bằng một nguồn: giá thế giới tính bằng USD/thùng hoặc USD/gallon, giá bán lẻ tính bằng đồng/lít và chỉ có trong văn bản điều hành, nên phải ghép với tỷ giá theo khoá ngày.

**Cách làm.** Bốn giai đoạn của `chay.py`, giai đoạn sau đọc tệp do giai đoạn trước ghi:

1. `nap`: kiểm tra bộ đệm dữ liệu thô, nguồn nào chưa có tệp thì tải về; đọc sáu nguồn bằng bốn lớp nạp (JSON phân trang, CSV đọc theo khối, Excel, bài viết) thành một bảng thô 254.644 dòng, 7 cột, mọi ô là chuỗi đúng như trong tệp gốc.
2. `lam-sach`: 8 bước nối tiếp, mỗi bước một lớp, xử lý kiểu dữ liệu sai, danh mục chưa chuẩn hoá, bản ghi trùng, giá trị thiếu rồi ghép các nguồn; ra bảng sạch 25.083 dòng, 20 cột, khoá (`ngay`, `ma_chuoi`).
3. `phan-tich`: năm phép phân tích dùng chung một đối tượng bảng giá, ghi bảy bảng `b1`-`b7` và 48 chỉ tiêu vào `ket_qua/tom_tat.json`.
4. `bieu-do`: 5 biểu đồ png, 300 dpi.

Ý nghĩa, đơn vị và miền giá trị của từng cột có trong `tai_lieu/tu_dien_du_lieu.md`.

## Nguon du lieu

Sáu nguồn, đều công khai và không cần đăng nhập. Cột "Dữ liệu thô" là số tệp, dung lượng và số dòng mà khâu nạp đọc được ở lần tải ngày 10/11/2026.

| Mã nguồn | Nội dung | Cách lấy và định dạng | Dữ liệu thô | Giấy phép |
|---|---|---|---|---|
| `eia` | Giá giao ngay (spot, FOB) hằng ngày của dầu thô Brent, WTI và các sản phẩm lọc dầu tại Mỹ, từ 2015 - U.S. Energy Information Administration, Open Data API v2, nhánh `petroleum/pri/spt` (https://www.eia.gov/opendata/) | REST API có phân trang (`offset`, `length`, 5.000 bản ghi mỗi trang), JSON; mỗi trang lưu thành một tệp | `data/raw/eia`: 7 trang, 10,79 MB, 32.760 dòng | Phạm vi công cộng: "U.S. government publications are in the public domain and are not subject to copyright protection" (https://www.eia.gov/about/copyrights_reuse.php) |
| `moit` | Thông báo điều hành giá xăng dầu của Bộ Công Thương: giá bán lẻ tối đa (đồng/lít) và giá thành phẩm Singapore bình quân kỳ (USD/thùng), viết trong câu văn (https://moit.gov.vn) | API tìm kiếm của cổng thông tin (JSON, phân trang 100 bài mỗi trang) rồi API nội dung từng bài; chỉ giữ bài có câu nêu giá trần; lưu JSON Lines | `data/raw/moit`: 17 tệp, 6,48 MB, 306 bài, 2.696 câu nêu giá | Chân trang ghi: ghi rõ nguồn "Cổng thông tin điện tử Bộ Công Thương" khi trích dẫn lại tin, và phải được đồng ý bằng văn bản khi khai thác. Đề tài chỉ trích số liệu giá để học tập, có ghi nguồn (xem ghi chú giấy phép bên dưới) |
| `bcp` | Tin về các kỳ điều chỉnh giá xăng dầu trên Báo điện tử Chính phủ, dùng để lấp các kỳ mà cổng Bộ Công Thương không trả về bài (https://baochinhphu.vn) | Trang tìm kiếm HTML theo bốn từ khoá, phân trang; rồi trang HTML của từng bài; chỉ giữ bài có câu nêu giá hoặc mức tăng giảm theo lít; lưu JSON Lines | `data/raw/bcp`: 126 tệp, 9,92 MB, 346 bài, 1.044 câu nêu giá | Chân trang ghi: ghi rõ nguồn "Báo Điện tử Chính phủ" hoặc "www.chinhphu.vn" khi phát hành lại thông tin |
| `ty_gia` | Tỷ giá báo cáo USD/VND cuối mỗi quý - U.S. Treasury, bộ Treasury Reporting Rates of Exchange (https://fiscaldata.treasury.gov/datasets/treasury-reporting-rates-exchange/treasury-reporting-rates-of-exchange) | REST API có phân trang (`page[number]`, `page[size]`), JSON | `data/raw/ty_gia`: 3 trang, 0,04 MB, 103 dòng (2001 - 9/2026) | Dữ liệu công khai của Chính phủ liên bang Hoa Kỳ (data.gov ghi access level: public) |
| `gpr` | Chỉ số rủi ro địa chính trị theo ngày (Geopolitical Risk Index) của Caldara và Iacoviello, đếm tỷ trọng bài báo nói về căng thẳng địa chính trị (https://www.matteoiacoviello.com/gpr.htm) | Một tệp Excel `.xls` tải từ địa chỉ cố định | `data/external/gpr`: 1 tệp, 3,28 MB, 15.281 dòng | Creative Commons BY (ghi trên trang nguồn) |
| `oxcgrt` | Chỉ số mức độ nghiêm ngặt của biện pháp chống dịch COVID-19 theo nước, theo ngày, 2020 - 2022 - Oxford COVID-19 Government Response Tracker (https://github.com/OxCGRT/covid-policy-dataset) | Một tệp CSV lớn tải từ địa chỉ cố định; đọc theo khối 50.000 dòng, chỉ lấy 4 cột | `data/external/oxcgrt`: 1 tệp, 43,84 MB, 202.760 dòng cấp quốc gia | Creative Commons BY 4.0 (ghi trong kho dữ liệu của nguồn) |

Tổng cộng 155 tệp, 74,3 MB. Tài liệu trích dẫn: Caldara, D. và Iacoviello, M. (2022), "Measuring Geopolitical Risk", American Economic Review 112(4); Hale, T. và cộng sự (2021), "A global panel database of pandemic policies (Oxford COVID-19 Government Response Tracker)", Nature Human Behaviour.

**Hợp nhất nguồn (điều kiện 1 của mục 3.11 và phụ lục hai nguồn).** Sáu nguồn được nối dọc thành một bảng thô chỉ để đi chung một dây chuyền làm sạch; việc ghép tính cho điều kiện hai nguồn là các phép `merge` thêm cột theo khoá có tên `ngay` ở bảng dưới. Mỗi phép ghép đều ghi ba số `trái, phải, kết quả` vào `ket_qua/nhat_ky.log`.

| Phép ghép | Bảng trái | Bảng phải | Khoá và kiểu ghép | Cột thêm vào | Số dòng trái / phải / kết quả |
|---|---|---|---|---|---|
| Giá với tỷ giá (`GhepNguon`) | Quan sát giá của `eia`, `moit`, `bcp`: `ngay`, `ma_chuoi`, `gia_goc`, `don_vi` | Tỷ giá của `ty_gia`, đã đưa về mỗi ngày một dòng: `ngay`, `ty_gia` | `ngay`; `how="left"`, `validate="many_to_one"` | `ty_gia`, từ đó tính `gia_usd_thung`, `gia_vnd_lit` | 25.083 / 2.332 / 25.083 |
| Giá với chỉ số bối cảnh (`GhepNguon`) | Bảng giá ở trên | Ba bảng tra cứu từ `gpr` và `oxcgrt`, mỗi ngày một dòng | `ngay`; `how="left"`, `validate="many_to_one"` | `gpr`, `phong_toa_tg`, `phong_toa_vn` | 25.083 / 2.332 / 25.083 ở cả ba lần |
| Giá bán lẻ với giá Singapore (`TyTrongGiaTheGioi`) | Giá bán lẻ quan sát trực tiếp của một mặt hàng | Giá thành phẩm Singapore bình quân kỳ của mặt hàng tương ứng | `ngay` (ngày điều hành); `how="inner"`, `validate="one_to_one"` | `ty_trong_pct`, `chenh_lech_dong_lit` | xăng E5 RON92: 302 / 223 / 220; dầu diesel: 305 / 223 / 221 |

Năm câu tự kiểm của phụ lục, áp cho cặp bảng giá - tỷ giá:

1. *Lược đồ khác nhau?* Có: bảng giá có `ma_chuoi`, `gia_goc`, `don_vi`; bảng tỷ giá chỉ có `ngay`, `ty_gia`.
2. *Khoá chung?* Cột `ngay`. Hai dòng cùng `ngay` cùng nói về một ngày lịch: bên trái là giá của một mặt hàng trong ngày đó, bên phải là tỷ giá áp cho ngày đó. Bốn kiểu viết ngày của các nguồn được đưa về cùng một kiểu `datetime` trước khi ghép.
3. *Bỏ nguồn tỷ giá thì sao?* Không quy được giá thế giới (USD/thùng, USD/gallon) và giá bán lẻ (đồng/lít) về cùng một đơn vị, nên không tính được mức thay đổi của giá thế giới theo đồng/lít ở vế 2 của câu hỏi, không tính được tỷ trọng giá Singapore trong giá bán lẻ (bảng `b3`) và không vẽ được hai loại giá trên cùng một trục (hình `h1`, `h4`).
4. *Có `merge` thật?* Có, ở `GhepNguon.ap_dung` (tệp `lam_sach.py`) và `TyTrongGiaTheGioi.theo_ky` (tệp `phan_tich.py`); không ghép theo số thứ tự dòng.
5. *Cột của nguồn thứ hai có trong kết quả?* Có: `ty_gia` tạo ra `gia_vnd_lit`, cột dùng trong các bảng `b2`, `b3` và hình `h1`, `h3`, `h4`; `gpr` dùng trong bảng `b4` và hình `h5`.

Số dòng sau khi ghép bằng đúng số dòng bảng trái (25.083) vì khoá bên phải là duy nhất: mỗi bảng tra cứu được đưa về đúng một dòng cho mỗi ngày trước khi ghép, và `validate="many_to_one"` sẽ báo lỗi nếu điều đó không còn đúng. Phần khoá không khớp được xử lý tường minh: tỷ giá chỉ có một giá trị mỗi quý nên 24.818 trên 25.083 dòng không có tỷ giá đúng ngày và được nội suy theo thời gian; phép ghép giá bán lẻ với giá Singapore chỉ giữ kỳ có cả hai giá (220 trên 302 kỳ của xăng E5 RON92), các kỳ còn lại không được tính tỷ trọng (xem bảng ở mục quyết định làm sạch).

**Năm điều kiện dữ liệu của mục 3.11.**

| Điều kiện | Bằng chứng |
|---|---|
| 1. Ít nhất hai nguồn độc lập hợp nhất bằng mã | Sáu nguồn của sáu đơn vị công bố khác nhau; ghép thêm cột bằng `merge` theo khoá `ngay` (bảng trên) |
| 2. Tệp từ 5 MB hoặc REST API có phân trang | Có cả hai: tệp OxCGRT 43,8 MB; API của EIA (7 trang) và của U.S. Treasury (3 trang) đều phân trang |
| 3. Từ 20.000 dòng sau khi hợp nhất | 25.083 dòng, 19 chuỗi giá |
| 4. Ít nhất ba trong bốn khuyết tật | Có đủ bốn: kiểu dữ liệu sai 224.367 ô, bản ghi trùng 565 dòng, danh mục chưa chuẩn hoá 960 ô, giá trị thiếu 35.777 ô (thiếu ở bảng tra cứu khi ghép) |
| 5. Có cột ngày, giấy phép cho phép dùng để học tập | Cột `ngay`; giấy phép từng nguồn ở bảng trên |

**Ghi chú về giấy phép và dữ liệu cá nhân.**

- Dữ liệu thô không nằm trong kho mã (thư mục `data/` bị `.gitignore` loại) và chỉ nộp kèm cho giảng viên theo mục 7 của đề bài; đề tài không phát hành lại bài viết của hai trang tin.
- Thứ lấy từ `moit` và `bcp` là số liệu giá trong thông tin điều hành. Theo Điều 15 Luật Sở hữu trí tuệ, tin tức thời sự thuần tuý đưa tin, văn bản hành chính và số liệu không thuộc phạm vi bảo hộ quyền tác giả. Riêng cổng Bộ Công Thương yêu cầu đồng ý bằng văn bản khi "khai thác" nội dung: nếu cần dùng ngoài mục đích học tập thì phải xin phép.
- Không có dữ liệu định danh cá nhân: chương trình không lưu trường tác giả, người đăng; chỉ giữ mã bài, tiêu đề, thời điểm đăng và thân bài. Thân bài là văn bản đã công bố nên có thể còn bút danh phóng viên ở cuối bài và tên người phát ngôn của cơ quan nhà nước; chương trình không trích và không dùng các tên này, chỉ tách câu nêu giá.
- Không vượt cơ chế chặn truy cập: chỉ gọi API và trang tìm kiếm công khai, không đăng nhập; `robots.txt` của hai trang (xem ngày 12/11/2026) không cấm các đường dẫn này; mỗi yêu cầu cách nhau ít nhất 0,5 giây và gửi kèm `User-Agent` nêu rõ mục đích học tập.

## Cach chay

Cần Python 3.11 trở lên và Git. Mọi lệnh chạy từ thư mục gốc của kho.

**Bước 1 - tải kho và tạo môi trường ảo.** Địa chỉ kho ghi trong tệp `DUONG_DAN_KHO.txt` của bài nộp. Trên Linux hoặc macOS:

```bash
git clone <dia-chi-kho> nhomNN_gia_xang_dau
cd nhomNN_gia_xang_dau
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Trên Windows (PowerShell), thay hai dòng tạo và kích hoạt môi trường ảo bằng:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Nếu PowerShell không cho chạy `Activate.ps1`, tài liệu `venv` của Python hướng dẫn chạy một lần lệnh `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`; cũng có thể bỏ bước kích hoạt và gọi thẳng `.venv\Scripts\python.exe` ở chỗ các lệnh dưới đây viết `python`, còn `pytest -q` thì viết `.venv\Scripts\python.exe -m pytest -q`.

**Bước 2 - đặt dữ liệu thô vào `data/`.** Kho mã không chứa dữ liệu. Có hai cách:

- *Để ra đúng từng con số đã nộp:* chép hai thư mục `data/raw` và `data/external` trong tệp nộp bài `MTH10605_<ma-lop>_NhomNN.zip` vào thư mục gốc của kho, giữ nguyên tên các thư mục con (`raw/eia`, `raw/moit`, `raw/bcp`, `raw/ty_gia`, `external/gpr`, `external/oxcgrt`).
- *Tải lại từ nguồn:* chạy `python chay.py --giai-doan nap` khi máy có mạng. Nguồn nào chưa có tệp trong `data/` thì chương trình tải về; lần tải ngày 10/11/2026 mất khoảng 30 phút vì phải lấy hơn 2.500 bài viết và nghỉ giữa các yêu cầu. Các nguồn được cập nhật hằng ngày nên bản tải lại có thêm ngày mới và các con số sẽ khác bản đã nộp. Có thể đặt khoá riêng cho API của EIA qua biến môi trường `EIA_API_KEY`; không đặt thì chương trình dùng khoá dùng thử `DEMO_KEY` của EIA.

**Bước 3 - kiểm thử và chạy toàn bộ.**

```bash
pytest -q
python chay.py --giai-doan tat-ca
```

`pytest -q` chạy 41 hàm kiểm thử, không cần mạng và không cần thư mục `data/`. Lệnh thứ hai chạy bốn giai đoạn nạp, làm sạch, phân tích, biểu đồ trong khoảng 10 giây, không cần mạng khi `data/` đã có dữ liệu thô, in ra bốn dòng `[xong] nap`, `[xong] lam-sach`, `[xong] phan-tich`, `[xong] bieu-do` và thoát với mã 0. Kết quả nằm trong `ket_qua/`: `tom_tat.json`, `nhat_ky.log`, 9 bảng csv và 5 hình png.

**Chạy từng giai đoạn hoặc dùng tệp cấu hình khác.**

```bash
python chay.py --giai-doan nap
python chay.py --giai-doan lam-sach
python chay.py --giai-doan phan-tich
python chay.py --giai-doan bieu-do
python chay.py --giai-doan tat-ca --cau-hinh cau_hinh.yaml
```

Mỗi giai đoạn đọc tệp do giai đoạn trước ghi ra đĩa, nên chạy lẻ hay chạy `tat-ca` đều cho cùng kết quả. Xoá `data/interim`, `data/processed` và `ket_qua` rồi chạy lại `tat-ca` sẽ tạo lại đầy đủ. Khi có lỗi (thiếu tệp, thiếu cột, cấu hình sai), chương trình in một dòng `[loi] ...` nêu rõ tệp hoặc cột và thoát với mã 1; giá trị `--giai-doan` không hợp lệ thì thoát với mã 2. Mọi ngưỡng, mốc thời gian, quy tắc chuẩn hoá và đường dẫn nằm trong `cau_hinh.yaml`: đổi một giá trị không cần mở tệp `.py` nào.

Notebook `notebooks/1.0-khao-sat-ban-dau.ipynb` chỉ ghi lại lần xem dữ liệu ban đầu; muốn mở phải cài riêng Jupyter (không có trong `requirements.txt` vì mã chạy chính không dùng).

## Cau truc thu muc

```text
nhomNN_gia_xang_dau/
|-- README.md                        bản mô tả này
|-- PHAN_CONG.md                     bảng phân công và số commit của từng thành viên
|-- requirements.txt                 thư viện phụ thuộc, ghim phiên bản bằng ==
|-- cau_hinh.yaml                    mọi đường dẫn, ngưỡng, quy tắc chuẩn hoá, sự kiện, seed
|-- chay.py                          điểm vào duy nhất (argparse), lớp ChuongTrinh
|-- .gitignore                       loại data/, ket_qua/, .venv/, __pycache__/
|-- data/
|   |-- raw/                         dữ liệu gốc tải qua API và trang tin (eia, moit, bcp, ty_gia)
|   |-- external/                    bảng tra cứu của bên thứ ba (gpr, oxcgrt)
|   |-- interim/                     bang_tho.csv, trang_thai.json - sinh ra từ mã
|   `-- processed/                   gia_xang_dau.csv (bảng sạch) - sinh ra từ mã
|-- src/
|   `-- gia_xang_dau/
|       |-- __init__.py              xuất đúng sáu hàm công khai
|       |-- cau_hinh.py              đọc và kiểm tra cau_hinh.yaml
|       |-- lop_co_so.py             ngoại lệ riêng, năm lớp trừu tượng, lớp dùng chung
|       |-- nap.py                   lớp tải về có bộ đệm, lớp nạp từng định dạng, nap_du_lieu
|       |-- lam_sach.py              tám bước làm sạch, lam_sach, thong_ke_lam_sach
|       |-- phan_tich.py             bảng giá, năm phép phân tích, tong_hop, tra_loi_cau_hoi
|       `-- bieu_do.py               năm biểu đồ, ve_bieu_do
|-- tests/
|   |-- conftest.py                  đường tìm gói và bảng mẫu dùng chung
|   |-- du_lieu_mau/                 dữ liệu giả lập nhỏ cho kiểm thử (mỗi tệp dưới 100 KB)
|   |-- test_nap.py
|   |-- test_lam_sach.py
|   |-- test_phan_tich.py
|   `-- test_bieu_do.py
|-- notebooks/
|   `-- 1.0-khao-sat-ban-dau.ipynb   khảo sát dữ liệu thô trước khi viết lớp
|-- ket_qua/
|   |-- hinh/                        h1 ... h5 (.png)
|   |-- bang/                        a1, a2, b1 ... b7 (.csv)
|   |-- tom_tat.json                 các số liệu chính
|   `-- nhat_ky.log                  nhật ký lần chạy gần nhất
`-- tai_lieu/
    |-- BAO_CAO.pdf
    |-- SLIDE.pdf
    `-- tu_dien_du_lieu.md           ý nghĩa, đơn vị, miền giá trị từng cột
```

Dữ liệu chảy một chiều: `raw` và `external` đi vào, `interim` giữ bảng thô đã nối, `processed` giữ bảng sạch, `ket_qua` giữ bảng, hình và tệp tóm tắt. Mã chỉ ghi vào `data/raw` và `data/external` ở một chỗ: bộ đệm tải về của giai đoạn `nap` (lớp `KhoDem`), và chỉ khi nguồn chưa có tệp nào; tệp đã có không bao giờ bị ghi đè hay sửa.

## Danh sach lop

59 lớp. Năm lớp trừu tượng (`abc.ABC`) nằm ở `lop_co_so.py`, mỗi lớp có từ bốn lớp con cài đè cùng một giao diện; lớp điều phối của mỗi khâu chứa một danh sách các đối tượng đó (quan hệ chứa) và gọi chúng qua giao diện chung.

| Tên lớp | Tệp | Trách nhiệm |
|---|---|---|
| `ChuongTrinh` | `chay.py` | Điều phối bốn giai đoạn nạp, làm sạch, phân tích, biểu đồ và ghi tệp tóm tắt. |
| `CauHinhNguon` | `src/gia_xang_dau/cau_hinh.py` | Khai báo một nguồn dữ liệu: tệp nằm ở đâu, đọc bằng lớp nào, tải từ đâu. |
| `QuyTacDanhMuc` | `src/gia_xang_dau/cau_hinh.py` | Một quy tắc đưa nhãn chuỗi thô về mã chuỗi chuẩn. |
| `CauHinh` | `src/gia_xang_dau/cau_hinh.py` | Nội dung cau_hinh.yaml đã kiểm tra, kèm cách đổi đường dẫn tương đối. |
| `DoAnError` | `src/gia_xang_dau/lop_co_so.py` | Gốc của mọi ngoại lệ do chương trình chủ động phát ra. |
| `CauHinhError` | `src/gia_xang_dau/lop_co_so.py` | Tệp cấu hình thiếu khoá hoặc có giá trị không hợp lệ. |
| `ThieuTepError` | `src/gia_xang_dau/lop_co_so.py` | Không tìm thấy tệp hoặc thư mục dữ liệu cần đọc. |
| `DinhDangError` | `src/gia_xang_dau/lop_co_so.py` | Nội dung tệp không đúng định dạng mong đợi. |
| `ThieuCotError` | `src/gia_xang_dau/lop_co_so.py` | Bảng dữ liệu thiếu một hoặc nhiều cột bắt buộc. |
| `BangRongError` | `src/gia_xang_dau/lop_co_so.py` | Bảng dữ liệu không có dòng nào. |
| `CotToanThieuError` | `src/gia_xang_dau/lop_co_so.py` | Một cột bắt buộc chỉ chứa giá trị thiếu. |
| `ThamSoError` | `src/gia_xang_dau/lop_co_so.py` | Tham số truyền vào hàm hoặc phương thức không hợp lệ. |
| `TaiVeError` | `src/gia_xang_dau/lop_co_so.py` | Không tải được dữ liệu từ nguồn bên ngoài. |
| `LuocDo` | `src/gia_xang_dau/lop_co_so.py` | Lược đồ cột của một bảng: cột nào bắt buộc và cột nào không được toàn thiếu. |
| `SuKien` | `src/gia_xang_dau/lop_co_so.py` | Một giai đoạn sự kiện (bối cảnh) tác động lên thị trường xăng dầu. |
| `LichSuKien` | `src/gia_xang_dau/lop_co_so.py` | Tập các sự kiện không chồng lấn nhau, tra được bối cảnh của từng ngày. |
| `KetQuaBuoc` | `src/gia_xang_dau/lop_co_so.py` | Số liệu ghi lại sau khi một bước làm sạch chạy xong. |
| `BoNap` | `src/gia_xang_dau/lop_co_so.py` | Lớp trừu tượng: nạp một nguồn dữ liệu thô và đưa về lược đồ cột chung của bảng thô. |
| `BoTai` | `src/gia_xang_dau/lop_co_so.py` | Lớp trừu tượng: tải dữ liệu thô của một nguồn về thư mục đệm khi chưa có sẵn. |
| `BuocLamSach` | `src/gia_xang_dau/lop_co_so.py` | Lớp trừu tượng: một bước trong dây chuyền làm sạch, nhận bảng và trả bảng mới kèm số liệu. |
| `PhepPhanTich` | `src/gia_xang_dau/lop_co_so.py` | Lớp trừu tượng: một phép phân tích trả lời một phần của câu hỏi. |
| `BieuDo` | `src/gia_xang_dau/lop_co_so.py` | Lớp trừu tượng: một biểu đồ phục vụ một phần của câu hỏi phân tích. |
| `KhachHttp` | `src/gia_xang_dau/nap.py` | Gửi yêu cầu HTTP GET có giãn cách giữa các lần gọi, thử lại và giới hạn thời gian. |
| `TaiApiPhanTrang` | `src/gia_xang_dau/nap.py` | Tải một REST API trả JSON có phân trang, mỗi trang lưu thành một tệp. |
| `TaiTep` | `src/gia_xang_dau/nap.py` | Tải một tệp đơn lẻ từ một địa chỉ cố định. |
| `TaiBaiViet` | `src/gia_xang_dau/nap.py` | Lớp trừu tượng: tải bài viết của một trang tin, liệt kê qua tìm kiếm phân trang rồi lấy từng bài. |
| `TaiBaiVietApi` | `src/gia_xang_dau/nap.py` | Tải bài viết từ cổng thông tin có API JSON: tìm kiếm phân trang và chi tiết bài. |
| `TaiBaiVietHtml` | `src/gia_xang_dau/nap.py` | Tải bài viết từ trang báo chỉ trả HTML: trang tìm kiếm và trang bài đều là HTML. |
| `KhoDem` | `src/gia_xang_dau/nap.py` | Bộ đệm dữ liệu thô: chỉ tải khi thư mục dữ liệu chưa có tệp của nguồn. |
| `NapJsonTrang` | `src/gia_xang_dau/nap.py` | Nạp các tệp JSON là từng trang kết quả của một API. |
| `NapCsvKhoi` | `src/gia_xang_dau/nap.py` | Nạp tệp CSV lớn bằng cách đọc từng khối và chỉ giữ cột, dòng cần dùng. |
| `NapExcel` | `src/gia_xang_dau/nap.py` | Nạp một trang tính Excel. |
| `NapBaiViet` | `src/gia_xang_dau/nap.py` | Nạp bài viết (JSON Lines) và tách các câu nêu giá bằng biểu thức chính quy. |
| `BoNapNhieuNguon` | `src/gia_xang_dau/nap.py` | Nạp mọi nguồn khai báo trong cấu hình và nối dọc thành một bảng thô. |
| `BoGiaTriThieu` | `src/gia_xang_dau/lam_sach.py` | Loại dòng mà ô ngày hoặc ô giá trị rỗng hay chỉ chứa ký hiệu thiếu. |
| `ChuyenKieuNgay` | `src/gia_xang_dau/lam_sach.py` | Đổi cột ngày từ chuỗi nhiều định dạng sang kiểu ngày. |
| `LocKhoangThoiGian` | `src/gia_xang_dau/lam_sach.py` | Chỉ giữ quan sát giá nằm trong khoảng phân tích khai báo ở cấu hình. |
| `ChuanHoaDanhMuc` | `src/gia_xang_dau/lam_sach.py` | Đưa nhãn chuỗi viết nhiều kiểu về một mã chuỗi chuẩn theo quy tắc trong cấu hình. |
| `ChuyenKieuSo` | `src/gia_xang_dau/lam_sach.py` | Đổi cột giá trị từ chuỗi (kiểu viết số của từng nguồn) sang số thực. |
| `BoBanGhiTrung` | `src/gia_xang_dau/lam_sach.py` | Loại bản ghi trùng khoá (ngày, mã chuỗi), giữ bản của nguồn được ưu tiên. |
| `SuyRaGiaTruoc` | `src/gia_xang_dau/lam_sach.py` | Bổ sung quan sát "giá ngay trước kỳ điều chỉnh" suy từ mức tăng giảm nêu trong câu. |
| `GhepNguon` | `src/gia_xang_dau/lam_sach.py` | Ghép bảng quan sát giá với các bảng tra cứu theo khoá ngày và tính cột quy đổi. |
| `BoLamSach` | `src/gia_xang_dau/lam_sach.py` | Dây chuyền làm sạch: chạy lần lượt các bước và gom số liệu của từng bước. |
| `ThongKeLamSach` | `src/gia_xang_dau/lam_sach.py` | Tính bốn con số thống kê làm sạch từ bảng trước và bảng sau khi làm sạch. |
| `BangGia` | `src/gia_xang_dau/phan_tich.py` | Bảng giá đã làm sạch, kèm các góc nhìn dùng chung cho mọi phép phân tích. |
| `BoTongHop` | `src/gia_xang_dau/phan_tich.py` | Tổng hợp thống kê mô tả của các cột giá trị theo nhóm. |
| `NhanSuKien` | `src/gia_xang_dau/phan_tich.py` | Gắn tên hiển thị và thứ tự thời gian của sự kiện vào một bảng kết quả. |
| `BienDongTheoBoiCanh` | `src/gia_xang_dau/phan_tich.py` | Độ biến động của giá thế giới trong từng bối cảnh, so với lúc bình thường. |
| `CuSocGia` | `src/gia_xang_dau/phan_tich.py` | Mức thay đổi lớn nhất của giá thế giới và giá bán lẻ trong từng sự kiện. |
| `TyTrongGiaTheGioi` | `src/gia_xang_dau/phan_tich.py` | Tỷ trọng giá thành phẩm thế giới (Singapore) trong giá bán lẻ cùng mặt hàng. |
| `TuongQuanBoiCanh` | `src/gia_xang_dau/phan_tich.py` | Tương quan theo tháng giữa giá, độ biến động và các chỉ số bối cảnh. |
| `DoPhuGiaBanLe` | `src/gia_xang_dau/phan_tich.py` | Độ phủ của chuỗi giá bán lẻ: số kỳ quan sát được và số khoảng bị thiếu kỳ điều hành. |
| `BoTraLoi` | `src/gia_xang_dau/phan_tich.py` | Gộp các phép phân tích thành câu trả lời cho câu hỏi của đề tài. |
| `BieuDoDienBienGia` | `src/gia_xang_dau/bieu_do.py` | Biểu đồ đường: giá thế giới và giá bán lẻ theo thời gian, tô nền các giai đoạn sự kiện. |
| `BieuDoBienDong` | `src/gia_xang_dau/bieu_do.py` | Biểu đồ cột ghép: độ biến động quy năm của giá thế giới trong từng bối cảnh. |
| `BieuDoCuSoc` | `src/gia_xang_dau/bieu_do.py` | Biểu đồ cột ghép: mức thay đổi giá lớn nhất của giá thế giới và giá bán lẻ trong sự kiện. |
| `BieuDoTyTrong` | `src/gia_xang_dau/bieu_do.py` | Biểu đồ đường: tỷ trọng giá thành phẩm thế giới trong giá bán lẻ theo từng kỳ điều hành. |
| `BieuDoGprBienDong` | `src/gia_xang_dau/bieu_do.py` | Biểu đồ phân tán: chỉ số rủi ro địa chính trị và độ biến động giá thế giới theo tháng. |
| `BoVeBieuDo` | `src/gia_xang_dau/bieu_do.py` | Dựng toàn bộ biểu đồ của đề tài từ bảng sạch và lưu vào một thư mục. |

**Kế thừa.** `BoTai` có 5 lớp con (`TaiApiPhanTrang`, `TaiTep`, `TaiBaiViet`, `TaiBaiVietApi`, `TaiBaiVietHtml`); `BoNap` có 4 lớp con (`NapJsonTrang`, `NapCsvKhoi`, `NapExcel`, `NapBaiViet`); `BuocLamSach` có 8 lớp con (`BoGiaTriThieu`, `ChuyenKieuNgay`, `LocKhoangThoiGian`, `ChuanHoaDanhMuc`, `ChuyenKieuSo`, `BoBanGhiTrung`, `SuyRaGiaTruoc`, `GhepNguon`); `PhepPhanTich` có 5 lớp con (`BienDongTheoBoiCanh`, `CuSocGia`, `TyTrongGiaTheGioi`, `TuongQuanBoiCanh`, `DoPhuGiaBanLe`); `BieuDo` có 5 lớp con (`BieuDoDienBienGia`, `BieuDoBienDong`, `BieuDoCuSoc`, `BieuDoTyTrong`, `BieuDoGprBienDong`). Trong đó `TaiBaiViet` là lớp trừu tượng trung gian: nó giữ khung chung của việc tải bài viết và để hai lớp con lo phần khác nhau giữa trang có API và trang chỉ có HTML. Tám lớp ngoại lệ kế thừa `DoAnError`, lớp này kế thừa `Exception`.

**Quan hệ chứa.** `KhoDem` chứa `KhachHttp` và tạo các `BoTai`; mỗi `BoTai` nhận một `KhachHttp` qua `__init__`; `BoNapNhieuNguon` chứa một `BoNap` cho mỗi nguồn; `BoLamSach` chứa danh sách `BuocLamSach`; `BoTraLoi` chứa một `BangGia` và danh sách `PhepPhanTich`; mỗi `PhepPhanTich` nhận `BangGia` qua `__init__`; `BoVeBieuDo` chứa danh sách `BieuDo`, mỗi biểu đồ nhận một `BangGia` hoặc một `PhepPhanTich`; `CauHinh` tạo ra `LichSuKien` chứa các `SuKien`.

**Phương thức đặc biệt, thuộc tính, phương thức tĩnh (đều được gọi trong mã chạy chính).** `CauHinh.__getitem__` (đọc khoá dạng `cau_hinh["lam_sach.kieu_so"]`); `__iter__` của `BoLamSach`, `BoVeBieuDo`, `LichSuKien`, `BoNapNhieuNguon`, `LuocDo` (duyệt bước, biểu đồ, sự kiện, bộ nạp, cột) và `__len__` của ba lớp đầu; `SuKien.__lt__` (sắp sự kiện theo ngày bắt đầu); `BangGia.__contains__` (`"brent" in bang_gia`), `BangGia.__len__`; `__repr__` của `CauHinh`, `BangGia`, `BoNap`, `BoTai`, `BuocLamSach`, `BieuDo` (dùng trong nhật ký và thông báo lỗi). `@property`: `CauHinh.seed`, `CauHinh.cac_nguon`, `BangGia.cac_chuoi`, `KetQuaBuoc.so_dong_loai`... `@classmethod`: `CauHinh.tu_tep`, `BoLamSach.buoc_mac_dinh`, `BoNapNhieuNguon.tao_bo_nap`. `@staticmethod`: `LuocDo.la_thieu`, `ChuyenKieuSo.doi_so`, `CuSocGia.do_cu_soc`, `BieuDo.dinh_dang_so`...

Sáu hàm công khai trong `src/gia_xang_dau/__init__.py` là lớp vỏ mỏng, mỗi hàm tạo đối tượng rồi gọi một phương thức: `nap_du_lieu` gọi `BoNapNhieuNguon.nap`, `lam_sach` gọi `BoLamSach.chay`, `thong_ke_lam_sach` gọi `ThongKeLamSach.tinh`, `tong_hop` gọi `BoTongHop.theo`, `tra_loi_cau_hoi` gọi `BoTraLoi.tra_loi`, `ve_bieu_do` gọi `BoVeBieuDo.ve_tat_ca`.

## Quyet dinh lam sach du lieu

Bảng thô có 254.644 dòng; bảng sạch có 25.083 dòng. Bốn con số của `thong_ke_lam_sach` (cũng là mục `thong_ke_lam_sach` trong `tom_tat.json`): `kieu_sai` = 224.367, `danh_muc_chuan_hoa` = 960, `ban_ghi_trung` = 565, `gia_tri_thieu` = 35.777. Bốn dòng đầu của bảng dưới ứng với bốn con số đó; các dòng sau là quyết định khác, có đếm và ghi nhật ký nhưng không tính vào bốn con số.

| Khuyết tật gặp phải | Cách xử lý | Lý do chọn cách đó |
|---|---|---|
| **Kiểu dữ liệu sai** - 224.367 ô. Ngày là chuỗi viết bốn kiểu: `20200115` (218.041 ô của GPR và OxCGRT), "15 giờ 30 ngày 15 tháng 01 năm 2020" (2.696 ô của Bộ Công Thương), `2026-11-05T14:50:00+07:00` (1.044 ô của báo), còn lại là `2020-01-15`. Số viết kiểu Việt Nam ở 2.586 ô: `19.845` nghĩa là 19845 đồng (dấu chấm ngăn hàng nghìn), `81,252` nghĩa là 81 phẩy 252 USD (dấu phẩy thập phân) | `ChuyenKieuNgay` thử lần lượt bốn biểu thức chính quy khai báo trong cấu hình; `ChuyenKieuSo` đổi theo kiểu viết khai báo cho từng nguồn, rồi đối chiếu khoảng hợp lý của đơn vị: 22 ô nằm ngoài khoảng được đọc lại theo kiểu chuẩn. Không ô nào bị loại vì không đổi được | Để pandas tự đoán thì `19.845` thành số 19 phẩy 845, sai một nghìn lần mà không báo lỗi, và `20200115` bị hiểu là một số nguyên. Khai báo kiểu viết theo nguồn làm cho việc đổi kiểu kiểm tra lại được; bước đối chiếu khoảng hợp lý bắt được chỗ chính nguồn viết không nhất quán (có bài viết `96.361 USD/thùng`) |
| **Danh mục chưa chuẩn hoá** - 960 ô nhãn viết khác nhãn chuẩn. Nhãn chuẩn "Dầu diesel 0.05S" còn được viết "Dầu điêzen 0.05S", "dầu diezel 0.05S", "Dầu diesl 0.05S"; nhãn chuẩn "Xăng E5RON92" còn được viết "xăng E5RON92", "xăng E5 RON92", "xăng E5"; tên mặt hàng còn đổi theo thời gian (RON95-III rồi E10 RON95-III) | `ChuanHoaDanhMuc` so nhãn đã đưa về chữ thường, Unicode NFC với 19 quy tắc (biểu thức chính quy kèm đơn vị và nguồn) trong mục `danh_muc` của cấu hình, gán `ma_chuoi` chuẩn. 2.791 dòng có nhãn ngoài danh mục phân tích bị loại (2.214 dòng propan của EIA, còn lại chủ yếu là dầu mazut tính theo đồng/kg) | Không chuẩn hoá thì một mặt hàng tách thành nhiều chuỗi ngắn và mọi phép `groupby` đếm thiếu. Quy tắc đặt trong cấu hình để thêm một cách viết mới không phải sửa mã. Xăng E10 RON95-III là sản phẩm khác, rẻ hơn, nên được giữ thành chuỗi riêng chứ không nối vào RON95-III |
| **Bản ghi trùng** - 565 dòng trùng khoá (`ngay`, `ma_chuoi`) bị loại: 561 dòng của báo và 4 dòng của Bộ. 533 dòng là giá của báo trùng khoá với thông báo của Bộ Công Thương; 32 dòng lặp lại trong cùng một nguồn (28 dòng là giá được nhắc lại trong cùng một bài, 4 dòng thuộc hai bài báo đăng cùng ngày 11/3/2026) | `BoBanGhiTrung` sắp theo thứ tự ưu tiên nguồn khai báo trong cấu hình (Bộ Công Thương, rồi báo, rồi EIA) và giữ dòng đầu của mỗi khoá; cùng nguồn thì giữ câu xuất hiện trước trong bài | Thông báo của Bộ là văn bản gốc, báo chỉ đưa lại và hay làm tròn. Trong 533 dòng của báo trùng khoá với Bộ, 520 dòng bằng đúng giá của Bộ, 8 dòng lệch không quá 10 đơn vị (7 dòng giá bán lẻ bị báo làm tròn xuống, 1 dòng giá Singapore lệch 0,1 USD/thùng) và 5 dòng lệch hơn vì báo nhắc lại giá của kỳ trước: lấy trung bình sẽ tạo ra một mức giá không có thật. Giữ cả hai thì kỳ đó được đếm hai lần. Ngày 11/3/2026 báo đăng hai bài cho hai kỳ điều hành liên tiếp, nên khoá theo ngày chỉ giữ được một kỳ; mức giá của kỳ kia vẫn có trong bảng, là dòng suy ra của ngày 10/3/2026. Tổng cộng 17 dòng bị loại mang giá khác dòng được giữ, trong đó 9 dòng lệch quá 10 đồng |
| **Giá trị thiếu** - 35.777 ô. Ô `ngay`, `gia_tri` rỗng: 0 ô trong bộ dữ liệu này (bước `BoGiaTriThieu` vẫn chạy và có kiểm thử). Phần thiếu thật sự xuất hiện khi ghép: bảng tra cứu không có giá trị đúng ngày quan sát ở 35.777 ô (tỷ giá 24.818, GPR 25, hai chỉ số phong toả 10.934) | `GhepNguon` điền theo quy tắc riêng của từng cột, khai báo trong mục `tra_cuu`: tỷ giá nội suy tuyến tính theo thời gian giữa hai mốc cuối quý; GPR giữ giá trị cuối tối đa 7 ngày; chỉ số phong toả bằng 0 trước ngày đầu của nguồn (1/1/2020). 22.474 ô chỉ số phong toả sau 31/12/2022 để nguyên là thiếu | Tỷ giá đổi chậm nên nội suy giữa hai mốc quý sai ít hơn nhiều so với dùng một tỷ giá cho cả năm; bỏ dòng thiếu tỷ giá thì mất gần hết bảng. Sau 2022 nguồn OxCGRT ngừng cập nhật: điền 0 là khẳng định một điều nguồn không nói, nên để thiếu và các phép tính tự bỏ qua |
| Quan sát nằm ngoài khoảng phân tích - 8.914 dòng giá trước 1/1/2018 (EIA 8.359, Bộ Công Thương 548, báo 7) | `LocKhoangThoiGian` loại dòng của nguồn giá; nguồn tra cứu được giữ nguyên để còn mốc nội suy trước khoảng | Xăng E5 RON92 thay xăng RON92 từ 1/1/2018; lấy trước mốc đó thì chuỗi giá bán lẻ chính đổi mặt hàng giữa chừng |
| Thiếu thông báo của một số kỳ điều hành ở cả hai nguồn | `SuyRaGiaTruoc` dùng mức tăng giảm nêu ngay trong câu ("giảm 778 đồng/lít so với giá bán lẻ hiện hành") để thêm 853 quan sát "giá của ngày liền trước kỳ điều chỉnh", đánh dấu `suy_ra = True`. Trong 898 câu có nêu mức tăng giảm, bỏ 35 câu chỉ nhắc lại kỳ trước và 10 câu mà ngày liền trước đã có quan sát | Giá bán lẻ là chuỗi bậc thang: thiếu một kỳ thì mức giá bị giữ sai cho tới kỳ sau. Dòng suy ra là phép trừ từ chính câu văn của nguồn, không phải ước lượng. Các chỗ vẫn còn thiếu được đếm ở bảng `b5` ("khoảng thiếu kỳ") |
| Giá âm: dầu WTI ngày 20/4/2020 là -36,98 USD/thùng | Giữ nguyên trong bảng sạch; phép tính lợi suất log bỏ phiên đó và phiên liền sau | Đây là giá thật của phiên đó, không phải lỗi nhập liệu; xoá đi là sửa dữ liệu. Nhưng không lấy được logarit của số âm |
| Ngày của bài báo là ngày đăng, không phải ngày giá có hiệu lực | Giữ ngày đăng; khi trùng khoá với thông báo của Bộ thì dòng của Bộ (có ngày hiệu lực) được giữ | Ngày đăng và ngày hiệu lực có thể lệch một ngày; đề tài đo theo kỳ và theo tháng nên chấp nhận sai số này thay vì đoán ngày hiệu lực từ câu văn của báo |

| Bước | Lớp | Dòng vào | Dòng ra | Dòng loại | Dòng thêm | Ô xử lý | Tính vào khoá |
|---|---|---|---|---|---|---|---|
| 1 | `BoGiaTriThieu` | 254.644 | 254.644 | 0 | 0 | 0 | `gia_tri_thieu` |
| 2 | `ChuyenKieuNgay` | 254.644 | 254.644 | 0 | 0 | 221.781 | `kieu_sai` |
| 3 | `LocKhoangThoiGian` | 254.644 | 245.730 | 8.914 | 0 | 0 |  |
| 4 | `ChuanHoaDanhMuc` | 245.730 | 242.939 | 2.791 | 0 | 960 | `danh_muc_chuan_hoa` |
| 5 | `ChuyenKieuSo` | 242.939 | 242.939 | 0 | 0 | 2.586 | `kieu_sai` |
| 6 | `BoBanGhiTrung` | 242.939 | 242.374 | 565 | 0 | 565 | `ban_ghi_trung` |
| 7 | `SuyRaGiaTruoc` | 242.374 | 243.227 | 0 | 853 | 853 |  |
| 8 | `GhepNguon` | 243.227 | 25.083 | 218.144 | 0 | 35.777 | `gia_tri_thieu` |

Ở bước 8, 218.144 dòng "bị loại" là dòng của ba nguồn tra cứu: sau khi ghép chúng trở thành cột của bảng giá nên không còn là dòng riêng. Bảng này cũng được ghi ra `ket_qua/bang/a1_cac_buoc_lam_sach.csv`; `a2_mau_doi_chieu.csv` là 40 giá rút ngẫu nhiên theo seed để đối chiếu tay với trang nguồn.

## Ket qua chinh

**Vế 1 - giá dầu thế giới biến động mạnh gấp mấy lần.** Lúc bình thường, độ biến động quy năm của dầu Brent là 31,5%. Trong đại dịch COVID-19 con số đó là 173,8%, gấp 5,52 lần; trong chiến sự Nga - Ukraine là 56,5%, gấp 1,79 lần; trong chiến sự Iran - Hormuz là 76,4%, gấp 2,43 lần. Bối cảnh biến động mạnh nhất là COVID-19 (2020).

| Bối cảnh | Số phiên | Độ biến động quy năm của Brent (%) | Gấp mấy lần lúc bình thường |
|---|---|---|---|
| Bình thường | 1.766 | 31,5 | 1,00 |
| COVID-19 (2020) | 105 | 173,8 | 5,52 |
| Nga - Ukraine (2022) | 130 | 56,5 | 1,79 |
| Israel - Hamas (2023) | 58 | 38,9 | 1,24 |
| Israel - Iran (2025) | 8 | 78,1 | 2,48 |
| Iran - Hormuz (2026) | 172 | 76,4 | 2,43 |

**Vế 2 - giá bán lẻ tăng giảm bằng bao nhiêu phần.** Xăng E5 RON92 đi theo khoảng sáu đến bảy phần mười mức thay đổi của giá Brent ở cả ba cú sốc: tỷ lệ truyền dẫn 0,59; 0,67; 0,68. Dầu diesel giảm ít hơn dầu thô khi giá lao dốc năm 2020 (tỷ lệ 0,53) nhưng tăng mạnh hơn dầu thô trong hai cuộc xung đột (tỷ lệ 1,32 và 1,67).

| Sự kiện | Brent, bình quân 7 ngày, đồng/lít | Xăng E5 RON92 | Tỷ lệ truyền dẫn | Dầu diesel 0.05S | Tỷ lệ truyền dẫn |
|---|---|---|---|---|---|
| COVID-19 (2020) | -75,6% (đến 27/4/2020) | -44,9%: 19.845 -> 10.942 đồng/lít (28/4/2020) | 0,59 | -40,4%: 16.548 -> 9.857 đồng/lít (13/5/2020) | 0,53 |
| Nga - Ukraine (2022) | +33,6% (đến 14/6/2022) | +22,6%: 25.532 -> 31.302 đồng/lít (21/6/2022) | 0,67 | +44,3%: 20.801 -> 30.019 đồng/lít (21/6/2022) | 1,32 |
| Iran - Hormuz (2026) | +79,5% (đến 8/10/2026) | +54,2%: 19.523 -> 30.114 đồng/lít (24/3/2026) | 0,68 | +132,3%: 19.279 -> 44.788 đồng/lít (7/4/2026) | 1,67 |

Giá bán lẻ cao nhất cả giai đoạn: xăng E5 RON92 31.302 đồng/lít (ngày 21/6/2022); dầu diesel 44.788 đồng/lít (ghi nhận ở ngày 7/4/2026, là giá của ngay trước kỳ điều chỉnh 8/4/2026).

**Bổ trợ - tỷ trọng giá thế giới trong giá bán lẻ.** Giá thành phẩm Singapore chiếm bình quân 60,0% giá bán lẻ xăng E5 RON92 lúc bình thường, 39,8% trong COVID-19, 66,9% trong chiến sự Nga - Ukraine và 89,0% trong chiến sự Iran - Hormuz. Với dầu diesel: 72,9%; 54,0%; 80,6%; 93,8%. Phần chênh giữa giá bán lẻ và giá Singapore của xăng E5 RON92 (thuế, phí, chi phí và lợi nhuận định mức, quỹ bình ổn) bình quân 7.900 đồng/lít lúc bình thường, 8.400 và 9.200 đồng/lít trong hai cú sốc đầu, nhưng chỉ còn 2.600 đồng/lít trong năm 2026 (bảng `b3`).

**Bổ trợ - tương quan theo tháng.** Giữa chỉ số GPR và độ biến động của Brent: 0,13 (106 tháng) - gần như không đi cùng nhau. Giữa chỉ số phong toả toàn cầu và giá Brent: -0,64; giữa chỉ số phong toả và độ biến động: 0,28 (36 tháng của 2020 - 2022). Giữa mức thay đổi theo tháng của giá Brent và giá xăng E5 RON92: 0,73 cùng tháng và 0,50 khi lấy giá Brent của tháng trước.

**Độ phủ của chuỗi giá bán lẻ.** Quan sát trực tiếp được 302 kỳ điều hành của xăng E5 RON92 và 305 kỳ của dầu diesel; còn 27 và 22 khoảng mà giữa hai quan sát có ít nhất một kỳ không thu thập được.

**Giới hạn cần đọc cùng kết quả.**

- Giá Brent ở đây là giá giao ngay của hàng thực (chuỗi `RBRTE` của EIA), không phải giá hợp đồng tương lai mà báo chí thường dẫn. Năm 2026 hai giá này tách xa nhau, nên mức tăng +79,5% là của giá giao ngay.
- Tỷ lệ truyền dẫn so hai mức cực trị trong cùng một sự kiện, và hai cực trị có thể rơi vào hai thời điểm khác nhau. Năm 2026 giá Brent có hai đợt lên đỉnh cao xấp xỉ nhau, đầu tháng 4 và đầu tháng 10 (hình `h1`); bình quân 7 ngày đạt mức cao nhất ngày 8/10/2026, còn giá bán lẻ lập đỉnh cuối tháng 3 - đầu tháng 4.
- Giá bán lẻ còn chịu chính sách thuế và quỹ bình ổn. Từ 24 giờ ngày 26/3/2026, Quyết định 482/QĐ-TTg đưa thuế bảo vệ môi trường với xăng, dầu diesel về 0 đồng/lít, thuế tiêu thụ đặc biệt với xăng về 0% và cho xăng, dầu diesel không phải tính nộp thuế giá trị gia tăng; ngày 12/4/2026 Quốc hội kéo dài chính sách này đến hết 30/6/2026 (nhóm chưa kiểm tra chính sách sau ngày đó). Tỷ lệ truyền dẫn vì vậy mô tả kết quả cuối cùng tới người mua, không tách được phần của thị trường và phần của chính sách.
- Số liệu của nguồn được giữ nguyên, kể cả quan sát bất thường: giá Brent ngày 2/10/2026 là 135,51 USD/thùng trong khi phiên liền trước là 114,82 và phiên liền sau là 125,51. Đỉnh tháng 10 dựa nhiều vào quan sát này; nếu nguồn đính chính thì ngày đạt đỉnh có thể đổi.
- Bối cảnh Israel - Iran (2025) chỉ có 8 phiên; con số của nó không đủ để so sánh.
- Hệ số tương quan chỉ mô tả hai chuỗi có đi cùng nhau hay không, không nói quan hệ nhân quả; đề tài không làm kiểm định thống kê.
- Tỷ giá là tỷ giá báo cáo cuối quý của U.S. Treasury được nội suy theo ngày, không phải tỷ giá giao dịch hằng ngày; ngày của giá thế giới theo phiên giao dịch ở Mỹ, ngày của giá bán lẻ theo giờ Việt Nam.

**Toàn bộ mục `ket_qua` của `ket_qua/tom_tat.json`** (48 khoá; số viết đúng như trong tệp). Ngoài ra: `so_dong_tho` = 254644, `so_dong_sach` = 25083, `thong_ke_lam_sach` = `{"gia_tri_thieu": 35777, "ban_ghi_trung": 565, "kieu_sai": 224367, "danh_muc_chuan_hoa": 960}`.

| Khoá | Giá trị |
|---|---|
| `bien_dong_brent_binh_thuong_pct_nam` | `31.5` |
| `bien_dong_brent_covid_2020_pct_nam` | `173.8` |
| `bien_dong_brent_covid_2020_gap_lan` | `5.52` |
| `bien_dong_brent_nga_ukraina_2022_pct_nam` | `56.5` |
| `bien_dong_brent_nga_ukraina_2022_gap_lan` | `1.79` |
| `bien_dong_brent_israel_hamas_2023_pct_nam` | `38.9` |
| `bien_dong_brent_israel_hamas_2023_gap_lan` | `1.24` |
| `bien_dong_brent_israel_iran_2025_pct_nam` | `78.1` |
| `bien_dong_brent_israel_iran_2025_gap_lan` | `2.48` |
| `bien_dong_brent_iran_hormuz_2026_pct_nam` | `76.4` |
| `bien_dong_brent_iran_hormuz_2026_gap_lan` | `2.43` |
| `boi_canh_bien_dong_manh_nhat` | `"COVID-19 (2020)"` |
| `brent_thay_doi_pct_covid_2020` | `-75.6` |
| `vn_e5ron92_thay_doi_pct_covid_2020` | `-44.9` |
| `truyen_dan_vn_e5ron92_covid_2020` | `0.59` |
| `vn_diesel_thay_doi_pct_covid_2020` | `-40.4` |
| `truyen_dan_vn_diesel_covid_2020` | `0.53` |
| `brent_thay_doi_pct_nga_ukraina_2022` | `33.6` |
| `vn_e5ron92_thay_doi_pct_nga_ukraina_2022` | `22.6` |
| `truyen_dan_vn_e5ron92_nga_ukraina_2022` | `0.67` |
| `vn_diesel_thay_doi_pct_nga_ukraina_2022` | `44.3` |
| `truyen_dan_vn_diesel_nga_ukraina_2022` | `1.32` |
| `brent_thay_doi_pct_iran_hormuz_2026` | `79.5` |
| `vn_e5ron92_thay_doi_pct_iran_hormuz_2026` | `54.2` |
| `truyen_dan_vn_e5ron92_iran_hormuz_2026` | `0.68` |
| `vn_diesel_thay_doi_pct_iran_hormuz_2026` | `132.3` |
| `truyen_dan_vn_diesel_iran_hormuz_2026` | `1.67` |
| `vn_e5ron92_cao_nhat_dong_lit` | `31302` |
| `vn_e5ron92_ngay_cao_nhat` | `"2022-06-21"` |
| `vn_diesel_cao_nhat_dong_lit` | `44788` |
| `vn_diesel_ngay_cao_nhat` | `"2026-04-07"` |
| `ty_trong_gia_singapore_vn_e5ron92_binh_thuong_pct` | `60.0` |
| `ty_trong_gia_singapore_vn_e5ron92_covid_2020_pct` | `39.8` |
| `ty_trong_gia_singapore_vn_e5ron92_nga_ukraina_2022_pct` | `66.9` |
| `ty_trong_gia_singapore_vn_e5ron92_iran_hormuz_2026_pct` | `89.0` |
| `ty_trong_gia_singapore_vn_diesel_binh_thuong_pct` | `72.9` |
| `ty_trong_gia_singapore_vn_diesel_covid_2020_pct` | `54.0` |
| `ty_trong_gia_singapore_vn_diesel_nga_ukraina_2022_pct` | `80.6` |
| `ty_trong_gia_singapore_vn_diesel_iran_hormuz_2026_pct` | `93.8` |
| `tuong_quan_gpr_va_bien_dong_gia_the_gioi` | `0.13` |
| `tuong_quan_phong_toa_va_gia_the_gioi` | `-0.64` |
| `tuong_quan_phong_toa_va_bien_dong_gia_the_gioi` | `0.28` |
| `tuong_quan_thay_doi_gia_the_gioi_va_ban_le_cung_thang` | `0.73` |
| `tuong_quan_thay_doi_gia_the_gioi_thang_truoc_va_ban_le` | `0.5` |
| `so_ky_quan_sat_vn_e5ron92` | `302` |
| `so_khoang_thieu_ky_vn_e5ron92` | `27` |
| `so_ky_quan_sat_vn_diesel` | `305` |
| `so_khoang_thieu_ky_vn_diesel` | `22` |

## Moi truong

- Python 3.11.18 trên Ubuntu 24.04.5 LTS (x86-64) là môi trường của lần chạy sinh ra các con số ở trên; môi trường ảo dựng mới từ `requirements.txt`.
- Đã chạy thử thêm với Python 3.12.3, 3.13.18 và 3.14.6 trên cùng hệ điều hành: `pytest -q` qua hết và `python chay.py --giai-doan tat-ca` cho các bảng, hình giống hệt.
- Python 3.10 trở xuống không cài được vì các phiên bản thư viện đã ghim cần Python 3.11 trở lên.
- Chưa chạy thử trên Windows và macOS. Để kết quả không phụ thuộc hệ điều hành ở ký tự xuống dòng, mọi tệp csv được ghi với `lineterminator="\n"`; mặc định của pandas là ký tự xuống dòng của hệ điều hành, tức `\r\n` trên Windows.
- Thư viện chính (ghim trong `requirements.txt`): pandas 2.3.3, NumPy 2.3.5, matplotlib 3.10.8, PyYAML 6.0.3, requests 2.32.5, xlrd 2.0.2, pytest 8.4.2.
- `requirements.txt` là kết quả `pip freeze` của môi trường ảo nói trên, gồm 25 gói. Gói `colorama` có mặt vì `pytest` khai báo cần nó trên Windows (`colorama>=0.4; sys_platform == "win32"`); ghim sẵn để danh sách gói cài ra giống nhau trên mọi hệ điều hành.
- Seed cố định 20262 (mục `du_an.seed` của `cau_hinh.yaml`), dùng khi rút mẫu đối chiếu. Chạy hai lần liên tiếp cho các tệp csv và png giống nhau từng byte; `tom_tat.json` chỉ khác ở `thoi_gian_chay_giay`.
