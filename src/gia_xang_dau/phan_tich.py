"""Lop va ham tong hop, phan tich va tra loi cau hoi.

BangGia boc bang sach va cung cap cac goc nhin dung chung (chuoi theo ngay, chuoi buoc
cua gia ban le, loi suat). Moi phep phan tich la mot lop con cua PhepPhanTich, nhan mot
BangGia va tra ve mot bang ket qua cung cac con so tom tat. BoTraLoi gop cac phep phan
tich thanh cau tra loi cho cau hoi cua de tai.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from .cau_hinh import CauHinh
from .lop_co_so import (
    BangRongError,
    LuocDo,
    PhepPhanTich,
    SuKien,
    ThamSoError,
    ThieuCotError,
)

NHAT_KY = logging.getLogger(__name__)


class BangGia:
    """Bang gia da lam sach, kem cac goc nhin dung chung cho moi phep phan tich."""

    def __init__(self, df: pd.DataFrame, cau_hinh: CauHinh) -> None:
        """Kiem tra luoc do va sap xep bang gia.

        Tham so:
            df: bang sach do khau lam sach tra ve.
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Khong co.

        Ngoai le:
            BangRongError: khi bang khong co dong nao.
            ThieuCotError: khi bang thieu cot cua luoc do bang sach.
            CotToanThieuError: khi cot gia chi chua gia tri thieu.
        """
        cot = tuple(cau_hinh["luoc_do.bang_sach"])
        LuocDo("bang sach", cot, ("gia_vnd_lit", "gia_usd_thung")).kiem_tra(df)
        bang = df.loc[:, list(cot)].copy()
        bang["ngay"] = pd.to_datetime(bang["ngay"])
        self._bang = bang.sort_values(["ma_chuoi", "ngay"], kind="stable").reset_index(drop=True)
        self._cau_hinh = cau_hinh

    def __repr__(self) -> str:
        """Mo ta bang gia, dung khi ghi nhat ky.

        Tham so:
            Khong co.

        Tra ve:
            Chuoi gom so dong, so chuoi va khoang thoi gian.

        Ngoai le:
            Khong co.
        """
        return (
            f"BangGia({len(self)} dong, {len(self.cac_chuoi)} chuoi, "
            f"{self.ngay_dau:%Y-%m-%d}..{self.ngay_cuoi:%Y-%m-%d})"
        )

    def __len__(self) -> int:
        """So quan sat gia trong bang.

        Tham so:
            Khong co.

        Tra ve:
            So nguyen.

        Ngoai le:
            Khong co.
        """
        return len(self._bang)

    def __contains__(self, ma_chuoi: object) -> bool:
        """Cho biet bang co quan sat cua mot chuoi hay khong, vi du `"brent" in bang_gia`.

        Tham so:
            ma_chuoi: ma chuoi chuan.

        Tra ve:
            True neu bang co it nhat mot quan sat cua chuoi.

        Ngoai le:
            Khong co.
        """
        return ma_chuoi in self.cac_chuoi

    @property
    def bang(self) -> pd.DataFrame:
        """Ban sao cua bang gia da sap xep theo ma chuoi va ngay.

        Tham so:
            Khong co.

        Tra ve:
            Bang theo luoc do bang sach.

        Ngoai le:
            Khong co.
        """
        return self._bang.copy()

    @property
    def cac_chuoi(self) -> list[str]:
        """Danh sach ma chuoi co trong bang.

        Tham so:
            Khong co.

        Tra ve:
            Danh sach ma chuoi, sap theo thu tu chu cai.

        Ngoai le:
            Khong co.
        """
        return sorted(self._bang["ma_chuoi"].unique())

    @property
    def ngay_dau(self) -> pd.Timestamp:
        """Ngay som nhat co quan sat.

        Tham so:
            Khong co.

        Tra ve:
            Moc thoi gian dau.

        Ngoai le:
            Khong co.
        """
        return self._bang["ngay"].min()

    @property
    def ngay_cuoi(self) -> pd.Timestamp:
        """Ngay muon nhat co quan sat.

        Tham so:
            Khong co.

        Tra ve:
            Moc thoi gian cuoi.

        Ngoai le:
            Khong co.
        """
        return self._bang["ngay"].max()

    def ten(self, ma_chuoi: str) -> str:
        """Ten hien thi cua mot chuoi.

        Tham so:
            ma_chuoi: ma chuoi chuan.

        Tra ve:
            Ten co dau dung trong bang va bieu do.

        Ngoai le:
            BangRongError: khi bang khong co chuoi nay.
        """
        dong = self._bang.loc[self._bang["ma_chuoi"].eq(ma_chuoi), "ten_chuoi"]
        if dong.empty:
            raise BangRongError(f"Bang gia khong co chuoi '{ma_chuoi}'.")
        return str(dong.iloc[0])

    def chuoi(self, ma_chuoi: str, cot: str = "gia_vnd_lit") -> pd.Series:
        """Lay mot chuoi gia theo ngay, chi gom nhung ngay co quan sat.

        Tham so:
            ma_chuoi: ma chuoi chuan, vi du "brent".
            cot: cot gia tri can lay, mac dinh la gia quy ra dong/lit.

        Tra ve:
            Chuoi so thuc co chi so la ngay tang dan, da bo gia tri thieu.

        Ngoai le:
            BangRongError: khi bang khong co quan sat nao cua chuoi nay.
            ThieuCotError: khi `cot` khong co trong bang.
        """
        if cot not in self._bang.columns:
            raise ThieuCotError(f"Bang gia khong co cot '{cot}'.")
        chon = self._bang.loc[self._bang["ma_chuoi"].eq(ma_chuoi), ["ngay", cot]].dropna()
        if chon.empty:
            raise BangRongError(f"Bang gia khong co quan sat nao cua chuoi '{ma_chuoi}'.")
        return chon.set_index("ngay")[cot].astype(float).rename(ma_chuoi)

    def theo_ngay(self, ma_chuoi: str, cot: str = "gia_vnd_lit") -> pd.Series:
        """Trai mot chuoi ra moi ngay lich, ngay khong co quan sat giu gia gan nhat truoc do.

        Gia ban le chi doi o ky dieu chinh nen giu nguyen den ky sau; gia giao
        ngay khong co o ngay nghi nen giu gia phien truoc.

        Tham so:
            ma_chuoi: ma chuoi chuan.
            cot: cot gia tri can lay.

        Tra ve:
            Chuoi theo ngay lich tu quan sat dau tien den quan sat cuoi cung cua chinh
            chuoi do; mot chuoi da ngung cong bo khong bi keo dai them.

        Ngoai le:
            BangRongError: khi bang khong co quan sat nao cua chuoi nay.
        """
        chuoi = self.chuoi(ma_chuoi, cot)
        lich = pd.date_range(chuoi.index.min(), chuoi.index.max(), freq="D", name="ngay")
        return chuoi.reindex(lich).ffill()

    def loi_suat_log(self, ma_chuoi: str) -> pd.Series:
        """Loi suat log giua hai phien lien tiep cua mot chuoi, tinh bang NumPy.

        Tham so:
            ma_chuoi: ma chuoi chuan.

        Tra ve:
            Chuoi ln(P_t / P_{t-1}) theo ngay; phien co gia khong duong (hoac
            phien ngay sau do) bi bo vi khong lay duoc logarit.

        Ngoai le:
            BangRongError: khi bang khong co quan sat nao cua chuoi nay.
        """
        gia = self.chuoi(ma_chuoi, "gia_usd_thung")
        gia_tri = gia.to_numpy()
        hop_le = (gia_tri[1:] > 0) & (gia_tri[:-1] > 0)
        loi_suat = np.full(len(gia_tri) - 1, np.nan)
        loi_suat[hop_le] = np.log(gia_tri[1:][hop_le] / gia_tri[:-1][hop_le])
        return pd.Series(loi_suat, index=gia.index[1:], name=ma_chuoi).dropna()

    def boi_canh_theo_ngay(self, ngay: pd.DatetimeIndex) -> pd.Series:
        """Tra ma su kien (boi canh) cua tung ngay theo lich su kien trong cau hinh.

        Tham so:
            ngay: cac ngay can tra.

        Tra ve:
            Chuoi ma su kien co chi so la `ngay`.

        Ngoai le:
            Khong co.
        """
        bang = self._cau_hinh.lich_su_kien.bang_theo_ngay(pd.Series(ngay))
        return bang.set_index("ngay")["su_kien"].reindex(ngay)

    def su_kien_co_du_lieu(self) -> list[SuKien]:
        """Cac su kien trong cau hinh co giao voi khoang thoi gian cua du lieu.

        Tham so:
            Khong co.

        Tra ve:
            Danh sach SuKien theo thu tu thoi gian.

        Ngoai le:
            Khong co.
        """
        return [
            su_kien
            for su_kien in self._cau_hinh.lich_su_kien
            if su_kien.bat_dau <= self.ngay_cuoi
            and su_kien.ngay_cuoi(self.ngay_cuoi) >= self.ngay_dau
        ]


class BoTongHop:
    """Tong hop thong ke mo ta cua cac cot gia tri theo nhom."""

    THONG_KE = {
        "so_quan_sat": "count",
        "trung_binh": "mean",
        "trung_vi": "median",
        "do_lech_chuan": "std",
        "nho_nhat": "min",
        "lon_nhat": "max",
    }

    def __init__(self, df: pd.DataFrame, cau_hinh: CauHinh) -> None:
        """Tao bo tong hop.

        Tham so:
            df: bang du lieu da lam sach.
            cau_hinh: cau hinh cua du an; `phan_tich.cot_tong_hop` la cac cot gia tri.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        self._df = df
        self._cau_hinh = cau_hinh

    def theo(self, theo: list[str]) -> pd.DataFrame:
        """Nhom theo cac cot chi dinh va tinh thong ke mo ta.

        Tham so:
            theo: danh sach ten cot dung de nhom.

        Tra ve:
            Bang moi, moi dong la mot nhom; voi moi cot gia tri co cac cot
            <cot>_so_quan_sat, _trung_binh, _trung_vi, _do_lech_chuan, _nho_nhat, _lon_nhat.

        Ngoai le:
            ThamSoError: khi `theo` rong.
            BangRongError: khi bang khong co dong nao.
            ThieuCotError: khi mot ten cot trong `theo` hoac cot gia tri khong co trong bang.
            CotToanThieuError: khi mot cot gia tri chi chua gia tri thieu.
        """
        if not theo:
            raise ThamSoError("Danh sach cot `theo` khong duoc rong.")
        cot_gia_tri = [str(cot) for cot in self._cau_hinh["phan_tich.cot_tong_hop"]]
        trung = [cot for cot in theo if cot in cot_gia_tri]
        if trung:
            raise ThamSoError(f"Cot {trung} la cot gia tri, khong dung de nhom.")
        LuocDo("bang can tong hop", (*theo, *cot_gia_tri), tuple(cot_gia_tri)).kiem_tra(self._df)
        nhom = self._df.groupby(theo, dropna=False, sort=True)[cot_gia_tri]
        bang = nhom.agg(list(self.THONG_KE.values()))
        ten_thong_ke = {ham: ten for ten, ham in self.THONG_KE.items()}
        bang.columns = [f"{cot}_{ten_thong_ke[ham]}" for cot, ham in bang.columns]
        return bang.reset_index()


class NhanSuKien:
    """Gan ten hien thi va thu tu thoi gian cua su kien vao mot bang ket qua."""

    def __init__(self, cau_hinh: CauHinh) -> None:
        """Tao bo gan nhan.

        Tham so:
            cau_hinh: cau hinh cua du an, noi khai bao lich su kien.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        lich = cau_hinh.lich_su_kien
        self._thu_tu = [lich.nhan_binh_thuong, *(su_kien.ma for su_kien in lich)]
        self._ten = {su_kien.ma: su_kien.ten_ngan for su_kien in lich}
        self._ten[lich.nhan_binh_thuong] = str(cau_hinh["su_kien.ten_binh_thuong"])
        self._loai = {su_kien.ma: su_kien.loai for su_kien in lich}
        self._loai[lich.nhan_binh_thuong] = lich.nhan_binh_thuong

    @property
    def thu_tu(self) -> list[str]:
        """Ma cac boi canh theo thu tu hien thi: binh thuong truoc, roi theo thoi gian.

        Tham so:
            Khong co.

        Tra ve:
            Danh sach ma su kien.

        Ngoai le:
            Khong co.
        """
        return list(self._thu_tu)

    def ten(self, ma: str) -> str:
        """Ten hien thi cua mot boi canh.

        Tham so:
            ma: ma su kien, hoac nhan binh thuong.

        Tra ve:
            Ten ngan co dau; tra lai chinh `ma` neu khong co trong lich su kien.

        Ngoai le:
            Khong co.
        """
        return self._ten.get(ma, ma)

    def loai(self, ma: str) -> str:
        """Loai boi canh (dich benh, xung dot, binh thuong) cua mot ma su kien.

        Tham so:
            ma: ma su kien, hoac nhan binh thuong.

        Tra ve:
            Ma loai boi canh; ma la khong co trong lich thi coi la binh thuong.

        Ngoai le:
            Khong co.
        """
        return self._loai.get(ma, self._thu_tu[0])

    def gan(self, bang: pd.DataFrame, sap_truoc: list[str]) -> pd.DataFrame:
        """Them cot `ten_su_kien`, `loai_boi_canh` va sap dong theo thu tu thoi gian.

        Tham so:
            bang: bang co cot `su_kien` chua ma su kien.
            sap_truoc: cac cot dung de sap truoc khi sap theo su kien.

        Tra ve:
            Bang moi da them hai cot va da sap xep, danh lai chi so.

        Ngoai le:
            ThieuCotError: khi bang khong co cot `su_kien`.
        """
        if "su_kien" not in bang.columns:
            raise ThieuCotError("Bang ket qua khong co cot 'su_kien' de gan nhan.")
        ket_qua = bang.copy()
        ket_qua["ten_su_kien"] = ket_qua["su_kien"].map(self._ten)
        ket_qua["loai_boi_canh"] = ket_qua["su_kien"].map(self._loai)
        thu_tu = ket_qua["su_kien"].map({ma: vi_tri for vi_tri, ma in enumerate(self._thu_tu)})
        ket_qua = ket_qua.assign(_thu_tu=thu_tu).sort_values([*sap_truoc, "_thu_tu"], kind="stable")
        return ket_qua.drop(columns="_thu_tu").reset_index(drop=True)


class BienDongTheoBoiCanh(PhepPhanTich):
    """Do bien dong cua gia the gioi trong tung boi canh, so voi luc binh thuong."""

    ten = "bien_dong_theo_boi_canh"
    ten_tep = "b1_bien_dong_theo_boi_canh.csv"

    def bang(self) -> pd.DataFrame:
        """Tinh do lech chuan cua loi suat log theo ngay, quy ve nam, cho tung boi canh.

        Tham so:
            Khong co.

        Tra ve:
            Bang moi dong la mot cap (chuoi, boi canh): so phien, do bien dong
            quy nam (%) va ty so so voi boi canh binh thuong cua cung chuoi.

        Ngoai le:
            BangRongError: khi khong chuoi nao trong `phan_tich.chuoi_bien_dong` du du lieu.
        """
        cau_hinh, bang_gia = self._cau_hinh, self._bang_gia
        so_ngay_nam = float(cau_hinh["phan_tich.so_ngay_giao_dich_nam"])
        toi_thieu = int(cau_hinh["phan_tich.so_phien_toi_thieu"])
        cac_dong = []
        for ma in cau_hinh["phan_tich.chuoi_bien_dong"]:
            if ma not in bang_gia:
                continue
            loi_suat = bang_gia.loi_suat_log(ma)
            boi_canh = bang_gia.boi_canh_theo_ngay(loi_suat.index).to_numpy()
            for su_kien, nhom in loi_suat.groupby(boi_canh):
                if len(nhom) < toi_thieu:
                    continue
                do_lech = float(np.std(nhom.to_numpy(), ddof=1))
                cac_dong.append(
                    {
                        "ma_chuoi": ma,
                        "ten_chuoi": bang_gia.ten(ma),
                        "su_kien": su_kien,
                        "so_phien": len(nhom),
                        "bien_dong_nam_pct": do_lech * np.sqrt(so_ngay_nam) * 100.0,
                    }
                )
        if not cac_dong:
            raise BangRongError("Khong chuoi gia the gioi nao du du lieu de tinh do bien dong.")
        bang = pd.DataFrame(cac_dong)
        binh_thuong = cau_hinh.lich_su_kien.nhan_binh_thuong
        goc = bang.loc[bang["su_kien"].eq(binh_thuong)].set_index("ma_chuoi")["bien_dong_nam_pct"]
        bang["gap_lan_binh_thuong"] = bang["bien_dong_nam_pct"] / bang["ma_chuoi"].map(goc)
        return NhanSuKien(cau_hinh).gan(bang, ["ma_chuoi"])

    def tom_tat(self) -> dict[str, object]:
        """Do bien dong cua chuoi dai dien gia the gioi va boi canh bien dong manh nhat.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien gom do bien dong luc binh thuong, ty so cua tung su kien va
            ten su kien co ty so lon nhat.

        Ngoai le:
            BangRongError: khi chuoi dai dien khong du du lieu.
        """
        ma = str(self._cau_hinh["phan_tich.chuoi_the_gioi"])
        binh_thuong = self._cau_hinh.lich_su_kien.nhan_binh_thuong
        bang = self.bang()
        bang = bang.loc[bang["ma_chuoi"].eq(ma)].set_index("su_kien")
        if binh_thuong not in bang.index:
            raise BangRongError(f"Chuoi '{ma}' khong co du phien binh thuong de so sanh.")
        ket_qua: dict[str, object] = {
            f"bien_dong_{ma}_binh_thuong_pct_nam": round(
                float(bang.loc[binh_thuong, "bien_dong_nam_pct"]), 1
            )
        }
        su_kien = bang.drop(index=binh_thuong)
        for ma_su_kien, dong in su_kien.iterrows():
            ket_qua[f"bien_dong_{ma}_{ma_su_kien}_pct_nam"] = round(
                float(dong["bien_dong_nam_pct"]), 1
            )
            ket_qua[f"bien_dong_{ma}_{ma_su_kien}_gap_lan"] = round(
                float(dong["gap_lan_binh_thuong"]), 2
            )
        if not su_kien.empty:
            manh_nhat = su_kien["gap_lan_binh_thuong"].idxmax()
            ket_qua["boi_canh_bien_dong_manh_nhat"] = str(su_kien.loc[manh_nhat, "ten_su_kien"])
        return ket_qua


class CuSocGia(PhepPhanTich):
    """Muc thay doi lon nhat cua gia the gioi va gia ban le trong tung su kien."""

    ten = "cu_soc_gia"
    ten_tep = "b2_cu_soc_gia_theo_su_kien.csv"

    def bang(self) -> pd.DataFrame:
        """So gia cuc tri trong su kien voi gia ngay truoc su kien, cho tung chuoi.

        Gia the gioi duoc lam tron bang binh quan truot (so ngay khai bao trong
        cau hinh) de so duoc voi gia ban le, von tinh tu gia binh quan ca ky. Huong
        cua cu soc (tang hay giam) lay theo gia the gioi; ty le truyen dan la muc
        thay doi (%) cua gia ban le chia cho muc thay doi (%) cua gia the gioi.

        Tham so:
            Khong co.

        Tra ve:
            Bang moi dong la mot cap (su kien, chuoi), gia tinh bang dong/lit.

        Ngoai le:
            BangRongError: khi khong su kien nao co du du lieu gia the gioi.
        """
        cau_hinh, bang_gia = self._cau_hinh, self._bang_gia
        ma_the_gioi = str(cau_hinh["phan_tich.chuoi_the_gioi"])
        cua_so = int(cau_hinh["phan_tich.cua_so_trung_binh_ngay"])
        the_gioi = bang_gia.theo_ngay(ma_the_gioi).rolling(cua_so, min_periods=cua_so).mean()
        cac_chuoi = {ma_the_gioi: the_gioi}
        for ma in cau_hinh["phan_tich.chuoi_ban_le"]:
            if ma in bang_gia:
                cac_chuoi[str(ma)] = bang_gia.theo_ngay(str(ma))
        cac_dong = []
        for su_kien in bang_gia.su_kien_co_du_lieu():
            ngay_cuoi = su_kien.ngay_cuoi(bang_gia.ngay_cuoi)
            moc = self.do_cu_soc(the_gioi, su_kien.bat_dau, ngay_cuoi, None)
            if moc is None:
                continue
            for ma, gia in cac_chuoi.items():
                dong = self.do_cu_soc(gia, su_kien.bat_dau, ngay_cuoi, str(moc["huong"]))
                if dong is None:
                    continue
                dong["ty_le_truyen_dan"] = dong["thay_doi_pct"] / moc["thay_doi_pct"]
                cac_dong.append(
                    {"su_kien": su_kien.ma, "ma_chuoi": ma, "ten_chuoi": bang_gia.ten(ma), **dong}
                )
        if not cac_dong:
            raise BangRongError("Khong su kien nao co du du lieu gia the gioi de do cu soc.")
        return NhanSuKien(cau_hinh).gan(pd.DataFrame(cac_dong), [])

    @staticmethod
    def do_cu_soc(
        gia: pd.Series, bat_dau: pd.Timestamp, ket_thuc: pd.Timestamp, huong: str | None
    ) -> dict[str, Any] | None:
        """Do muc thay doi lon nhat cua mot chuoi gia trong mot khoang thoi gian.

        Tham so:
            gia: chuoi gia theo ngay lich.
            bat_dau: ngay dau cua khoang.
            ket_thuc: ngay cuoi cua khoang.
            huong: "tang" (lay gia cao nhat), "giam" (lay gia thap nhat), hoac
                None de tu chon huong co muc thay doi lon hon.

        Tra ve:
            Tu dien gom huong, gia ngay truoc khoang, gia cuc tri, ngay dat cuc
            tri, muc thay doi (%) va muc thay doi tuyet doi; None neu chuoi
            khong co gia ngay truoc khoang hoac trong khoang.

        Ngoai le:
            Khong co.
        """
        truoc = gia.loc[: bat_dau - pd.Timedelta(days=1)].dropna()
        trong = gia.loc[bat_dau:ket_thuc].dropna()
        if truoc.empty or trong.empty:
            return None
        gia_truoc = float(truoc.iloc[-1])
        if huong is None:
            tang, giam = trong.max() / gia_truoc - 1.0, trong.min() / gia_truoc - 1.0
            huong = "tang" if tang >= abs(giam) else "giam"
        ngay = trong.idxmax() if huong == "tang" else trong.idxmin()
        cuc_tri = float(trong.loc[ngay])
        return {
            "huong": huong,
            "gia_truoc": gia_truoc,
            "gia_cuc_tri": cuc_tri,
            "ngay_cuc_tri": ngay.strftime("%Y-%m-%d"),
            "thay_doi_pct": (cuc_tri / gia_truoc - 1.0) * 100.0,
            "thay_doi_dong_lit": cuc_tri - gia_truoc,
        }

    def tom_tat(self) -> dict[str, object]:
        """Muc thay doi va ty le truyen dan cua cac mat hang chinh trong cac su kien chinh.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien: voi moi su kien chinh co muc thay doi (%) cua gia the gioi,
            cua tung mat hang chinh va ty le truyen dan; kem gia ban le cao nhat
            ca giai doan cua tung mat hang chinh.

        Ngoai le:
            BangRongError: khi khong su kien nao co du du lieu.
        """
        cau_hinh, bang_gia = self._cau_hinh, self._bang_gia
        ma_the_gioi = str(cau_hinh["phan_tich.chuoi_the_gioi"])
        mat_hang = [str(ma) for ma in cau_hinh["phan_tich.mat_hang_chinh"]]
        bang = self.bang().set_index(["su_kien", "ma_chuoi"])
        ket_qua: dict[str, object] = {}
        for su_kien in cau_hinh["phan_tich.su_kien_chinh"]:
            for ma in (ma_the_gioi, *mat_hang):
                if (su_kien, ma) not in bang.index:
                    continue
                dong = bang.loc[(su_kien, ma)]
                ket_qua[f"{ma}_thay_doi_pct_{su_kien}"] = round(float(dong["thay_doi_pct"]), 1)
                if ma != ma_the_gioi:
                    ket_qua[f"truyen_dan_{ma}_{su_kien}"] = round(
                        float(dong["ty_le_truyen_dan"]), 2
                    )
        for ma in mat_hang:
            if ma in bang_gia:
                gia = bang_gia.chuoi(ma)
                ket_qua[f"{ma}_cao_nhat_dong_lit"] = int(round(float(gia.max())))
                ket_qua[f"{ma}_ngay_cao_nhat"] = gia.idxmax().strftime("%Y-%m-%d")
        return ket_qua


class TyTrongGiaTheGioi(PhepPhanTich):
    """Ty trong gia thanh pham the gioi (Singapore) trong gia ban le cung mat hang."""

    ten = "ty_trong_gia_the_gioi"
    ten_tep = "b3_ty_trong_gia_the_gioi_trong_gia_ban_le.csv"

    def theo_ky(self) -> pd.DataFrame:
        """Ghep gia ban le voi gia thanh pham the gioi cua cung ky dieu hanh theo khoa `ngay`.

        Tham so:
            Khong co.

        Tra ve:
            Bang moi dong la mot ky dieu hanh cua mot mat hang: gia ban le, gia
            the gioi (dong/lit), ty trong (%) va phan chenh (dong/lit).

        Ngoai le:
            BangRongError: khi khong cap mat hang nao co ky chung.
        """
        bang = self._bang_gia.bang
        cot = ["ngay", "gia_vnd_lit"]
        cac_cap = []
        for cap in self._cau_hinh["phan_tich.cap_ty_trong"]:
            la_ban_le = bang["ma_chuoi"].eq(str(cap["ban_le"])) & ~bang["suy_ra"].astype(bool)
            ban_le = bang.loc[la_ban_le, [*cot, "su_kien"]]
            the_gioi = bang.loc[bang["ma_chuoi"].eq(str(cap["the_gioi"])), cot]
            ghep = ban_le.merge(
                the_gioi,
                on="ngay",
                how="inner",
                suffixes=("_ban_le", "_the_gioi"),
                validate="one_to_one",
            )
            cac_cap.append(ghep.assign(ban_le=str(cap["ban_le"]), the_gioi=str(cap["the_gioi"])))
        theo_ky = pd.concat(cac_cap, ignore_index=True) if cac_cap else pd.DataFrame()
        if theo_ky.empty:
            raise BangRongError("Khong co ky nao vua co gia ban le vua co gia thanh pham the gioi.")
        theo_ky["ty_trong_pct"] = (
            theo_ky["gia_vnd_lit_the_gioi"] / theo_ky["gia_vnd_lit_ban_le"] * 100
        )
        theo_ky["chenh_lech_dong_lit"] = (
            theo_ky["gia_vnd_lit_ban_le"] - theo_ky["gia_vnd_lit_the_gioi"]
        )
        return theo_ky.sort_values(["ban_le", "ngay"], kind="stable").reset_index(drop=True)

    def bang(self) -> pd.DataFrame:
        """Trung binh ty trong va phan chenh theo mat hang va boi canh.

        Tham so:
            Khong co.

        Tra ve:
            Bang moi dong la mot cap (mat hang ban le, boi canh): so ky, ty trong
            trung binh (%) va phan chenh trung binh (dong/lit).

        Ngoai le:
            BangRongError: khi khong cap mat hang nao co ky chung.
        """
        nhom = self.theo_ky().groupby(["ban_le", "the_gioi", "su_kien"], sort=False)
        bang = nhom.agg(
            so_ky=("ty_trong_pct", "size"),
            ty_trong_tb_pct=("ty_trong_pct", "mean"),
            chenh_lech_tb_dong_lit=("chenh_lech_dong_lit", "mean"),
        ).reset_index()
        bang.insert(1, "ten_ban_le", bang["ban_le"].map(self._bang_gia.ten))
        return NhanSuKien(self._cau_hinh).gan(bang, ["ban_le"])

    def tom_tat(self) -> dict[str, object]:
        """Ty trong trung binh cua cac mat hang chinh luc binh thuong va trong su kien chinh.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien ten chi tieu -> ty trong (%).

        Ngoai le:
            BangRongError: khi khong cap mat hang nao co ky chung.
        """
        cau_hinh = self._cau_hinh
        bang = self.bang().set_index(["ban_le", "su_kien"])
        can_xem = [cau_hinh.lich_su_kien.nhan_binh_thuong, *cau_hinh["phan_tich.su_kien_chinh"]]
        ket_qua: dict[str, object] = {}
        for ma in cau_hinh["phan_tich.mat_hang_chinh"]:
            for su_kien in can_xem:
                if (ma, su_kien) in bang.index:
                    gia_tri = float(bang.loc[(ma, su_kien), "ty_trong_tb_pct"])
                    ket_qua[f"ty_trong_gia_singapore_{ma}_{su_kien}_pct"] = round(gia_tri, 1)
        return ket_qua


class TuongQuanBoiCanh(PhepPhanTich):
    """Tuong quan theo thang giua gia, do bien dong va cac chi so boi canh."""

    ten = "tuong_quan_boi_canh"
    ten_tep = "b4_tuong_quan_theo_thang.csv"

    def theo_thang(self) -> pd.DataFrame:
        """Gop so lieu ve tung thang: gia, do bien dong, chi so boi canh, muc thay doi.

        Boi canh cua mot thang la boi canh cua ngay dai dien trong thang do, khai bao
        o `phan_tich.ngay_dai_dien_thang` cua cau hinh.

        Tham so:
            Khong co.

        Tra ve:
            Bang co chi so la thang (ngay dau thang) voi cac cot: bien_dong_thang_pct,
            gia_the_gioi_usd, gpr, phong_toa_tg, thay_doi_the_gioi_pct,
            thay_doi_ban_le_pct, su_kien.

        Ngoai le:
            BangRongError: khi thieu chuoi gia the gioi.
        """
        cau_hinh, bang_gia = self._cau_hinh, self._bang_gia
        ma_the_gioi = str(cau_hinh["phan_tich.chuoi_the_gioi"])
        so_ngay_nam = float(cau_hinh["phan_tich.so_ngay_giao_dich_nam"])
        toi_thieu = int(cau_hinh["phan_tich.so_phien_toi_thieu_thang"])
        loi_suat = bang_gia.loi_suat_log(ma_the_gioi)
        theo_thang = loi_suat.groupby(loi_suat.index.to_period("M")).agg(["std", "count"])
        bien_dong = (
            theo_thang["std"].where(theo_thang["count"] >= toi_thieu) * np.sqrt(so_ngay_nam) * 100
        )
        quan_sat = bang_gia.bang
        quan_sat = quan_sat.loc[quan_sat["ma_chuoi"].eq(ma_the_gioi)]
        thang = quan_sat["ngay"].dt.to_period("M")
        chi_so = quan_sat.groupby(thang)[["gia_usd_thung", "gpr", "phong_toa_tg"]].mean()
        gia_the_gioi = bang_gia.theo_ngay(ma_the_gioi)
        bang = pd.DataFrame(
            {
                "bien_dong_thang_pct": bien_dong,
                "gia_the_gioi_usd": chi_so["gia_usd_thung"],
                "gpr": chi_so["gpr"],
                "phong_toa_tg": chi_so["phong_toa_tg"],
                "thay_doi_the_gioi_pct": self.thay_doi_thang(gia_the_gioi),
            }
        )
        ma_ban_le = str(cau_hinh["phan_tich.mat_hang_chinh"][0])
        if ma_ban_le in bang_gia:
            bang["thay_doi_ban_le_pct"] = self.thay_doi_thang(bang_gia.theo_ngay(ma_ban_le))
        else:
            bang["thay_doi_ban_le_pct"] = np.nan
        ngay_dai_dien = int(cau_hinh["phan_tich.ngay_dai_dien_thang"])
        moc_thang = bang.index.to_timestamp() + pd.Timedelta(days=ngay_dai_dien - 1)
        bang["su_kien"] = bang_gia.boi_canh_theo_ngay(pd.DatetimeIndex(moc_thang)).to_numpy()
        bang.index = bang.index.to_timestamp()
        return bang.rename_axis("thang")

    @staticmethod
    def thay_doi_thang(gia_theo_ngay: pd.Series) -> pd.Series:
        """Muc thay doi (%) cua gia binh quan thang so voi thang truoc.

        Tham so:
            gia_theo_ngay: chuoi gia theo ngay lich.

        Tra ve:
            Chuoi phan tram co chi so la ky thang.

        Ngoai le:
            Khong co.
        """
        binh_quan = gia_theo_ngay.groupby(gia_theo_ngay.index.to_period("M")).mean()
        return binh_quan.pct_change() * 100.0

    @staticmethod
    def he_so_tuong_quan(x: pd.Series, y: pd.Series, so_ky_toi_thieu: int) -> tuple[float, int]:
        """He so tuong quan Pearson cua hai chuoi tren cac ky ca hai cung co gia tri.

        Tham so:
            x: chuoi thu nhat.
            y: chuoi thu hai, cung chi so voi `x`.
            so_ky_toi_thieu: so ky chung it nhat phai co de tinh he so.

        Tra ve:
            Cap (he so tuong quan, so ky dung de tinh); he so la NaN neu so ky
            chung it hon `so_ky_toi_thieu`.

        Ngoai le:
            Khong co.
        """
        chung = pd.concat([x, y], axis=1).dropna()
        if len(chung) < so_ky_toi_thieu:
            return float("nan"), len(chung)
        he_so = np.corrcoef(chung.iloc[:, 0].to_numpy(), chung.iloc[:, 1].to_numpy())[0, 1]
        return float(he_so), len(chung)

    def bang(self) -> pd.DataFrame:
        """Tinh cac he so tuong quan theo thang.

        Tham so:
            Khong co.

        Tra ve:
            Bang moi dong la mot cap bien: ten chi tieu, he so tuong quan, so thang.

        Ngoai le:
            BangRongError: khi thieu chuoi gia the gioi.
        """
        thang = self.theo_thang()
        co_phong_toa = thang["phong_toa_tg"].where(thang["phong_toa_tg"] > 0)
        cac_cap = {
            "gpr_va_bien_dong_gia_the_gioi": (thang["gpr"], thang["bien_dong_thang_pct"]),
            "phong_toa_va_gia_the_gioi": (co_phong_toa, thang["gia_the_gioi_usd"]),
            "phong_toa_va_bien_dong_gia_the_gioi": (co_phong_toa, thang["bien_dong_thang_pct"]),
            "thay_doi_gia_the_gioi_va_ban_le_cung_thang": (
                thang["thay_doi_the_gioi_pct"],
                thang["thay_doi_ban_le_pct"],
            ),
            "thay_doi_gia_the_gioi_thang_truoc_va_ban_le": (
                thang["thay_doi_the_gioi_pct"].shift(1),
                thang["thay_doi_ban_le_pct"],
            ),
        }
        toi_thieu = int(self._cau_hinh["phan_tich.so_thang_toi_thieu_tuong_quan"])
        cac_dong = []
        for ten, (x, y) in cac_cap.items():
            he_so, so_thang = self.he_so_tuong_quan(x, y, toi_thieu)
            cac_dong.append({"chi_tieu": ten, "he_so_tuong_quan": he_so, "so_thang": so_thang})
        return pd.DataFrame(cac_dong)

    def tom_tat(self) -> dict[str, object]:
        """Cac he so tuong quan theo thang, lam tron hai chu so.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien `tuong_quan_<chi tieu>` -> he so; bo qua chi tieu khong tinh duoc.

        Ngoai le:
            BangRongError: khi thieu chuoi gia the gioi.
        """
        bang = self.bang().dropna(subset=["he_so_tuong_quan"])
        return {
            f"tuong_quan_{dong.chi_tieu}": round(float(dong.he_so_tuong_quan), 2)
            for dong in bang.itertuples()
        }


class DoPhuGiaBanLe(PhepPhanTich):
    """Do phu cua chuoi gia ban le: so ky quan sat duoc va so khoang bi thieu ky dieu hanh."""

    ten = "do_phu_gia_ban_le"
    ten_tep = "b5_do_phu_gia_ban_le.csv"

    def bang(self) -> pd.DataFrame:
        """Dem theo chuoi va nam: ky quan sat, dong suy ra, khoang thieu ky, khoang cach dai nhat.

        Mot "khoang thieu ky" la cho ma gia ngay truoc ky dieu chinh (dong suy ra)
        khac gia quan sat lien truoc: giua hai quan sat co it nhat mot ky dieu hanh
        khong thu thap duoc.

        Tham so:
            Khong co.

        Tra ve:
            Bang moi dong la mot cap (chuoi ban le, nam).

        Ngoai le:
            BangRongError: khi bang gia khong co chuoi ban le nao trong cau hinh.
        """
        sai_so = float(self._cau_hinh["lam_sach.sai_so_lam_tron"])
        bang = self._bang_gia.bang
        cac_bang = []
        for ma in (str(ma) for ma in self._cau_hinh["phan_tich.chuoi_ban_le"]):
            chuoi = bang.loc[bang["ma_chuoi"].eq(ma)]
            if chuoi.empty:
                continue
            suy_ra = chuoi["suy_ra"].astype(bool)
            lech = (chuoi["gia_goc"] - chuoi["gia_goc"].shift(1)).abs()
            khoang_cach = chuoi.loc[~suy_ra, "ngay"].diff().dt.days
            chi_tieu = pd.DataFrame(
                {
                    "nam": chuoi["nam"],
                    "so_ky_quan_sat": (~suy_ra).astype(int),
                    "so_dong_suy_ra": suy_ra.astype(int),
                    "so_khoang_thieu_ky": (suy_ra & lech.gt(sai_so)).astype(int),
                    "khoang_cach_lon_nhat_ngay": khoang_cach.reindex(chuoi.index),
                }
            )
            theo_nam = chi_tieu.groupby("nam").agg(
                so_ky_quan_sat=("so_ky_quan_sat", "sum"),
                so_dong_suy_ra=("so_dong_suy_ra", "sum"),
                so_khoang_thieu_ky=("so_khoang_thieu_ky", "sum"),
                khoang_cach_lon_nhat_ngay=("khoang_cach_lon_nhat_ngay", "max"),
            )
            ten_cot = "khoang_cach_lon_nhat_ngay"
            theo_nam[ten_cot] = theo_nam[ten_cot].astype("Int64")
            theo_nam.insert(0, "ten_chuoi", self._bang_gia.ten(ma))
            theo_nam.insert(0, "ma_chuoi", ma)
            cac_bang.append(theo_nam.reset_index())
        if not cac_bang:
            raise BangRongError("Bang gia khong co chuoi gia ban le nao khai bao trong cau hinh.")
        ket_qua = pd.concat(cac_bang, ignore_index=True)
        return ket_qua.loc[:, ["ma_chuoi", "ten_chuoi", "nam", *ket_qua.columns[3:]]]

    def tom_tat(self) -> dict[str, object]:
        """Tong so ky quan sat va so khoang thieu ky cua cac mat hang chinh.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien `so_ky_quan_sat_<ma>` va `so_khoang_thieu_ky_<ma>` -> so nguyen.

        Ngoai le:
            BangRongError: khi bang gia khong co chuoi ban le nao trong cau hinh.
        """
        tong = self.bang().groupby("ma_chuoi")[["so_ky_quan_sat", "so_khoang_thieu_ky"]].sum()
        ket_qua: dict[str, object] = {}
        for ma in (str(ma) for ma in self._cau_hinh["phan_tich.mat_hang_chinh"]):
            if ma in tong.index:
                ket_qua[f"so_ky_quan_sat_{ma}"] = int(tong.loc[ma, "so_ky_quan_sat"])
                ket_qua[f"so_khoang_thieu_ky_{ma}"] = int(tong.loc[ma, "so_khoang_thieu_ky"])
        return ket_qua


class BoTraLoi:
    """Gop cac phep phan tich thanh cau tra loi cho cau hoi cua de tai."""

    def __init__(self, df: pd.DataFrame, cau_hinh: CauHinh) -> None:
        """Dung bang gia va cac phep phan tich.

        Tham so:
            df: bang sach do khau lam sach tra ve.
            cau_hinh: cau hinh cua du an.

        Tra ve:
            Khong co.

        Ngoai le:
            BangRongError: khi bang khong co dong nao.
            ThieuCotError: khi bang thieu cot cua luoc do bang sach.
            CotToanThieuError: khi cot gia chi chua gia tri thieu.
        """
        self._df = df
        self._cau_hinh = cau_hinh
        self._bang_gia = BangGia(df, cau_hinh)
        NHAT_KY.info("Phan tich tren %r", self._bang_gia)
        self._cac_phep: list[PhepPhanTich] = [
            BienDongTheoBoiCanh(self._bang_gia, cau_hinh),
            CuSocGia(self._bang_gia, cau_hinh),
            TyTrongGiaTheGioi(self._bang_gia, cau_hinh),
            TuongQuanBoiCanh(self._bang_gia, cau_hinh),
            DoPhuGiaBanLe(self._bang_gia, cau_hinh),
        ]

    def tra_loi(self) -> dict[str, object]:
        """Gop cac con so tom tat cua moi phep phan tich.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien ten chi tieu -> con so hoac chuoi; phep phan tich khong du
            du lieu duoc bo qua va ghi vao nhat ky.

        Ngoai le:
            BangRongError: khi khong phep phan tich nao tinh duoc.
        """
        ket_qua: dict[str, object] = {}
        for phep in self._cac_phep:
            try:
                ket_qua.update(phep.tom_tat())
            except BangRongError as loi:
                NHAT_KY.warning("Bo qua phep phan tich %s: %s", phep.ten, loi)
        if not ket_qua:
            raise BangRongError("Du lieu khong du de tra loi bat ky phan nao cua cau hoi.")
        return ket_qua

    def cac_bang(self) -> dict[str, pd.DataFrame]:
        """Cac bang ket qua can ghi ra tep, gom ca cac bang tong hop theo nhom.

        Tham so:
            Khong co.

        Tra ve:
            Tu dien ten tep csv -> bang; phep phan tich khong du du lieu duoc bo qua.

        Ngoai le:
            ThieuCotError: khi cot nhom khai bao trong cau hinh khong co trong bang.
        """
        cac_bang: dict[str, pd.DataFrame] = {}
        for phep in self._cac_phep:
            try:
                cac_bang[phep.ten_tep] = phep.bang()
            except BangRongError as loi:
                NHAT_KY.warning("Khong lap duoc bang %s: %s", phep.ten_tep, loi)
        bo_tong_hop = BoTongHop(self._df, self._cau_hinh)
        for ten_tep, theo in self._cau_hinh["phan_tich.nhom_tong_hop"].items():
            cac_bang[str(ten_tep)] = bo_tong_hop.theo([str(cot) for cot in theo])
        return cac_bang


def tong_hop(df: pd.DataFrame, theo: list[str]) -> pd.DataFrame:
    """Tong hop so lieu theo cac cot duoc chi dinh.

    Tham so:
        df: bang du lieu da lam sach.
        theo: danh sach ten cot dung de nhom.

    Tra ve:
        Bang moi, moi dong la mot nhom, kem cac cot thong ke mo ta.

    Ngoai le:
        ThieuCotError: khi mot ten cot trong `theo` khong co trong df.
        BangRongError: khi df khong co dong nao.
        CotToanThieuError: khi mot cot gia tri chi chua gia tri thieu.
        ThamSoError: khi `theo` rong hoac chua cot gia tri.
    """
    return BoTongHop(df, CauHinh.tu_tep()).theo(theo)


def tra_loi_cau_hoi(df: pd.DataFrame) -> dict[str, object]:
    """Tra loi cau hoi phan tich bang cac con so tinh tu bang sach.

    Tham so:
        df: bang du lieu da lam sach.

    Tra ve:
        Tu dien ten chi tieu -> con so hoac chuoi, moi khoa tra loi mot phan cua cau hoi.

    Ngoai le:
        BangRongError: khi df khong co dong nao hoac khong du du lieu de tra loi.
        ThieuCotError: khi df thieu cot cua luoc do bang sach.
        CotToanThieuError: khi cot gia chi chua gia tri thieu.
    """
    return BoTraLoi(df, CauHinh.tu_tep()).tra_loi()
