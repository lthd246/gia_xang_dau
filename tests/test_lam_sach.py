"""Kiem thu lam_sach va thong_ke_lam_sach: luoc do, tinh lap lai, bat bien, tinh huong bien."""

from __future__ import annotations

import pandas as pd
import pytest

from gia_xang_dau import lam_sach, thong_ke_lam_sach
from gia_xang_dau.lop_co_so import BangRongError, CotToanThieuError, ThamSoError, ThieuCotError

COT_THO = ["nguon", "tep", "ngay", "chuoi", "gia_tri", "don_vi", "van_ban"]
COT_SACH = [
    "ngay",
    "nam",
    "thang",
    "ma_chuoi",
    "ten_chuoi",
    "thi_truong",
    "nhom_hang",
    "nguon",
    "suy_ra",
    "gia_goc",
    "don_vi",
    "ty_gia",
    "gia_usd_thung",
    "gia_vnd_lit",
    "thay_doi_pct",
    "gpr",
    "phong_toa_tg",
    "phong_toa_vn",
    "su_kien",
    "loai_boi_canh",
]
CAU_E5 = "Xăng E5RON92: không cao hơn 19.845 đồng/lít (giảm 30 đồng/lít so với giá hiện hành);"
# cau diesel bi cat giua chung (het cua so ky tu sau gia): muc giam khong doc tron duoc
CAU_DIESEL = "Dầu điêzen 0.05S: không cao hơn 16.540 đồng/lít (giảm 1.030 đồng/lí"
CAU_BAO = "xăng E5RON92 không cao hơn 19.845 đồng/lít (giảm 30 đồng/lít so với giá hiện hành)"


def bang_tho_nho() -> pd.DataFrame:
    """Bang tho 14 dong soan tay, moi dong mang mot tinh huong de tinh tay so lieu lam sach."""
    ngay_moit = "15 giờ 00’ ngày 15 tháng 01 năm 2020"
    dong = [
        # nguon, ngay, chuoi, gia_tri, don_vi, van_ban
        ("eia", "2020-01-02", "RBRTE", "66.25", "$/BBL", ""),
        ("eia", "2020-01-03", "RBRTE", "68.60", "$/BBL", ""),
        ("eia", "2020-01-03", "RBRTE", "68.60", "$/BBL", ""),  # trung dong tren
        ("eia", "2020-01-06", "RBRTE", "", "$/BBL", ""),  # thieu gia tri
        ("eia", "2017-12-29", "RBRTE", "66.73", "$/BBL", ""),  # ngoai khoang phan tich
        ("eia", "2020-01-02", "EER_EPLLPA_PF4_Y44MB_DPG", "0.44", "$/GAL", ""),  # ngoai danh muc
        ("moit", ngay_moit, "Xăng E5RON92", "19.845", "đồng/lít", CAU_E5),
        ("moit", ngay_moit, "Dầu điêzen 0.05S", "16.540", "đồng/lít", CAU_DIESEL),
        ("bcp", "2020-01-15T15:20:00+07:00", "xăng E5RON92", "19.845", "đồng/lít", CAU_BAO),
        ("ty_gia", "2019-12-31", "Vietnam-Dong", "23155", "VND/USD", ""),
        ("ty_gia", "2020-03-31", "Vietnam-Dong", "23600", "VND/USD", ""),
        ("gpr", "20200102", "GPRD", "95.5", "chi so", ""),
        ("gpr", "20200103", "GPRD", "310.25", "chi so", ""),
        ("oxcgrt", "20200115", "VNM", "25.0", "chi so 0-100", ""),
    ]
    bang = pd.DataFrame(dong, columns=["nguon", "ngay", "chuoi", "gia_tri", "don_vi", "van_ban"])
    bang.insert(1, "tep", "soan_tay")
    return bang


def test_lam_sach_bang_mau_dung_luoc_do(bang_sach_mau: pd.DataFrame) -> None:
    """Bang sach co dung 20 cot theo thu tu, khoa (ngay, ma_chuoi) khong trung, gia la so duong."""
    assert list(bang_sach_mau.columns) == COT_SACH
    assert not bang_sach_mau.duplicated(["ngay", "ma_chuoi"]).any()
    assert pd.api.types.is_datetime64_any_dtype(bang_sach_mau["ngay"])
    assert pd.api.types.is_float_dtype(bang_sach_mau["gia_goc"])
    assert bang_sach_mau["gia_vnd_lit"].gt(0).all()
    assert set(bang_sach_mau["thi_truong"]) == {"the_gioi", "singapore", "viet_nam"}


def test_lam_sach_ghep_nguon_them_cot_khong_them_dong(bang_sach_mau: pd.DataFrame) -> None:
    """Ghep theo khoa `ngay`: moi quan sat gia nhan dung mot ty gia, noi suy giua hai moc quy."""
    # 23155 (31/12/2019) -> 23600 (31/3/2020), 91 ngay; ngay 15/1/2020 cach moc dau 15 ngay
    ty_gia_15_1 = 23155 + (23600 - 23155) * 15 / 91
    dong = bang_sach_mau.loc[
        bang_sach_mau["ngay"].eq("2020-01-15") & bang_sach_mau["ma_chuoi"].eq("sg_ron92")
    ]
    assert len(dong) == 1
    assert dong["ty_gia"].iloc[0] == pytest.approx(ty_gia_15_1)
    # 70,514 USD/thung quy ra dong/lit: nhan ty gia, chia so lit trong mot thung
    assert dong["gia_vnd_lit"].iloc[0] == pytest.approx(70.514 * ty_gia_15_1 / 158.987294928)
    assert dong["su_kien"].iloc[0] == "binh_thuong"


def test_lam_sach_khong_sua_bang_dau_vao(bang_tho_mau: pd.DataFrame) -> None:
    """Bang truyen vao giu nguyen noi dung va kieu sau khi lam sach."""
    ban_sao = bang_tho_mau.copy(deep=True)
    lam_sach(bang_tho_mau)
    pd.testing.assert_frame_equal(bang_tho_mau, ban_sao)


def test_lam_sach_chay_lai_cho_cung_ket_qua(
    bang_tho_mau: pd.DataFrame, bang_sach_mau: pd.DataFrame
) -> None:
    """Goi lai tren cung bang tho cho bang sach giong het lan truoc."""
    pd.testing.assert_frame_equal(lam_sach(bang_tho_mau), bang_sach_mau)


def test_lam_sach_bang_rong() -> None:
    """Bang tho khong co dong nao: bao BangRongError."""
    with pytest.raises(BangRongError):
        lam_sach(pd.DataFrame(columns=COT_THO))


def test_lam_sach_thieu_cot_bat_buoc(bang_tho_mau: pd.DataFrame) -> None:
    """Bang tho thieu cot `gia_tri`: bao ThieuCotError."""
    with pytest.raises(ThieuCotError):
        lam_sach(bang_tho_mau.drop(columns=["gia_tri"]))


def test_lam_sach_cot_toan_thieu(bang_tho_mau: pd.DataFrame) -> None:
    """Cot `gia_tri` chi chua o rong: bao CotToanThieuError."""
    with pytest.raises(CotToanThieuError):
        lam_sach(bang_tho_mau.assign(gia_tri=""))


def test_thong_ke_lam_sach_khop_so_tinh_tay() -> None:
    """Bat bien: bon con so thong ke tren bang 14 dong soan tay bang dung so dem tay.

    Bang sach con 5 dong: Brent 2/1 va 3/1, xang E5RON92 15/1, diesel 15/1 va mot dong
    suy ra (xang E5RON92 14/1 = 19.845 + 30); cau diesel bi cat giua muc giam nen khong
    sinh dong suy ra. Dem tay:
    - gia_tri_thieu = 1 o `gia_tri` rong (dong 4)
        + 5 o ty gia (khong ngay nao trung moc cuoi quy nen deu phai noi suy)
        + 0 o GPR (2/1 va 3/1 co san; 14/1 va 15/1 cach moc cuoi qua 7 ngay nen de thieu)
        + 3 o phong_toa_tg + 3 o phong_toa_vn (ba dong truoc moc dau 15/1 duoc gan 0) = 12
    - ban_ghi_trung = 1 (dong Brent 3/1 lap lai) + 1 (bao lap lai gia E5RON92 15/1 cua bo) = 2
    - kieu_sai = 6 o ngay khong o dang yyyy-mm-dd (2 moit, 1 bao, 2 GPR, 1 OxCGRT)
        + 3 o so viet kieu Viet Nam ("19.845" hai lan, "16.540") = 9
    - danh_muc_chuan_hoa = 2 ("Dầu điêzen 0.05S" va "xăng E5RON92" khac nhan chuan)
    """
    tho = bang_tho_nho()
    sach = lam_sach(tho)
    assert len(sach) == 5
    assert sach.loc[sach["suy_ra"], ["ma_chuoi", "gia_goc"]].to_numpy().tolist() == [
        ["vn_e5ron92", 19875.0]
    ]
    assert thong_ke_lam_sach(tho, sach) == {
        "gia_tri_thieu": 12,
        "ban_ghi_trung": 2,
        "kieu_sai": 9,
        "danh_muc_chuan_hoa": 2,
    }


def test_thong_ke_lam_sach_dung_bon_khoa_so_nguyen(
    bang_tho_mau: pd.DataFrame, bang_sach_mau: pd.DataFrame
) -> None:
    """Ket qua co dung bon khoa quy dinh, moi gia tri la so nguyen khong am."""
    thong_ke = thong_ke_lam_sach(bang_tho_mau, bang_sach_mau)
    assert list(thong_ke) == ["gia_tri_thieu", "ban_ghi_trung", "kieu_sai", "danh_muc_chuan_hoa"]
    assert all(type(gia_tri) is int and gia_tri >= 0 for gia_tri in thong_ke.values())
    # 6 dong trung trong du lieu mau: 1 dong EIA lap lai, 4 gia bao trung thong bao ngay 30/1,
    # 1 cau bao nhac lai ky 29/2 trong bai ngay 15/3
    assert thong_ke["ban_ghi_trung"] == 6


def test_thong_ke_lam_sach_bang_sau_khong_phai_cua_bang_truoc(
    bang_tho_mau: pd.DataFrame, bang_sach_mau: pd.DataFrame
) -> None:
    """Bang `sau` bi cat bot dong nen khong con la ket qua lam sach cua `truoc`: bao ThamSoError."""
    with pytest.raises(ThamSoError):
        thong_ke_lam_sach(bang_tho_mau, bang_sach_mau.iloc[:-3])


def test_thong_ke_lam_sach_bang_rong(bang_sach_mau: pd.DataFrame) -> None:
    """Bang `truoc` khong co dong nao: bao BangRongError."""
    with pytest.raises(BangRongError):
        thong_ke_lam_sach(pd.DataFrame(columns=COT_THO), bang_sach_mau)


def test_thong_ke_lam_sach_bang_sau_thieu_cot(
    bang_tho_mau: pd.DataFrame, bang_sach_mau: pd.DataFrame
) -> None:
    """Bang `sau` thieu cot cua luoc do bang sach: bao ThieuCotError."""
    with pytest.raises(ThieuCotError):
        thong_ke_lam_sach(bang_tho_mau, bang_sach_mau.drop(columns=["gia_vnd_lit"]))
