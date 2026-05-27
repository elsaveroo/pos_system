# kasir/views/pengaturan.py
"""View untuk pengaturan toko dan manajemen pengguna."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..models import PengaturanToko


@login_required
def pengaturan_view(request):
    return render(request, 'kasir/pengaturan.html', {
        'setting': PengaturanToko.get_settings(),
        'users': User.objects.all(),
        'tab': request.GET.get('tab', 'profil'),
    })


@login_required
@require_POST
def simpan_profil_toko(request):
    s = PengaturanToko.get_settings()
    s.nama_toko = request.POST.get('nama_toko', s.nama_toko)
    s.alamat = request.POST.get('alamat', s.alamat)
    s.telepon = request.POST.get('telepon', s.telepon)
    s.whatsapp = request.POST.get('whatsapp', s.whatsapp)
    s.npwp = request.POST.get('npwp', s.npwp)
    if request.FILES.get('logo'):
        s.logo = request.FILES['logo']
    if request.FILES.get('qris_image'):
        s.qris_image = request.FILES['qris_image']
    s.save()
    messages.success(request, 'Profil toko berhasil disimpan.')
    return redirect('/pengaturan/?tab=profil')


@login_required
@require_POST
def simpan_struk_pajak(request):
    s = PengaturanToko.get_settings()
    s.ppn_aktif = 'ppn_aktif' in request.POST
    s.diskon_maksimal = request.POST.get('diskon_maksimal', s.diskon_maksimal)
    s.pembulatan = request.POST.get('pembulatan', s.pembulatan)
    s.format_nomor_transaksi = request.POST.get('format_nomor', s.format_nomor_transaksi)
    s.reset_nomor = request.POST.get('reset_nomor', s.reset_nomor)
    s.ukuran_kertas = request.POST.get('ukuran_kertas', s.ukuran_kertas)
    s.margin_printer = int(request.POST.get('margin_printer', 5) or 5)
    s.cetak_otomatis = 'cetak_otomatis' in request.POST
    s.catatan_struk = request.POST.get('catatan_struk', s.catatan_struk)
    s.save()
    messages.success(request, 'Pengaturan berhasil disimpan.')
    return redirect('/pengaturan/?tab=struk')


@login_required
@require_POST
def tambah_user(request):
    username = request.POST.get('username', '').strip()
    full_name = request.POST.get('full_name', '').strip()
    password = request.POST.get('password', '')

    if User.objects.filter(username=username).exists():
        messages.error(request, f'Username {username} sudah digunakan.')
    else:
        u = User.objects.create_user(username=username, password=password)
        parts = full_name.split(' ', 1)
        u.first_name = parts[0]
        u.last_name = parts[1] if len(parts) > 1 else ''
        u.is_staff = request.POST.get('is_staff') == 'on'
        u.save()
        messages.success(request, f'User {username} berhasil ditambahkan.')
    return redirect('/pengaturan/?tab=pengguna')


@login_required
@csrf_exempt
def hapus_user(request, pk):
    if request.method == 'DELETE':
        if request.user.pk == int(pk):
            return JsonResponse({'ok': False, 'error': 'Tidak bisa menghapus diri sendiri'})
        get_object_or_404(User, pk=pk).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})


@login_required
@csrf_exempt
def ganti_password(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    if not request.user.is_staff:
        return JsonResponse({'ok': False, 'error': 'Akses ditolak'})
    try:
        u = get_object_or_404(User, pk=pk)
        pw = request.POST.get('password', '').strip()
        if not pw or len(pw) < 4:
            return JsonResponse({'ok': False, 'error': 'Password minimal 4 karakter'})
        u.set_password(pw)
        u.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
