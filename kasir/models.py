from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PengaturanToko(models.Model):
    nama_toko = models.CharField(max_length=200, default='Toko Sumber Rezeki')
    alamat = models.TextField(blank=True)
    telepon = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    npwp = models.CharField(max_length=30, blank=True)
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)
    qris_image = models.ImageField(upload_to='qris/', null=True, blank=True,
        help_text='Upload gambar QR code QRIS untuk ditampilkan saat pembayaran')
    # Struk & Pajak
    ppn_aktif = models.BooleanField(default=True)
    ppn_persen = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    diskon_maksimal = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    pembulatan = models.CharField(max_length=20, default='none',
        choices=[('none','Tidak ada'),('up','Ke atas'),('down','Ke bawah')])
    format_nomor_transaksi = models.CharField(max_length=50, default='TRX-YYYY-{seq}')
    reset_nomor = models.CharField(max_length=10, default='bulan',
        choices=[('hari','Setiap hari'),('bulan','Setiap bulan'),('tahun','Setiap tahun'),('tidak','Tidak reset')])
    ukuran_kertas = models.CharField(max_length=20, default='thermal58',
        choices=[('thermal58','Thermal 58mm'),('thermal80','Thermal 80mm'),('thermal88','Thermal 88mm'),('a4','A4')])
    margin_printer = models.IntegerField(default=5)
    cetak_otomatis = models.BooleanField(default=True)
    catatan_struk = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Pengaturan Toko'

    def __str__(self):
        return self.nama_toko

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Kategori(models.Model):
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField(blank=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = 'Kategori'


class Produk(models.Model):
    SATUAN_CHOICES = [
        ('pcs', 'Pcs'), ('botol', 'Botol'), ('cup', 'Cup'),
        ('kg', 'Kg'), ('gram', 'Gram'), ('liter', 'Liter'),
        ('porsi', 'Porsi'), ('pack', 'Pack'),
    ]
    kode = models.CharField(max_length=30, unique=True)
    barcode = models.CharField(max_length=50, blank=True)
    nama = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True)
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True)
    satuan = models.CharField(max_length=10, choices=SATUAN_CHOICES, default='pcs')
    harga_beli = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    harga_jual = models.DecimalField(max_digits=12, decimal_places=0)
    stok = models.IntegerField(default=0)
    stok_minimum = models.IntegerField(default=0)
    gambar = models.ImageField(upload_to='produk/', null=True, blank=True)
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

    @property
    def stok_rendah(self):
        return self.stok <= max(self.stok_minimum, 5)

    class Meta:
        verbose_name_plural = 'Produk'
        ordering = ['nama']


class Transaksi(models.Model):
    METODE_CHOICES = [('tunai','Tunai'),('qris','QRIS'),('debit','Debit')]
    STATUS_CHOICES = [('lunas','Lunas'),('batal','Dibatalkan')]

    nomor = models.CharField(max_length=50, unique=True)
    kasir = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    diskon_persen = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    diskon_nominal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    ppn_persen = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ppn_nominal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    metode_bayar = models.CharField(max_length=10, choices=METODE_CHOICES, default='tunai')
    jumlah_bayar = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    kembalian = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='lunas')
    catatan = models.TextField(blank=True)
    tanggal = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nomor

    class Meta:
        verbose_name_plural = 'Transaksi'
        ordering = ['-tanggal']


class DetailTransaksi(models.Model):
    transaksi = models.ForeignKey(Transaksi, on_delete=models.CASCADE, related_name='items')
    produk = models.ForeignKey(Produk, on_delete=models.SET_NULL, null=True)
    nama_produk = models.CharField(max_length=200)
    kode_produk = models.CharField(max_length=30)
    harga_satuan = models.DecimalField(max_digits=12, decimal_places=0)
    jumlah = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.transaksi.nomor} - {self.nama_produk}"


class KategoriPengeluaran(models.Model):
    WARNA_CHOICES = [
        ('orange','Orange'),('green','Hijau'),('purple','Ungu'),
        ('blue','Biru'),('red','Merah'),('yellow','Kuning'),
    ]
    nama = models.CharField(max_length=100)
    warna = models.CharField(max_length=10, choices=WARNA_CHOICES, default='blue')

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = 'Kategori Pengeluaran'


class Pengeluaran(models.Model):
    kategori = models.ForeignKey(KategoriPengeluaran, on_delete=models.SET_NULL, null=True)
    deskripsi = models.CharField(max_length=300)
    nominal = models.DecimalField(max_digits=12, decimal_places=0)
    tanggal = models.DateTimeField(default=timezone.now)
    lampiran = models.FileField(upload_to='pengeluaran/', null=True, blank=True)
    dicatat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.deskripsi

    class Meta:
        verbose_name_plural = 'Pengeluaran'
        ordering = ['-tanggal']
