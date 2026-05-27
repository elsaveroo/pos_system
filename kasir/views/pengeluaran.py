# kasir/views/pengeluaran.py
"""View untuk manajemen pengeluaran toko."""

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ..models import KategoriPengeluaran, Pengeluaran
from ._helpers import ensure_default_data


@login_required
def pengeluaran_view(request):
    ensure_default_data()
    qs = Pengeluaran.objects.select_related('kategori', 'dicatat_oleh').all()

    q = request.GET.get('q', '')
    kat = request.GET.get('kategori', '')
    tgl_dari = request.GET.get('tgl_dari', '')
    tgl_sampai = request.GET.get('tgl_sampai', '')

    if q:
        qs = qs.filter(deskripsi__icontains=q)
    if kat:
        qs = qs.filter(kategori_id=kat)
    if tgl_dari:
        qs = qs.filter(tanggal__date__gte=tgl_dari)
    if tgl_sampai:
        qs = qs.filter(tanggal__date__lte=tgl_sampai)

    total = qs.aggregate(t=Sum('nominal'))['t'] or 0

    return render(request, 'kasir/pengeluaran.html', {
        'pengeluaran_list': qs,
        'total': total,
        'jumlah': qs.count(),
        'kategori_list': KategoriPengeluaran.objects.all(),
        'search': q,
        'kat_filter': kat,
        'tgl_dari': tgl_dari,
        'tgl_sampai': tgl_sampai,
    })


@login_required
@csrf_exempt
def tambah_pengeluaran(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    try:
        tanggal_str = request.POST.get('tanggal')
        tanggal = (
            datetime.strptime(tanggal_str, '%Y-%m-%d')
            if tanggal_str else timezone.now()
        )
        kat_id = request.POST.get('kategori')
        nominal_str = request.POST.get('nominal', '0').replace('.', '').replace(',', '')
        Pengeluaran.objects.create(
            tanggal=tanggal,
            kategori=get_object_or_404(KategoriPengeluaran, id=kat_id) if kat_id else None,
            deskripsi=request.POST.get('deskripsi', ''),
            nominal=int(nominal_str or 0),
            lampiran=request.FILES.get('lampiran'),
            dicatat_oleh=request.user,
        )
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
@csrf_exempt
def hapus_pengeluaran(request, pk):
    if request.method == 'DELETE':
        get_object_or_404(Pengeluaran, pk=pk).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False})
