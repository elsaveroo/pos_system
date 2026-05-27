# kasir/views/setup.py
"""View untuk setup awal aplikasi (first-run). Tidak memerlukan autentikasi."""

from django.contrib.auth.models import User
from django.http import JsonResponse

from ..models import Kategori, KategoriPengeluaran, PengaturanToko


def setup_initial(request):
    """Dipanggil sekali saat pertama kali dijalankan untuk membuat superuser + data default."""
    created = []

    if not User.objects.filter(is_superuser=True).exists():
        u = User.objects.create_superuser('admin', '', 'admin123')
        u.first_name = 'Admin'
        u.last_name = 'Toko'
        u.save()
        created.append('superuser admin/admin123')

    if Kategori.objects.count() == 0:
        for nama in ['Makanan', 'Minuman', 'Lainnya']:
            Kategori.objects.get_or_create(nama=nama)
        created.append('3 kategori produk')

    if KategoriPengeluaran.objects.count() == 0:
        for nama, warna in [
            ('Operasional', 'blue'),
            ('Bahan Baku', 'orange'),
            ('Gaji', 'green'),
            ('Lainnya', 'purple'),
        ]:
            KategoriPengeluaran.objects.get_or_create(nama=nama, defaults={'warna': warna})
        created.append('4 kategori pengeluaran')

    PengaturanToko.get_settings()  # pastikan baris settings ada

    msg = 'Setup selesai: ' + ', '.join(created) if created else 'Sudah pernah di-setup sebelumnya.'
    return JsonResponse({'ok': True, 'msg': msg, 'created': created})
