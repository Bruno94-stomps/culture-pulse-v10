from dotenv import load_dotenv
import os
from supabase import create_client
from pprint import pprint

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
print('SUPABASE_URL', url)
print('SERVICE_KEY present', bool(key))
if not url or not key:
    raise SystemExit('Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env')
client = create_client(url, key)

for table in ['cultural_signals', 'projects', 'profiles', 'brand_profiles', 'learned_weights', 'model_weights', 'analysis_performance', 'signal_feedback', 'collected_data', 'discovered_patterns']:
    try:
        res = client.table(table).select('id').limit(1).execute()
        data = getattr(res, 'data', None)
        err = getattr(res, 'error', None)
        if err:
            print(table, {'exists': False, 'error': err})
        elif data is None:
            print(table, {'exists': False, 'data': None})
        else:
            print(table, {'exists': True, 'sample_rows': len(data), 'data': data})
    except Exception as e:
        print(table, {'exists': False, 'error': str(e)})

try:
    sample = client.table('cultural_signals').select('*').limit(3).execute()
    print('cultural_signals sample count', len(sample.data or []))
    pprint(sample.data)
except Exception as e:
    print('sample error', e)
