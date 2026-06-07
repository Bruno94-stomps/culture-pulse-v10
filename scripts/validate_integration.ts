import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';

const env = fs.readFileSync('.env', 'utf8');
const get = (k: string) => env.split(/\r?\n/).find((l) => l.startsWith(`${k}=`))?.split('=')[1];
const url = get('SUPABASE_URL');
const key = get('SUPABASE_SERVICE_KEY');
const fastapiToken = get('NEXT_PUBLIC_FASTAPI_TOKEN') || get('FASTAPI_TOKEN') || 'cp_enterprise_2025_unlimited';

if (!url || !key) {
  throw new Error('Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env');
}

const supabase = createClient(url, key, { auth: { persistSession: false } });

async function run() {
  const email = 'integration_test_user@culturepulse.test';
  const password = 'Test1234!';

  const usersRes = await supabase.auth.admin.listUsers();
  let user = usersRes.data?.users?.find((u) => u.email === email);
  if (!user) {
    const createRes = await supabase.auth.admin.createUser({ email, password, email_confirm: true });
    if (createRes.error) throw createRes.error;
    user = createRes.data?.user;
    console.log('created user', user?.id);
  } else {
    console.log('user exists', user.id);
  }
  if (!user?.id) throw new Error('User ID missing');

  const { data: profileData } = await supabase.from('profiles').select('id,email').eq('id', user.id).single();
  if (!profileData) {
    const insertRes = await supabase.from('profiles').insert([{ id: user.id, email: user.email }]);
    if (insertRes.error) throw insertRes.error;
    console.log('created profile row for', user.id);
  } else {
    console.log('profile exists for', user.id);
  }

  const project = {
    user_id: user.id,
    name: 'Integration Test Project',
    brand: 'Teste Integracao',
    keywords: ['São Paulo', 'jovem', 'moda'],
    segment: 'moda',
    objective: 'lançamento',
    regions: ['São Paulo'],
    audiences: ['jovens'],
    circles: ['moda', 'tecnologia'],
    period_days: 30,
    status: 'draft',
  } as const;

  const insertProj = await supabase.from('projects').insert(project).select().single();
  if (insertProj.error) throw insertProj.error;
  const proj = insertProj.data;
  console.log('project created', proj.id);

  const baseUrl = 'http://127.0.0.1:8000';
  const analysisPayload = {
    project_id: proj.id,
    brand_name: proj.brand,
    segment: proj.segment,
    location: 'São Paulo - Capital',
    demographics: {
      faixa_etaria: '16-25',
      classe_social: 'B',
      genero: 'Todos',
      escolaridade: 'não especificado',
      renda_familiar: 'média',
    },
    keywords: proj.keywords,
    regions: proj.regions,
    audiences: proj.audiences,
    circles: proj.circles,
    period_days: proj.period_days,
    business_goal: proj.objective,
    context_text: proj.keywords.join(', '),
    outlier_mode: false,
  };

  const analysisRes = await fetch(`${baseUrl}/api/v8/analysis/brand`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${fastapiToken}`,
    },
    body: JSON.stringify(analysisPayload),
  });
  const analysisText = await analysisRes.text();
  console.log('analysis status', analysisRes.status);
  console.log(analysisText);

  console.log('Starting demo model training to support business insights...');
  const trainRes = await fetch(`${baseUrl}/api/v8/ml/models/demo/quick-train`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${fastapiToken}`,
    },
  });
  const trainJson = await trainRes.json();
  console.log('train status', trainRes.status, trainJson);

  const waitForModel = async () => {
    const maxAttempts = 10;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      const modelsRes = await fetch(`${baseUrl}/api/v8/ml/models`, {
        headers: {
          Authorization: `Bearer ${fastapiToken}`,
        },
      });
      const modelsJson = await modelsRes.json();
      const active = modelsJson.find((m: any) => m.is_active || m.active);
      console.log(`poll ${attempt}: active model = ${active?.name ?? 'none'}`, modelsJson);
      if (active && active.name === 'cultural_demo') {
        return true;
      }
      await new Promise((resolve) => setTimeout(resolve, 1500));
    }
    return false;
  };

  const trained = await waitForModel();
  if (!trained) {
    throw new Error('Demo model was not activated in time');
  }

  const businessContextPayload = {
    project_id: proj.id,
    user_id: user.id,
    brand: proj.brand,
    segment: proj.segment,
    objective: proj.objective,
    keywords: proj.keywords,
    audiences: proj.audiences,
    regions: proj.regions,
    circles: proj.circles,
    business_goal: proj.objective,
  };

  const insightsRes = await fetch(`${baseUrl}/api/v8/ml/analyze/business-insights`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${fastapiToken}`,
    },
    body: JSON.stringify({ texts: proj.keywords, business_context: businessContextPayload }),
  });
  const insightsText = await insightsRes.text();
  console.log('insights status', insightsRes.status);
  console.log(insightsText);
}

run().catch((error) => {
  console.error('ERROR', error);
  process.exit(1);
});
