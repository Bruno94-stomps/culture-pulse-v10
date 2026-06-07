"use client";

import { createClient } from "@/lib/supabase/client";
import { useDashboardContext } from "./DashboardContext";

export default function useDashboardSupabaseClient() {
  const { user, plan } = useDashboardContext();
  const supabase = createClient();
  return { supabase, user, plan };
}
