"""Doc cau_hinh.yaml, kiem tra gia tri va cung cap truy cap co kieu cho ca goi."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .lop_co_so import CauHinhError, LichSuKien, SuKien, ThamSoError


@dataclass(frozen=True)
class CauHinhNguon:
    """Khai bao mot nguon du lieu: tep nam o dau, doc bang lop nao, tai tu dau."""

    ten: str
    mo_ta: str
    loai: str
    dinh_dang: str
    vai_tro: str
    thu_muc: str
    mau_ten_tep: str
    doc: dict[str, Any] = field(default_factory=dict)
    tai_ve: dict[str, Any] = field(default_factory=dict)
    gia_tri_co_dinh: dict[str, str] = field(default_factory=dict)

    @property
    def mau_tep(self) -> str:
        """Mau tim tep tinh tu thu muc du lieu.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi dang "raw/eia/gia_giao_ngay_trang_*.json".

        Ngoai le:
            Khong co.
        """
        return f"{self.thu_muc}/{self.mau_ten_tep}"


@dataclass(frozen=True)
class QuyTacDanhMuc:
    """Mot quy tac dua nhan chuoi tho ve ma chuoi chuan."""

    ma: str
    ten: str
    thi_truong: str
    nhom_hang: str
    don_vi: str
    nguon: tuple[str, ...]
    nhan_chuan: str
    mau: re.Pattern[str]
    mau_don_vi: re.Pattern[str]


class CauHinh:
    """Noi dung cau_hinh.yaml da kiem tra, kem cach doi duong dan tuong doi."""

    TEN_TEP_MAC_DINH = "cau_hinh.yaml"
    KHOA_BAT_BUOC = (
        "du_an",
        "duong_dan",
        "tai_ve",
        "nguon",
        "luoc_do",
        "lam_sach",
        "danh_muc",
        "don_vi",
        "tra_cuu",
        "su_kien",
        "phan_tich",
        "bieu_do",
    )
    LOAI_NGUON = ("json_trang", "csv_khoi", "excel", "bai_viet")
    VAI_TRO = ("gia", "tra_cuu")

    def __init__(self, noi_dung: dict[str, Any], thu_muc_goc: Path) -> None:
        """Tao cau hinh tu noi dung da doc.

        Tham so:
            noi_dung: tu dien doc tu tep yaml.
            thu_muc_goc: thu muc goc cua kho, moi duong dan tuong doi tinh tu day.

        Tra ve:
            Khong co.

        Ngoai le:
            CauHinhError: khi thieu khoa bat buoc hoac gia tri khong hop le.
        """
        self._noi_dung = noi_dung
        self._thu_muc_goc = thu_muc_goc
        self._kiem_tra()

    def __repr__(self) -> str:
        """Mo ta ngan gon cau hinh, dung khi ghi nhat ky.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi gom ten thu muc goc va so nguon du lieu.

        Ngoai le:
            Khong co.
        """
        return f"CauHinh(thu_muc_goc={self._thu_muc_goc.name!r}, so_nguon={len(self.cac_nguon)})"

    def __getitem__(self, khoa: str) -> Any:
        """Lay mot gia tri cau hinh theo duong dan khoa, vi du cau_hinh["lam_sach.kieu_so"].

        Tham so:
            khoa: ten khoa, cac cap cach nhau bang dau cham.

        Tra ve:
            Gia tri tuong ung trong tep cau hinh.

        Ngoai le:
            CauHinhError: khi tep cau hinh khong co khoa nay.
        """
        hien_tai: Any = self._noi_dung
        for phan in khoa.split("."):
            if not isinstance(hien_tai, dict) or phan not in hien_tai:
                raise CauHinhError(f"Tep cau hinh thieu khoa '{khoa}'.")
            hien_tai = hien_tai[phan]
        return hien_tai

    @classmethod
    def tu_tep(
        cls, duong_dan: str | Path | None = None, thu_muc_goc: str | Path | None = None
    ) -> CauHinh:
        """Doc cau hinh tu tep yaml.

        Tham so:
            duong_dan: duong dan tep cau hinh; bo trong thi dung cau_hinh.yaml o
                thu muc goc cua kho.
            thu_muc_goc: thu muc dung de doi duong dan tuong doi trong cau hinh;
                bo trong thi dung thu muc goc cua kho.

        Tra ve:
            Doi tuong CauHinh da kiem tra.

        Ngoai le:
            CauHinhError: khi tep khong ton tai, khong phai yaml hop le hoac thieu khoa.
        """
        goc = cls.thu_muc_goc_kho() if thu_muc_goc is None else Path(thu_muc_goc)
        tep = goc / cls.TEN_TEP_MAC_DINH if duong_dan is None else Path(duong_dan)
        if not tep.is_file():
            raise CauHinhError(f"Khong tim thay tep cau hinh '{tep}'.")
        try:
            noi_dung = yaml.safe_load(tep.read_text(encoding="utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError) as loi:
            mo_ta = " ".join(str(loi).split())
            raise CauHinhError(f"Tep cau hinh '{tep}' khong phai yaml hop le: {mo_ta}") from loi
        if not isinstance(noi_dung, dict):
            raise CauHinhError(f"Tep cau hinh '{tep}' phai la mot tu dien o cap ngoai cung.")
        return cls(noi_dung, goc)

    @staticmethod
    def thu_muc_goc_kho() -> Path:
        """Thu muc goc cua kho, suy ra tu vi tri cua goi ma nguon.

        Tham so:
            Khong co.

        Tra ve:
            Duong dan thu muc chua `src/`, `data/` va cau_hinh.yaml.

        Ngoai le:
            Khong co.
        """
        return Path(__file__).resolve().parents[2]

    @property
    def thu_muc_goc(self) -> Path:
        """Thu muc goc dung de doi duong dan tuong doi.

        Tham so:
            Khong co.

        Tra ve:
            Duong dan thu muc goc.

        Ngoai le:
            Khong co.
        """
        return self._thu_muc_goc

    def duong_dan(self, ten: str) -> Path:
        """Doi mot duong dan khai bao trong muc `duong_dan` thanh duong dan day du.

        Tham so:
            ten: ten khoa trong muc `duong_dan`, vi du "bang_sach".

        Tra ve:
            Duong dan tinh tu thu muc goc cua kho.

        Ngoai le:
            CauHinhError: khi khoa khong co trong cau hinh.
        """
        return self._thu_muc_goc / str(self[f"duong_dan.{ten}"])

    def tuong_doi(self, duong_dan: Path) -> str:
        """Viet mot duong dan o dang tuong doi so voi thu muc goc, dung dau '/'.

        Tham so:
            duong_dan: duong dan can viet lai.

        Tra ve:
            Chuoi duong dan tuong doi; neu nam ngoai kho thi tra ve ten tep.

        Ngoai le:
            Khong co.
        """
        try:
            return duong_dan.resolve().relative_to(self._thu_muc_goc.resolve()).as_posix()
        except ValueError:
            return duong_dan.name

    @property
    def seed(self) -> int:
        """Gia tri seed dung cho moi buoc co yeu to ngau nhien.

        Tham so:
            Khong co.

        Tra ve:
            So nguyen seed.

        Ngoai le:
            Khong co.
        """
        return int(self["du_an.seed"])

    @property
    def dpi(self) -> int:
        """Do phan giai khi luu bieu do.

        Tham so:
            Khong co.

        Tra ve:
            So diem anh tren mot inch.

        Ngoai le:
            Khong co.
        """
        return int(self["bieu_do.dpi"])

    @property
    def cac_nguon(self) -> list[CauHinhNguon]:
        """Danh sach nguon du lieu da khai bao.

        Tham so:
            Khong co.

        Tra ve:
            Danh sach CauHinhNguon theo thu tu trong tep cau hinh.

        Ngoai le:
            Khong co.
        """
        return [
            CauHinhNguon(
                ten=str(muc["ten"]),
                mo_ta=str(muc["mo_ta"]),
                loai=str(muc["loai"]),
                dinh_dang=str(muc["dinh_dang"]),
                vai_tro=str(muc["vai_tro"]),
                thu_muc=str(muc["thu_muc"]),
                mau_ten_tep=str(muc["mau_ten_tep"]),
                doc=dict(muc.get("doc") or {}),
                tai_ve=dict(muc.get("tai_ve") or {}),
                gia_tri_co_dinh={
                    str(k): str(v) for k, v in (muc.get("gia_tri_co_dinh") or {}).items()
                },
            )
            for muc in self["nguon"]
        ]

    @property
    def quy_tac_danh_muc(self) -> list[QuyTacDanhMuc]:
        """Cac quy tac chuan hoa nhan chuoi, theo thu tu uu tien.

        Tham so:
            Khong co.

        Tra ve:
            Danh sach QuyTacDanhMuc voi bieu thuc chinh quy da bien dich.

        Ngoai le:
            Khong co.
        """
        return [
            QuyTacDanhMuc(
                ma=str(muc["ma"]),
                ten=str(muc["ten"]),
                thi_truong=str(muc["thi_truong"]),
                nhom_hang=str(muc["nhom_hang"]),
                don_vi=str(muc["don_vi"]),
                nguon=tuple(str(ten) for ten in muc["nguon"]),
                nhan_chuan=str(muc["nhan_chuan"]),
                mau=re.compile(str(muc["mau"]), re.IGNORECASE),
                mau_don_vi=re.compile(str(muc["mau_don_vi"]), re.IGNORECASE),
            )
            for muc in self["danh_muc"]
        ]

    def quy_tac_theo_ma(self, ma: str) -> QuyTacDanhMuc:
        """Tim quy tac danh muc cua mot ma chuoi chuan.

        Tham so:
            ma: ma chuoi chuan, vi du "vn_ron95".

        Tra ve:
            Quy tac danh muc cua chuoi, noi co ten hien thi va nhom hang.

        Ngoai le:
            CauHinhError: khi muc `danh_muc` khong khai bao ma chuoi nay.
        """
        for quy_tac in self.quy_tac_danh_muc:
            if quy_tac.ma == ma:
                return quy_tac
        raise CauHinhError(f"Muc 'danh_muc' cua cau hinh khong khai bao chuoi '{ma}'.")

    @property
    def lich_su_kien(self) -> LichSuKien:
        """Lich cac su kien (boi canh) khai bao trong cau hinh.

        Tham so:
            Khong co.

        Tra ve:
            Doi tuong LichSuKien.

        Ngoai le:
            Khong co.
        """
        cac_su_kien = [
            SuKien(
                ma=str(muc["ma"]),
                ten=str(muc["ten"]),
                ten_ngan=str(muc.get("ten_ngan", muc["ten"])),
                loai=str(muc["loai"]),
                bat_dau=pd.Timestamp(muc["bat_dau"]),
                ket_thuc=None if muc.get("ket_thuc") is None else pd.Timestamp(muc["ket_thuc"]),
                nguon=str(muc.get("nguon", "")),
            )
            for muc in self["su_kien.danh_sach"]
        ]
        return LichSuKien(cac_su_kien, str(self["su_kien.nhan_binh_thuong"]))

    @property
    def ngay_bat_dau(self) -> pd.Timestamp:
        """Ngay dau cua khoang phan tich.

        Tham so:
            Khong co.

        Tra ve:
            Moc thoi gian dau khoang.

        Ngoai le:
            Khong co.
        """
        return pd.Timestamp(self["phan_tich.bat_dau"])

    @property
    def ngay_ket_thuc(self) -> pd.Timestamp | None:
        """Ngay cuoi cua khoang phan tich.

        Tham so:
            Khong co.

        Tra ve:
            Moc thoi gian cuoi khoang, hoac None neu lay den het du lieu.

        Ngoai le:
            Khong co.
        """
        gia_tri = self["phan_tich.ket_thuc"]
        return None if gia_tri is None else pd.Timestamp(gia_tri)

    def _kiem_tra(self) -> None:
        """Kiem tra khoa bat buoc, kieu va mien gia tri cua cau hinh."""
        thieu = [khoa for khoa in self.KHOA_BAT_BUOC if khoa not in self._noi_dung]
        if thieu:
            raise CauHinhError(f"Tep cau hinh thieu cac muc: {thieu}.")
        self._kiem_tra_du_an()
        self._kiem_tra_nguon()
        self._kiem_tra_quy_tac()
        self._kiem_tra_khoang_va_su_kien()

    def _kiem_tra_du_an(self) -> None:
        """Kiem tra muc `du_an`: seed la so nguyen, so nhom va tung MSSV la chuoi."""
        seed = self["du_an.seed"]
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise CauHinhError(f"du_an.seed phai la so nguyen, dang la {seed!r}.")
        if not isinstance(self["du_an.thanh_vien"], list) or not self["du_an.thanh_vien"]:
            raise CauHinhError("du_an.thanh_vien phai la danh sach MSSV khong rong.")
        # khong co dau nhay kep thi YAML doc 07 thanh so 7: so nhom va MSSV phai la chuoi
        nhom_va_mssv = [self["du_an.nhom"], *self["du_an.thanh_vien"]]
        if not all(isinstance(gia_tri, str) for gia_tri in nhom_va_mssv):
            raise CauHinhError(
                'du_an.nhom va tung MSSV phai dat trong dau nhay kep, vi du "07"; '
                f"dang doc duoc {nhom_va_mssv!r}."
            )
        for khoa in ("du_an.nhom", "du_an.cau_hoi"):
            if not str(self[khoa]).strip():
                raise CauHinhError(f"{khoa} khong duoc de trong.")
        if int(self["bieu_do.dpi"]) < 150:
            raise CauHinhError("bieu_do.dpi phai tu 150 tro len.")

    def _kiem_tra_nguon(self) -> None:
        """Kiem tra danh sach nguon: du truong, ten khong trung, loai hop le."""
        cac_muc = self["nguon"]
        if not isinstance(cac_muc, list) or len(cac_muc) < 2:
            raise CauHinhError("Muc `nguon` phai khai bao it nhat hai nguon du lieu.")
        can_co = ("ten", "mo_ta", "loai", "dinh_dang", "vai_tro", "thu_muc", "mau_ten_tep")
        for muc in cac_muc:
            thieu = [khoa for khoa in can_co if khoa not in muc]
            if thieu:
                raise CauHinhError(f"Nguon {muc.get('ten', '?')!r} thieu truong: {thieu}.")
            if muc["loai"] not in self.LOAI_NGUON:
                raise CauHinhError(
                    f"Nguon {muc['ten']!r}: loai {muc['loai']!r} khong thuoc {self.LOAI_NGUON}."
                )
            if muc["vai_tro"] not in self.VAI_TRO:
                raise CauHinhError(
                    f"Nguon {muc['ten']!r}: vai_tro {muc['vai_tro']!r} khong thuoc {self.VAI_TRO}."
                )
        ten = [muc["ten"] for muc in cac_muc]
        if len(set(ten)) != len(ten):
            raise CauHinhError(f"Ten nguon bi trung: {ten}.")

    def _kiem_tra_quy_tac(self) -> None:
        """Kiem tra moi bieu thuc chinh quy trong cau hinh deu bien dich duoc."""
        ten_nguon = {muc["ten"] for muc in self["nguon"]}
        for muc in self["danh_muc"]:
            la = [ten for ten in muc.get("nguon") or ["?"] if ten not in ten_nguon]
            if la:
                raise CauHinhError(f"danh_muc '{muc.get('ma')}': nguon {la} chua khai bao.")
            if muc.get("don_vi") not in self["don_vi"]:
                raise CauHinhError(
                    f"danh_muc '{muc.get('ma')}': don_vi {muc.get('don_vi')!r} chua khai bao."
                )
            for khoa in ("mau", "mau_don_vi"):
                vi_tri = f"danh_muc '{muc.get('ma')}'.{khoa}"
                self._bien_dich(str(muc.get(khoa, "")), vi_tri)
                if re.compile(str(muc[khoa])).groups > 0:
                    raise CauHinhError(f"{vi_tri}: chi duoc dung nhom khong bat (?:...).")
        for ten, mau in self["lam_sach.mau_ngay"].items():
            self._bien_dich(str(mau), f"lam_sach.mau_ngay.{ten}")
        for thu_tu, mau in enumerate(self["lam_sach.mau_thay_doi"]):
            ten = f"lam_sach.mau_thay_doi[{thu_tu}]"
            nhom = self._bien_dich(str(mau), ten).groupindex
            if not {"chieu", "muc"} <= set(nhom):
                raise CauHinhError(f"Muc '{ten}' phai co hai nhom dat ten 'chieu' va 'muc'.")

    @staticmethod
    def _bien_dich(mau: str, vi_tri: str) -> re.Pattern[str]:
        """Bien dich mot bieu thuc chinh quy, bao loi kem vi tri trong cau hinh."""
        try:
            return re.compile(mau)
        except re.error as loi:
            raise CauHinhError(f"Bieu thuc chinh quy o {vi_tri} khong hop le: {loi}") from loi

    def _kiem_tra_khoang_va_su_kien(self) -> None:
        """Kiem tra khoang phan tich va danh sach su kien."""
        try:
            bat_dau = self.ngay_bat_dau
            ket_thuc = self.ngay_ket_thuc
            lich = self.lich_su_kien
        except (ValueError, TypeError, KeyError, ThamSoError) as loi:
            raise CauHinhError(f"Moc thoi gian trong cau hinh khong hop le: {loi}") from loi
        if ket_thuc is not None and ket_thuc <= bat_dau:
            raise CauHinhError("phan_tich.ket_thuc phai sau phan_tich.bat_dau.")
        if len(lich) == 0:
            raise CauHinhError("su_kien.danh_sach phai co it nhat mot su kien.")
