const fs = require("fs");
const { createClient } = require("@supabase/supabase-js");

const env = fs.existsSync(".env") ? fs.readFileSync(".env", "utf8") : "";
const getEnv = (key) => {
  if (process.env[key]) return process.env[key];
  const match = env.split(/\r?\n/).find((line) => line.startsWith(`${key}=`));
  return match ? match.slice(key.length + 1) : undefined;
};

const SUPABASE_URL = getEnv("SUPABASE_URL") || getEnv("NEXT_PUBLIC_SUPABASE_URL");
const SUPABASE_SERVICE_KEY = getEnv("SUPABASE_SERVICE_KEY");
const FASTAPI_URL = getEnv("PROJECT_ANALYSIS_FASTAPI_URL") || getEnv("NEXT_PUBLIC_FASTAPI_URL") || getEnv("NEXT_PUBLIC_API_URL") || "http://127.0.0.1:8000";
const FASTAPI_TOKEN = getEnv("FASTAPI_TOKEN") || getEnv("NEXT_PUBLIC_FASTAPI_TOKEN") || "cp_demo_2025_free_tier";
const APP_URL = getEnv("PROJECT_ANALYSIS_APP_URL") || getEnv("NEXT_PUBLIC_APP_URL") || "http://127.0.0.1:3000";

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment or .env");
}

const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: { persistSession: false },
});
const client = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: { persistSession: false },
});

async function fetchJson(url, init) {
  const res = await fetch(url, init);
  const text = await res.text();
  try {
    return { res, body: JSON.parse(text), text };
  } catch {
    return { res, body: null, text };
  }
}

async function waitForProjectReady(projectId, token) {
  const url = `${APP_URL}/api/projects/${projectId}`;
  const maxAttempts = 12;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const { res, body, text } = await fetchJson(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      throw new Error(`GET route failed: ${res.status} ${text}`);
    }
    const project = body?.data;
    if (project?.status === "ready") {
      return project;
    }
    if (attempt < maxAttempts) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  }
  throw new Error(`Project did not reach ready status within timeout`);
}

async function run() {
  const email = "project_analysis_test@culturepulse.test";
  const password = "Test1234!";

  const listRes = await admin.auth.admin.listUsers();
  if (listRes.error) throw listRes.error;

  let user = listRes.data?.users?.find((u) => u.email === email);
  if (!user) {
    const createRes = await admin.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
    });
    if (createRes.error) throw createRes.error;
    user = createRes.data?.user;
    console.log("Created test user", user.id);
  } else {
    console.log("Found existing test user", user.id);
    const updateRes = await admin.auth.admin.updateUserById(user.id, {
      password,
      email_confirm: true,
    });
    if (updateRes.error) throw updateRes.error;
  }

  if (!user?.id) throw new Error("User ID missing");

  const profileRes = await admin.from("profiles").select("id,email").eq("id", user.id).single();
  if (profileRes.error && profileRes.error.code !== "PGRST116") {
    throw profileRes.error;
  }
  if (!profileRes.data) {
    const insertRes = await admin.from("profiles").insert([{ id: user.id, email: user.email }]);
    if (insertRes.error) throw insertRes.error;
    console.log("Created profile row for user");
  }

  const uniqueSuffix = Date.now();
  const projectData = {
    user_id: user.id,
    name: `Project Analysis Test ${uniqueSuffix}`,
    brand: "Teste Análise",
    keywords: ["São Paulo", "moda", "jovem"],
    segment: "moda",
    objective: "lançamento",
    regions: ["São Paulo"],
    audiences: ["jovens"],
    circles: ["moda", "tecnologia"],
    period_days: 30,
    status: "draft",
  };

  const projectRes = await admin.from("projects").insert(projectData).select().single();
  if (projectRes.error) throw projectRes.error;
  const project = projectRes.data;
  console.log("Created project", project.id);

  const signInRes = await client.auth.signInWithPassword({ email, password });
  if (signInRes.error) throw signInRes.error;
  const accessToken = signInRes.data?.session?.access_token;
  if (!accessToken) throw new Error("Failed to sign in route validation user");

  const routeUrl = `${APP_URL}/api/projects/${project.id}`;
  console.log("Using APP_URL:", APP_URL);
  console.log("Triggering project analysis via POST", routeUrl);

  const { res: postRes, body: postBody, text: postText } = await fetchJson(routeUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!postRes.ok) {
    console.error("POST /api/projects/[id] failed", postRes.status, postText);
    process.exit(1);
  }
  console.log("POST response", JSON.stringify(postBody, null, 2));
  if (postBody?.status !== "success") {
    throw new Error(`Unexpected POST response status: ${postBody?.status}`);
  }

  const projectAfter = await waitForProjectReady(project.id, accessToken);
  console.log("Project status is ready");

  if (!projectAfter.analysis_data) {
    throw new Error("Project analysis_data missing after route execution");
  }
  if (!projectAfter.analysis_data.brand_analysis) {
    throw new Error("brand_analysis missing in project.analysis_data");
  }
  if (!projectAfter.analysis_data.business_insights) {
    throw new Error("business_insights missing in project.analysis_data");
  }
  if (!Array.isArray(projectAfter.analysis_data.business_insights.insights)) {
    throw new Error("business_insights.insights is not an array");
  }
  if (projectAfter.analysis_data.business_insights.project_id !== projectAfter.id) {
    throw new Error("Stored business_insights.project_id does not match project id");
  }
  if (projectAfter.analysis_data.business_insights.user_id !== user.id) {
    throw new Error("Stored business_insights.user_id does not match authenticated user id");
  }

  const directBusinessContext = {
    project_id: projectAfter.id,
    user_id: user.id,
    brand: projectAfter.brand,
    segment: projectAfter.segment,
    objective: projectAfter.objective,
    keywords: projectAfter.keywords ?? [],
    regions: projectAfter.regions ?? [],
    audiences: projectAfter.audiences ?? [],
    circles: projectAfter.circles ?? [],
    period_days: projectAfter.period_days,
    business_goal: projectAfter.objective || `Entendimento cultural para ${projectAfter.brand}`,
  };

  const directPayload = {
    texts: projectAfter.keywords && projectAfter.keywords.length > 0
      ? projectAfter.keywords
      : [projectAfter.objective || projectAfter.brand || "Análise de contexto"],
    business_context: directBusinessContext,
    model_name: "cultural_demo",
  };

  const fastApiUrl = process.env.PROJECT_ANALYSIS_FASTAPI_URL || process.env.NEXT_PUBLIC_FASTAPI_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const fastApiToken = process.env.FASTAPI_TOKEN || process.env.NEXT_PUBLIC_FASTAPI_TOKEN || "cp_demo_2025_free_tier";
  const { res: directRes, body: directBody, text: directText } = await fetchJson(`${fastApiUrl}/api/v8/ml/analyze/business-insights`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${fastApiToken}`,
    },
    body: JSON.stringify(directPayload),
  });

  if (!directRes.ok) {
    throw new Error(`Direct ML endpoint failed: ${directRes.status} ${directText}`);
  }
  if (!directBody || typeof directBody !== "object") {
    throw new Error("Direct ML endpoint did not return a valid JSON object");
  }
  if (!Array.isArray(directBody.insights)) {
    throw new Error("Direct ML endpoint insights is not an array");
  }
  if (directBody.project_id !== projectAfter.id) {
    throw new Error("Direct ML endpoint project_id mismatch");
  }
  if (directBody.user_id !== user.id) {
    throw new Error("Direct ML endpoint user_id mismatch");
  }
  if (directBody.context_source !== "business_context") {
    throw new Error("Direct ML endpoint context_source missing or incorrect");
  }
  if (!directBody.model_used) {
    throw new Error("Direct ML endpoint model_used is missing");
  }

  console.log("Business insights stored successfully:", {
    count: projectAfter.analysis_data.business_insights.insights.length,
    model_used: projectAfter.analysis_data.business_insights.model_used,
    context_source: projectAfter.analysis_data.business_insights.context_source,
  });
  console.log("Direct ML endpoint contract validated successfully:", {
    count: directBody.insights.length,
    project_id: directBody.project_id,
    user_id: directBody.user_id,
    model_used: directBody.model_used,
  });
  console.log("Project analysis flow test passed.");
}

run().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});
