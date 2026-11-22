"""Cau hinh chung cua pytest: duong tim goi `gia_xang_dau` va cac bang mau dung chung."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

THU_MUC_KIEM_THU = Path(__file__).resolve().parent


def pytest_configure(config: pytest.Config) -> None:
    """Them thu muc `src` vao duong tim mo-dun truoc khi pytest nap cac tep kiem thu.

    Tham so:
        config: doi tuong cau hinh cua pytest (khong dung den).

    Tra ve:
        Khong co.

    Ngoai le:
        Khong co.
    """
    thu_muc_src = str(THU_MUC_KIEM_THU.parent / "src")
    if thu_muc_src not in sys.path:
        sys.path.insert(0, thu_muc_src)


@pytest.fixture(scope="session")
def thu_muc_mau() -> Path:
    """Thu muc du lieu mau, co cung cau truc voi thu muc `data/`."""
    return THU_MUC_KIEM_THU / "du_lieu_mau"


@pytest.fixture(scope="session")
def bang_tho_mau(thu_muc_mau: Path) -> pd.DataFrame:
    """Bang tho nap tu toan bo du lieu mau (dung chung, khong duoc sua)."""
    from gia_xang_dau import nap_du_lieu

    return nap_du_lieu(thu_muc_mau)


@pytest.fixture(scope="session")
def bang_sach_mau(bang_tho_mau: pd.DataFrame) -> pd.DataFrame:
    """Bang sach lam tu bang tho mau (dung chung, khong duoc sua)."""
    from gia_xang_dau import lam_sach

    return lam_sach(bang_tho_mau)
