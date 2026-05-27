# kasir/views/kategori.py
"""View untuk manajemen kategori produk."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..models import Kategori, KategoriPengeluaran, Produk
from ._helpers import ensure_default_data


@login_required
def api_kategori_list(request):
    return JsonResponse({'kategori': [
        {'id': k.id, 'nama': k.nama, 'deskripsi': k.deskripsi}
        for k in Kategori.objects.all().order_by('nama')
    ]})


@login_required
def auto_init_kategori(request):
    """Auto-create kategori produk & pengeluaran default jika belum ada."""
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
    return JsonResponse({'kategori': [
        {'id': k.id, 'nama': k.nama}
        for k in Kategori.objects.all().order_by('nama')
    ]})


@login_required
@csrf_exempt
def tambah_kategori(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    try:
        nama = request.POST.get('nama', '').strip()
        if not nama:
            return JsonResponse({'ok': False, 'error': 'Nama kategori wajib diisi'})
        if Kategori.objects.filter(nama__iexact=nama).exists():
            return JsonResponse({'ok': False, 'error': f'Kategori "{nama}" sudah ada'})
        k = Kategori.objects.create(nama=nama, deskripsi=request.POST.get('deskripsi', ''))
        return JsonResponse({'ok': True, 'id': k.id, 'nama': k.nama})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
@csrf_exempt
def edit_kategori(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    try:
        k = get_object_or_404(Kategori, pk=pk)
        nama = request.POST.get('nama', '').strip()
        if not nama:
            return JsonResponse({'ok': False, 'error': 'Nama kategori wajib diisi'})
        if Kategori.objects.filter(nama__iexact=nama).exclude(pk=pk).exists():
            return JsonResponse({'ok': False, 'error': f'Kategori "{nama}" sudah ada'})
        k.nama = nama
        k.deskripsi = request.POST.get('deskripsi', k.deskripsi)
        k.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
@csrf_exempt
def hapus_kategori(request, pk):
    if request.method == 'DELETE':
        k = get_object_or_404(Kategori, pk=pk)
        jumlah = Produk.objects.filter(kategori=k).count()
        if jumlah > 0:
            return JsonResponse({
                'ok': False,
                'error': f'Kategori ini digunakan oleh {jumlah} produk. Pindahkan produk dulu sebelum menghapus.',
            })
        k.delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})
