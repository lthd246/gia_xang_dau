"""Lop truu tuong, lop dung chung va cac ngoai le rieng cua goi gia_xang_dau.

Mo-dun nay khong nhap mo-dun nao khac trong goi khi chay, nen moi mo-dun con lai
deu co the dung no ma khong so nhap vong.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pandas as pd
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .cau_hinh import CauHinh, CauHinhNguon
    from .nap import KhachHttp
    from .phan_tich import BangGia


class DoAnError(Exception):
    """Goc cua moi ngoai le do chuong trinh chu dong phat ra."""


class CauHinhError(DoAnError):
    """Tep cau hinh thieu khoa hoac co gia tri khong hop le."""


class ThieuTepError(DoAnError):
    """Khong tim thay tep hoac thu muc du lieu can doc."""


class DinhDangError(DoAnError):
    """Noi dung tep khong dung dinh dang mong doi."""


class ThieuCotError(DoAnError):
    """Bang du lieu thieu mot hoac nhieu cot bat buoc."""


class BangRongError(DoAnError):
    """Bang du lieu khong co dong nao."""


class CotToanThieuError(DoAnError):
    """Mot cot bat buoc chi chua gia tri thieu."""


class ThamSoError(DoAnError):
    """Tham so truyen vao ham hoac phuong thuc khong hop le."""


class TaiVeError(DoAnError):
    """Khong tai duoc du lieu tu nguon ben ngoai."""


class LuocDo:
    """Luoc do cot cua mot bang: cot nao bat buoc va cot nao khong duoc toan thieu."""

    def __init__(
        self,
        ten: str,
        cot_bat_buoc: tuple[str, ...],
        cot_can_gia_tri: tuple[str, ...] = (),
    ) -> None:
        """Tao luoc do.

        Tham so:
            ten: ten bang, dung trong thong bao loi.
            cot_bat_buoc: cac cot phai co mat trong bang.
            cot_can_gia_tri: cac cot phai co it nhat mot gia tri khac thieu.

        Tra ve:
            Khong co.

        Ngoai le:
            ThamSoError: khi `cot_can_gia_tri` co cot khong nam trong `cot_bat_buoc`.
        """
        thua = [cot for cot in cot_can_gia_tri if cot not in cot_bat_buoc]
        if thua:
            raise ThamSoError(f"Luoc do '{ten}': cot {thua} khong nam trong cot bat buoc.")
        self._ten = ten
        self._cot_bat_buoc = tuple(cot_bat_buoc)
        self._cot_can_gia_tri = tuple(cot_can_gia_tri)

    def __iter__(self) -> Iterator[str]:
        """Duyet ten cac cot bat buoc theo thu tu khai bao.

        Tham so:
            Khong co.

        Tra ve:
            Bo lap qua ten cot.

        Ngoai le:
            Khong co.
        """
        return iter(self._cot_bat_buoc)

    def cot_thieu(self, df: pd.DataFrame) -> list[str]:
        """Liet ke cac cot bat buoc khong co trong bang.

        Tham so:
            df: bang can kiem tra.

        Tra ve:
            Danh sach ten cot bi thieu, theo thu tu khai bao trong luoc do.

        Ngoai le:
            Khong co.
        """
        return [cot for cot in self if cot not in df.columns]

    def kiem_tra(self, df: pd.DataFrame) -> None:
        """Kiem tra bang co dung luoc do hay khong.

        Tham so:
            df: bang can kiem tra.

        Tra ve:
            Khong co.

        Ngoai le:
            BangRongError: khi bang khong co dong nao.
            ThieuCotError: khi bang thieu cot bat buoc.
            CotToanThieuError: khi mot cot can gia tri chi chua gia tri thieu.
        """
        if len(df) == 0:
            raise BangRongError(f"Bang '{self._ten}' khong co dong nao.")
        thieu = self.cot_thieu(df)
        if thieu:
            raise ThieuCotError(f"Bang '{self._ten}' thieu cot bat buoc: {thieu}.")
        for cot in self._cot_can_gia_tri:
            if self.la_thieu(df[cot]).all():
                raise CotToanThieuError(
                    f"Cot '{cot}' cua bang '{self._ten}' chi chua gia tri thieu."
                )

    @staticmethod
    def la_thieu(cot: pd.Series) -> pd.Series:
        """Danh dau o thieu: NaN, None hoac chuoi chi gom khoang trang.

        Tham so:
            cot: mot cot du lieu bat ky.

        Tra ve:
            Cot bool cung chi so, True o nhung o bi thieu.

        Ngoai le:
            Khong co.
        """
        la_chuoi_rong = cot.astype("string").str.strip().eq("").fillna(False).astype(bool)
        return cot.isna() | la_chuoi_rong


@dataclass(frozen=True)
class SuKien:
    """Mot giai doan su kien (boi canh) tac dong len thi truong xang dau."""

    ma: str
    ten: str
    ten_ngan: str
    loai: str
    bat_dau: pd.Timestamp
    ket_thuc: pd.Timestamp | None
    nguon: str

    def __lt__(self, khac: SuKien) -> bool:
        """So sanh hai su kien theo ngay bat dau, de sap lich su kien theo thoi gian.

        Tham so:
            khac: su kien dem so sanh.

        Tra ve:
            True neu su kien nay bat dau truoc su kien kia.

        Ngoai le:
            Khong co.
        """
        return self.bat_dau < khac.bat_dau

    def ngay_cuoi(self, ngay_cuoi_du_lieu: pd.Timestamp) -> pd.Timestamp:
        """Ngay cuoi thuc te cua su kien khi doi chieu voi du lieu.

        Tham so:
            ngay_cuoi_du_lieu: ngay moi nhat co trong du lieu.

        Tra ve:
            `ket_thuc` neu su kien da khai bao ngay ket thuc, nguoc lai la
            `ngay_cuoi_du_lieu` (su kien con dang dien ra).

        Ngoai le:
            Khong co.
        """
        return ngay_cuoi_du_lieu if self.ket_thuc is None else self.ket_thuc


class LichSuKien:
    """Tap cac su kien khong chong lan nhau, tra duoc boi canh cua tung ngay."""

    def __init__(self, su_kien: list[SuKien], nhan_binh_thuong: str) -> None:
        """Tao lich su kien.

        Tham so:
            su_kien: danh sach su kien doc tu cau hinh.
            nhan_binh_thuong: nhan gan cho nhung ngay khong thuoc su kien nao.

        Tra ve:
            Khong co.

        Ngoai le:
            ThamSoError: khi hai su kien chong lan thoi gian hoac trung ma.
        """
        self._su_kien = sorted(su_kien)
        self._nhan_binh_thuong = nhan_binh_thuong
        ma = [sk.ma for sk in self._su_kien]
        if len(set(ma)) != len(ma):
            raise ThamSoError(f"Ma su kien bi trung: {ma}.")
        for truoc, sau in zip(self._su_kien, self._su_kien[1:]):
            if truoc.ket_thuc is None or sau.bat_dau <= truoc.ket_thuc:
                raise ThamSoError(f"Su kien '{truoc.ma}' va '{sau.ma}' chong lan thoi gian.")

    def __len__(self) -> int:
        """So su kien trong lich.

        Tham so:
            Khong co.

        Tra ve:
            So nguyen.

        Ngoai le:
            Khong co.
        """
        return len(self._su_kien)

    def __iter__(self) -> Iterator[SuKien]:
        """Duyet tung su kien theo thu tu thoi gian.

        Tham so:
            Khong co.

        Tra ve:
            Bo lap qua cac doi tuong SuKien.

        Ngoai le:
            Khong co.
        """
        return iter(self._su_kien)

    @property
    def nhan_binh_thuong(self) -> str:
        """Nhan cua nhung ngay khong thuoc su kien nao.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi nhan, vi du "binh_thuong".

        Ngoai le:
            Khong co.
        """
        return self._nhan_binh_thuong

    def bang_theo_ngay(self, ngay: pd.Series) -> pd.DataFrame:
        """Lap bang tra cuu boi canh cho tung ngay, dung de ghep theo khoa `ngay`.

        Tham so:
            ngay: cot ngay (kieu datetime) can tra cuu, co the lap lai.

        Tra ve:
            Bang ba cot `ngay`, `su_kien`, `loai_boi_canh`; moi ngay dung mot dong.

        Ngoai le:
            Khong co.
        """
        bang = pd.DataFrame({"ngay": pd.Series(ngay.dropna().unique()).sort_values()})
        bang["su_kien"] = self._nhan_binh_thuong
        bang["loai_boi_canh"] = self._nhan_binh_thuong
        for su_kien in self:
            trong_khoang = bang["ngay"].ge(su_kien.bat_dau)
            if su_kien.ket_thuc is not None:
                trong_khoang &= bang["ngay"].le(su_kien.ket_thuc)
            bang.loc[trong_khoang, "su_kien"] = su_kien.ma
            bang.loc[trong_khoang, "loai_boi_canh"] = su_kien.loai
        return bang.reset_index(drop=True)


@dataclass
class KetQuaBuoc:
    """So lieu ghi lai sau khi mot buoc lam sach chay xong."""

    ten: str
    so_dong_vao: int
    so_dong_ra: int
    so_o_xu_ly: int
    ly_do: str
    theo_nguon: dict[str, int] = field(default_factory=dict)

    @property
    def so_dong_loai(self) -> int:
        """So dong bi loai o buoc nay.

        Tham so:
            Khong co.

        Tra ve:
            So dong vao tru so dong ra; bang 0 neu buoc lam tang so dong.

        Ngoai le:
            Khong co.
        """
        return max(self.so_dong_vao - self.so_dong_ra, 0)

    @property
    def so_dong_them(self) -> int:
        """So dong duoc them o buoc nay.

        Tham so:
            Khong co.

        Tra ve:
            So dong ra tru so dong vao; bang 0 neu buoc lam giam so dong.

        Ngoai le:
            Khong co.
        """
        return max(self.so_dong_ra - self.so_dong_vao, 0)


class BoNap(ABC):
    """Nap mot nguon du lieu tho va dua ve luoc do cot chung cua bang tho."""

    COT_THO: tuple[str, ...] = ("nguon", "tep", "ngay", "chuoi", "gia_tri", "don_vi", "van_ban")

    def __init__(self, nguon: CauHinhNguon) -> None:
        """Tao bo nap cho mot nguon.

        Tham so:
            nguon: khai bao nguon doc tu cau_hinh.yaml.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._nguon = nguon

    def __repr__(self) -> str:
        """Mo ta bo nap, dung trong thong bao loi va nhat ky.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi gom ten lop, ten nguon va mau ten tep.

        Ngoai le:
            Khong co.
        """
        return f"{type(self).__name__}(nguon={self._nguon.ten!r}, mau_tep={self._nguon.mau_tep!r})"

    @property
    def nguon(self) -> CauHinhNguon:
        """Khai bao nguon ma bo nap nay phu trach.

        Tham so:
            Khong co.

        Tra ve:
            Doi tuong CauHinhNguon.

        Ngoai le:
            Khong co.
        """
        return self._nguon

    @abstractmethod
    def doc_tep(self, tep: Path) -> pd.DataFrame:
        """Doc mot tep tho thanh bang.

        Tham so:
            tep: duong dan tep can doc.

        Tra ve:
            Bang co cac cot `ngay`, `chuoi`, `gia_tri`, va tuy nguon co them
            `don_vi`, `van_ban`; gia tri giu nguyen nhu trong tep.

        Ngoai le:
            DinhDangError: khi noi dung tep khong doc duoc.
            ThieuCotError: khi tep thieu truong da khai bao trong cau hinh.
        """

    def tim_tep(self, thu_muc: Path) -> list[Path]:
        """Tim cac tep cua nguon nay ben trong mot thu muc.

        Tham so:
            thu_muc: thu muc du lieu (chua `raw/` va `external/`), hoac mot thu
                muc con cua no.

        Tra ve:
            Danh sach tep khop mau, da sap xep theo ten.

        Ngoai le:
            Khong co.
        """
        tim_thay = sorted(thu_muc.glob(self._nguon.mau_tep))
        if not tim_thay:
            mau = Path(self._nguon.mau_tep)
            tim_thay = sorted(
                tep for tep in thu_muc.rglob(mau.name) if tep.parent.name == mau.parent.name
            )
        return tim_thay

    def nap(self, thu_muc: Path) -> pd.DataFrame:
        """Nap toan bo tep cua nguon trong thu muc va noi doc lai.

        Tham so:
            thu_muc: thu muc du lieu can tim tep.

        Tra ve:
            Bang tho theo luoc do `COT_THO`, moi cot la chuoi.

        Ngoai le:
            ThieuTepError: khi khong tim thay tep nao khop mau cua nguon.
        """
        cac_tep = self.tim_tep(thu_muc)
        if not cac_tep:
            raise ThieuTepError(f"Khong tim thay tep nao cho {self!r} trong thu muc '{thu_muc}'.")
        cac_bang = [self.nap_tep(tep) for tep in cac_tep]
        return pd.concat(cac_bang, ignore_index=True)

    def nap_tep(self, tep: Path) -> pd.DataFrame:
        """Nap mot tep va dua ve luoc do cot chung.

        Tham so:
            tep: duong dan tep can nap.

        Tra ve:
            Bang tho theo luoc do `COT_THO`, moi cot la chuoi.

        Ngoai le:
            ThieuTepError: khi tep khong ton tai.
        """
        if not tep.is_file():
            raise ThieuTepError(f"Khong tim thay tep '{tep}'.")
        bang = self.doc_tep(tep)
        for cot, gia_tri in self._nguon.gia_tri_co_dinh.items():
            bang[cot] = gia_tri
        bang["nguon"] = self._nguon.ten
        bang["tep"] = tep.name
        for cot in self.COT_THO:
            if cot not in bang.columns:
                bang[cot] = ""
        bang = bang.loc[:, list(self.COT_THO)].astype(object)
        return bang.where(bang.notna(), "").astype(str).reset_index(drop=True)

    def _chon_cot(self, bang: pd.DataFrame, tep: Path) -> pd.DataFrame:
        """Lay cac cot khai bao trong `doc.cot` va doi sang ten cot chung."""
        anh_xa = {str(goc): str(chung) for chung, goc in self._nguon.doc["cot"].items()}
        if len(bang.columns) == 0:
            return pd.DataFrame(columns=list(anh_xa.values()))
        thieu = [goc for goc in anh_xa if goc not in bang.columns]
        if thieu:
            raise ThieuCotError(f"Tep '{tep.name}' thieu truong: {thieu}.")
        return bang.loc[:, list(anh_xa)].rename(columns=anh_xa)


class BoTai(ABC):
    """Tai du lieu tho cua mot nguon ve thu muc dem khi chua co san."""

    def __init__(self, nguon: CauHinhNguon, khach: KhachHttp) -> None:
        """Tao bo tai cho mot nguon.

        Tham so:
            nguon: khai bao nguon doc tu cau_hinh.yaml; muc `tai_ve` mo ta cach tai.
            khach: khach HTTP dung de gui yeu cau (quan he chua).

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._nguon = nguon
        self._khach = khach

    def __repr__(self) -> str:
        """Mo ta bo tai, dung khi ghi nhat ky.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi gom ten lop va ten nguon.

        Ngoai le:
            Khong co.
        """
        return f"{type(self).__name__}(nguon={self._nguon.ten!r})"

    @abstractmethod
    def tai(self, thu_muc_dich: Path) -> list[Path]:
        """Tai du lieu va ghi thanh tep trong thu muc dich.

        Tham so:
            thu_muc_dich: thu muc se chua cac tep tai ve.

        Tra ve:
            Danh sach tep da ghi.

        Ngoai le:
            TaiVeError: khi khong ket noi duoc hoac may chu tra loi.
        """


class BuocLamSach(ABC):
    """Mot buoc trong day chuyen lam sach: nhan bang, tra bang moi kem so lieu."""

    ten: str = ""
    khoa_thong_ke: str | None = None

    def __init__(self, cau_hinh: CauHinh) -> None:
        """Tao buoc lam sach.

        Tham so:
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._cau_hinh = cau_hinh

    def __repr__(self) -> str:
        """Mo ta buoc lam sach, dung khi ghi nhat ky.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi gom ten lop va ten buoc.

        Ngoai le:
            Khong co.
        """
        return f"{type(self).__name__}(ten={self.ten!r})"

    @abstractmethod
    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Ap dung buoc lam sach len mot bang ma khong sua bang truyen vao.

        Tham so:
            df: bang dau vao cua buoc.

        Tra ve:
            Cap (bang moi, so lieu cua buoc).

        Ngoai le:
            ThieuCotError: khi bang thieu cot ma buoc can.
        """

    def _ket_qua(
        self,
        truoc: pd.DataFrame,
        sau: pd.DataFrame,
        so_o_xu_ly: int,
        ly_do: str,
        theo_nguon: dict[str, int] | None = None,
    ) -> KetQuaBuoc:
        """Dong goi so lieu cua buoc thanh KetQuaBuoc."""
        return KetQuaBuoc(
            ten=self.ten,
            so_dong_vao=len(truoc),
            so_dong_ra=len(sau),
            so_o_xu_ly=int(so_o_xu_ly),
            ly_do=ly_do,
            theo_nguon=dict(theo_nguon or {}),
        )


class PhepPhanTich(ABC):
    """Mot phep phan tich tra loi mot phan cua cau hoi."""

    ten: str = ""
    ten_tep: str = ""

    def __init__(self, bang_gia: BangGia, cau_hinh: CauHinh) -> None:
        """Tao phep phan tich.

        Tham so:
            bang_gia: bang gia da lam sach, dung chung giua cac phep phan tich.
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._bang_gia = bang_gia
        self._cau_hinh = cau_hinh

    @abstractmethod
    def bang(self) -> pd.DataFrame:
        """Ket qua cua phep phan tich o dang bang.

        Tham so:
            Khong co.

        Tra ve:
            Bang ket qua, san sang ghi ra tep csv.

        Ngoai le:
            BangRongError: khi du lieu khong du de tinh.
        """

    @abstractmethod
    def tom_tat(self) -> dict[str, object]:
        """Cac con so chinh rut ra tu phep phan tich.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien ten chi tieu -> con so hoac chuoi.

        Ngoai le:
            BangRongError: khi du lieu khong du de tinh.
        """


class BieuDo(ABC):
    """Mot bieu do phuc vu mot phan cua cau hoi phan tich."""

    ten_tep: str = ""

    def __init__(self, cau_hinh: CauHinh) -> None:
        """Tao bieu do.

        Tham so:
            cau_hinh: cau hinh cua du an (kich thuoc, dpi, mau).

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._cau_hinh = cau_hinh

    def __repr__(self) -> str:
        """Mo ta bieu do, dung khi ghi nhat ky.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi gom ten lop va ten tep hinh.

        Ngoai le:
            Khong co.
        """
        return f"{type(self).__name__}(ten_tep={self.ten_tep!r})"

    def tao_hinh(self) -> tuple[Figure, Axes]:
        """Tao hinh trong co mot he truc, kich thuoc lay tu cau hinh.

        Tham so:
            Khong co.

        Tra ve:
            Cap (hinh, he truc) cua matplotlib.

        Ngoai le:
            CauHinhError: khi cau hinh thieu khoa `bieu_do.kich_thuoc`.
        """
        rong, cao = (float(so) for so in self._cau_hinh["bieu_do.kich_thuoc"])
        hinh = Figure(figsize=(rong, cao), layout="constrained")
        return hinh, hinh.add_subplot()

    def mau(self, ten: str) -> str:
        """Tra ma mau khai bao trong cau hinh.

        Tham so:
            ten: ten mau trong muc `bieu_do.mau`, vi du "xang" hay "xung_dot".

        Tra ve:
            Ma mau dang "#rrggbb".

        Ngoai le:
            CauHinhError: khi cau hinh khong khai bao mau nay.
        """
        return str(self._cau_hinh[f"bieu_do.mau.{ten}"])

    def to_nen_su_kien(self, truc: Axes, tu_ngay: pd.Timestamp, den_ngay: pd.Timestamp) -> None:
        """To nen va ghi ten tung su kien nam trong khoang thoi gian cua truc hoanh.

        Ten ghi tren hinh bo phan nam trong ngoac cua `ten_ngan` vi truc hoanh da co nam.

        Tham so:
            truc: he truc co truc hoanh la ngay.
            tu_ngay: ngay dau cua du lieu tren hinh.
            den_ngay: ngay cuoi cua du lieu tren hinh, dung cho su kien chua ket thuc.

        Tra ve:
            Khong co.

        Ngoai le:
            CauHinhError: khi cau hinh khong khai bao mau cho loai su kien.
        """
        for su_kien in self._cau_hinh.lich_su_kien:
            ket_thuc = su_kien.ngay_cuoi(den_ngay)
            if su_kien.bat_dau > den_ngay or ket_thuc < tu_ngay:
                continue
            mau = self.mau(su_kien.loai)
            ten_khong_nam = su_kien.ten_ngan.split(" (")[0]
            truc.axvspan(su_kien.bat_dau, ket_thuc, color=mau, alpha=0.13, linewidth=0)
            truc.text(
                su_kien.bat_dau,
                0.985,
                f" {ten_khong_nam}",
                rotation=90,
                color=mau,
                fontsize=8,
                va="top",
                ha="left",
                transform=truc.get_xaxis_transform(),
            )

    def mau_chuoi(self, ma_chuoi: str) -> str:
        """Tra ma mau cua mot chuoi gia, giong nhau tren moi bieu do.

        Tham so:
            ma_chuoi: ma chuoi chuan, vi du "vn_diesel".

        Tra ve:
            Mau rieng cua chuoi neu muc `bieu_do.mau_chuoi` co khai bao, neu khong
            thi mau cua nhom hang ma chuoi thuoc ve.

        Ngoai le:
            CauHinhError: khi muc `danh_muc` cua cau hinh khong khai bao chuoi nay.
        """
        mau_rieng = self._cau_hinh["bieu_do.mau_chuoi"]
        if ma_chuoi in mau_rieng:
            return str(mau_rieng[ma_chuoi])
        return self.mau(self._cau_hinh.quy_tac_theo_ma(ma_chuoi).nhom_hang)

    def ve_cot_ghep(
        self, truc: Axes, bang: pd.DataFrame, ten_cot: list[str], ten_nhom: list[str]
    ) -> None:
        """Ve bieu do cot ghep: moi dong cua bang la mot nhom, moi cot la mot day cot.

        Tham so:
            truc: he truc de ve.
            bang: bang so; dong la nhom tren truc hoanh, ten cot la ma chuoi cua
                tung day so lieu (dung de chon mau).
            ten_cot: ten hien thi cua tung day (ghi o chu giai), cung thu tu cot.
            ten_nhom: ten hien thi cua tung nhom (ghi o truc hoanh), cung thu tu dong.

        Tra ve:
            Khong co.

        Ngoai le:
            CauHinhError: khi cau hinh khong khai bao chuoi la ten cot cua bang.
        """
        so_day = bang.shape[1]
        be_rong = 0.82 / so_day
        vi_tri = pd.RangeIndex(len(bang)).to_numpy(dtype=float)
        for thu_tu in range(so_day):
            gia_tri = bang.iloc[:, thu_tu].to_numpy(dtype=float)
            cac_cot = truc.bar(
                vi_tri + (thu_tu - (so_day - 1) / 2) * be_rong,
                gia_tri,
                be_rong,
                color=self.mau_chuoi(str(bang.columns[thu_tu])),
                label=ten_cot[thu_tu],
            )
            nhan = ["" if pd.isna(so) else self.dinh_dang_so(so) for so in gia_tri]
            truc.bar_label(cac_cot, labels=nhan, fontsize=7, padding=2)
        truc.set_xticks(vi_tri, ten_nhom)
        truc.margins(y=0.12)
        truc.grid(axis="y", alpha=0.3)
        truc.legend(fontsize=8, frameon=False)

    @staticmethod
    def dinh_dang_so(gia_tri: float, vi_tri: int | None = None) -> str:
        """Viet mot so theo kieu Viet Nam: dau cham ngan cach hang nghin, khong phan le.

        Tham so:
            gia_tri: so can viet.
            vi_tri: vi tri vach chia tren truc; matplotlib truyen vao, khong dung den.

        Tra ve:
            Chuoi so, vi du 25000 -> "25.000".

        Ngoai le:
            Khong co.
        """
        return f"{gia_tri:,.0f}".replace(",", ".")

    @abstractmethod
    def ve(self) -> Figure:
        """Dung hinh.

        Tham so:
            Khong co.

        Tra ve:
            Doi tuong Figure cua matplotlib, chua luu ra tep.

        Ngoai le:
            BangRongError: khi du lieu khong du de ve.
        """

    def luu(self, thu_muc: Path) -> Path:
        """Ve va luu bieu do thanh tep png.

        Tham so:
            thu_muc: thu muc chua tep hinh.

        Tra ve:
            Duong dan tep png da ghi.

        Ngoai le:
            BangRongError: khi du lieu khong du de ve.
        """
        thu_muc.mkdir(parents=True, exist_ok=True)
        duong_dan = thu_muc / self.ten_tep
        hinh = self.ve()
        hinh.savefig(duong_dan, dpi=self._cau_hinh.dpi, facecolor="white")
        return duong_dan
