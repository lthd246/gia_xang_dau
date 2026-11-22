"""Kiem thu ham tong_hop va tra_loi_cau_hoi: doi chieu voi so tinh tay va cac tinh huong bien."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gia_xang_dau import tong_hop, tra_loi_cau_hoi
from gia_xang_dau.lop_co_so import BangRongError, CotToanThieuError, ThamSoError, ThieuCotError


def gia_brent_mau(thu_muc_mau: Path) -> pd.Series:
    """Doc thang gia Brent tu tep EIA mau, khong qua ma nguon cua goi (duong tinh doc lap)."""
    tep = thu_muc_mau / "raw" / "eia" / "gia_giao_ngay_trang_001.json"
    ban_ghi = json.loads(tep.read_text(encoding="utf-8"))["response"]["data"]
    gia = {
        dong["period"]: float(dong["value"])
        for dong in ban_ghi
        if dong["series"] == "RBRTE" and dong["value"] is not None and dong["period"] >= "2018"
    }
    return pd.Series(gia).sort_index()


def test_tong_hop_theo_mot_cot_khop_so_tinh_tay(bang_sach_mau: pd.DataFrame) -> None:
    """Nhom theo `ma_chuoi`: thong ke cua xang E5RON92 bang so tinh tay tu 10 quan sat mau."""
    # 5 gia cong bo (15/1, 30/1, 14/2, 29/2, 15/3) va 5 gia suy ra cua ngay lien truoc
    gia = [19875, 19845, 19845, 19268, 19268, 18346, 18346, 17345, 17345, 16057]
    bang = tong_hop(bang_sach_mau, ["ma_chuoi"]).set_index("ma_chuoi")
    dong = bang.loc["vn_e5ron92"]
    assert dong["gia_vnd_lit_so_quan_sat"] == 10
    assert dong["gia_vnd_lit_trung_binh"] == pytest.approx(sum(gia) / 10)
    assert dong["gia_vnd_lit_trung_vi"] == pytest.approx((19268 + 18346) / 2)
    assert dong["gia_vnd_lit_nho_nhat"] == pytest.approx(16057)
    assert dong["gia_vnd_lit_lon_nhat"] == pytest.approx(19875)
    assert dong["gia_vnd_lit_do_lech_chuan"] == pytest.approx(np.std(gia, ddof=1))
    # dong dau cua chuoi khong co quan sat truoc nen khong co muc thay doi
    assert dong["thay_doi_pct_so_quan_sat"] == 9


def test_tong_hop_theo_hai_cot_du_nhom_va_du_dong(bang_sach_mau: pd.DataFrame) -> None:
    """Nhom theo hai cot: 3 thi truong x 2 boi canh = 6 nhom, tong so quan sat bang so dong."""
    bang = tong_hop(bang_sach_mau, ["thi_truong", "su_kien"])
    assert list(bang.columns[:2]) == ["thi_truong", "su_kien"]
    assert len(bang) == 6
    assert bang["gia_vnd_lit_so_quan_sat"].sum() == len(bang_sach_mau)


def test_tong_hop_khong_sua_bang_dau_vao(bang_sach_mau: pd.DataFrame) -> None:
    """Bang truyen vao giu nguyen sau khi tong hop."""
    ban_sao = bang_sach_mau.copy(deep=True)
    tong_hop(bang_sach_mau, ["nam", "thang"])
    pd.testing.assert_frame_equal(bang_sach_mau, ban_sao)


def test_tong_hop_cot_khong_ton_tai(bang_sach_mau: pd.DataFrame) -> None:
    """Ten cot nhom khong co trong bang: bao ThieuCotError."""
    with pytest.raises(ThieuCotError):
        tong_hop(bang_sach_mau, ["cot_khong_co"])


def test_tong_hop_bang_rong(bang_sach_mau: pd.DataFrame) -> None:
    """Bang khong co dong nao: bao BangRongError."""
    with pytest.raises(BangRongError):
        tong_hop(bang_sach_mau.iloc[0:0], ["ma_chuoi"])


def test_tong_hop_cot_gia_tri_toan_thieu(bang_sach_mau: pd.DataFrame) -> None:
    """Cot gia tri `gia_vnd_lit` chi chua gia tri thieu: bao CotToanThieuError."""
    with pytest.raises(CotToanThieuError):
        tong_hop(bang_sach_mau.assign(gia_vnd_lit=np.nan), ["ma_chuoi"])


def test_tong_hop_danh_sach_cot_rong(bang_sach_mau: pd.DataFrame) -> None:
    """Danh sach cot nhom rong: bao ThamSoError."""
    with pytest.raises(ThamSoError):
        tong_hop(bang_sach_mau, [])


def test_tra_loi_cau_hoi_tra_ve_so_va_chuoi(bang_sach_mau: pd.DataFrame) -> None:
    """Ket qua la tu dien co it nhat ba chi tieu, gia tri la so hoac chuoi, ghi duoc ra JSON."""
    ket_qua = tra_loi_cau_hoi(bang_sach_mau)
    assert len(ket_qua) >= 3
    assert all(type(gia_tri) in (int, float, str) for gia_tri in ket_qua.values())
    assert all(not (isinstance(g, float) and math.isnan(g)) for g in ket_qua.values())
    assert json.loads(json.dumps(ket_qua, ensure_ascii=False)) == ket_qua
    assert ket_qua["boi_canh_bien_dong_manh_nhat"] == "COVID-19 (2020)"


def test_tra_loi_cau_hoi_bien_dong_khop_tinh_doc_lap(
    bang_sach_mau: pd.DataFrame, thu_muc_mau: Path
) -> None:
    """Do bien dong cua Brent bang so tinh lai truc tiep tu tep EIA mau bang NumPy."""
    gia = gia_brent_mau(thu_muc_mau)
    loi_suat = np.log(gia.to_numpy()[1:] / gia.to_numpy()[:-1])
    trong_su_kien = gia.index[1:] >= "2020-01-30"  # su kien COVID-19 bat dau 30/1/2020
    binh_thuong = np.std(loi_suat[~trong_su_kien], ddof=1) * math.sqrt(252) * 100
    su_kien = np.std(loi_suat[trong_su_kien], ddof=1) * math.sqrt(252) * 100
    ket_qua = tra_loi_cau_hoi(bang_sach_mau)
    assert ket_qua["bien_dong_brent_binh_thuong_pct_nam"] == round(binh_thuong, 1)
    assert ket_qua["bien_dong_brent_covid_2020_pct_nam"] == round(su_kien, 1)
    assert ket_qua["bien_dong_brent_covid_2020_gap_lan"] == round(su_kien / binh_thuong, 2)


def test_tra_loi_cau_hoi_cu_soc_gia_ban_le_khop_so_tinh_tay(bang_sach_mau: pd.DataFrame) -> None:
    """Muc giam lon nhat cua gia ban le trong su kien bang so tinh tay tu du lieu mau."""
    ket_qua = tra_loi_cau_hoi(bang_sach_mau)
    # ngay truoc su kien (29/1): E5RON92 19.845, diesel 16.540; thap nhat trong su kien (15/3):
    # E5RON92 16.057, diesel 13.039
    assert ket_qua["vn_e5ron92_thay_doi_pct_covid_2020"] == round((16057 / 19845 - 1) * 100, 1)
    assert ket_qua["vn_diesel_thay_doi_pct_covid_2020"] == round((13039 / 16540 - 1) * 100, 1)
    # diesel co mot khoang thieu ky cai san: gia truoc ky 29/2 (15.242) khac gia ky 14/2 (15.521)
    assert ket_qua["so_khoang_thieu_ky_vn_diesel"] == 1
    assert ket_qua["so_khoang_thieu_ky_vn_e5ron92"] == 0
    assert ket_qua["so_ky_quan_sat_vn_e5ron92"] == 5


def test_tra_loi_cau_hoi_bang_rong(bang_sach_mau: pd.DataFrame) -> None:
    """Bang khong co dong nao: bao BangRongError."""
    with pytest.raises(BangRongError):
        tra_loi_cau_hoi(bang_sach_mau.iloc[0:0])


def test_tra_loi_cau_hoi_thieu_cot(bang_sach_mau: pd.DataFrame) -> None:
    """Bang thieu cot `su_kien` cua luoc do bang sach: bao ThieuCotError."""
    with pytest.raises(ThieuCotError):
        tra_loi_cau_hoi(bang_sach_mau.drop(columns=["su_kien"]))


def test_tra_loi_cau_hoi_cot_gia_toan_thieu(bang_sach_mau: pd.DataFrame) -> None:
    """Cot gia `gia_usd_thung` chi chua gia tri thieu: bao CotToanThieuError."""
    with pytest.raises(CotToanThieuError):
        tra_loi_cau_hoi(bang_sach_mau.assign(gia_usd_thung=np.nan))
