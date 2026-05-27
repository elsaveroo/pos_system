# kasir/views/kasir.py
"""View untuk halaman utama kasir, simpan transaksi, dan batal transaksi."""

import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.db.models import F, Q

from ..models import (
    Kategori, Produk, Transaksi, DetailTransaksi, PengaturanToko,
)
from ._helpers import ensure_default_data


@login_required
def kasir_view(request):
    setting = PengaturanToko.get_settings()
    ensure_default_data()
    return render(request, 'kasir/kasir.html', {
        'produk_list': Produk.objects.filter(aktif=True).select_related('kategori'),
        'kategori_list': Kategori.objects.all().order_by('nama'),
        'setting': setting,
        'has_qris': bool(setting.qris_image),
    })


@login_required
@csrf_exempt
def simpan_transaksi(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'})
    try:
        d = json.loads(request.body)
        items = d.get('items', [])
        if not items:
            return JsonResponse({'ok': False, 'error': 'Keranjang kosong'})

        setting = PengaturanToko.get_settings()
        subtotal = Decimal(str(d['subtotal']))
        diskon_persen = Decimal(str(d.get('diskon_persen', 0)))
        diskon_nominal = Decimal(str(d.get('diskon_nominal', 0)))
        ppn_nominal = Decimal(str(d.get('ppn', 0)))
        total = Decimal(str(d['total']))
        jumlah_bayar = Decimal(str(d.get('jumlah_bayar', total)))
        kembalian = max(jumlah_bayar - total, Decimal('0'))

        now = timezone.now()
        seq = Transaksi.objects.filter(
            tanggal__year=now.year, tanggal__month=now.month
        ).count() + 1
        nomor = f"TRX-{now.year}-{seq:03d}"
        while Transaksi.objects.filter(nomor=nomor).exists():
            seq += 1
            nomor = f"TRX-{now.year}-{seq:03d}"

        trx = Transaksi.objects.create(
            nomor=nomor,
            kasir=request.user,
            subtotal=subtotal,
            diskon_persen=diskon_persen,
            diskon_nominal=diskon_nominal,
            ppn_persen=setting.ppn_persen,
            ppn_nominal=ppn_nominal,
            total=total,
            metode_bayar=d.get('metode_bayar', 'tunai'),
            jumlah_bayar=jumlah_bayar,
            kembalian=kembalian,
        )

        for item in items:
            p = get_object_or_404(Produk, id=item['id'])
            qty = int(item['jumlah'])
            DetailTransaksi.objects.create(
                transaksi=trx,
                produk=p,
                nama_produk=p.nama,
                kode_produk=p.kode,
                harga_satuan=p.harga_jual,
                jumlah=qty,
                subtotal=p.harga_jual * qty,
            )
            p.stok = max(p.stok - qty, 0)
            p.save(update_fields=['stok'])

        return JsonResponse({'ok': True, 'nomor': nomor, 'kembalian': int(kembalian)})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required
@csrf_exempt
def batal_transaksi(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'})
    try:
        trx = get_object_or_404(Transaksi, pk=pk)
        if trx.status == 'batal':
            return JsonResponse({'ok': False, 'error': 'Transaksi sudah dibatalkan'})
        for item in trx.items.all():
            if item.produk:
                item.produk.stok += item.jumlah
                item.produk.save(update_fields=['stok'])
        trx.status = 'batal'
        trx.save(update_fields=['status'])
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
