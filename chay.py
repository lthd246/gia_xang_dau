"""Diem vao duy nhat cua chuong trinh.

Cach goi:
    python chay.py --giai-doan tat-ca --cau-hinh cau_hinh.yaml
    python chay.py --giai-doan nap | lam-sach | phan-tich | bieu-do

Moi giai doan doc dau vao tu dia va ghi dau ra ra dia, nen chay tung giai doan hay
chay `tat-ca` deu cho cung ket qua. Giai doan nao xong thi in dung mot dong
`[xong] <ten>`; chi tiet nam trong ket_qua/nhat_ky.log.
"""

from __future__ import annotations

import argparse
import json
import logging
import platform
import sys
import time
from pathlib import Path
from typing import Any

THU_MUC_GOC = Path(__file__).resolve().parent
CAC_GIAI_DOAN = ("nap", "lam-sach", "phan-tich", "bieu-do")
NHAT_KY = logging.getLogger("chay")


def doc_tham_so(argv: list[str] | None = None) -> argparse.Namespace:
    """Doc tham so dong lenh.

    Tham so:
        argv: danh sach tham so; bo trong thi lay tu dong lenh.

    Tra ve:
        Doi tuong co hai thuoc tinh `giai_doan` va `cau_hinh`.

    Ngoai le:
        SystemExit: khi tham so khong hop le (argparse thoat voi ma 2).
    """
    bo_doc = argparse.ArgumentParser(description="Phan tich bien dong gia xang dau.")
    bo_doc.add_argument(
        "--giai-doan",
        required=True,
        choices=[*CAC_GIAI_DOAN, "tat-ca"],
        help="giai doan can chay",
    )
    bo_doc.add_argument(
        "--cau-hinh",
        default=str(THU_MUC_GOC / "cau_hinh.yaml"),
        help="tep cau hinh (mac dinh: cau_hinh.yaml o thu muc goc)",
    )
    return bo_doc.parse_args(argv)


def cai_dat_nhat_ky(tep: Path) -> None:
    """Dua moi thong diep logging vao tep nhat ky cua lan chay nay.

    Tham so:
        tep: duong dan tep nhat ky; tep cu bi ghi de.

    Tra ve:
        Khong co.

    Ngoai le:
        OSError: khi khong tao duoc tep nhat ky.
    """
    tep.parent.mkdir(parents=True, exist_ok=True)
    goc = logging.getLogger()
    for bo_xu_ly in list(goc.handlers):
        goc.removeHandler(bo_xu_ly)
    bo_ghi = logging.FileHandler(tep, mode="w", encoding="utf-8")
    bo_ghi.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"))
    goc.addHandler(bo_ghi)
    goc.setLevel(logging.INFO)


class ChuongTrinh:
    """Dieu phoi bon giai doan nap, lam sach, phan tich, bieu do va ghi tep tom tat."""

    def __init__(self, cau_hinh: Any) -> None:
        """Tao chuong trinh.

        Tham so:
            cau_hinh: doi tuong CauHinh cua goi gia_xang_dau.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._cau_hinh = cau_hinh
        self._buoc = {
            "nap": self.nap,
            "lam-sach": self.lam_sach,
            "phan-tich": self.phan_tich,
            "bieu-do": self.bieu_do,
        }

    def chay(self, giai_doan: str) -> None:
        """Chay mot giai doan, hoac ca bon giai doan khi `giai_doan` la "tat-ca".

        Tham so:
            giai_doan: mot trong nap, lam-sach, phan-tich, bieu-do, tat-ca.

        Tra ve:
            Khong co.

        Ngoai le:
            DoAnError: khi du lieu hoac cau hinh co van de; thong bao neu ro tep, cot.
        """
        can_chay = CAC_GIAI_DOAN if giai_doan == "tat-ca" else (giai_doan,)
        for ten in can_chay:
            bat_dau = time.perf_counter()
            NHAT_KY.info("=== Bat dau giai doan %s ===", ten)
            ket_qua = self._buoc[ten]()
            ket_qua["giay"] = round(time.perf_counter() - bat_dau, 2)
            self._ghi_trang_thai(ten, ket_qua)
            self._ghi_tom_tat()
            NHAT_KY.info("=== Xong giai doan %s sau %.2f giay ===", ten, ket_qua["giay"])
            print(f"[xong] {ten}")

    def nap(self) -> dict[str, Any]:
        """Bao dam bo dem du lieu tho, nap moi nguon va ghi bang tho.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien co khoa `so_dong_tho`.

        Ngoai le:
            ThieuTepError: khi thieu tep cua mot nguon ma khong tai duoc.
        """
        from gia_xang_dau.nap import BoNapNhieuNguon, KhoDem

        KhoDem(self._cau_hinh).dam_bao()
        bang = BoNapNhieuNguon(self._cau_hinh).nap(self._cau_hinh.duong_dan("du_lieu"))
        tep = self._cau_hinh.duong_dan("bang_tho")
        tep.parent.mkdir(parents=True, exist_ok=True)
        bang.to_csv(tep, index=False, encoding="utf-8", lineterminator="\n")
        NHAT_KY.info("Nap: %d dong tho -> %s", len(bang), self._cau_hinh.tuong_doi(tep))
        return {"so_dong_tho": len(bang)}

    def lam_sach(self) -> dict[str, Any]:
        """Doc bang tho, lam sach, ghi bang sach va hai bang kiem chung.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien co cac khoa `so_dong_sach`, `thong_ke_lam_sach`, `bang`.

        Ngoai le:
            ThieuTepError: khi chua co bang tho (chua chay giai doan nap).
        """
        import pandas as pd

        from gia_xang_dau.lam_sach import BoLamSach

        cau_hinh = self._cau_hinh
        tep_tho = self._tep_dau_vao("bang_tho", "nap")
        tho = pd.read_csv(tep_tho, dtype=str, keep_default_na=False, encoding="utf-8")
        bo_lam_sach = BoLamSach(cau_hinh)
        sach = bo_lam_sach.chay(tho)
        tep_sach = cau_hinh.duong_dan("bang_sach")
        tep_sach.parent.mkdir(parents=True, exist_ok=True)
        sach.to_csv(tep_sach, index=False, encoding="utf-8", lineterminator="\n")
        ten_bang = cau_hinh["lam_sach.ten_bang"]
        cac_bang = self._ghi_bang(
            {
                str(ten_bang["cac_buoc"]): bo_lam_sach.bang_bao_cao(),
                str(ten_bang["mau_doi_chieu"]): bo_lam_sach.mau_doi_chieu(sach),
            }
        )
        NHAT_KY.info(
            "Lam sach: %d dong vao, %d dong ra -> %s",
            len(tho),
            len(sach),
            cau_hinh.tuong_doi(tep_sach),
        )
        return {
            "so_dong_sach": len(sach),
            "thong_ke_lam_sach": bo_lam_sach.thong_ke(),
            "bang": cac_bang,
        }

    def phan_tich(self) -> dict[str, Any]:
        """Doc bang sach, tra loi cau hoi va ghi cac bang ket qua.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien co cac khoa `ket_qua`, `bang`.

        Ngoai le:
            ThieuTepError: khi chua co bang sach (chua chay giai doan lam-sach).
        """
        from gia_xang_dau.phan_tich import BoTraLoi

        bo_tra_loi = BoTraLoi(self._doc_bang_sach(), self._cau_hinh)
        ket_qua = bo_tra_loi.tra_loi()
        cac_bang = self._ghi_bang(bo_tra_loi.cac_bang())
        NHAT_KY.info("Phan tich: %d chi tieu, %d bang", len(ket_qua), len(cac_bang))
        return {"ket_qua": ket_qua, "bang": cac_bang}

    def bieu_do(self) -> dict[str, Any]:
        """Doc bang sach va ve cac bieu do.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien co khoa `hinh`.

        Ngoai le:
            ThieuTepError: khi chua co bang sach (chua chay giai doan lam-sach).
        """
        from gia_xang_dau.bieu_do import BoVeBieuDo

        bo_ve = BoVeBieuDo(self._doc_bang_sach(), self._cau_hinh)
        cac_hinh = bo_ve.ve_tat_ca(self._cau_hinh.duong_dan("hinh"))
        NHAT_KY.info("Bieu do: %d hinh", len(cac_hinh))
        return {"hinh": [self._cau_hinh.tuong_doi(tep) for tep in cac_hinh]}

    def _ghi_bang(self, cac_bang: dict[str, Any]) -> list[str]:
        """Ghi tung bang ket qua ra thu muc bang, tra ve duong dan tuong doi cua cac tep."""
        thu_muc = self._cau_hinh.duong_dan("bang")
        thu_muc.mkdir(parents=True, exist_ok=True)
        cac_tep = []
        for ten_tep, bang in cac_bang.items():
            tep = thu_muc / ten_tep
            bang.to_csv(
                tep, index=False, encoding="utf-8-sig", float_format="%.4f", lineterminator="\n"
            )
            NHAT_KY.info("Da ghi bang %s (%d dong)", ten_tep, len(bang))
            cac_tep.append(self._cau_hinh.tuong_doi(tep))
        return cac_tep

    def _tep_dau_vao(self, ten: str, giai_doan_truoc: str) -> Path:
        """Tra ve tep dau vao cua mot giai doan, bao loi ro neu chua co."""
        from gia_xang_dau.lop_co_so import ThieuTepError

        tep = self._cau_hinh.duong_dan(ten)
        if not tep.is_file():
            raise ThieuTepError(
                f"Chua co tep '{self._cau_hinh.tuong_doi(tep)}'. "
                f"Hay chay truoc: python chay.py --giai-doan {giai_doan_truoc}"
            )
        return tep

    def _doc_bang_sach(self) -> Any:
        """Doc bang sach tu dia, cot `ngay` o kieu ngay."""
        import pandas as pd

        tep = self._tep_dau_vao("bang_sach", "lam-sach")
        return pd.read_csv(
            tep, parse_dates=["ngay"], encoding="utf-8", float_precision="round_trip"
        )

    def _ghi_trang_thai(self, giai_doan: str, ket_qua: dict[str, Any]) -> None:
        """Luu ket qua cua mot giai doan vao tep trang thai trong data/interim."""
        tep = self._cau_hinh.duong_dan("trang_thai")
        tep.parent.mkdir(parents=True, exist_ok=True)
        trang_thai = self._doc_trang_thai()
        trang_thai[giai_doan] = ket_qua
        tep.write_text(json.dumps(trang_thai, ensure_ascii=False, indent=2), encoding="utf-8")

    def _doc_trang_thai(self) -> dict[str, Any]:
        """Doc tep trang thai; chua co thi tra ve tu dien rong."""
        tep = self._cau_hinh.duong_dan("trang_thai")
        if not tep.is_file():
            return {}
        return json.loads(tep.read_text(encoding="utf-8"))

    def _ghi_tom_tat(self) -> None:
        """Ghi ket_qua/tom_tat.json tu ket qua moi nhat cua tung giai doan."""
        from gia_xang_dau.nap import BoNapNhieuNguon

        cau_hinh = self._cau_hinh
        trang_thai = self._doc_trang_thai()
        thu_muc_du_lieu = cau_hinh.duong_dan("du_lieu")
        nguon_du_lieu = []
        for bo_nap in BoNapNhieuNguon(cau_hinh):
            cac_tep = bo_nap.tim_tep(thu_muc_du_lieu)
            vi_tri = cac_tep[0] if len(cac_tep) == 1 else thu_muc_du_lieu / bo_nap.nguon.thu_muc
            nguon_du_lieu.append(
                {
                    "ten": bo_nap.nguon.mo_ta,
                    "loai": bo_nap.nguon.dinh_dang,
                    "duong_dan": cau_hinh.tuong_doi(vi_tri),
                }
            )
        tom_tat = {
            "nhom": str(cau_hinh["du_an.nhom"]),
            "thanh_vien": [str(ma) for ma in cau_hinh["du_an.thanh_vien"]],
            "cau_hoi": " ".join(str(cau_hinh["du_an.cau_hoi"]).split()),
            "nguon_du_lieu": nguon_du_lieu,
            "so_dong_tho": trang_thai.get("nap", {}).get("so_dong_tho"),
            "so_dong_sach": trang_thai.get("lam-sach", {}).get("so_dong_sach"),
            "thong_ke_lam_sach": trang_thai.get("lam-sach", {}).get("thong_ke_lam_sach"),
            "ket_qua": trang_thai.get("phan-tich", {}).get("ket_qua"),
            "hinh": trang_thai.get("bieu-do", {}).get("hinh", []),
            "bang": [
                *trang_thai.get("lam-sach", {}).get("bang", []),
                *trang_thai.get("phan-tich", {}).get("bang", []),
            ],
            "seed": cau_hinh.seed,
            "phien_ban_python": platform.python_version(),
            "thoi_gian_chay_giay": round(
                sum(float(muc.get("giay", 0.0)) for muc in trang_thai.values()), 1
            ),
        }
        tep = cau_hinh.duong_dan("tom_tat")
        tep.parent.mkdir(parents=True, exist_ok=True)
        tep.write_text(json.dumps(tom_tat, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Chay chuong trinh theo tham so dong lenh.

    Tham so:
        argv: danh sach tham so; bo trong thi lay tu dong lenh.

    Tra ve:
        Ma thoat: 0 khi thanh cong, 1 khi co loi du lieu, cau hinh hay moi truong.

    Ngoai le:
        SystemExit: khi tham so dong lenh khong hop le (argparse thoat voi ma 2).
    """
    tham_so = doc_tham_so(argv)
    for luong in (sys.stdout, sys.stderr):
        # man hinh khong hien duoc mot ky tu thi in ma cua ky tu do, khong de vang loi ma hoa
        if hasattr(luong, "reconfigure"):
            luong.reconfigure(errors="backslashreplace")
    sys.path.insert(0, str(THU_MUC_GOC / "src"))
    # truoc khi mo duoc tep nhat ky, thong diep logging khong duoc tu in ra man hinh
    logging.getLogger().addHandler(logging.NullHandler())
    try:
        from gia_xang_dau.cau_hinh import CauHinh
        from gia_xang_dau.lop_co_so import DoAnError
    except ImportError as loi:
        print(
            f"[loi] Thieu thu vien ({loi}). Hay chay: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1
    try:
        cau_hinh = CauHinh.tu_tep(tham_so.cau_hinh, THU_MUC_GOC)
        cai_dat_nhat_ky(cau_hinh.duong_dan("nhat_ky"))
        NHAT_KY.info(
            "Python %s | giai doan %s | %r", platform.python_version(), tham_so.giai_doan, cau_hinh
        )
        ChuongTrinh(cau_hinh).chay(tham_so.giai_doan)
    except DoAnError as loi:
        NHAT_KY.error("%s: %s", type(loi).__name__, loi)
        print(f"[loi] {type(loi).__name__}: {loi}", file=sys.stderr)
        return 1
    except Exception as loi:  # bien cuoi cung: khong de truy vet tran ra man hinh
        NHAT_KY.exception("Loi khong luong truoc")
        print(
            f"[loi] Loi khong luong truoc ({type(loi).__name__}: {loi}). "
            "Xem chi tiet trong ket_qua/nhat_ky.log",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
