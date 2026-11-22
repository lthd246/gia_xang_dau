"""Lop va ham lam sach: xu ly bon loai khuyet tat roi ghep cac nguon theo khoa.

Bang tho (moi cot la chuoi) di qua mot day chuyen gom cac buoc doc lap, moi buoc la
mot lop con cua BuocLamSach:

    BoGiaTriThieu -> ChuyenKieuNgay -> LocKhoangThoiGian -> ChuanHoaDanhMuc
    -> ChuyenKieuSo -> BoBanGhiTrung -> SuyRaGiaTruoc -> GhepNguon

Khong buoc nao sua bang truyen vao va khong buoc nao ghi tep.
"""

from __future__ import annotations

import logging
import unicodedata
from typing import Any, Iterator

import numpy as np
import pandas as pd

from .cau_hinh import CauHinh
from .lop_co_so import BoNap, BuocLamSach, KetQuaBuoc, LuocDo, ThamSoError

NHAT_KY = logging.getLogger(__name__)

KHOA_THONG_KE = ("gia_tri_thieu", "ban_ghi_trung", "kieu_sai", "danh_muc_chuan_hoa")


class BoGiaTriThieu(BuocLamSach):
    """Loai dong ma o `ngay` hoac o `gia_tri` rong hay chi chua ky hieu thieu."""

    ten = "bo_gia_tri_thieu"
    khoa_thong_ke = "gia_tri_thieu"

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Danh dau o thieu o hai cot `ngay`, `gia_tri` roi loai dong chua chung.

        Tham so:
            df: bang tho, moi cot la chuoi.

        Tra ve:
            Cap (bang da loai dong thieu, so lieu cua buoc); `so_o_xu_ly` la so o thieu.

        Ngoai le:
            Khong co.
        """
        ky_hieu = [str(k).lower() for k in self._cau_hinh["lam_sach.ky_hieu_thieu"]]
        thieu_ngay = self.la_ky_hieu_thieu(df["ngay"], ky_hieu)
        thieu_gia = self.la_ky_hieu_thieu(df["gia_tri"], ky_hieu)
        bi_loai = thieu_ngay | thieu_gia
        bang = df.loc[~bi_loai].copy()
        return bang, self._ket_qua(
            df,
            bang,
            int(thieu_ngay.sum() + thieu_gia.sum()),
            "o ngay/gia_tri rong hoac la ky hieu thieu: loai dong, khong tu dat gia thay the",
            df.loc[bi_loai, "nguon"].value_counts().to_dict(),
        )

    @staticmethod
    def la_ky_hieu_thieu(cot: pd.Series, ky_hieu: list[str]) -> pd.Series:
        """Danh dau o rong hoac o chi chua mot ky hieu thieu (khong phan biet hoa thuong).

        Tham so:
            cot: cot chuoi can xet.
            ky_hieu: cac ky hieu duoc coi la thieu, viet thuong, vi du ["na", "null"].

        Tra ve:
            Cot bool cung chi so, True o nhung o thieu.

        Ngoai le:
            Khong co.
        """
        gon = cot.astype("string").str.strip().str.lower()
        return (LuocDo.la_thieu(cot) | gon.isin(ky_hieu).fillna(False)).astype(bool)


class ChuyenKieuNgay(BuocLamSach):
    """Doi cot `ngay` tu chuoi nhieu dinh dang sang kieu ngay."""

    ten = "chuyen_kieu_ngay"
    khoa_thong_ke = "kieu_sai"

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Thu lan luot cac mau ngay trong cau hinh; dong khong doi duoc thi loai.

        Tham so:
            df: bang co cot `ngay` dang chuoi.

        Tra ve:
            Cap (bang voi `ngay` kieu datetime, so lieu cua buoc); `so_o_xu_ly` la
            so o khong o dang chuan (doi duoc bang quy tac rieng hoac phai loai).

        Ngoai le:
            Khong co.
        """
        ngay, dang = self.doi_ngay(df["ngay"], dict(self._cau_hinh["lam_sach.mau_ngay"]))
        khong_chuan = dang.ne(str(self._cau_hinh["lam_sach.dang_ngay_chuan"]))
        bang = df.assign(ngay=ngay).loc[ngay.notna()].copy()
        so_loai = int(ngay.isna().sum())
        return bang, self._ket_qua(
            df,
            bang,
            int(khong_chuan.sum()),
            "ngay khong o dang chuan: doi theo mau trong cau hinh; "
            f"{so_loai} o khong doi duoc bi loai",
            dang[khong_chuan].replace("", "khong_doi_duoc").value_counts().to_dict(),
        )

    @staticmethod
    def doi_ngay(cot: pd.Series, cac_mau: dict[str, str]) -> tuple[pd.Series, pd.Series]:
        """Doi mot cot chuoi sang ngay bang cach thu tung bieu thuc chinh quy.

        Tham so:
            cot: cot chuoi ngay tho.
            cac_mau: ten dang -> bieu thuc chinh quy co ba nhom dat ten `nam`,
                `thang`, `ngay`. Mau dung truoc duoc uu tien.

        Tra ve:
            Cap (cot ngay kieu datetime, cot ten dang da khop); o khong khop mau
            nao hoac ngay khong ton tai nhan NaT va ten dang rong.

        Ngoai le:
            Khong co.
        """
        van_ban = cot.astype("string").str.strip()
        ket_qua = pd.Series(pd.NaT, index=cot.index, dtype="datetime64[ns]")
        dang = pd.Series("", index=cot.index, dtype=object)
        for ten, mau in cac_mau.items():
            con_lai = ket_qua.isna()
            if not con_lai.any():
                break
            khop = van_ban[con_lai].str.extract(mau).apply(pd.to_numeric, errors="coerce")
            khop = khop.astype(float).dropna()
            if khop.empty:
                continue
            phan = khop.rename(columns={"nam": "year", "thang": "month", "ngay": "day"})
            gia_tri = pd.to_datetime(phan[["year", "month", "day"]].astype(int), errors="coerce")
            gia_tri = gia_tri.dropna()
            ket_qua.loc[gia_tri.index] = gia_tri.astype("datetime64[ns]")
            dang.loc[gia_tri.index] = ten
        return ket_qua, dang


class LocKhoangThoiGian(BuocLamSach):
    """Chi giu quan sat gia nam trong khoang phan tich khai bao o cau hinh."""

    ten = "loc_khoang_thoi_gian"

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Loai dong cua nguon gia nam ngoai khoang [bat_dau, ket_thuc].

        Nguon tra cuu (ty gia, chi so) duoc giu nguyen de con moc truoc va sau khoang.

        Tham so:
            df: bang co cot `ngay` kieu datetime va cot `nguon`.

        Tra ve:
            Cap (bang da loc, so lieu cua buoc).

        Ngoai le:
            Khong co.
        """
        nguon_gia = [n.ten for n in self._cau_hinh.cac_nguon if n.vai_tro == "gia"]
        ngoai = df["ngay"].lt(self._cau_hinh.ngay_bat_dau)
        if self._cau_hinh.ngay_ket_thuc is not None:
            ngoai |= df["ngay"].gt(self._cau_hinh.ngay_ket_thuc)
        bi_loai = ngoai & df["nguon"].isin(nguon_gia)
        bang = df.loc[~bi_loai].copy()
        return bang, self._ket_qua(
            df,
            bang,
            0,
            "quan sat gia nam ngoai khoang phan tich khai bao trong cau hinh",
            df.loc[bi_loai, "nguon"].value_counts().to_dict(),
        )


class ChuanHoaDanhMuc(BuocLamSach):
    """Dua nhan chuoi viet nhieu kieu ve mot ma chuoi chuan theo quy tac trong cau hinh."""

    ten = "chuan_hoa_danh_muc"
    khoa_thong_ke = "danh_muc_chuan_hoa"
    COT_THEM = ("ma_chuoi", "ten_chuoi", "thi_truong", "nhom_hang", "don_vi_chuan")

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Gan ma chuoi chuan; dong cua nguon co quy tac ma khong khop thi loai.

        Nguon khong co quy tac nao (bang tra cuu) giu nguyen nhan lam ma chuoi.

        Tham so:
            df: bang co cac cot `nguon`, `chuoi`, `don_vi`.

        Tra ve:
            Cap (bang them cac cot ma_chuoi, ten_chuoi, thi_truong, nhom_hang,
            don_vi_chuan; so lieu cua buoc); `so_o_xu_ly` la so o nhan khac nhan chuan.

        Ngoai le:
            Khong co.
        """
        quy_tac = self._cau_hinh.quy_tac_danh_muc
        nhan = self.gon_nhan(df["chuoi"])
        don_vi = self.gon_nhan(df["don_vi"])
        bang = df.copy()
        for cot in self.COT_THEM:
            bang[cot] = pd.Series(pd.NA, index=bang.index, dtype=object)
        da_chuan = pd.Series(False, index=bang.index)
        for muc in quy_tac:
            khop = (
                bang["ma_chuoi"].isna()
                & bang["nguon"].isin(muc.nguon)
                & nhan.str.contains(muc.mau, regex=True)
                & don_vi.str.contains(muc.mau_don_vi, regex=True)
            )
            gia_tri = (muc.ma, muc.ten, muc.thi_truong, muc.nhom_hang, muc.don_vi)
            bang.loc[khop, list(self.COT_THEM)] = gia_tri
            da_chuan |= khop & bang["chuoi"].ne(muc.nhan_chuan)
        co_quy_tac = bang["nguon"].isin({ten for muc in quy_tac for ten in muc.nguon})
        bang.loc[~co_quy_tac, "ma_chuoi"] = bang.loc[~co_quy_tac, "chuoi"]
        ngoai_danh_muc = co_quy_tac & bang["ma_chuoi"].isna()
        ket_qua = bang.loc[~ngoai_danh_muc].copy()
        return ket_qua, self._ket_qua(
            df,
            ket_qua,
            int(da_chuan.sum()),
            "nhan viet khac nhan chuan duoc quy ve ma chuan; nhan ngoai danh muc phan tich bi loai",
            df.loc[ngoai_danh_muc, "chuoi"].value_counts().head(8).to_dict(),
        )

    @staticmethod
    def gon_nhan(cot: pd.Series) -> pd.Series:
        """Dua nhan ve dang de so khop: Unicode NFC, chu thuong, gop khoang trang.

        Tham so:
            cot: cot nhan tho.

        Tra ve:
            Cot chuoi da gon, cung chi so.

        Ngoai le:
            Khong co.
        """
        chuan = cot.astype(str).map(lambda nhan: unicodedata.normalize("NFC", nhan))
        return chuan.str.lower().str.replace(r"\s+", " ", regex=True).str.strip()


class ChuyenKieuSo(BuocLamSach):
    """Doi cot `gia_tri` tu chuoi (kieu viet so cua tung nguon) sang so thuc."""

    ten = "chuyen_kieu_so"
    khoa_thong_ke = "kieu_sai"

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Doi so theo kieu viet cua tung nguon, kiem tra khoang hop ly theo don vi.

        So viet kieu Viet Nam (cham ngan nghin, phay thap phan) duoc doi theo kieu
        do; neu ket qua nam ngoai khoang hop ly cua don vi thi thu doc lai theo
        kieu chuan. Dong khong doi duoc hoac van ngoai khoang thi loai.

        Tham so:
            df: bang co cac cot `nguon`, `gia_tri`, `don_vi_chuan`.

        Tra ve:
            Cap (bang them cot `gia_goc` kieu so thuc, so lieu cua buoc);
            `so_o_xu_ly` la so o ma doc thang bang pd.to_numeric khong ra dung gia
            tri (so viet kieu Viet Nam, hoac khong doc duoc).

        Ngoai le:
            Khong co.
        """
        kieu_so = {str(k): str(v) for k, v in self._cau_hinh["lam_sach.kieu_so"].items()}
        kieu = df["nguon"].map(kieu_so).fillna("chuan")
        gia = pd.Series(np.nan, index=df.index, dtype=float)
        for ten_kieu in kieu.unique():
            chon = kieu.eq(ten_kieu)
            gia.loc[chon] = self.doi_so(df.loc[chon, "gia_tri"], ten_kieu)
        thap, cao = self._khoang_hop_ly(df["don_vi_chuan"])
        ngoai_khoang = gia.lt(thap) | gia.gt(cao)
        doc_lai = self.doi_so(df.loc[ngoai_khoang, "gia_tri"], "chuan")
        hop_ly = doc_lai.ge(thap[ngoai_khoang]) & doc_lai.le(cao[ngoai_khoang])
        gia.loc[ngoai_khoang] = doc_lai.where(hop_ly)
        doc_thang = pd.to_numeric(df["gia_tri"], errors="coerce")
        khong_chuan = ~doc_thang.eq(gia)
        bang = df.assign(gia_goc=gia).loc[gia.notna()].copy()
        return bang, self._ket_qua(
            df,
            bang,
            int(khong_chuan.sum()),
            f"so viet kieu Viet Nam (doc thang se sai): doi theo kieu viet cua nguon; "
            f"{int(hop_ly.sum())} o doc lai theo kieu chuan vi ngoai khoang hop ly; "
            f"{int(gia.isna().sum())} o khong doi duoc bi loai",
            df.loc[khong_chuan, "nguon"].value_counts().to_dict(),
        )

    @staticmethod
    def doi_so(cot: pd.Series, kieu: str) -> pd.Series:
        """Doi mot cot chuoi so sang so thuc theo kieu viet so.

        Tham so:
            cot: cot chuoi so tho.
            kieu: "viet" (cham ngan nghin, phay thap phan) hoac "chuan" (phay
                ngan nghin, cham thap phan).

        Tra ve:
            Cot so thuc cung chi so; o khong doi duoc nhan NaN.

        Ngoai le:
            ThamSoError: khi `kieu` khong thuoc hai gia tri tren.
        """
        van_ban = cot.astype("string").str.replace(r"\s", "", regex=True)
        if kieu == "viet":
            van_ban = van_ban.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        elif kieu == "chuan":
            van_ban = van_ban.str.replace(",", "", regex=False)
        else:
            raise ThamSoError(f"Kieu viet so {kieu!r} phai la 'viet' hoac 'chuan'.")
        return pd.to_numeric(van_ban, errors="coerce").astype(float)

    def _khoang_hop_ly(self, don_vi: pd.Series) -> tuple[pd.Series, pd.Series]:
        """Tra ve can duoi va can tren hop ly cua tung dong theo don vi chuan."""
        khoang = {
            str(ma): (float(muc["khoang_hop_ly"][0]), float(muc["khoang_hop_ly"][1]))
            for ma, muc in self._cau_hinh["don_vi"].items()
        }
        thap = don_vi.map(lambda ma: khoang.get(ma, (-np.inf, np.inf))[0]).astype(float)
        cao = don_vi.map(lambda ma: khoang.get(ma, (-np.inf, np.inf))[1]).astype(float)
        return thap, cao


class BoBanGhiTrung(BuocLamSach):
    """Loai ban ghi trung khoa (ngay, ma chuoi), giu ban cua nguon duoc uu tien."""

    ten = "bo_ban_ghi_trung"
    khoa_thong_ke = "ban_ghi_trung"

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Giu mot dong cho moi khoa; quan sat gia trung nhau giua cac nguon duoc gop.

        Voi nguon gia, khoa la (ngay, ma_chuoi) bat ke nguon nao; voi nguon tra cuu,
        khoa gom ca ten nguon. Dong duoc giu la dong cua nguon dung truoc trong
        `lam_sach.uu_tien_nguon`; cung nguon thi giu dong xuat hien truoc (trong mot
        bai bao, cau dau tien la gia ky nay, cac cau sau thuong nhac lai ky truoc).

        Tham so:
            df: bang co cac cot `nguon`, `ngay`, `ma_chuoi`, `gia_goc`.

        Tra ve:
            Cap (bang khong con khoa trung, so lieu cua buoc); `so_o_xu_ly` la so
            dong trung bi loai.

        Ngoai le:
            Khong co.
        """
        nguon_gia = [n.ten for n in self._cau_hinh.cac_nguon if n.vai_tro == "gia"]
        uu_tien = {
            ten: thu_tu for thu_tu, ten in enumerate(self._cau_hinh["lam_sach.uu_tien_nguon"])
        }
        sai_so = float(self._cau_hinh["lam_sach.sai_so_lam_tron"])
        bang = df.assign(
            _nhom=df["nguon"].where(~df["nguon"].isin(nguon_gia), "gia"),
            _uu_tien=df["nguon"].map(uu_tien).fillna(len(uu_tien)),
        )
        khoa = ["_nhom", "ngay", "ma_chuoi"]
        bang = bang.sort_values("_uu_tien", kind="stable")
        trung = bang.duplicated(khoa, keep="first")
        lech = (bang["gia_goc"] - bang.groupby(khoa)["gia_goc"].transform("first")).abs()
        so_lech = int((trung & lech.gt(0)).sum())
        so_lech_lon = int((trung & lech.gt(sai_so)).sum())
        ket_qua = bang.loc[~trung].sort_index().drop(columns=["_nhom", "_uu_tien"])
        return ket_qua, self._ket_qua(
            df,
            ket_qua,
            int(trung.sum()),
            f"trung khoa (ngay, ma_chuoi): giu dong cua nguon uu tien; {so_lech} dong trung co gia "
            f"tri lech voi dong duoc giu, trong do {so_lech_lon} dong lech qua {sai_so:g} don vi",
            bang.loc[trung, "nguon"].value_counts().to_dict(),
        )


class SuyRaGiaTruoc(BuocLamSach):
    """Bo sung quan sat "gia ngay truoc ky dieu chinh" suy tu muc tang giam neu trong cau."""

    ten = "suy_ra_gia_truoc"

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Them dong (ngay - 1, gia - muc thay doi) cho cau co neu muc tang giam.

        Cau "không cao hơn 20.512 đồng/lít (giảm 778 đồng/lít so với giá bán lẻ hiện hành)"
        cho biet ngay truoc do gia la 21.290. Dong suy ra giup chuoi gia dung muc
        ngay ca khi thong bao cua ky lien truoc khong thu thap duoc. Khong suy ra
        khi (a) gia trong cau bang gia quan sat lien truoc cua chinh chuoi do, vi
        cau chi nhac lai mot ky da qua, hoac (b) ngay lien truoc da co quan sat.

        Tham so:
            df: bang da bo ban ghi trung, co cac cot `ngay`, `ma_chuoi`, `gia_goc`,
                `van_ban`.

        Tra ve:
            Cap (bang them cot bool `suy_ra` va cac dong suy ra, so lieu cua buoc);
            `so_o_xu_ly` la so dong duoc them.

        Ngoai le:
            Khong co.
        """
        van_ban = df["van_ban"].astype("string")
        khop = pd.DataFrame({"chieu": pd.NA, "muc": pd.NA}, index=df.index, dtype="string")
        for mau in self._cau_hinh["lam_sach.mau_thay_doi"]:
            chua_khop = khop["chieu"].isna()
            thu = van_ban.loc[chua_khop].str.extract(str(mau))
            khop.loc[chua_khop, ["chieu", "muc"]] = thu[["chieu", "muc"]]
        muc = ChuyenKieuSo.doi_so(khop["muc"], "viet")
        la_tang = khop["chieu"].eq(str(self._cau_hinh["lam_sach.nhan_tang"])).fillna(False)
        la_giam = khop["chieu"].eq(str(self._cau_hinh["lam_sach.nhan_giam"])).fillna(False)
        thay_doi = pd.Series(np.where(la_tang, muc, np.where(la_giam, -muc, 0.0)), index=df.index)
        co_muc = khop["chieu"].notna() & ~((la_tang | la_giam) & muc.isna())
        theo_thoi_gian = df.sort_values(["ma_chuoi", "ngay"], kind="stable")
        gia_ky_truoc = theo_thoi_gian.groupby("ma_chuoi")["gia_goc"].shift(1).reindex(df.index)
        sai_so = float(self._cau_hinh["lam_sach.sai_so_lam_tron"])
        nhac_lai = co_muc & (df["gia_goc"] - gia_ky_truoc).abs().le(sai_so)
        chon = co_muc & ~nhac_lai
        them = df.loc[chon].assign(
            ngay=df.loc[chon, "ngay"] - pd.Timedelta(days=1),
            gia_goc=df.loc[chon, "gia_goc"] - thay_doi.loc[chon],
            suy_ra=True,
        )
        them = them.loc[them["ngay"].ge(self._cau_hinh.ngay_bat_dau) & them["gia_goc"].gt(0)]
        da_co = pd.MultiIndex.from_frame(df[["ma_chuoi", "ngay"]])
        da_co_quan_sat = pd.MultiIndex.from_frame(them[["ma_chuoi", "ngay"]]).isin(da_co)
        them = them.loc[~da_co_quan_sat]
        bang = pd.concat([df.assign(suy_ra=False), them], ignore_index=True)
        return bang, self._ket_qua(
            df,
            bang,
            len(them),
            f"{int(co_muc.sum())} cau co neu muc tang/giam: them quan sat gia cua ngay lien truoc "
            f"ky dieu chinh; bo {int(nhac_lai.sum())} cau chi nhac lai ky truoc va "
            f"{int(da_co_quan_sat.sum())} cau ma ngay lien truoc da co quan sat",
            them["nguon"].value_counts().to_dict(),
        )


class GhepNguon(BuocLamSach):
    """Ghep bang quan sat gia voi cac bang tra cuu theo khoa `ngay` va tinh cot quy doi."""

    ten = "ghep_nguon"
    khoa_thong_ke = "gia_tri_thieu"

    def ap_dung(self, df: pd.DataFrame) -> tuple[pd.DataFrame, KetQuaBuoc]:
        """Tach quan sat gia va bang tra cuu, ghep trai theo `ngay`, them cot quy doi.

        Moi bang tra cuu duoc dua ve dung mot dong cho moi ngay truoc khi ghep,
        nen so dong sau khi ghep bang so dong quan sat gia (kiem bang
        `validate="many_to_one"`).

        Tham so:
            df: bang dai da doi kieu, chuan hoa danh muc va bo trung.

        Tra ve:
            Cap (bang sach theo luoc do `luoc_do.bang_sach`, so lieu cua buoc);
            `so_o_xu_ly` la so o tra cuu ma nguon khong co gia tri dung ngay do va
            da duoc dien theo quy tac (noi suy, giu gia tri cuoi, gan truoc moc dau).

        Ngoai le:
            Khong co.
        """
        nguon_gia = [n.ten for n in self._cau_hinh.cac_nguon if n.vai_tro == "gia"]
        la_gia = df["nguon"].isin(nguon_gia)
        gia = df.loc[la_gia].copy()
        tra_cuu = df.loc[~la_gia]
        so_o_dien = con_thieu = 0
        chi_tiet: dict[str, int] = {}
        for muc in self._cau_hinh["tra_cuu"]:
            bang_tra = self.bang_tra_cuu(tra_cuu, muc, gia["ngay"])
            cot, cot_dien = str(muc["cot"]), f"_{muc['cot']}_dien"
            truoc = len(gia)
            gia = gia.merge(bang_tra, on="ngay", how="left", validate="many_to_one")
            da_dien = int(gia[cot_dien].sum())
            NHAT_KY.info(
                "Ghep cot %s: trai %d dong, phai %d dong, ket qua %d dong; "
                "%d o duoc dien theo quy tac, %d o con thieu",
                cot,
                truoc,
                len(bang_tra),
                len(gia),
                da_dien,
                int(gia[cot].isna().sum()),
            )
            so_o_dien += da_dien
            con_thieu += int(gia[cot].isna().sum())
            chi_tiet[cot] = da_dien
            gia = gia.drop(columns=cot_dien)
        lich = self._cau_hinh.lich_su_kien.bang_theo_ngay(gia["ngay"])
        gia = gia.merge(lich, on="ngay", how="left", validate="many_to_one")
        bang = self._them_cot_quy_doi(gia)
        bang = bang.sort_values(["ngay", "ma_chuoi"], kind="stable").reset_index(drop=True)
        bang = bang.loc[:, list(self._cau_hinh["luoc_do.bang_sach"])]
        return bang, self._ket_qua(
            df,
            bang,
            so_o_dien,
            "o tra cuu khong co gia tri dung ngay quan sat: dien theo quy tac cua tung cot trong "
            f"cau hinh; {con_thieu} o ngoai pham vi quy tac de nguyen la thieu; dong cua bang tra "
            "cuu tro thanh cot nen khong con la dong rieng",
            chi_tiet,
        )

    @staticmethod
    def bang_tra_cuu(
        tra_cuu: pd.DataFrame, muc: dict[str, Any], ngay_can: pd.Series
    ) -> pd.DataFrame:
        """Lap bang tra cuu mot cot, dung mot dong cho moi ngay can tra.

        Tham so:
            tra_cuu: cac dong da lam sach cua nguon tra cuu (cot nguon, ngay,
                ma_chuoi, gia_goc).
            muc: khai bao trong `tra_cuu` cua cau hinh: cot, nguon, va tuy chon
                chuoi (chi lay mot ma chuoi), noi_suy (noi suy tuyen tinh theo thoi
                gian giua hai moc), giu_cuoi_toi_da_ngay (sau moc cuoi thi giu gia
                tri cuoi toi da bay nhieu ngay), truoc_ngay_dau (gia tri gan cho
                ngay truoc moc dau).
            ngay_can: cot ngay cua bang quan sat gia.

        Tra ve:
            Bang ba cot: `ngay`, cot tra cuu, va cot bool `_<cot>_dien` cho biet
            gia tri cua ngay do la gia tri dien theo quy tac (True: noi suy, giu
            gia tri cuoi, gan gia tri truoc moc dau) hay nguon co san (False).

        Ngoai le:
            Khong co.
        """
        cot = str(muc["cot"])
        chon = tra_cuu.loc[tra_cuu["nguon"].eq(str(muc["nguon"]))]
        if muc.get("chuoi") is not None:
            chon = chon.loc[chon["ma_chuoi"].eq(str(muc["chuoi"]))]
        goc = chon.groupby("ngay")["gia_goc"].mean().sort_index()
        can = pd.DatetimeIndex(sorted(ngay_can.dropna().unique()))
        day_du = goc.reindex(goc.index.union(can))
        co_san = day_du.notna()
        if muc.get("noi_suy"):
            day_du = day_du.interpolate(method="time", limit_area="inside")
        if len(goc) > 0 and muc.get("giu_cuoi_toi_da_ngay") is not None:
            han_giu = goc.index.max() + pd.Timedelta(days=int(muc["giu_cuoi_toi_da_ngay"]))
            sau_cuoi = (day_du.index > goc.index.max()) & (day_du.index <= han_giu)
            day_du.loc[sau_cuoi] = goc.iloc[-1]
        if len(goc) > 0 and muc.get("truoc_ngay_dau") is not None:
            day_du.loc[day_du.index < goc.index.min()] = float(muc["truoc_ngay_dau"])
        dien = day_du.notna() & ~co_san
        bang = pd.DataFrame(
            {"ngay": day_du.index, cot: day_du.to_numpy(), f"_{cot}_dien": dien.to_numpy()}
        )
        return bang.loc[bang["ngay"].isin(can)].reset_index(drop=True)

    def _them_cot_quy_doi(self, gia: pd.DataFrame) -> pd.DataFrame:
        """Quy moi gia ve USD/thung va dong/lit bang NumPy, them cot thoi gian va bien dong."""
        don_vi = self._cau_hinh["don_vi"]
        lit_moi_thung = float(self._cau_hinh["lam_sach.lit_moi_thung"])
        he_so = gia["don_vi_chuan"].map(lambda ma: float(don_vi[ma]["he_so_thung"])).to_numpy()
        la_vnd = gia["don_vi_chuan"].map(lambda ma: don_vi[ma]["tien"] == "vnd").to_numpy()
        gia_thung = gia["gia_goc"].to_numpy(dtype=float) * he_so
        ty_gia = gia["ty_gia"].to_numpy(dtype=float)
        usd_thung = np.where(la_vnd, gia_thung / ty_gia, gia_thung)
        bang = gia.assign(
            don_vi=gia["don_vi_chuan"],
            gia_usd_thung=usd_thung,
            gia_vnd_lit=usd_thung * ty_gia / lit_moi_thung,
            nam=gia["ngay"].dt.year,
            thang=gia["ngay"].dt.month,
        ).sort_values(["ma_chuoi", "ngay"], kind="stable")
        gia_truoc = bang.groupby("ma_chuoi")["gia_goc"].shift(1)
        bang["thay_doi_pct"] = np.where(
            gia_truoc.gt(0) & bang["gia_goc"].gt(0),
            (bang["gia_goc"] / gia_truoc - 1.0) * 100.0,
            np.nan,
        )
        return bang


class BoLamSach:
    """Day chuyen lam sach: chay lan luot cac buoc va gom so lieu cua tung buoc."""

    def __init__(self, cau_hinh: CauHinh, cac_buoc: list[BuocLamSach] | None = None) -> None:
        """Tao day chuyen lam sach.

        Tham so:
            cau_hinh: cau hinh cua du an.
            cac_buoc: danh sach buoc theo thu tu chay; bo trong thi dung day
                chuyen mac dinh gom tam buoc.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._cau_hinh = cau_hinh
        self._cac_buoc = cac_buoc if cac_buoc is not None else self.buoc_mac_dinh(cau_hinh)
        self._bao_cao: list[KetQuaBuoc] = []

    def __len__(self) -> int:
        """So buoc cua day chuyen lam sach.

        Tham so:
            Khong co.

        Tra ve:
            So nguyen.

        Ngoai le:
            Khong co.
        """
        return len(self._cac_buoc)

    def __iter__(self) -> Iterator[BuocLamSach]:
        """Duyet tung buoc lam sach theo thu tu chay.

        Tham so:
            Khong co.

        Tra ve:
            Bo lap qua cac doi tuong BuocLamSach.

        Ngoai le:
            Khong co.
        """
        return iter(self._cac_buoc)

    @classmethod
    def buoc_mac_dinh(cls, cau_hinh: CauHinh) -> list[BuocLamSach]:
        """Day chuyen mac dinh, theo dung thu tu phai chay.

        Tham so:
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Danh sach tam buoc lam sach.

        Ngoai le:
            Khong co.
        """
        return [
            BoGiaTriThieu(cau_hinh),
            ChuyenKieuNgay(cau_hinh),
            LocKhoangThoiGian(cau_hinh),
            ChuanHoaDanhMuc(cau_hinh),
            ChuyenKieuSo(cau_hinh),
            BoBanGhiTrung(cau_hinh),
            SuyRaGiaTruoc(cau_hinh),
            GhepNguon(cau_hinh),
        ]

    def chay(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chay ca day chuyen tren bang tho.

        Tham so:
            df: bang tho theo luoc do chung cua khau nap.

        Tra ve:
            Bang sach; bang truyen vao khong bi sua.

        Ngoai le:
            BangRongError: khi bang tho khong co dong nao.
            ThieuCotError: khi bang tho thieu cot bat buoc.
            CotToanThieuError: khi cot `ngay` hoac `gia_tri` chi chua gia tri thieu.
        """
        LuocDo("bang tho", BoNap.COT_THO, ("ngay", "gia_tri")).kiem_tra(df)
        bang = df.loc[:, list(BoNap.COT_THO)]
        self._bao_cao = []
        NHAT_KY.info("Lam sach: %d buoc, %d dong vao", len(self), len(bang))
        for buoc in self:
            bang, ket_qua = buoc.ap_dung(bang)
            self._bao_cao.append(ket_qua)
            NHAT_KY.info(
                "%r: vao %d dong, ra %d dong, loai %d dong, them %d dong, xu ly %d o "
                "| ly do: %s | %s",
                buoc,
                ket_qua.so_dong_vao,
                ket_qua.so_dong_ra,
                ket_qua.so_dong_loai,
                ket_qua.so_dong_them,
                ket_qua.so_o_xu_ly,
                ket_qua.ly_do,
                ket_qua.theo_nguon,
            )
        return bang

    def bang_bao_cao(self) -> pd.DataFrame:
        """So lieu tung buoc cua lan chay gan nhat, o dang bang de ghi ra tep.

        Tham so:
            Khong co.

        Tra ve:
            Bang moi dong la mot buoc: so dong vao, ra, loai, them, so o xu ly,
            khoa thong ke ma buoc dong gop, ly do va chi tiet theo nguon.

        Ngoai le:
            ThamSoError: khi day chuyen chua duoc chay lan nao.
        """
        if not self._bao_cao:
            raise ThamSoError("Phai goi chay() truoc khi lay bang so lieu tung buoc.")
        cac_dong = []
        for thu_tu, (buoc, ket_qua) in enumerate(zip(self, self._bao_cao), start=1):
            chi_tiet = "; ".join(f"{khoa}: {so}" for khoa, so in ket_qua.theo_nguon.items())
            cac_dong.append(
                {
                    "thu_tu": thu_tu,
                    "buoc": ket_qua.ten,
                    "khoa_thong_ke": buoc.khoa_thong_ke or "",
                    "so_dong_vao": ket_qua.so_dong_vao,
                    "so_dong_ra": ket_qua.so_dong_ra,
                    "so_dong_loai": ket_qua.so_dong_loai,
                    "so_dong_them": ket_qua.so_dong_them,
                    "so_o_xu_ly": ket_qua.so_o_xu_ly,
                    "ly_do": ket_qua.ly_do,
                    "chi_tiet": chi_tiet,
                }
            )
        return pd.DataFrame(cac_dong)

    def mau_doi_chieu(self, sach: pd.DataFrame) -> pd.DataFrame:
        """Rut ngau nhien mot so quan sat gia tach tu bai viet de doi chieu tay voi nguon.

        Mau duoc rut bang seed trong cau hinh nen moi lan chay cho cung mot mau.

        Tham so:
            sach: bang sach do `chay` tra ve.

        Tra ve:
            Bang gom ngay, ma va ten chuoi, gia goc, don vi, nguon cua cac quan sat
            duoc rut, sap theo ngay; so dong lay tu `phan_tich.so_dong_mau_doi_chieu`.

        Ngoai le:
            ThieuCotError: khi bang sach thieu cot can thiet.
            BangRongError: khi bang sach khong co dong nao.
        """
        cot = ("ngay", "ma_chuoi", "ten_chuoi", "gia_goc", "don_vi", "nguon", "suy_ra")
        LuocDo("bang sach", cot).kiem_tra(sach)
        nguon_bai_viet = [n.ten for n in self._cau_hinh.cac_nguon if n.loai == "bai_viet"]
        ung_vien = sach.loc[sach["nguon"].isin(nguon_bai_viet) & ~sach["suy_ra"].astype(bool)]
        so_dong = min(int(self._cau_hinh["phan_tich.so_dong_mau_doi_chieu"]), len(ung_vien))
        mau = ung_vien.sample(n=so_dong, random_state=self._cau_hinh.seed)
        mau = mau.sort_values(["ngay", "ma_chuoi"], kind="stable")
        return mau.loc[:, [ten for ten in cot if ten != "suy_ra"]].reset_index(drop=True)

    def thong_ke(self) -> dict[str, int]:
        """Gom so lieu cua lan chay gan nhat thanh bon con so theo loai khuyet tat.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien co dung bon khoa gia_tri_thieu, ban_ghi_trung, kieu_sai,
            danh_muc_chuan_hoa; moi gia tri la so o (hoac so dong trung) da xu ly.

        Ngoai le:
            ThamSoError: khi day chuyen chua duoc chay lan nao.
        """
        if not self._bao_cao:
            raise ThamSoError("Phai goi chay() truoc khi lay thong ke lam sach.")
        tong = dict.fromkeys(KHOA_THONG_KE, 0)
        for buoc, ket_qua in zip(self, self._bao_cao):
            if buoc.khoa_thong_ke is not None:
                tong[buoc.khoa_thong_ke] += ket_qua.so_o_xu_ly
        return tong


class ThongKeLamSach:
    """Tinh bon con so thong ke lam sach tu bang truoc va bang sau khi lam sach."""

    def __init__(self, truoc: pd.DataFrame, sau: pd.DataFrame, cau_hinh: CauHinh) -> None:
        """Tao bo thong ke.

        Tham so:
            truoc: bang tho truoc khi lam sach.
            sau: bang sach, ket qua lam sach cua `truoc`.
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._truoc = truoc
        self._sau = sau
        self._cau_hinh = cau_hinh

    def tinh(self) -> dict[str, int]:
        """Dem so o da xu ly cho tung loai khuyet tat.

        Day chuyen lam sach duoc chay lai tren `truoc` de dem; `sau` duoc doi
        chieu luoc do va so dong voi ket qua chay lai.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien co dung bon khoa gia_tri_thieu, ban_ghi_trung, kieu_sai,
            danh_muc_chuan_hoa, moi gia tri la mot so nguyen.

        Ngoai le:
            BangRongError: khi `truoc` hoac `sau` khong co dong nao.
            ThieuCotError: khi `truoc` hoac `sau` thieu cot bat buoc.
            ThamSoError: khi `sau` khong co cung so dong voi ket qua lam sach `truoc`.
        """
        cot_sach = tuple(self._cau_hinh["luoc_do.bang_sach"])
        LuocDo("bang sach", cot_sach).kiem_tra(self._sau)
        bo_lam_sach = BoLamSach(self._cau_hinh)
        chay_lai = bo_lam_sach.chay(self._truoc)
        if len(chay_lai) != len(self._sau):
            raise ThamSoError(
                f"Bang `sau` co {len(self._sau)} dong, khac ket qua lam sach bang `truoc` "
                f"({len(chay_lai)} dong)."
            )
        return bo_lam_sach.thong_ke()


def lam_sach(df: pd.DataFrame) -> pd.DataFrame:
    """Lam sach bang tho va ghep cac nguon thanh bang dung cho phan tich.

    Tham so:
        df: bang tho do `nap_du_lieu` tra ve.

    Tra ve:
        Bang sach, moi dong la mot quan sat gia cua mot chuoi trong mot ngay, kem
        ty gia, chi so boi canh va gia da quy doi. Bang `df` khong bi sua.

    Ngoai le:
        BangRongError: khi `df` khong co dong nao.
        ThieuCotError: khi `df` thieu cot bat buoc.
        CotToanThieuError: khi cot `ngay` hoac `gia_tri` chi chua gia tri thieu.
    """
    return BoLamSach(CauHinh.tu_tep()).chay(df)


def thong_ke_lam_sach(truoc: pd.DataFrame, sau: pd.DataFrame) -> dict[str, int]:
    """Dem so o da xu ly cho tung loai khuyet tat khi lam sach.

    Tham so:
        truoc: bang tho truoc khi lam sach.
        sau: bang sach do `lam_sach(truoc)` tra ve.

    Tra ve:
        Tu dien co dung bon khoa "gia_tri_thieu", "ban_ghi_trung", "kieu_sai",
        "danh_muc_chuan_hoa", moi khoa ung voi mot so nguyen.

    Ngoai le:
        BangRongError: khi mot trong hai bang khong co dong nao.
        ThieuCotError: khi mot trong hai bang thieu cot bat buoc.
        ThamSoError: khi `sau` khong phai ket qua lam sach cua `truoc`.
    """
    return ThongKeLamSach(truoc, sau, CauHinh.tu_tep()).tinh()
