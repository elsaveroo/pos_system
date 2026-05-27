# kasir/views/auth.py
"""View untuk autentikasi: login dan logout."""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from ..models import Kategori, KategoriPengeluaran, PengaturanToko


def login_view(request):
    if request.user.is_authenticated:
        return redirect('kasir')

    # Auto-setup: buat admin + data default jika pertama kali dijalankan
    if not User.objects.filter(is_superuser=True).exists():
        u = User.objects.create_superuser('admin', '', 'admin123')
        u.first_name = 'Admin'
        u.last_name = 'Toko'
        u.save()

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

    error = None
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', ''),
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'kasir'))
        error = 'Username atau password salah.'

    return render(request, 'kasir/login.html', {
        'error': error,
        'setting': PengaturanToko.get_settings(),
    })


def logout_view(request):
    logout(request)
    return redirect('login')
