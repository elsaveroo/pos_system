# kasir/views/transaksi.py
"""View untuk riwayat transaksi, detail, ekspor, dan reset data."""

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from ..models import DetailTransaksi, Pengeluaran, Transaksi


@login_required
def riwayat_view(request):
    qs = Transaksi.objects.prefetch_related('items').select_related('kasir')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(nomor__icontains=q) | Q(items__nama_produk__icontains=q)
        ).distinct()

    total_penjualan = (
        Transaksi.objects.filter(status='lunas').aggregate(t=Sum('total'))['t'] or 0
    )
    total_pengeluaran = Pengeluaran.objects.aggregate(t=Sum('nominal'))['t'] or 0

    return render(request, 'kasir/riwayat.html', {
        'transaksi_list': qs[:100],
        'total_transaksi': Transaksi.objects.count(),
        'total_penjualan': total_penjualan,
        'laba': total_penjualan - total_pengeluaran,
        'search': q,
    })


@login_required
def api_detail_transaksi(request, pk):
    trx = get_object_or_404(Transaksi, pk=pk)
    return JsonResponse({
        'nomor': trx.nomor,
        'tanggal': trx.tanggal.strftime('%d/%m/%Y %H:%M'),
        'kasir': (
            trx.kasir.get_full_name() or trx.kasir.username
            if trx.kasir else '-'
        ),
        'status': trx.get_status_display(),
        'status_raw': trx.status,
        'items': [
            {
                'nama': it.nama_produk,
                'harga': int(it.harga_satuan),
                'jumlah': it.jumlah,
                'subtotal': int(it.subtotal),
            }
            for it in trx.items.all()
        ],
        'subtotal': int(trx.subtotal),
        'diskon': int(trx.diskon_nominal),
        'ppn': int(trx.ppn_nominal),
        'total': int(trx.total),
        'metode': trx.get_metode_bayar_display(),
        'jumlah_bayar': int(trx.jumlah_bayar),
        'kembalian': int(trx.kembalian),
    })


@login_required
def ekspor_transaksi(request):
    data = [
        {
            'nomor': t.nomor,
            'tanggal': t.tanggal.strftime('%d/%m/%Y %H:%M'),
            'kasir': (
                t.kasir.get_full_name() or t.kasir.username
                if t.kasir else '-'
            ),
            'subtotal': int(t.subtotal),
            'diskon': int(t.diskon_nominal),
            'ppn': int(t.ppn_nominal),
            'total': int(t.total),
            'metode': t.get_metode_bayar_display(),
            'status': t.get_status_display(),
        }
        for t in Transaksi.objects.select_related('kasir').all()
    ]
    return JsonResponse({'transaksi': data})


@login_required
@csrf_exempt
def reset_transaksi(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    if not request.user.is_superuser:
        return JsonResponse({'ok': False, 'error': 'Hanya superuser yang bisa reset data'})
    try:
        DetailTransaksi.objects.all().delete()
        Transaksi.objects.all().delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
