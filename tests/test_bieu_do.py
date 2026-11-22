"""Kiem thu ham ve_bieu_do: tep png tao ra, noi ghi tep va cac tinh huong bien."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gia_xang_dau import ve_bieu_do
from gia_xang_dau.lop_co_so import BangRongError, CotToanThieuError, ThieuCotError

CHU_KY_PNG = b"\x89PNG\r\n\x1a\n"


def do_phan_giai_dpi(tep: Path) -> float:
    """Doc do phan giai (dpi) ghi trong khoi pHYs cua mot tep png."""
    du_lieu = tep.read_bytes()
    vi_tri = du_lieu.index(b"pHYs")
    (diem_moi_met,) = struct.unpack(">I", du_lieu[vi_tri + 4 : vi_tri + 8])
    return diem_moi_met * 0.0254


def test_ve_bieu_do_tao_du_nam_tep_png(bang_sach_mau: pd.DataFrame, tmp_path: Path) -> None:
    """Du lieu mau du de ve ca nam bieu do; moi tep la png hop le, do phan giai tu 150 dpi."""
    cac_tep = ve_bieu_do(bang_sach_mau, tmp_path)
    assert [tep.name[:2] for tep in cac_tep] == ["h1", "h2", "h3", "h4", "h5"]
    for tep in cac_tep:
        assert isinstance(tep, Path)
        assert tep.suffix == ".png"
        assert tep.read_bytes().startswith(CHU_KY_PNG)
        assert do_phan_giai_dpi(tep) >= 150


def test_ve_bieu_do_chi_ghi_vao_thu_muc_ra(bang_sach_mau: pd.DataFrame, tmp_path: Path) -> None:
    """Ham tu tao thu muc ra neu chua co va khong ghi tep nao ngoai thu muc do."""
    thu_muc_ra = tmp_path / "hinh" / "lan_1"
    cac_tep = ve_bieu_do(bang_sach_mau, str(thu_muc_ra))
    assert all(tep.parent == thu_muc_ra for tep in cac_tep)
    assert sorted(tep.name for tep in thu_muc_ra.iterdir()) == sorted(tep.name for tep in cac_tep)
    assert [tep.name for tep in tmp_path.iterdir()] == ["hinh"]


def test_ve_bieu_do_khong_sua_bang_dau_vao(bang_sach_mau: pd.DataFrame, tmp_path: Path) -> None:
    """Bang truyen vao giu nguyen sau khi ve."""
    ban_sao = bang_sach_mau.copy(deep=True)
    ve_bieu_do(bang_sach_mau, tmp_path)
    pd.testing.assert_frame_equal(bang_sach_mau, ban_sao)


def test_ve_bieu_do_thieu_chuoi_ban_le_van_ve_phan_con_lai(
    bang_sach_mau: pd.DataFrame, tmp_path: Path
) -> None:
    """Bang chi con gia the gioi: bieu do ty trong gia ban le bi bo qua, cac bieu do khac van ve."""
    chi_the_gioi = bang_sach_mau.loc[bang_sach_mau["thi_truong"].eq("the_gioi")]
    ten_tep = [tep.name[:2] for tep in ve_bieu_do(chi_the_gioi, tmp_path)]
    assert "h4" not in ten_tep
    assert {"h1", "h2"} <= set(ten_tep)


def test_ve_bieu_do_bang_rong(bang_sach_mau: pd.DataFrame, tmp_path: Path) -> None:
    """Bang khong co dong nao: bao BangRongError va khong ghi tep."""
    with pytest.raises(BangRongError):
        ve_bieu_do(bang_sach_mau.iloc[0:0], tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_ve_bieu_do_thieu_cot(bang_sach_mau: pd.DataFrame, tmp_path: Path) -> None:
    """Bang thieu cot `ma_chuoi` cua luoc do bang sach: bao ThieuCotError."""
    with pytest.raises(ThieuCotError):
        ve_bieu_do(bang_sach_mau.drop(columns=["ma_chuoi"]), tmp_path)


def test_ve_bieu_do_cot_gia_toan_thieu(bang_sach_mau: pd.DataFrame, tmp_path: Path) -> None:
    """Cot gia `gia_vnd_lit` chi chua gia tri thieu: bao CotToanThieuError."""
    with pytest.raises(CotToanThieuError):
        ve_bieu_do(bang_sach_mau.assign(gia_vnd_lit=np.nan), tmp_path)
