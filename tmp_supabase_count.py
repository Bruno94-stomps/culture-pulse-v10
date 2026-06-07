from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
if not url or not key:
    raise SystemExit('Missing SUPABASE_URL or SUPABASE_SERVICE_KEY')
client = create_client(url, key)

from datetime import datetime, timedelta

names = ['signals_public', 'signals_pro', 'signals_executive', 'cultural_signals', 'signal_labels']
for name in names:
    try:
        res = client.table(name).select('*', count='exact', head=True).execute()
        print(name, 'count=', getattr(res, 'count', None), 'data_len=', len(res.data or []), 'error=', getattr(res, 'error', None))
        if name == 'signals_public':
            print('  sample rows:', res.data or [])
    except Exception as exc:
        print(name, 'error=', type(exc).__name__, str(exc))

print('\n=== cultural_signals time slices ===')
now = datetime.utcnow()
for delta, label in [(1, '24h'), (90, '90d'), (365, '365d')]:
    cutoff = now - timedelta(days=delta)
    try:
        res = client.table('cultural_signals').select('id', count='exact', head=True).gte('ts', cutoff.isoformat() + 'Z').execute()
        print(f'cultural_signals last {label}:', getattr(res, 'count', None), 'rows=', len(res.data or []))
    except Exception as exc:
        print(f'cultural_signals last {label} error=', type(exc).__name__, str(exc))

print('\n=== signals_public / signals_pro / signals_executive sample rows ===')
for name in ['signals_public', 'signals_pro', 'signals_executive']:
    try:
        sample = client.table(name).select('*').limit(3).execute()
        print(name, 'sample len=', len(sample.data or []))
        for row in sample.data or []:
            print(' ', row)
    except Exception as exc:
        print(name, 'sample error=', type(exc).__name__, str(exc))
