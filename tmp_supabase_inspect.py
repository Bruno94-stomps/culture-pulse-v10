from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

for table in ['cultural_signals', 'projects', 'profiles']:
    res = client.table(table).select('id').limit(1).execute()
    print('---', table)
    print('type', type(res))
    print('repr', repr(res))
    print('dir', [a for a in dir(res) if not a.startswith('_')])
    try:
        print('data', res.data)
    except Exception as e:
        print('data error', e)
    try:
        print('error', getattr(res, 'error', None))
    except Exception as e:
        print('error attr error', e)
    try:
        print('status', getattr(res, 'status_code', None))
    except Exception as e:
        print('status attr error', e)
