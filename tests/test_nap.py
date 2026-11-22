"""Kiem thu ham nap_du_lieu tren du lieu mau va cac tinh huong tep hong, tep thieu."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from gia_xang_dau import nap_du_lieu
from gia_xang_dau.lop_co_so import DinhDangError, ThieuCotError, ThieuTepError

COT_THO = ["nguon", "tep", "ngay", "chuoi", "gia_tri", "don_vi", "van_ban"]


def anh_chup_thu_muc(thu_muc: Path) -> dict[str, tuple[int, int]]:
    """Ghi lai kich thuoc va thoi diem sua cua moi tep trong mot thu muc."""
    return {
        str(tep.relative_to(thu_muc)): (tep.stat().st_size, tep.stat().st_mtime_ns)
        for tep in sorted(thu_muc.rglob("*"))
        if tep.is_file()
    }


def test_nap_du_lieu_thu_muc_mau_dung_luoc_do_va_so_dong(bang_tho_mau: pd.DataFrame) -> None:
    """Nap ca thu muc mau: dung bay cot, moi o la chuoi, so dong tung nguon dem tay duoc."""
    assert list(bang_tho_mau.columns) == COT_THO
    assert all(isinstance(o, str) for o in bang_tho_mau.to_numpy().ravel())
    # eia: 52 phien x 2 chuoi dau tho + 12 xang + 1 trung + 1 nam 2017 + 1 thieu + 2 propan = 121
    # oxcgrt: 56 ngay x 3 nuoc = 168 (3 dong cap bang bi loc khi nap); gpr: 72 ngay - 1 = 71
    # moit: 10 + 10 + 9 cau gia (bai thu tu khong co thoi diem ap dung nen bi bo qua) = 29
    # bcp: 6 + 4 + 4 cau gia = 14; ty_gia: 3 moc cuoi quy
    assert bang_tho_mau["nguon"].value_counts().to_dict() == {
        "oxcgrt": 168,
        "eia": 121,
        "gpr": 71,
        "moit": 29,
        "bcp": 14,
        "ty_gia": 3,
    }


def test_nap_du_lieu_mot_tep_chi_nap_nguon_cua_tep_do(thu_muc_mau: Path) -> None:
    """Dua duong dan mot tep: chi nap tep do, gia tri con nguyen dang chuoi nhu trong tep."""
    bang = nap_du_lieu(thu_muc_mau / "raw" / "ty_gia" / "ty_gia_trang_001.json")
    assert bang["nguon"].unique().tolist() == ["ty_gia"]
    assert bang["ngay"].tolist() == ["2019-09-30", "2019-12-31", "2020-03-31"]
    assert bang["gia_tri"].tolist() == ["23210.0", "23155.0", "23600.0"]
    assert bang["don_vi"].unique().tolist() == ["VND/USD"]


def test_nap_du_lieu_hai_nguon_trung_ten_tep_chon_theo_thu_muc(thu_muc_mau: Path) -> None:
    """Hai nguon bai viet cung ten tep bai_viet.jsonl: nguon duoc chon theo thu muc chua tep."""
    bang = nap_du_lieu(thu_muc_mau / "raw" / "bcp" / "bai_viet.jsonl")
    assert bang["nguon"].unique().tolist() == ["bcp"]
    assert len(bang) == 14
    assert bang["ngay"].str.startswith("2020-").all()


def test_nap_du_lieu_tach_gia_tu_van_ban_bai_viet(bang_tho_mau: pd.DataFrame) -> None:
    """Cau gia trong bai viet duoc tach thanh nhan, so (con viet kieu Viet Nam) va don vi."""
    moit = bang_tho_mau.loc[bang_tho_mau["nguon"].eq("moit")]
    dong = moit.loc[moit["chuoi"].eq("Xăng E5RON92")].iloc[0]
    assert dong["gia_tri"] == "19.845"
    assert dong["don_vi"] == "đồng/lít"
    assert dong["ngay"] == "15 giờ 00’ ngày 15 tháng 01 năm 2020"
    assert "giảm 30 đồng/lít" in dong["van_ban"]
    the_gioi = moit.loc[moit["don_vi"].eq("USD/thùng"), "gia_tri"]
    assert "70,514" in the_gioi.tolist()


def test_nap_du_lieu_khong_ghi_tep(thu_muc_mau: Path) -> None:
    """Ham nap chi doc: thu muc du lieu khong doi sau khi nap."""
    truoc = anh_chup_thu_muc(thu_muc_mau)
    nap_du_lieu(thu_muc_mau)
    assert anh_chup_thu_muc(thu_muc_mau) == truoc


def test_nap_du_lieu_duong_dan_khong_ton_tai(tmp_path: Path) -> None:
    """Duong dan khong ton tai: bao ThieuTepError, khong tra ve bang rong."""
    with pytest.raises(ThieuTepError):
        nap_du_lieu(tmp_path / "khong_co_thu_muc_nay")


def test_nap_du_lieu_thu_muc_rong(tmp_path: Path) -> None:
    """Thu muc khong co tep cua nguon nao: bao ThieuTepError."""
    with pytest.raises(ThieuTepError):
        nap_du_lieu(tmp_path)


def test_nap_du_lieu_tep_thieu_cot_bat_buoc(tmp_path: Path) -> None:
    """Tep dung ten nhung ban ghi thieu truong `exchange_rate`: bao ThieuCotError."""
    tep = tmp_path / "ty_gia_trang_001.json"
    ban_ghi = {"effective_date": "2020-03-31", "country_currency_desc": "Vietnam-Dong"}
    tep.write_text(json.dumps({"data": [ban_ghi]}), encoding="utf-8")
    with pytest.raises(ThieuCotError):
        nap_du_lieu(tep)


def test_nap_du_lieu_tep_khong_phai_json(tmp_path: Path) -> None:
    """Tep dung ten nhung noi dung khong phai JSON: bao DinhDangError."""
    tep = tmp_path / "ty_gia_trang_001.json"
    tep.write_text("day khong phai la json", encoding="utf-8")
    with pytest.raises(DinhDangError):
        nap_du_lieu(tep)
