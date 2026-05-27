# kasir/views/_helpers.py
"""Fungsi utilitas yang digunakan bersama oleh beberapa view."""

from ..models import Kategori, KategoriPengeluaran, PengaturanToko


def ensure_default_data():
    """Pastikan kategori produk & pengeluaran default sudah ada di DB."""
    if Kategori.objects.count() == 0:
        for nama in ['Makanan', 'Minuman', 'Lainnya']:
            Kategori.objects.get_or_create(nama=nama)
    if KategoriPengeluaran.objects.count() == 0:
        for nama, warna in [
            ('Operasional', 'blue'),
            ('Bahan Baku', 'orange'),
            ('Gaji', 'green'),
            ('Lainnya', 'purple'),
        ]:
            KategoriPengeluaran.objects.get_or_create(nama=nama, defaults={'warna': warna})
    PengaturanToko.get_settings()
