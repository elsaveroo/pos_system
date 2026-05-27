# kasir/views/laporan.py
"""View untuk halaman laporan penjualan dan pengeluaran."""

import json
from datetime import datetime as dt, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from ..models import Pengeluaran, PengaturanToko, Transaksi


@login_required
def laporan_view(request):
    today = timezone.now().date()

    # Filter tanggal
    dari_str = request.GET.get('dari', '')
    sampai_str = request.GET.get('sampai', '')
    try:
        dari_date = dt.strptime(dari_str, '%Y-%m-%d').date() if dari_str else None
        sampai_date = dt.strptime(sampai_str, '%Y-%m-%d').date() if sampai_str else None
    except ValueError:
        dari_date = sampai_date = None

    # Data grafik 7 hari terakhir
    labels, pend_data, peng_data = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        pend = (
            Transaksi.objects.filter(tanggal__date=d, status='lunas')
            .aggregate(t=Sum('total'))['t'] or 0
        )
        peng = (
            Pengeluaran.objects.filter(tanggal__date=d)
            .aggregate(t=Sum('nominal'))['t'] or 0
        )
        labels.append(d.strftime('%d %b'))
        pend_data.append(int(pend))
        peng_data.append(int(peng))

    # Queryset dengan filter tanggal
    trx_qs = Transaksi.objects.filter(status='lunas')
    peng_qs = Pengeluaran.objects.all()
    if dari_date:
        trx_qs = trx_qs.filter(tanggal__date__gte=dari_date)
        peng_qs = peng_qs.filter(tanggal__date__gte=dari_date)
    if sampai_date:
        trx_qs = trx_qs.filter(tanggal__date__lte=sampai_date)
        peng_qs = peng_qs.filter(tanggal__date__lte=sampai_date)

    metode = {m: trx_qs.filter(metode_bayar=m).count() for m in ['tunai', 'qris', 'debit']}
    total_pend = trx_qs.aggregate(t=Sum('total'))['t'] or 0
    total_peng = peng_qs.aggregate(t=Sum('nominal'))['t'] or 0

    return render(request, 'kasir/laporan.html', {
        'total_transaksi': trx_qs.count(),
        'total_pendapatan': total_pend,
        'total_pengeluaran': total_peng,
        'laba_kotor': total_pend - total_peng,
        'chart_labels': json.dumps(labels),
        'chart_pendapatan': json.dumps(pend_data),
        'chart_pengeluaran': json.dumps(peng_data),
        'metode_tunai': metode['tunai'],
        'metode_qris': metode['qris'],
        'metode_debit': metode['debit'],
        'total_trx_count': sum(metode.values()),
        'filter_dari': dari_str,
        'filter_sampai': sampai_str,
        'setting': PengaturanToko.get_settings(),
        'transaksi_terbaru': (
            Transaksi.objects.select_related('kasir').order_by('-tanggal')[:20]
        ),
    })
