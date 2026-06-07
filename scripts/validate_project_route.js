const fs = require("fs");
const { createClient } = require("@supabase/supabase-js");

const env = fs.readFileSync(".env", "utf8");
const getEnv = (key) => {
  const line = env.split(/\r?\n/).find((l) => l.startsWith(`${key}=`));
  return line ? line.split("=").slice(1).join("=") : undefined;
};

const SUPABASE_URL = getEnv("SUPABASE_URL");
const SUPABASE_SERVICE_KEY = getEnv("SUPABASE_SERVICE_KEY");
const NEXT_PUBLIC_SUPABASE_URL = getEnv("NEXT_PUBLIC_SUPABASE_URL");
const NEXT_PUBLIC_SUPABASE_ANON_KEY = getEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY");

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env");
}
if (!NEXT_PUBLIC_SUPABASE_URL || !NEXT_PUBLIC_SUPABASE_ANON_KEY) {
  throw new Error("Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY in .env");
}

const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: { persistSession: false },
});

async function run() {
  const email = "route_validation_user@culturepulse.test";
  const password = "Test1234!";

  let user = null;
  const listRes = await admin.auth.admin.listUsers();
  if (listRes.error) throw listRes.error;

  user = listRes.data?.users?.find((u) => u.email === email);
  if (!user) {
    const createRes = await admin.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
    });
    if (createRes.error) throw createRes.error;
    user = createRes.data?.user;
    console.log("Created route validation user", user.id);
  } else {
    console.log("Existing route validation user", user.id);
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
    console.log("Created profile row for route validation user");
  }

  const emailClient = createClient(NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, {
    auth: { persistSession: false },
  });
  const signIn = await emailClient.auth.signInWithPassword({ email, password });
  if (signIn.error) throw signIn.error;
  const accessToken = signIn.data?.session?.access_token;
  if (!accessToken) throw new Error("Failed to sign in route validation user");

  const project = {
    user_id: user.id,
    name: "Route Validation Project",
    brand: "Validacao de Rota",
    keywords: ["moda", "jovem", "São Paulo"],
    segment: "moda",
    objective: "teste de rota autenticada",
    regions: ["São Paulo"],
    audiences: ["jovens"],
    circles: ["moda", "tecnologia"],
    period_days: 30,
    status: "draft",
  };

  const projectRes = await admin.from("projects").insert(project).select().single();
  if (projectRes.error) throw projectRes.error;
  const createdProject = projectRes.data;
  console.log("Created project", createdProject.id);

  const baseUrl = "http://127.0.0.1:3000";
  const routeUrl = `${baseUrl}/api/projects/${createdProject.id}`;

  console.log("Calling POST route with Authorization bearer token...");
  const routeRes = await fetch(routeUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });
  const routeJson = await routeRes.text();
  console.log("POST /api/projects/[id] status", routeRes.status);
  console.log(routeJson);

  console.log("Calling GET route with same bearer token...");
  const getRes = await fetch(routeUrl, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  const getJson = await getRes.json();
  console.log("GET /api/projects/[id] status", getRes.status);
  console.log(JSON.stringify(getJson, null, 2));

  const storedInsights = getJson?.data?.analysis_data?.business_insights;
  if (storedInsights) {
    console.log("Stored business insights summary:", {
      count: storedInsights.insights?.length,
      model_used: storedInsights.model_used,
      context_source: storedInsights.context_source,
      business_goal: storedInsights.business_goal,
    });
  } else {
    console.warn("No stored business insights found in project analysis_data");
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
