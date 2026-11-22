"""Lop va ham nap du lieu: tai ve co bo dem, doc tung dinh dang, noi thanh bang tho.

Hai nhom lop:
    - Nhom tai (KhachHttp, TaiApiPhanTrang, TaiTep, TaiBaiViet, KhoDem): chi chay o
      giai doan `nap` cua chay.py khi thu muc du lieu chua co tep cua nguon.
    - Nhom nap (NapJsonTrang, NapCsvKhoi, NapExcel, NapBaiViet, BoNapNhieuNguon): chi
      doc tep, khong bao gio ghi tep.
"""

from __future__ import annotations

import fnmatch
import html
import json
import logging
import os
import re
import shutil
import time
import unicodedata
from abc import abstractmethod
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
import requests
from xlrd import XLRDError

from .cau_hinh import CauHinh, CauHinhNguon
from .lop_co_so import (
    BoNap,
    BoTai,
    CauHinhError,
    DinhDangError,
    TaiVeError,
    ThieuCotError,
    ThieuTepError,
)

NHAT_KY = logging.getLogger(__name__)


class KhachHttp:
    """Gui yeu cau HTTP GET co gian cach giua cac lan goi, thu lai va gioi han thoi gian."""

    def __init__(
        self, tac_nhan: str, cho_giay: float, so_lan_thu: int, het_gio_giay: float
    ) -> None:
        """Tao khach HTTP.

        Tham so:
            tac_nhan: chuoi User-Agent gui kem moi yeu cau.
            cho_giay: so giay nghi toi thieu giua hai yeu cau lien tiep.
            so_lan_thu: so lan thu toi da cho mot yeu cau.
            het_gio_giay: thoi gian cho toi da cua mot yeu cau.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._phien = requests.Session()
        self._phien.headers["User-Agent"] = tac_nhan
        self._cho_giay = cho_giay
        self._so_lan_thu = so_lan_thu
        self._het_gio_giay = het_gio_giay
        self._lan_goi_cuoi = 0.0

    @classmethod
    def tu_cau_hinh(cls, cau_hinh: CauHinh) -> KhachHttp:
        """Tao khach HTTP tu muc `tai_ve` cua cau hinh.

        Tham so:
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Doi tuong KhachHttp.

        Ngoai le:
            CauHinhError: khi muc `tai_ve` thieu khoa.
        """
        return cls(
            tac_nhan=str(cau_hinh["tai_ve.tac_nhan"]),
            cho_giay=float(cau_hinh["tai_ve.cho_giay"]),
            so_lan_thu=int(cau_hinh["tai_ve.so_lan_thu"]),
            het_gio_giay=float(cau_hinh["tai_ve.het_gio_giay"]),
        )

    def lay(self, url: str, tham_so: dict[str, Any] | None = None) -> bytes:
        """Gui mot yeu cau GET va tra ve noi dung tho.

        Tham so:
            url: dia chi can goi.
            tham_so: tham so truy van, co the bo trong.

        Tra ve:
            Noi dung phan hoi o dang byte, dung nhu may chu tra ve.

        Ngoai le:
            TaiVeError: khi het so lan thu ma van khong nhan duoc ma 200.
        """
        loi_cuoi = "chua goi"
        for lan in range(1, self._so_lan_thu + 1):
            self._nghi()
            try:
                phan_hoi = self._phien.get(url, params=tham_so, timeout=self._het_gio_giay)
            except requests.RequestException as loi:
                loi_cuoi = type(loi).__name__
            else:
                if phan_hoi.status_code == 200:
                    return phan_hoi.content
                loi_cuoi = f"HTTP {phan_hoi.status_code}"
                if phan_hoi.status_code in (400, 401, 403, 404):
                    break
            NHAT_KY.warning("Goi %s lan %d that bai: %s", url, lan, loi_cuoi)
            time.sleep(self._cho_giay * 2**lan)
        raise TaiVeError(f"Khong tai duoc '{url}' ({loi_cuoi}). Kiem tra ket noi mang.")

    def _nghi(self) -> None:
        """Nghi cho du khoang cach toi thieu giua hai yeu cau."""
        con_lai = self._cho_giay - (time.monotonic() - self._lan_goi_cuoi)
        if con_lai > 0:
            time.sleep(con_lai)
        self._lan_goi_cuoi = time.monotonic()


class TaiApiPhanTrang(BoTai):
    """Tai mot REST API tra JSON co phan trang, moi trang luu thanh mot tep."""

    def tai(self, thu_muc_dich: Path) -> list[Path]:
        """Goi lan luot tung trang cho den khi het du lieu.

        Tham so:
            thu_muc_dich: thu muc se chua cac tep trang.

        Tra ve:
            Danh sach tep da ghi, moi tep la mot trang dung nhu API tra ve.

        Ngoai le:
            TaiVeError: khi khong goi duoc API hoac trang dau khong co ban ghi.
            DinhDangError: khi phan hoi khong phai JSON dung cau truc.
        """
        cau = self._nguon.tai_ve
        kich_thuoc = int(cau["kich_thuoc_trang"])
        tham_so = dict(cau.get("tham_so") or {})
        tham_so[str(cau["tham_so_kich_thuoc"])] = kich_thuoc
        if "tham_so_khoa" in cau:
            khoa = os.environ.get(str(cau["bien_moi_truong_khoa"]), str(cau["khoa_mac_dinh"]))
            tham_so[str(cau["tham_so_khoa"])] = khoa
        thu_muc_dich.mkdir(parents=True, exist_ok=True)
        da_ghi: list[Path] = []
        for trang in range(1, int(cau["so_trang_toi_da"]) + 1):
            tham_so[str(cau["tham_so_vi_tri"])] = self.vi_tri_trang(
                trang, kich_thuoc, str(cau["kieu_vi_tri"])
            )
            noi_dung = self._khach.lay(str(cau["url"]), tham_so)
            ban_ghi = NapJsonTrang.ban_ghi_trong(
                NapJsonTrang.giai_ma_json(noi_dung, str(cau["url"])),
                list(self._nguon.doc["duong_ban_ghi"]),
                str(cau["url"]),
            )
            if not ban_ghi:
                break
            tep = thu_muc_dich / str(cau["ten_tep"]).format(trang=trang)
            tep.write_bytes(noi_dung)
            da_ghi.append(tep)
            NHAT_KY.info("Nguon %s: trang %d co %d ban ghi", self._nguon.ten, trang, len(ban_ghi))
            if len(ban_ghi) < kich_thuoc:
                break
        if not da_ghi:
            raise TaiVeError(f"API '{cau['url']}' khong tra ve ban ghi nao.")
        return da_ghi

    @staticmethod
    def vi_tri_trang(trang: int, kich_thuoc: int, kieu_vi_tri: str) -> int:
        """Tinh gia tri tham so vi tri cho mot trang.

        Tham so:
            trang: so thu tu trang, bat dau tu 1.
            kich_thuoc: so ban ghi moi trang.
            kieu_vi_tri: "do_doi" (so ban ghi bo qua) hoac "so_trang".

        Tra ve:
            So nguyen dua vao tham so vi tri cua API.

        Ngoai le:
            CauHinhError: khi `kieu_vi_tri` khong thuoc hai gia tri tren.
        """
        if kieu_vi_tri == "do_doi":
            return (trang - 1) * kich_thuoc
        if kieu_vi_tri == "so_trang":
            return trang
        raise CauHinhError(f"kieu_vi_tri {kieu_vi_tri!r} phai la 'do_doi' hoac 'so_trang'.")


class TaiTep(BoTai):
    """Tai mot tep don le tu mot dia chi co dinh."""

    def tai(self, thu_muc_dich: Path) -> list[Path]:
        """Tai tep va ghi dung nhu may chu tra ve.

        Tham so:
            thu_muc_dich: thu muc se chua tep.

        Tra ve:
            Danh sach mot phan tu la tep da ghi.

        Ngoai le:
            TaiVeError: khi khong tai duoc tep.
        """
        cau = self._nguon.tai_ve
        thu_muc_dich.mkdir(parents=True, exist_ok=True)
        tep = thu_muc_dich / str(cau["ten_tep"])
        tep.write_bytes(self._khach.lay(str(cau["url"])))
        NHAT_KY.info("Nguon %s: da tai %s (%d byte)", self._nguon.ten, tep.name, tep.stat().st_size)
        return [tep]


class TaiBaiViet(BoTai):
    """Tai bai viet cua mot trang tin: liet ke qua tim kiem phan trang roi lay tung bai.

    Lop nay giu khung chung (duyet danh sach, loc bai, ghi tep JSON Lines); hai
    viec phu thuoc trang tin - liet ke bai va lay noi dung mot bai - do lop con dam nhan.
    """

    def tai(self, thu_muc_dich: Path) -> list[Path]:
        """Tai danh sach bai roi noi dung tung bai, chi giu bai khop mau loc.

        Moi trang ket qua tim kiem duoc luu nguyen van. Noi dung bai duoc ghi vao
        mot tep JSON Lines, moi dong mot bai, chi gom ma bai, tieu de, thoi diem
        dang va than bai (khong luu ten nguoi viet, nguoi dang).

        Tham so:
            thu_muc_dich: thu muc se chua cac tep.

        Tra ve:
            Danh sach tep da ghi: cac trang tim kiem va tep bai viet.

        Ngoai le:
            TaiVeError: khi khong goi duoc trang tin hoac khong bai nao khop mau loc.
            DinhDangError: khi phan hoi khong dung cau truc mong doi.
        """
        cau = self._nguon.tai_ve
        thu_muc_dich.mkdir(parents=True, exist_ok=True)
        cac_trang, ma_bai = self._liet_ke(thu_muc_dich)
        tep_bai = thu_muc_dich / str(cau["ten_tep_bai"])
        mau_loc = re.compile(str(cau["mau_loc"]))
        so_giu = 0
        with tep_bai.open("w", encoding="utf-8") as dau_ra:
            for thu_tu, ma in enumerate(ma_bai, start=1):
                bai = self._lay_bai(ma)
                if bai is not None and mau_loc.search(NapBaiViet.van_ban_thuan(bai["content"])):
                    dau_ra.write(json.dumps(bai, ensure_ascii=False) + "\n")
                    so_giu += 1
                if thu_tu % 100 == 0:
                    NHAT_KY.info("Nguon %s: da xet %d/%d bai", self._nguon.ten, thu_tu, len(ma_bai))
        NHAT_KY.info("Nguon %s: giu %d/%d bai khop mau loc", self._nguon.ten, so_giu, len(ma_bai))
        if so_giu == 0:
            raise TaiVeError(f"Khong bai nao cua nguon '{self._nguon.ten}' khop mau loc.")
        return [*cac_trang, tep_bai]

    @abstractmethod
    def _liet_ke(self, thu_muc_dich: Path) -> tuple[list[Path], list[str]]:
        """Luu cac trang tim kiem va tra ve (tep da luu, ma cac bai can lay)."""

    @abstractmethod
    def _lay_bai(self, ma: str) -> dict[str, Any] | None:
        """Lay mot bai theo ma; tra ve tu dien co khoa `content`, hoac None neu bai rong."""


class TaiBaiVietApi(TaiBaiViet):
    """Tai bai viet tu cong thong tin co API JSON: tim kiem phan trang va chi tiet bai."""

    def _liet_ke(self, thu_muc_dich: Path) -> tuple[list[Path], list[str]]:
        """Goi API tim kiem tung trang, luu trang va gom ma cac bai thuoc loai can lay."""
        cau = self._nguon.tai_ve
        kich_thuoc = int(cau["kich_thuoc_trang"])
        tham_so = dict(cau["tham_so_tim"])
        tham_so[str(cau["tham_so_kich_thuoc"])] = kich_thuoc
        cac_trang: list[Path] = []
        ma_bai: dict[str, None] = {}
        for trang in range(1, int(cau["so_trang_toi_da"]) + 1):
            tham_so[str(cau["tham_so_vi_tri"])] = trang
            noi_dung = self._khach.lay(str(cau["url_tim"]), tham_so)
            ban_ghi = NapJsonTrang.ban_ghi_trong(
                NapJsonTrang.giai_ma_json(noi_dung, str(cau["url_tim"])),
                list(cau["duong_ban_ghi"]),
                str(cau["url_tim"]),
            )
            if not ban_ghi:
                break
            tep = thu_muc_dich / str(cau["ten_tep_tim"]).format(trang=trang)
            tep.write_bytes(noi_dung)
            cac_trang.append(tep)
            for muc in ban_ghi:
                if muc.get("type") in cau["loai_bai"]:
                    ma_bai[str(muc["id"])] = None
            NHAT_KY.info(
                "Nguon %s: trang tim kiem %d co %d bai", self._nguon.ten, trang, len(ban_ghi)
            )
            if len(ban_ghi) < kich_thuoc:
                break
        return cac_trang, list(ma_bai)

    def _lay_bai(self, ma: str) -> dict[str, Any] | None:
        """Goi API chi tiet, chi giu cac truong khai bao o `truong_giu`."""
        cau = self._nguon.tai_ve
        tham_so = dict(cau["tham_so_bai"])
        tham_so[str(cau["tham_so_ma_bai"])] = ma
        noi_dung = self._khach.lay(str(cau["url_bai"]), tham_so)
        if not noi_dung.strip():
            NHAT_KY.warning("Nguon %s: bai %s tra ve rong, bo qua", self._nguon.ten, ma)
            return None
        bai = NapJsonTrang.giai_ma_json(noi_dung, f"{cau['url_bai']}?id={ma}")
        if not isinstance(bai, dict) or not bai.get("content"):
            return None
        return {truong: bai.get(truong) for truong in cau["truong_giu"]}


class TaiBaiVietHtml(TaiBaiViet):
    """Tai bai viet tu trang bao chi tra HTML: trang tim kiem va trang bai deu la HTML."""

    THE_DIV = re.compile(r"<(/?)div\b", re.IGNORECASE)

    def _liet_ke(self, thu_muc_dich: Path) -> tuple[list[Path], list[str]]:
        """Duyet ket qua tim kiem cua tung tu khoa cho den khi gap bai cu hon `tu_ngay`."""
        cau = self._nguon.tai_ve
        tu_ngay = pd.Timestamp(cau["tu_ngay"])
        cac_trang: list[Path] = []
        ma_bai: dict[str, None] = {}
        for thu_tu, tu_khoa in enumerate(cau["tu_khoa"], start=1):
            da_thay: dict[str, pd.Timestamp] = {}
            for trang in range(1, int(cau["so_trang_toi_da"]) + 1):
                noi_dung, cac_muc = self._lay_trang_tim_kiem(str(tu_khoa), trang, da_thay)
                if not cac_muc:
                    break
                tep = thu_muc_dich / str(cau["ten_tep_tim"]).format(tu_khoa=thu_tu, trang=trang)
                tep.write_bytes(noi_dung)
                cac_trang.append(tep)
                da_thay.update(cac_muc)
                ma_bai.update({ma: None for ma, ngay in cac_muc.items() if ngay >= tu_ngay})
                NHAT_KY.info(
                    "Nguon %s: tu khoa %r trang %d co %d bai",
                    self._nguon.ten,
                    tu_khoa,
                    trang,
                    len(cac_muc),
                )
                if max(cac_muc.values()) < tu_ngay:
                    break
        return cac_trang, list(ma_bai)

    def _lay_trang_tim_kiem(
        self, tu_khoa: str, trang: int, da_thay: dict[str, pd.Timestamp]
    ) -> tuple[bytes, dict[str, pd.Timestamp]]:
        """Tai mot trang tim kiem va chi nhan khi hai lan tai lien tiep cho cung ket qua hop le.

        May chu tim kiem doi khi tra nham trang (lap lai trang da xem, hoac trang
        cua mot truy van khac). Moi trang vi vay duoc tai it nhat hai lan; trang
        khong hop le (xem `ly_do_trang_sai`) hoac hai lan tai khac nhau thi tai lai.
        Tra ve noi dung tho va tu dien duong dan bai -> ngay dang.
        """
        cau = self._nguon.tai_ve
        mau_muc = re.compile(str(cau["mau_muc"]), re.DOTALL)
        tu_ngay = pd.Timestamp(cau["tu_ngay"])
        tham_so = {str(cau["tham_so_tu_khoa"]): tu_khoa, str(cau["tham_so_vi_tri"]): trang}
        lan_truoc: list[str] | None = None
        ly_do: str | None = "chua tai"
        for lan in range(1, int(cau["so_lan_thu_trang"]) + 1):
            noi_dung = self._khach.lay(str(cau["url_tim"]), tham_so)
            cac_muc = {
                html.unescape(muc["url"]): pd.Timestamp(
                    int(muc["nam"]), int(muc["thang"]), int(muc["ngay"])
                )
                for muc in mau_muc.finditer(noi_dung.decode("utf-8", errors="replace"))
            }
            ly_do = self.ly_do_trang_sai(cac_muc, trang, da_thay, tu_ngay)
            if ly_do is None and lan_truoc == list(cac_muc):
                return noi_dung, cac_muc
            if ly_do is None:
                ly_do = "hai lan tai cho ket qua khac nhau"
                lan_truoc = list(cac_muc)
                continue
            NHAT_KY.warning(
                "Nguon %s: tu khoa %r trang %d khong hop le (%s), tai lai lan %d",
                self._nguon.ten,
                tu_khoa,
                trang,
                ly_do,
                lan,
            )
            lan_truoc = None
            time.sleep(2.0 * lan)
        raise TaiVeError(
            f"Trang tim kiem {trang} cua tu khoa {tu_khoa!r} khong on dinh ({ly_do}). "
            "Hay chay lai giai doan nap sau it phut."
        )

    @staticmethod
    def ly_do_trang_sai(
        cac_muc: dict[str, pd.Timestamp],
        trang: int,
        da_thay: dict[str, pd.Timestamp],
        tu_ngay: pd.Timestamp,
    ) -> str | None:
        """Kiem tra mot trang ket qua tim kiem co noi tiep dung cac trang truoc khong.

        Ket qua tim kiem xep tu moi den cu, nen mot trang dung phai: (a) co bai
        chua thay o cac trang truoc, (b) khong chua bai moi hon bai cu nhat da
        thay, (c) neu la trang dau thi co bai khong cu hon `tu_ngay`.

        Tham so:
            cac_muc: duong dan bai -> ngay dang cua trang vua tai.
            trang: so thu tu trang, tinh tu 1.
            da_thay: duong dan bai -> ngay dang cua cac trang truoc, cung tu khoa.
            tu_ngay: moc thoi gian som nhat can lay.

        Tra ve:
            None neu trang hop le (ke ca trang rong, tuc da het ket qua); nguoc lai
            la chuoi neu ly do.

        Ngoai le:
            Khong co.
        """
        if not cac_muc:
            return None
        if set(cac_muc) <= set(da_thay):
            return "lap lai trang da xem"
        if da_thay and max(cac_muc.values()) > min(da_thay.values()):
            return "co bai moi hon bai cu nhat cua trang truoc"
        if trang == 1 and max(cac_muc.values()) < tu_ngay:
            return "trang dau khong co bai nao tu moc thoi gian can lay"
        return None

    def _lay_bai(self, ma: str) -> dict[str, Any] | None:
        """Tai trang bai, tach tieu de, thoi diem dang, tom tat va than bai."""
        cau = self._nguon.tai_ve
        trang = self._khach.lay(str(cau["url_goc"]) + ma).decode("utf-8", errors="replace")
        thoi_diem = re.search(str(cau["mau_thoi_diem_dang"]), trang)
        than_bai = self.khoi_div(trang, str(cau["mau_the_noi_dung"]))
        if thoi_diem is None or than_bai is None:
            NHAT_KY.warning(
                "Nguon %s: bai %s thieu thoi diem dang hoac than bai", self._nguon.ten, ma
            )
            return None
        tieu_de = re.search(str(cau["mau_tieu_de"]), trang, re.DOTALL)
        tom_tat = re.search(str(cau["mau_tom_tat"]), trang, re.DOTALL)
        return {
            "id": ma,
            "title": html.unescape(tieu_de["tieu_de"]).strip() if tieu_de else "",
            "publishTime": html.unescape(thoi_diem["thoi_diem"]),
            "content": (f"<p>{tom_tat['tom_tat']}</p>" if tom_tat else "") + than_bai,
        }

    @classmethod
    def khoi_div(cls, trang: str, mau_the_mo: str) -> str | None:
        """Cat nguyen mot khoi <div>, ke ca cac div long ben trong.

        Tham so:
            trang: ma HTML cua ca trang.
            mau_the_mo: bieu thuc chinh quy khop the mo cua khoi can lay.

        Tra ve:
            Ma HTML cua khoi tu the mo den the dong tuong ung, hoac None neu
            khong thay the mo hay khoi khong dong.

        Ngoai le:
            Khong co.
        """
        the_mo = re.search(mau_the_mo, trang)
        if the_mo is None:
            return None
        do_sau = 0
        for the in cls.THE_DIV.finditer(trang, the_mo.start()):
            do_sau += -1 if the.group(1) else 1
            if do_sau == 0:
                return trang[the_mo.start() : trang.find(">", the.end()) + 1]
        return None


class KhoDem:
    """Bo dem du lieu tho: chi tai khi thu muc du lieu chua co tep cua nguon."""

    LOP_THEO_KIEU: dict[str, type[BoTai]] = {
        "api_phan_trang": TaiApiPhanTrang,
        "tep": TaiTep,
        "bai_viet_api": TaiBaiVietApi,
        "bai_viet_html": TaiBaiVietHtml,
    }

    def __init__(self, cau_hinh: CauHinh, khach: KhachHttp | None = None) -> None:
        """Tao bo dem.

        Tham so:
            cau_hinh: cau hinh cua du an.
            khach: khach HTTP; bo trong thi tao tu cau hinh khi can tai.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._cau_hinh = cau_hinh
        self._khach = khach

    def dam_bao(self) -> dict[str, int]:
        """Bao dam moi nguon deu co tep trong thu muc du lieu, thieu thi tai ve.

        Tep tai ve duoc ghi vao thu muc tam roi moi chuyen sang thu muc du lieu,
        nen thu muc du lieu khong bao gio chua tep tai do. Tep da co thi khong
        bao gio bi ghi de.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien ten nguon -> so tep vua tai (0 neu da co san).

        Ngoai le:
            TaiVeError: khi nguon chua co tep ma khong tai duoc.
            CauHinhError: khi nguon khong khai bao cach tai.
        """
        thu_muc_du_lieu = self._cau_hinh.duong_dan("du_lieu")
        so_tep_moi: dict[str, int] = {}
        for nguon in self._cau_hinh.cac_nguon:
            co_san = BoNapNhieuNguon.tao_bo_nap(nguon).tim_tep(thu_muc_du_lieu)
            if co_san:
                NHAT_KY.info("Nguon %s: da co %d tep, khong tai lai", nguon.ten, len(co_san))
                so_tep_moi[nguon.ten] = 0
                continue
            bo_tai = self._tao_bo_tai(nguon)
            NHAT_KY.info("Nguon %s: chua co tep, bat dau tai bang %r", nguon.ten, bo_tai)
            thu_muc_tam = self._cau_hinh.duong_dan("tai_tam") / nguon.ten
            if thu_muc_tam.exists():
                shutil.rmtree(thu_muc_tam)
            cac_tep = bo_tai.tai(thu_muc_tam)
            thu_muc_dich = thu_muc_du_lieu / nguon.thu_muc
            thu_muc_dich.mkdir(parents=True, exist_ok=True)
            for tep in cac_tep:
                shutil.move(str(tep), str(thu_muc_dich / tep.name))
            shutil.rmtree(thu_muc_tam)
            so_tep_moi[nguon.ten] = len(cac_tep)
        return so_tep_moi

    def _tao_bo_tai(self, nguon: CauHinhNguon) -> BoTai:
        """Chon lop tai theo `tai_ve.kieu` cua nguon."""
        kieu = nguon.tai_ve.get("kieu")
        if kieu not in self.LOP_THEO_KIEU:
            raise CauHinhError(
                f"Nguon '{nguon.ten}': tai_ve.kieu {kieu!r} khong thuoc {list(self.LOP_THEO_KIEU)}."
            )
        if self._khach is None:
            self._khach = KhachHttp.tu_cau_hinh(self._cau_hinh)
        return self.LOP_THEO_KIEU[kieu](nguon, self._khach)


class NapJsonTrang(BoNap):
    """Nap cac tep JSON la tung trang ket qua cua mot API."""

    def doc_tep(self, tep: Path) -> pd.DataFrame:
        """Doc mot trang JSON va lay cac truong da khai bao.

        Tham so:
            tep: tep JSON cua mot trang ket qua.

        Tra ve:
            Bang voi cac cot chung, gia tri giu nguyen nhu trong tep.

        Ngoai le:
            DinhDangError: khi tep khong phai JSON hoac thieu duong toi ban ghi.
            ThieuCotError: khi ban ghi thieu truong khai bao trong `doc.cot`.
        """
        du_lieu = self.giai_ma_json(tep.read_bytes(), tep.name)
        ban_ghi = self.ban_ghi_trong(du_lieu, list(self._nguon.doc["duong_ban_ghi"]), tep.name)
        return self._chon_cot(pd.DataFrame.from_records(ban_ghi), tep)

    @staticmethod
    def giai_ma_json(noi_dung: bytes, noi: str) -> Any:
        """Giai ma mot khoi byte thanh doi tuong JSON.

        Tham so:
            noi_dung: noi dung tho.
            noi: ten tep hoac dia chi, dung trong thong bao loi.

        Tra ve:
            Doi tuong Python tuong ung voi JSON.

        Ngoai le:
            DinhDangError: khi noi dung khong phai JSON UTF-8 hop le.
        """
        try:
            return json.loads(noi_dung.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as loi:
            raise DinhDangError(f"'{noi}' khong phai JSON hop le: {loi}") from loi

    @staticmethod
    def ban_ghi_trong(du_lieu: Any, duong: list[str], noi: str) -> list[dict[str, Any]]:
        """Di theo mot duong khoa de lay danh sach ban ghi trong JSON long nhau.

        Tham so:
            du_lieu: doi tuong JSON da giai ma.
            duong: day khoa tu cap ngoai vao trong, vi du ["response", "data"].
            noi: ten tep hoac dia chi, dung trong thong bao loi.

        Tra ve:
            Danh sach ban ghi (moi ban ghi la mot tu dien).

        Ngoai le:
            DinhDangError: khi thieu mot khoa tren duong di hoac dich khong phai
                danh sach hay tu dien cac ban ghi.
        """
        hien_tai = du_lieu
        for khoa in duong:
            if not isinstance(hien_tai, dict) or khoa not in hien_tai:
                raise DinhDangError(f"'{noi}' thieu khoa '{khoa}' tren duong {duong}.")
            hien_tai = hien_tai[khoa]
        if isinstance(hien_tai, dict):
            hien_tai = list(hien_tai.values())
        if not isinstance(hien_tai, list):
            raise DinhDangError(f"'{noi}': gia tri tai {duong} khong phai danh sach ban ghi.")
        return hien_tai


class NapCsvKhoi(BoNap):
    """Nap tep CSV lon bang cach doc tung khoi va chi giu cot, dong can dung."""

    def doc_tep(self, tep: Path) -> pd.DataFrame:
        """Doc tep CSV theo khoi, loc dong theo dieu kien trong `doc.loc`.

        Tham so:
            tep: tep CSV can doc.

        Tra ve:
            Bang voi cac cot chung, moi gia tri la chuoi nhu trong tep.

        Ngoai le:
            DinhDangError: khi tep rong hoac khong doc duoc nhu CSV.
            ThieuCotError: khi tep thieu cot khai bao trong `doc.cot` hoac `doc.loc`.
        """
        cau = self._nguon.doc
        dieu_kien = {str(cot): str(gia_tri) for cot, gia_tri in (cau.get("loc") or {}).items()}
        can_doc = sorted({*map(str, cau["cot"].values()), *dieu_kien})
        try:
            tieu_de = pd.read_csv(tep, nrows=0, encoding="utf-8").columns
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as loi:
            raise DinhDangError(f"Tep '{tep.name}' khong doc duoc nhu CSV: {loi}") from loi
        thieu = [cot for cot in can_doc if cot not in tieu_de]
        if thieu:
            raise ThieuCotError(f"Tep '{tep.name}' thieu cot: {thieu}.")
        cac_khoi = []
        doc_khoi = pd.read_csv(
            tep,
            usecols=can_doc,
            dtype=str,
            keep_default_na=False,
            chunksize=int(cau["kich_thuoc_khoi"]),
            encoding="utf-8",
        )
        for khoi in doc_khoi:
            giu = pd.Series(True, index=khoi.index)
            for cot, gia_tri in dieu_kien.items():
                giu &= khoi[cot].eq(gia_tri)
            cac_khoi.append(khoi.loc[giu])
        bang = pd.concat(cac_khoi, ignore_index=True) if cac_khoi else pd.DataFrame(columns=can_doc)
        return self._chon_cot(bang, tep)


class NapExcel(BoNap):
    """Nap mot trang tinh Excel."""

    def doc_tep(self, tep: Path) -> pd.DataFrame:
        """Doc trang tinh khai bao trong `doc` va lay cac cot can dung.

        Tham so:
            tep: tep Excel (.xls) can doc.

        Tra ve:
            Bang voi cac cot chung, gia tri giu nguyen nhu trong o.

        Ngoai le:
            DinhDangError: khi tep khong phai Excel hop le hoac thieu trang tinh.
            ThieuCotError: khi trang tinh thieu cot khai bao trong `doc.cot`.
        """
        cau = self._nguon.doc
        try:
            bang = pd.read_excel(
                tep,
                sheet_name=cau["trang_tinh"],
                header=int(cau["dong_tieu_de"]),
                dtype=object,
            )
        except (XLRDError, ValueError, KeyError) as loi:
            raise DinhDangError(f"Tep '{tep.name}' khong doc duoc nhu Excel: {loi}") from loi
        return self._chon_cot(bang, tep)


class NapBaiViet(BoNap):
    """Nap bai viet (JSON Lines) va tach cac cau neu gia bang bieu thuc chinh quy."""

    THE_XUONG_DONG = re.compile(r"<br\s*/?>|</(?:p|div|li|tr|h[1-6])>", re.IGNORECASE)
    THE_BAT_KY = re.compile(r"<[^>]+>")
    KHOANG_TRANG = re.compile(r"[ \t ​﻿]+")

    def doc_tep(self, tep: Path) -> pd.DataFrame:
        """Doc tep bai viet, moi cau neu gia thanh mot dong.

        Neu nguon khai bao `mau_thoi_diem`, ngay cua moi dong la cau neu thoi diem
        ap dung trong bai; bai khong co cau do thi khong phai thong bao dieu hanh
        gia va bi bo qua. Neu khong khai bao, ngay la thoi diem dang bai, va bai
        dang muon hon duoc xet truoc: ngay nao co hai lan dieu chinh thi gia cuoi
        ngay dung truoc va duoc giu khi bo ban ghi trung.

        Tham so:
            tep: tep JSON Lines, moi dong la mot bai viet.

        Tra ve:
            Bang voi cac cot `ngay`, `chuoi`, `gia_tri`, `don_vi`, `van_ban`; so
            va ngay con o dang chuoi nhu trong bai.

        Ngoai le:
            DinhDangError: khi mot dong khong phai JSON hop le.
            ThieuCotError: khi bai thieu truong khai bao trong `doc`.
        """
        cau = self._nguon.doc
        mau_thoi_diem = re.compile(str(cau["mau_thoi_diem"])) if cau.get("mau_thoi_diem") else None
        cac_mau_gia = [re.compile(str(mau)) for mau in cau["mau_gia"]]
        so_ky_tu_sau = int(cau["so_ky_tu_sau_cau_gia"])
        cac_dong: list[dict[str, str]] = []
        so_bai = so_bo_qua = 0
        cac_bai = list(self._doc_tung_bai(tep))
        if mau_thoi_diem is None:
            truong = str(cau["truong_thoi_diem"])
            cac_bai.sort(key=lambda bai: str(bai[truong]), reverse=True)
        for bai in cac_bai:
            so_bai += 1
            van_ban = self.van_ban_thuan(bai[str(cau["truong_noi_dung"])])
            ngay = self._ngay_cua_bai(bai, van_ban, mau_thoi_diem)
            if ngay is None:
                so_bo_qua += 1
                continue
            for mau in cac_mau_gia:
                for khop in mau.finditer(van_ban):
                    cac_dong.append(
                        {
                            "ngay": ngay,
                            "chuoi": khop.group("chuoi").strip(),
                            "gia_tri": khop.group("gia_tri"),
                            "don_vi": khop.group("don_vi"),
                            "van_ban": self._cau_chua(
                                van_ban, khop.start(), khop.end(), so_ky_tu_sau
                            ),
                        }
                    )
        NHAT_KY.info(
            "Nguon %s: %d bai, bo qua %d bai khong co thoi diem ap dung, tach duoc %d cau gia",
            self._nguon.ten,
            so_bai,
            so_bo_qua,
            len(cac_dong),
        )
        return pd.DataFrame(cac_dong, columns=["ngay", "chuoi", "gia_tri", "don_vi", "van_ban"])

    def _ngay_cua_bai(
        self, bai: dict[str, Any], van_ban: str, mau_thoi_diem: re.Pattern[str] | None
    ) -> str | None:
        """Lay chuoi ngay tho cua bai: cau neu thoi diem ap dung, hoac thoi diem dang."""
        if mau_thoi_diem is None:
            return str(bai[str(self._nguon.doc["truong_thoi_diem"])])
        thoi_diem = mau_thoi_diem.search(van_ban)
        return None if thoi_diem is None else thoi_diem.group("ngay")

    def _doc_tung_bai(self, tep: Path) -> Iterator[dict[str, Any]]:
        """Duyet tung dong JSON cua tep, kiem tra cac truong ma cau hinh khai bao."""
        cau = self._nguon.doc
        can_co = [
            str(cau[khoa]) for khoa in ("truong_noi_dung", "truong_thoi_diem") if cau.get(khoa)
        ]
        with tep.open(encoding="utf-8") as dau_vao:
            for so_dong, dong in enumerate(dau_vao, start=1):
                if not dong.strip():
                    continue
                bai = NapJsonTrang.giai_ma_json(dong.encode("utf-8"), f"{tep.name} dong {so_dong}")
                la_bai = isinstance(bai, dict)
                thieu = [truong for truong in can_co if not la_bai or truong not in bai]
                if thieu:
                    raise ThieuCotError(f"Tep '{tep.name}' dong {so_dong} thieu truong {thieu}.")
                yield bai

    @classmethod
    def van_ban_thuan(cls, ma_html: str | None) -> str:
        """Doi mot doan HTML thanh van ban thuan, moi doan mot dong.

        Tham so:
            ma_html: noi dung HTML cua bai viet, co the la None.

        Tra ve:
            Van ban da bo the, giai ma thuc the HTML, dua ve dang Unicode NFC va
            gop khoang trang.

        Ngoai le:
            Khong co.
        """
        van_ban = cls.THE_XUONG_DONG.sub("\n", ma_html or "")
        van_ban = html.unescape(cls.THE_BAT_KY.sub("", van_ban))
        van_ban = unicodedata.normalize("NFC", van_ban)
        cac_dong = (cls.KHOANG_TRANG.sub(" ", dong).strip() for dong in van_ban.splitlines())
        return "\n".join(dong for dong in cac_dong if dong)

    @staticmethod
    def _cau_chua(van_ban: str, dau: int, cuoi: int, so_ky_tu_sau: int) -> str:
        """Lay doan van tu cho khop den het dong, toi da `so_ky_tu_sau` ky tu sau cho khop."""
        cuoi_dong = van_ban.find("\n", cuoi)
        cuoi_dong = len(van_ban) if cuoi_dong == -1 else cuoi_dong
        return van_ban[dau : min(cuoi_dong, cuoi + so_ky_tu_sau)]


class BoNapNhieuNguon:
    """Nap moi nguon khai bao trong cau hinh va noi doc thanh mot bang tho."""

    LOP_THEO_LOAI: dict[str, type[BoNap]] = {
        "json_trang": NapJsonTrang,
        "csv_khoi": NapCsvKhoi,
        "excel": NapExcel,
        "bai_viet": NapBaiViet,
    }

    def __init__(self, cau_hinh: CauHinh) -> None:
        """Tao bo nap cho moi nguon trong cau hinh.

        Tham so:
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Khong co.

        Ngoai le:
            CauHinhError: khi mot nguon co `loai` khong ho tro.
        """
        self._cau_hinh = cau_hinh
        self._bo_nap = {nguon.ten: self.tao_bo_nap(nguon) for nguon in cau_hinh.cac_nguon}

    def __iter__(self) -> Iterator[BoNap]:
        """Duyet bo nap cua tung nguon theo thu tu khai bao trong cau hinh.

        Tham so:
            Khong co.

        Tra ve:
            Bo lap qua cac doi tuong BoNap.

        Ngoai le:
            Khong co.
        """
        return iter(self._bo_nap.values())

    @classmethod
    def tao_bo_nap(cls, nguon: CauHinhNguon) -> BoNap:
        """Tao doi tuong nap phu hop voi `loai` cua nguon.

        Tham so:
            nguon: khai bao nguon doc tu cau hinh.

        Tra ve:
            Doi tuong thuoc mot lop con cua BoNap.

        Ngoai le:
            CauHinhError: khi `loai` khong co lop nap tuong ung.
        """
        if nguon.loai not in cls.LOP_THEO_LOAI:
            raise CauHinhError(
                f"Nguon '{nguon.ten}': loai {nguon.loai!r} khong thuoc {list(cls.LOP_THEO_LOAI)}."
            )
        return cls.LOP_THEO_LOAI[nguon.loai](nguon)

    def nap(self, duong_dan: str | Path) -> pd.DataFrame:
        """Nap du lieu tho tu mot thu muc du lieu hoac tu mot tep nguon.

        Tham so:
            duong_dan: thu muc chua `raw/` va `external/` (nap moi nguon), hoac
                duong dan mot tep cua mot nguon (chi nap tep do). Duong dan
                tuong doi duoc tinh tu thu muc hien hanh, khong thay thi tinh
                tu thu muc goc cua kho.

        Tra ve:
            Bang tho theo luoc do chung, moi cot la chuoi.

        Ngoai le:
            ThieuTepError: khi duong dan khong ton tai, hoac thu muc thieu tep
                cua mot nguon, hoac ten tep khong khop nguon nao.
        """
        vi_tri = self._tim_duong_dan(Path(duong_dan))
        if vi_tri.is_dir():
            cac_bang = [bo_nap.nap(vi_tri) for bo_nap in self]
        else:
            cac_bang = [self._bo_nap_cho_tep(vi_tri).nap_tep(vi_tri)]
        bang = pd.concat(cac_bang, ignore_index=True)
        for ten, so_dong in bang["nguon"].value_counts(sort=False).items():
            NHAT_KY.info("Nap nguon %s: %d dong", ten, so_dong)
        return bang

    def _tim_duong_dan(self, duong_dan: Path) -> Path:
        """Tim duong dan theo thu muc hien hanh roi theo thu muc goc cua kho."""
        if duong_dan.exists():
            return duong_dan
        tu_goc = self._cau_hinh.thu_muc_goc / duong_dan
        if not duong_dan.is_absolute() and tu_goc.exists():
            return tu_goc
        raise ThieuTepError(f"Khong tim thay duong dan du lieu '{duong_dan}'.")

    def _bo_nap_cho_tep(self, tep: Path) -> BoNap:
        """Chon bo nap co mau ten tep khop voi tep; trung ten thi xet them ten thu muc chua tep."""
        khop_ten = [bo for bo in self if fnmatch.fnmatch(tep.name, bo.nguon.mau_ten_tep)]
        khop_thu_muc = [bo for bo in khop_ten if Path(bo.nguon.thu_muc).name == tep.parent.name]
        ung_vien = khop_thu_muc or khop_ten
        if len(ung_vien) == 1:
            return ung_vien[0]
        if not ung_vien:
            raise ThieuTepError(
                f"Tep '{tep.name}' khong khop mau ten tep cua nguon nao trong cau hinh."
            )
        raise ThieuTepError(
            f"Tep '{tep.name}' khop mau ten tep cua nhieu nguon "
            f"({[bo.nguon.ten for bo in ung_vien]}); hay dat tep trong thu muc mang ten nguon."
        )


def nap_du_lieu(duong_dan: str | Path) -> pd.DataFrame:
    """Nap du lieu tho thanh mot bang theo luoc do chung.

    Tham so:
        duong_dan: thu muc du lieu chua `raw/` va `external/`, hoac mot tep nguon.

    Tra ve:
        Bang tho, moi dong la mot quan sat cua mot nguon, moi cot la chuoi dung
        nhu trong tep goc: nguon, tep, ngay, chuoi, gia_tri, don_vi, van_ban.

    Ngoai le:
        ThieuTepError: khi duong dan khong ton tai hoac thieu tep cua mot nguon.
        DinhDangError: khi mot tep khong dung dinh dang da khai bao.
        ThieuCotError: khi mot tep thieu truong da khai bao trong cau hinh.
    """
    return BoNapNhieuNguon(CauHinh.tu_tep()).nap(duong_dan)
