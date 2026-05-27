#!/usr/bin/env python3
"""
Script setup otomatis untuk POS System.
Jalankan: python setup.py
"""
import subprocess, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))

def run(cmd, **kw):
    print(f'  $ {cmd}')
    r = subprocess.run(cmd, shell=True, cwd=BASE, **kw)
    return r.returncode == 0

print('\n🔧  POS System — Setup Otomatis')
print('=' * 40)

# 1. Install deps
print('\n[1/4] Install dependencies...')
run('pip install django pillow --break-system-packages -q', capture_output=False)

# 2. Migrate
print('\n[2/4] Migrasi database...')
run('python manage.py migrate', capture_output=False)

# 3. Seed
print('\n[3/4] Mengisi data awal...')
run('python manage.py shell < seed_data.py', capture_output=False)

# 4. Collectstatic (opsional)
print('\n[4/4] Selesai!')
print('\n' + '=' * 40)
print('Jalankan server:')
print('  python manage.py runserver')
print('\nBuka browser:')
print('  http://127.0.0.1:8000')
print('\nLogin:')
print('  Admin : admin / admin123')
print('  Kasir : kasir1 / kasir123')
print('=' * 40 + '\n')
