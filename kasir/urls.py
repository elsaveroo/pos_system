from django.urls import path
from . import views

urlpatterns = [
    path('', views.kasir_view, name='kasir'),
    path('login/', views.login_view, name='login'),
    path('setup/', views.setup_initial, name='setup_initial'),  # first-run setup
    path('logout/', views.logout_view, name='logout'),

    # API kategori produk
    path('api/kategori/', views.api_kategori_list, name='api_kategori'),
    path('api/kategori/init/', views.auto_init_kategori, name='auto_init_kategori'),
    path('api/kategori/tambah/', views.tambah_kategori, name='tambah_kategori'),
    path('api/kategori/edit/<int:pk>/', views.edit_kategori, name='edit_kategori'),
    path('api/kategori/hapus/<int:pk>/', views.hapus_kategori, name='hapus_kategori'),

    # API produk — urutan penting: path statis sebelum <int:pk>
    path('api/produk/', views.api_produk, name='api_produk'),
    path('api/produk/tambah/', views.tambah_produk, name='tambah_produk'),
    path('api/produk/<int:pk>/', views.api_produk_detail, name='api_produk_detail'),
    path('api/produk/edit/<int:pk>/', views.edit_produk, name='edit_produk'),
    path('api/produk/hapus/<int:pk>/', views.hapus_produk, name='hapus_produk'),

    # API transaksi
    path('api/transaksi/simpan/', views.simpan_transaksi, name='simpan_transaksi'),
    path('api/transaksi/<int:pk>/', views.api_detail_transaksi, name='api_detail_transaksi'),
    path('api/transaksi/batal/<int:pk>/', views.batal_transaksi, name='batal_transaksi'),

    # API pengeluaran
    path('api/pengeluaran/tambah/', views.tambah_pengeluaran, name='tambah_pengeluaran'),
    path('api/pengeluaran/hapus/<int:pk>/', views.hapus_pengeluaran, name='hapus_pengeluaran'),

    # API user
    path('api/user/hapus/<int:pk>/', views.hapus_user, name='hapus_user'),
    path('api/notifikasi/', views.api_notifikasi, name='api_notifikasi'),
    path('api/user/ganti-password/<int:pk>/', views.ganti_password, name='ganti_password'),
    path('api/ekspor/transaksi/', views.ekspor_transaksi, name='ekspor_transaksi'),
    path('api/reset-transaksi/', views.reset_transaksi, name='reset_transaksi'),

    # Pages
    path('riwayat/', views.riwayat_view, name='riwayat'),
    path('laporan/', views.laporan_view, name='laporan'),
    path('pengeluaran/', views.pengeluaran_view, name='pengeluaran'),
    path('barang-stok/', views.barang_stok_view, name='barang_stok'),
    path('pengaturan/', views.pengaturan_view, name='pengaturan'),
    path('pengaturan/profil/simpan/', views.simpan_profil_toko, name='simpan_profil'),
    path('pengaturan/struk/simpan/', views.simpan_struk_pajak, name='simpan_struk'),
    path('pengaturan/user/tambah/', views.tambah_user, name='tambah_user'),
]
