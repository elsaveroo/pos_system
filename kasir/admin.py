from django.contrib import admin
from .models import Kategori, Produk, Transaksi, DetailTransaksi, Pengeluaran, KategoriPengeluaran, PengaturanToko

admin.site.register(Kategori)
admin.site.register(Produk)
admin.site.register(Transaksi)
admin.site.register(DetailTransaksi)
admin.site.register(Pengeluaran)
admin.site.register(KategoriPengeluaran)
admin.site.register(PengaturanToko)
