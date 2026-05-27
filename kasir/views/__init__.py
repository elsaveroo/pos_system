# kasir/views/__init__.py
# Re-export semua views dari modul masing-masing
# sehingga urls.py tetap bisa import dari `.views` tanpa perubahan

from .auth import login_view, logout_view
from .kasir import kasir_view, simpan_transaksi, batal_transaksi
from .produk import (
    api_produk,
    api_produk_detail,
    tambah_produk,
    edit_produk,
    hapus_produk,
    barang_stok_view,
)
from .kategori import (
    api_kategori_list,
    auto_init_kategori,
    tambah_kategori,
    edit_kategori,
    hapus_kategori,
)
from .transaksi import (
    riwayat_view,
    api_detail_transaksi,
    ekspor_transaksi,
    reset_transaksi,
)
from .laporan import laporan_view
from .pengeluaran import (
    pengeluaran_view,
    tambah_pengeluaran,
    hapus_pengeluaran,
)
from .pengaturan import (
    pengaturan_view,
    simpan_profil_toko,
    simpan_struk_pajak,
    tambah_user,
    hapus_user,
    ganti_password,
)
from .notifikasi import api_notifikasi
from .setup import setup_initial

__all__ = [
    # auth
    'login_view', 'logout_view',
    # kasir
    'kasir_view', 'simpan_transaksi', 'batal_transaksi',
    # produk
    'api_produk', 'api_produk_detail', 'tambah_produk', 'edit_produk', 'hapus_produk',
    'barang_stok_view',
    # kategori
    'api_kategori_list', 'auto_init_kategori', 'tambah_kategori', 'edit_kategori', 'hapus_kategori',
    # transaksi
    'riwayat_view', 'api_detail_transaksi', 'ekspor_transaksi', 'reset_transaksi',
    # laporan
    'laporan_view',
    # pengeluaran
    'pengeluaran_view', 'tambah_pengeluaran', 'hapus_pengeluaran',
    # pengaturan
    'pengaturan_view', 'simpan_profil_toko', 'simpan_struk_pajak',
    'tambah_user', 'hapus_user', 'ganti_password',
    # notifikasi
    'api_notifikasi',
    # setup
    'setup_initial',
]
