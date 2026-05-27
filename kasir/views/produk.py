# kasir/views/produk.py
"""View untuk manajemen produk: list, tambah, edit, hapus, dan detail."""

from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from ..models import Kategori, Produk
from ._helpers import ensure_default_data


@login_required
def api_produk(request):
    if request.GET.get('all'):
        qs = Produk.objects.select_related('kategori').all()
    else:
        qs = Produk.objects.filter(aktif=True).select_related('kategori')

    kat = request.GET.get('kategori')
    q = request.GET.get('q', '')
    if kat:
        qs = qs.filter(kategori_id=kat)
    if q:
        qs = qs.filter(Q(nama__icontains=q) | Q(kode__icontains=q))

    return JsonResponse({'produk': [
        {
            'id': p.id,
            'kode': p.kode,
            'nama': p.nama,
            'kategori': p.kategori.nama if p.kategori else '',
            'satuan': p.satuan,
            'harga_beli': int(p.harga_beli),
            'harga': int(p.harga_jual),
            'stok': p.stok,
            'stok_min': p.stok_minimum,
            'gambar': p.gambar.url if p.gambar else None,
            'stok_rendah': p.stok <= p.stok_minimum,
        }
        for p in qs
    ]})


@login_required
def api_produk_detail(request, pk):
    p = get_object_or_404(Produk, pk=pk)
    return JsonResponse({
        'id': p.id,
        'kode': p.kode,
        'barcode': p.barcode,
        'nama': p.nama,
        'deskripsi': p.deskripsi,
        'kategori_id': p.kategori_id,
        'satuan': p.satuan,
        'harga_beli': int(p.harga_beli),
        'harga_jual': int(p.harga_jual),
        'stok': p.stok,
        'stok_minimum': p.stok_minimum,
        'aktif': p.aktif,
        'gambar': p.gambar.url if p.gambar else None,
    })


@login_required
@csrf_exempt
def tambah_produk(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    try:
        kode = request.POST.get('kode', '').strip()
        if Produk.objects.filter(kode=kode).exists():
            return JsonResponse({'ok': False, 'error': f'Kode {kode} sudah digunakan'})

        kat_id = request.POST.get('kategori')
        Produk.objects.create(
            nama=request.POST.get('nama', '').strip(),
            kode=kode,
            barcode=request.POST.get('barcode', '').strip(),
            deskripsi=request.POST.get('deskripsi', ''),
            kategori=get_object_or_404(Kategori, id=kat_id) if kat_id else None,
            satuan=request.POST.get('satuan', 'pcs'),
            harga_beli=int(request.POST.get('harga_beli', '0').replace('.', '') or 0),
            harga_jual=int(request.POST.get('harga_jual', '0').replace('.', '') or 0),
            stok=int(request.POST.get('stok', '0') or 0),
            stok_minimum=int(request.POST.get('stok_minimum', '20') or 20),
            aktif=request.POST.get('aktif') == 'on',
            gambar=request.FILES.get('gambar'),
        )
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
@csrf_exempt
def edit_produk(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'})
    try:
        p = get_object_or_404(Produk, pk=pk)
        kode = request.POST.get('kode', '').strip()
        if kode and Produk.objects.filter(kode=kode).exclude(pk=pk).exists():
            return JsonResponse({'ok': False, 'error': f'Kode {kode} sudah digunakan produk lain'})

        kat_id = request.POST.get('kategori', '').strip()
        p.nama = request.POST.get('nama', p.nama).strip() or p.nama
        if kode:
            p.kode = kode
        p.barcode = request.POST.get('barcode', p.barcode)
        p.deskripsi = request.POST.get('deskripsi', p.deskripsi)

        if 'kategori' in request.POST:
            p.kategori = get_object_or_404(Kategori, id=kat_id) if kat_id else None

        p.satuan = request.POST.get('satuan', p.satuan)

        hb = request.POST.get('harga_beli', '').replace('.', '').replace(',', '')
        hj = request.POST.get('harga_jual', '').replace('.', '').replace(',', '')
        if hb:
            p.harga_beli = int(hb)
        if hj:
            p.harga_jual = int(hj)

        st = request.POST.get('stok', '')
        sm = request.POST.get('stok_minimum', '')
        if st:
            p.stok = int(st)
        if sm:
            p.stok_minimum = int(sm)

        aktif_val = request.POST.get('aktif')
        if aktif_val is not None:
            p.aktif = aktif_val == 'on'

        if request.FILES.get('gambar'):
            p.gambar = request.FILES['gambar']

        p.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
@csrf_exempt
def hapus_produk(request, pk):
    if request.method == 'DELETE':
        get_object_or_404(Produk, pk=pk).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})


@login_required
def barang_stok_view(request):
    ensure_default_data()
    qs = Produk.objects.select_related('kategori').all()

    q = request.GET.get('q', '')
    kat = request.GET.get('kategori', '')
    if q:
        qs = qs.filter(Q(nama__icontains=q) | Q(kode__icontains=q))
    if kat:
        qs = qs.filter(kategori_id=kat)

    stok_rendah = Produk.objects.filter(
        aktif=True, stok_minimum__gt=0, stok__lte=F('stok_minimum')
    ).count()

    return render(request, 'kasir/barang_stok.html', {
        'produk_list': qs,
        'kategori_list': Kategori.objects.all().order_by('nama'),
        'stok_rendah_count': stok_rendah,
        'search': q,
        'kat_filter': kat,
        'total_produk': qs.count(),
    })
