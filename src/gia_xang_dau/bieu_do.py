"""Lop va ham ve bieu do.

Moi bieu do la mot lop con cua BieuDo: nhan mot bang gia hoac mot phep phan tich
(quan he hop thanh) va tra ve mot Figure. Viec ghi tep chi dien ra trong BieuDo.luu,
va chi ghi vao thu muc duoc truyen vao. Mo-dun dung giao dien huong doi tuong cua
matplotlib (Figure), khong dung pyplot, nen khong chon backend va khong mo cua so.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from .cau_hinh import CauHinh
from .lop_co_so import BangRongError, BieuDo
from .phan_tich import (
    BangGia,
    BienDongTheoBoiCanh,
    CuSocGia,
    NhanSuKien,
    TuongQuanBoiCanh,
    TyTrongGiaTheGioi,
)

NHAT_KY = logging.getLogger(__name__)


class BieuDoDienBienGia(BieuDo):
    """Duong gia the gioi va gia ban le theo thoi gian, to nen cac giai doan su kien."""

    ten_tep = "h1_dien_bien_gia_va_su_kien.png"

    def __init__(self, cau_hinh: CauHinh, bang_gia: BangGia) -> None:
        """Tao bieu do.

        Tham so:
            cau_hinh: cau hinh cua du an.
            bang_gia: bang gia da lam sach.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        super().__init__(cau_hinh)
        self._bang_gia = bang_gia

    def ve(self) -> Figure:
        """Ve gia the gioi (duong lien) va gia ban le (duong bac thang), cung don vi dong/lit.

        Tham so:
            Khong co.

        Tra ve:
            Hinh co mot truc tung bat dau tu 0.

        Ngoai le:
            BangRongError: khi bang gia khong co chuoi gia the gioi.
        """
        cau_hinh, bang_gia = self._cau_hinh, self._bang_gia
        ma_the_gioi = str(cau_hinh["phan_tich.chuoi_the_gioi"])
        the_gioi = bang_gia.theo_ngay(ma_the_gioi)
        hinh, truc = self.tao_hinh()
        truc.plot(
            the_gioi.index,
            the_gioi.to_numpy(),
            linewidth=0.9,
            color=self.mau_chuoi(ma_the_gioi),
            label=f"{bang_gia.ten(ma_the_gioi)} (giá giao ngay, quy ra đồng/lít)",
        )
        cao_nhat = float(the_gioi.max())
        for ma in (str(ma) for ma in cau_hinh["phan_tich.mat_hang_chinh"]):
            if ma not in bang_gia:
                continue
            gia = bang_gia.chuoi(ma)
            truc.step(
                gia.index,
                gia.to_numpy(),
                where="post",
                linewidth=1.3,
                color=self.mau_chuoi(ma),
                label=bang_gia.ten(ma),
            )
            cao_nhat = max(cao_nhat, float(gia.max()))
        self.to_nen_su_kien(truc, the_gioi.index.min(), bang_gia.ngay_cuoi)
        truc.set_xlim(the_gioi.index.min(), bang_gia.ngay_cuoi)
        truc.set_ylim(0, cao_nhat * float(cau_hinh["bieu_do.he_so_truc_tung"]))
        truc.yaxis.set_major_formatter(FuncFormatter(self.dinh_dang_so))
        truc.set_xlabel("Ngày (giá bán lẻ là giá tối đa, giữ nguyên đến kỳ điều chỉnh sau)")
        truc.set_ylabel("Giá (đồng/lít)")
        truc.set_title(
            f"Giá dầu thô thế giới và giá bán lẻ xăng dầu Việt Nam, "
            f"{the_gioi.index.min():%m/%Y} - {bang_gia.ngay_cuoi:%m/%Y}"
        )
        truc.grid(axis="y", alpha=0.3)
        hinh.legend(loc="outside lower center", ncols=2, fontsize=8, frameon=False)
        return hinh


class BieuDoBienDong(BieuDo):
    """Cot ghep: do bien dong quy nam cua gia the gioi trong tung boi canh."""

    ten_tep = "h2_bien_dong_theo_boi_canh.png"

    def __init__(self, cau_hinh: CauHinh, phep: BienDongTheoBoiCanh) -> None:
        """Tao bieu do.

        Tham so:
            cau_hinh: cau hinh cua du an.
            phep: phep phan tich do bien dong theo boi canh.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        super().__init__(cau_hinh)
        self._phep = phep

    def ve(self) -> Figure:
        """Ve moi boi canh mot nhom cot, moi chuoi gia mot cot.

        Tham so:
            Khong co.

        Tra ve:
            Hinh cot ghep, truc tung la do bien dong quy nam (%), bat dau tu 0.

        Ngoai le:
            BangRongError: khi khong chuoi nao du du lieu.
        """
        bang = self._phep.bang()
        ten_chuoi = dict(zip(bang["ma_chuoi"], bang["ten_chuoi"]))
        so_phien = bang.groupby("su_kien")["so_phien"].max()
        bang_xoay = bang.pivot(index="su_kien", columns="ma_chuoi", values="bien_dong_nam_pct")
        nhan = NhanSuKien(self._cau_hinh)
        cac_su_kien = [ma for ma in nhan.thu_tu if ma in bang_xoay.index]
        cac_chuoi = [
            str(ma) for ma in self._cau_hinh["phan_tich.chuoi_bien_dong"] if ma in bang_xoay.columns
        ]
        nhan_nhom = []
        for ma in cac_su_kien:
            ten_xuong_dong = nhan.ten(ma).replace(" (", "\n(")
            nhan_nhom.append(f"{ten_xuong_dong}\n{self.dinh_dang_so(so_phien[ma])} phiên")
        hinh, truc = self.tao_hinh()
        self.ve_cot_ghep(
            truc,
            bang_xoay.loc[cac_su_kien, cac_chuoi],
            [ten_chuoi[ma] for ma in cac_chuoi],
            nhan_nhom,
        )
        truc.set_ylim(bottom=0)
        truc.set_xlabel("Bối cảnh (số phiên giao dịch của chuỗi có nhiều phiên nhất)")
        truc.set_ylabel("Độ biến động quy năm (%)")
        truc.set_title("Độ biến động quy năm của giá xăng dầu thế giới theo bối cảnh")
        return hinh


class BieuDoCuSoc(BieuDo):
    """Cot ghep: muc thay doi gia lon nhat cua gia the gioi va gia ban le trong su kien."""

    ten_tep = "h3_cu_soc_gia_va_truyen_dan.png"

    def __init__(self, cau_hinh: CauHinh, phep: CuSocGia) -> None:
        """Tao bieu do.

        Tham so:
            cau_hinh: cau hinh cua du an.
            phep: phep phan tich cu soc gia theo su kien.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        super().__init__(cau_hinh)
        self._phep = phep

    def ve(self) -> Figure:
        """Ve moi su kien chinh mot nhom cot, moi chuoi gia mot cot.

        Tham so:
            Khong co.

        Tra ve:
            Hinh cot ghep, truc tung la muc thay doi (%) so voi ngay truoc su kien.

        Ngoai le:
            BangRongError: khi khong su kien chinh nao co du du lieu.
        """
        cau_hinh = self._cau_hinh
        bang = self._phep.bang()
        chinh = [str(ma) for ma in cau_hinh["phan_tich.su_kien_chinh"]]
        bang = bang.loc[bang["su_kien"].isin(chinh)]
        if bang.empty:
            raise BangRongError("Khong su kien chinh nao co du du lieu de ve cu soc gia.")
        ma_the_gioi = str(cau_hinh["phan_tich.chuoi_the_gioi"])
        cua_so = int(cau_hinh["phan_tich.cua_so_trung_binh_ngay"])
        ten_chuoi = dict(zip(bang["ma_chuoi"], bang["ten_chuoi"]))
        ten_chuoi[ma_the_gioi] = f"{ten_chuoi[ma_the_gioi]} (bình quân {cua_so} ngày)"
        cac_chuoi = list(dict.fromkeys(bang["ma_chuoi"]))
        bang_xoay = bang.pivot(index="su_kien", columns="ma_chuoi", values="thay_doi_pct")
        nhan = NhanSuKien(cau_hinh)
        cac_su_kien = [ma for ma in nhan.thu_tu if ma in bang_xoay.index]
        hinh, truc = self.tao_hinh()
        self.ve_cot_ghep(
            truc,
            bang_xoay.loc[cac_su_kien, cac_chuoi],
            [ten_chuoi[ma] for ma in cac_chuoi],
            [nhan.ten(ma) for ma in cac_su_kien],
        )
        truc.axhline(0, color="black", linewidth=0.8)
        truc.yaxis.set_major_formatter(FuncFormatter(self.dinh_dang_so))
        truc.set_xlabel("Sự kiện (mức thay đổi tính so với giá của ngày ngay trước sự kiện)")
        truc.set_ylabel("Thay đổi lớn nhất (%)")
        truc.set_title("Cú sốc giá trong từng sự kiện: giá thế giới và giá bán lẻ Việt Nam")
        return hinh


class BieuDoTyTrong(BieuDo):
    """Duong: ty trong gia thanh pham the gioi trong gia ban le theo tung ky dieu hanh."""

    ten_tep = "h4_ty_trong_gia_the_gioi_trong_gia_ban_le.png"

    def __init__(self, cau_hinh: CauHinh, phep: TyTrongGiaTheGioi) -> None:
        """Tao bieu do.

        Tham so:
            cau_hinh: cau hinh cua du an.
            phep: phep phan tich ty trong gia the gioi trong gia ban le.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        super().__init__(cau_hinh)
        self._phep = phep

    def ve(self) -> Figure:
        """Ve ty trong (%) theo ngay dieu hanh cho cac mat hang chinh, to nen su kien.

        Tham so:
            Khong co.

        Tra ve:
            Hinh duong, truc tung la ty trong (%), bat dau tu 0.

        Ngoai le:
            BangRongError: khi khong mat hang chinh nao co ky chung voi gia the gioi.
        """
        cau_hinh = self._cau_hinh
        theo_ky = self._phep.theo_ky()
        mat_hang = [str(ma) for ma in cau_hinh["phan_tich.mat_hang_chinh"]]
        theo_ky = theo_ky.loc[theo_ky["ban_le"].isin(mat_hang)]
        if theo_ky.empty:
            raise BangRongError("Khong mat hang chinh nao co ky chung voi gia the gioi.")
        hinh, truc = self.tao_hinh()
        for ma in mat_hang:
            chon = theo_ky.loc[theo_ky["ban_le"].eq(ma)]
            if chon.empty:
                continue
            quy_tac = cau_hinh.quy_tac_theo_ma(ma)
            truc.plot(
                chon["ngay"],
                chon["ty_trong_pct"].to_numpy(),
                marker="o",
                markersize=2.2,
                linewidth=0.7,
                color=self.mau_chuoi(ma),
                label=quy_tac.ten,
            )
        truc.axhline(
            100,
            color="black",
            linewidth=0.8,
            linestyle="--",
            label="100%: giá thế giới bằng giá bán lẻ",
        )
        self.to_nen_su_kien(truc, theo_ky["ngay"].min(), theo_ky["ngay"].max())
        cao_nhat = max(100.0, float(theo_ky["ty_trong_pct"].max()))
        truc.set_ylim(0, cao_nhat * float(cau_hinh["bieu_do.he_so_truc_tung"]))
        truc.set_xlabel("Ngày điều hành giá")
        truc.set_ylabel("Giá thành phẩm Singapore / giá bán lẻ (%)")
        truc.set_title("Tỷ trọng giá thành phẩm thế giới trong giá bán lẻ xăng dầu Việt Nam")
        truc.grid(axis="y", alpha=0.3)
        truc.legend(loc="lower right", fontsize=8, frameon=False)
        return hinh


class BieuDoGprBienDong(BieuDo):
    """Phan tan: chi so rui ro dia chinh tri va do bien dong gia the gioi theo thang."""

    ten_tep = "h5_rui_ro_dia_chinh_tri_va_bien_dong.png"

    def __init__(self, cau_hinh: CauHinh, phep: TuongQuanBoiCanh) -> None:
        """Tao bieu do.

        Tham so:
            cau_hinh: cau hinh cua du an.
            phep: phep phan tich tuong quan theo thang.

        Tra ve:
            Khong co.

        Ngoai le:
            Khong co.
        """
        super().__init__(cau_hinh)
        self._phep = phep

    def ve(self) -> Figure:
        """Ve moi thang mot diem, to mau theo loai boi canh, ghi ten cac thang bien dong nhat.

        Tham so:
            Khong co.

        Tra ve:
            Hinh phan tan, hai truc deu bat dau tu 0.

        Ngoai le:
            BangRongError: khi khong thang nao co du ca chi so GPR va do bien dong.
        """
        cau_hinh = self._cau_hinh
        thang = self._phep.theo_thang().dropna(subset=["gpr", "bien_dong_thang_pct"])
        if thang.empty:
            raise BangRongError("Khong thang nao co du chi so GPR va do bien dong de ve.")
        nhan = NhanSuKien(cau_hinh)
        loai = thang["su_kien"].map(nhan.loai)
        hinh, truc = self.tao_hinh()
        for ma_loai, ten_loai in cau_hinh["bieu_do.nhan_loai"].items():
            chon = thang.loc[loai.eq(ma_loai)]
            if chon.empty:
                continue
            truc.scatter(
                chon["gpr"].to_numpy(),
                chon["bien_dong_thang_pct"].to_numpy(),
                s=22,
                alpha=0.85,
                color=self.mau(str(ma_loai)),
                label=f"{ten_loai} ({len(chon)} tháng)",
            )
        so_ghi = int(cau_hinh["bieu_do.so_thang_ghi_nhan"])
        for moc, dong in thang.nlargest(so_ghi, "bien_dong_thang_pct").iterrows():
            truc.annotate(
                f"{moc:%m/%Y}",
                (dong["gpr"], dong["bien_dong_thang_pct"]),
                fontsize=7,
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
            )
        he_so, so_thang = self._phep.he_so_tuong_quan(
            thang["gpr"],
            thang["bien_dong_thang_pct"],
            int(cau_hinh["phan_tich.so_thang_toi_thieu_tuong_quan"]),
        )
        he_so_viet = f"{he_so:.2f}".replace(".", ",")
        truc.set_xlim(left=0)
        truc.set_ylim(bottom=0)
        truc.set_xlabel("Chỉ số rủi ro địa chính trị GPR, bình quân tháng (điểm chỉ số)")
        truc.set_ylabel("Độ biến động trong tháng, quy năm (%)")
        truc.set_title("Rủi ro địa chính trị và độ biến động của giá dầu Brent theo tháng")
        truc.grid(alpha=0.3)
        truc.legend(
            loc="upper right",
            fontsize=8,
            frameon=False,
            title=f"Hệ số tương quan r = {he_so_viet} ({so_thang} tháng)",
            title_fontsize=8,
        )
        return hinh


class BoVeBieuDo:
    """Dung toan bo bieu do cua de tai tu bang sach va luu vao mot thu muc."""

    def __init__(self, df: pd.DataFrame, cau_hinh: CauHinh) -> None:
        """Dung bang gia, cac phep phan tich va cac bieu do dung chung.

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
        bang_gia = BangGia(df, cau_hinh)
        self._cac_bieu_do: list[BieuDo] = [
            BieuDoDienBienGia(cau_hinh, bang_gia),
            BieuDoBienDong(cau_hinh, BienDongTheoBoiCanh(bang_gia, cau_hinh)),
            BieuDoCuSoc(cau_hinh, CuSocGia(bang_gia, cau_hinh)),
            BieuDoTyTrong(cau_hinh, TyTrongGiaTheGioi(bang_gia, cau_hinh)),
            BieuDoGprBienDong(cau_hinh, TuongQuanBoiCanh(bang_gia, cau_hinh)),
        ]

    def __len__(self) -> int:
        """So bieu do ma bo ve se ve.

        Tham so:
            Khong co.

        Tra ve:
            So nguyen.

        Ngoai le:
            Khong co.
        """
        return len(self._cac_bieu_do)

    def __iter__(self) -> Iterator[BieuDo]:
        """Duyet tung bieu do theo thu tu ve.

        Tham so:
            Khong co.

        Tra ve:
            Bo lap qua cac doi tuong BieuDo.

        Ngoai le:
            Khong co.
        """
        return iter(self._cac_bieu_do)

    def ve_tat_ca(self, thu_muc: Path) -> list[Path]:
        """Ve va luu tung bieu do; bieu do khong du du lieu thi bo qua va ghi nhat ky.

        Tham so:
            thu_muc: thu muc chua cac tep png.

        Tra ve:
            Danh sach duong dan cac tep png da ghi, theo thu tu bieu do.

        Ngoai le:
            BangRongError: khi khong bieu do nao ve duoc.
        """
        NHAT_KY.info("Ve %d bieu do vao thu muc '%s'", len(self), thu_muc.name)
        cac_tep = []
        for bieu_do in self:
            try:
                cac_tep.append(bieu_do.luu(thu_muc))
            except BangRongError as loi:
                NHAT_KY.warning("Bo qua %r: %s", bieu_do, loi)
                continue
            NHAT_KY.info("Da luu %r", bieu_do)
        if not cac_tep:
            raise BangRongError("Du lieu khong du de ve bat ky bieu do nao.")
        return cac_tep


def ve_bieu_do(df: pd.DataFrame, thu_muc_ra: str | Path) -> list[Path]:
    """Ve cac bieu do tra loi cau hoi va luu thanh tep png.

    Tham so:
        df: bang du lieu da lam sach.
        thu_muc_ra: thu muc chua tep hinh; ham chi ghi tep vao thu muc nay.

    Tra ve:
        Danh sach duong dan cac tep png da ghi.

    Ngoai le:
        BangRongError: khi df khong co dong nao hoac khong du du lieu de ve.
        ThieuCotError: khi df thieu cot cua luoc do bang sach.
        CotToanThieuError: khi cot gia chi chua gia tri thieu.
    """
    return BoVeBieuDo(df, CauHinh.tu_tep()).ve_tat_ca(Path(thu_muc_ra))
