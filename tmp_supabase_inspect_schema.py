from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)

print('SUPABASE_URL', url)
print('SERVICE_KEY present', bool(key))

# Check alternative names for known expected tables
alt_names = [
    'signal_labels', 'signals_public', 'signals_pro', 'signals_executive',
    'cultural_signals_v2', 'cultural_signals_view', 'cultural_signals_public',
    'brand_profiles', 'brand_profiles_public', 'brand_details',
    'analysis_performance', 'strategy_weights', 'model_weights',
    'learned_weights', 'signal_feedback', 'feedback_signals',
    'collected_data', 'discovered_patterns', 'project_data', 'profile_data',
    'profiles_data', 'projects_data'
]
print('\nChecking alternative names:')
for name in alt_names:
    try:
        check = client.table(name).select('id').limit(1).execute()
        print(name, 'ok', 'data_len=', len(check.data or []), 'error=', getattr(check, 'error', None))
    except Exception as exc:
        print(name, 'error', exc)

print('\nInspecting sample rows for likely tables:')
inspect_names = ['signal_labels', 'signals_pro', 'signals_executive', 'signals_public']
for name in inspect_names:
    try:
        sample = client.table(name).select('*').limit(2).execute()
        print('\n===', name, '===')
        print('rows', len(sample.data or []))
        for row in sample.data or []:
            print(row)
    except Exception as exc:
        print(name, 'sample error', exc)
