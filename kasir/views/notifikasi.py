# kasir/views/notifikasi.py
"""View untuk API notifikasi: stok rendah/habis dan ringkasan transaksi hari ini."""

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import JsonResponse
from django.utils import timezone

from ..models import Produk, Transaksi


@login_required
def api_notifikasi(request):
    notifs = []
    today = timezone.now().date()

    # Stok habis
    for p in Produk.objects.filter(aktif=True, stok=0, stok_minimum__gt=0).order_by('nama')[:10]:
        notifs.append({
            'id': f'habis_{p.id}',
            'type': 'error',
            'msg': f'⛔ {p.nama} — STOK HABIS',
            'time': 'Segera restok',
        })

    # Stok rendah
    produk_rendah = Produk.objects.filter(
        aktif=True, stok__gt=0, stok_minimum__gt=0,
        stok__lte=F('stok_minimum'),
    ).order_by('stok')[:10]
    for p in produk_rendah:
        notifs.append({
            'id': f'rendah_{p.id}',
            'type': 'warning',
            'msg': f'⚠️ {p.nama} — sisa {p.stok} {p.satuan} (min. {p.stok_minimum})',
            'time': 'Stok rendah',
        })

    # Ringkasan transaksi hari ini
    trx_hari = Transaksi.objects.filter(tanggal__date=today, status='lunas').count()
    pend_hari = (
        Transaksi.objects.filter(tanggal__date=today, status='lunas')
        .aggregate(t=Sum('total'))['t'] or 0
    )
    if trx_hari > 0:
        notifs.insert(0, {
            'id': f'trx_{today}',
            'type': 'success',
            'msg': f'✅ Hari ini: {trx_hari} transaksi — Rp {int(pend_hari):,}'.replace(',', '.'),
            'time': 'Hari ini',
        })

    # Jika tidak ada notifikasi penting
    if not notifs:
        total_produk = Produk.objects.filter(aktif=True).count()
        if total_produk == 0:
            notifs.append({
                'id': 'no_produk',
                'type': 'info',
                'msg': 'Belum ada produk. Tambahkan produk di menu Barang & Stok.',
                'time': '',
            })
        else:
            notifs.append({
                'id': 'aman',
                'type': 'info',
                'msg': f'✅ Semua {total_produk} produk stok aman',
                'time': '',
            })

    return JsonResponse({'notif': notifs})
