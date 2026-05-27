"""
Jalankan dengan: python manage.py shell < seed_data.py
ATAU: python manage.py runscript seed_data  (jika django-extensions terpasang)
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from kasir.models import (Kategori, Produk, KategoriPengeluaran,
                          PengaturanToko)
from django.core.files.base import ContentFile
import io, struct, zlib

# ── Buat PNG 80×80 warna solid ──────────────────────────────────────────────
def make_png(hex_color, text_lines=None):
    """Buat PNG 80x80 warna solid tanpa library eksternal."""
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    W, H = 80, 80
    raw = b''
    for y in range(H):
        row = b'\x00'
        for x in range(W):
            # Lingkaran kecil di tengah lebih terang
            dist = ((x - W//2)**2 + (y - H//2)**2) ** 0.5
            if dist < 22:
                fr = min(255, r + 60)
                fg = min(255, g + 60)
                fb = min(255, b + 60)
                row += bytes([fr, fg, fb])
            else:
                row += bytes([r, g, b])
        raw += row
    def crc(data):
        return struct.pack('>I', zlib.crc32(data) & 0xffffffff)
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + crc(t + d)
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    idat = chunk(b'IDAT', zlib.compress(raw))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            idat + chunk(b'IEND', b''))


# ── Superuser ────────────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', '', 'admin123')
    u.first_name = 'Admin'; u.last_name = 'Toko'; u.save()
    print('✓ Superuser  admin / admin123')
else:
    print('- Superuser sudah ada')

# ── Kasir ────────────────────────────────────────────────────────────────────
if not User.objects.filter(username='kasir1').exists():
    u = User.objects.create_user('kasir1', '', 'kasir123')
    u.first_name = 'Budi'; u.last_name = 'Santoso'; u.save()
    print('✓ User kasir1 / kasir123')

# ── Pengaturan toko ──────────────────────────────────────────────────────────
s = PengaturanToko.get_settings()
s.nama_toko = 'Toko Sumber Rezeki'
s.alamat = 'Jl. Raya No. 123, Batam'
s.telepon = '0778-123456'
s.whatsapp = '08123456789'
s.save()
print('✓ Pengaturan toko')

# ── Kategori produk ──────────────────────────────────────────────────────────
cats = ['Minuman', 'Makanan', 'Snack', 'Rokok', 'Sembako']
cat_objs = {}
for nama in cats:
    obj, _ = Kategori.objects.get_or_create(nama=nama)
    cat_objs[nama] = obj
print(f'✓ {len(cats)} kategori produk')

# ── Kategori pengeluaran ─────────────────────────────────────────────────────
peng_cats = [
    ('Operasional', 'blue'), ('Belanja Stok', 'green'),
    ('Gaji', 'purple'), ('Listrik & Air', 'orange'), ('Lainnya', 'gray'),
]
for nama, warna in peng_cats:
    KategoriPengeluaran.objects.get_or_create(nama=nama, defaults={'warna': warna if warna != 'gray' else 'blue'})
print(f'✓ {len(peng_cats)} kategori pengeluaran')

# ── Produk dengan gambar PNG ──────────────────────────────────────────────────
products = [
    # (kode, nama, kategori, harga_beli, harga_jual, stok, stok_min, satuan, warna_hex)
    ('MNM-001', 'Aqua Botol 600ml',       'Minuman', 2500,  4000,  120, 20, 'botol', '3B82F6'),
    ('MNM-002', 'Teh Botol Sosro 450ml',  'Minuman', 4000,  6000,   80, 15, 'botol', '10B981'),
    ('MNM-003', 'Coca-Cola 330ml',        'Minuman', 5500,  8000,   60, 10, 'botol', 'EF4444'),
    ('MNM-004', 'Sprite 330ml',           'Minuman', 5500,  8000,   55, 10, 'botol', '34D399'),
    ('MNM-005', 'Kopi Kapal Api Sachet',  'Minuman', 1500,  2500,  200, 30, 'pcs',  '92400E'),
    ('MNM-006', 'Susu Ultra Milk 250ml',  'Minuman', 4500,  6500,   70, 15, 'pcs',  'FCD34D'),
    ('MKN-001', 'Indomie Goreng',         'Makanan', 2800,  4000,  150, 30, 'pcs',  'F59E0B'),
    ('MKN-002', 'Indomie Kuah Ayam Bwng', 'Makanan', 2800,  4000,  150, 30, 'pcs',  'FB923C'),
    ('MKN-003', 'Pop Mie Ayam 75g',       'Makanan', 4500,  6500,  100, 20, 'pcs',  'FBBF24'),
    ('MKN-004', 'Bihun Jagung Rose',      'Makanan', 3000,  4500,   80, 15, 'pack', 'A3E635'),
    ('SNK-001', 'Chitato Sapi Panggang',  'Snack',   7000, 10000,   50, 10, 'pcs',  'C084FC'),
    ('SNK-002', 'Oreo Original',          'Snack',   7500, 11000,   60, 12, 'pcs',  '818CF8'),
    ('SNK-003', 'Malkist Abon',           'Snack',   4000,  6000,   80, 15, 'pcs',  'F472B6'),
    ('SNK-004', 'Taro Net Original 65g',  'Snack',   6000,  9000,   45, 10, 'pcs',  'FB7185'),
    ('RKK-001', 'Rokok Sampoerna Mild 16','Rokok',  21000, 24000,  100, 20, 'pack', '374151'),
    ('RKK-002', 'Rokok Gudang Garam Merah','Rokok', 19000, 22000,   80, 15, 'pack', '7F1D1D'),
    ('SMB-001', 'Gula Pasir 1kg',         'Sembako', 13500, 16000,  50, 10, 'kg',   'FDE68A'),
    ('SMB-002', 'Minyak Goreng Filma 1L', 'Sembako', 17000, 20000,  40,  8, 'liter','FCA5A5'),
    ('SMB-003', 'Beras Premium 5kg',      'Sembako', 70000, 80000,  20,  5, 'kg',   'D1FAE5'),
    ('SMB-004', 'Telur Ayam 1kg',         'Sembako', 24000, 28000,  30,  5, 'kg',   'FEF3C7'),
]

created = 0
for kode, nama, kat_nama, hb, hj, stok, stok_min, satuan, warna in products:
    if Produk.objects.filter(kode=kode).exists():
        continue
    png_bytes = make_png(warna)
    p = Produk(
        kode=kode, nama=nama,
        kategori=cat_objs[kat_nama],
        harga_beli=hb, harga_jual=hj,
        stok=stok, stok_minimum=stok_min,
        satuan=satuan, aktif=True,
    )
    fname = f"{kode.lower().replace('-','_')}.png"
    p.gambar.save(fname, ContentFile(png_bytes), save=False)
    p.save()
    created += 1

print(f'✓ {created} produk ditambahkan ({Produk.objects.count()} total)')
print()
print('=' * 45)
print('SELESAI! Jalankan server dengan:')
print('  python manage.py runserver')
print()
print('Login:')
print('  Admin  → admin / admin123')
print('  Kasir  → kasir1 / kasir123')
print('=' * 45)
