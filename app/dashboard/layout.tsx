import { redirect } from "next/navigation";
import { getCurrentPlan } from "@/lib/plan";
import { createClient } from "@/lib/supabase/server";
import DashboardShell from "@/components/dashboard/DashboardShell";

/**
 * Layout do dashboard — Server Component.
 * Lê sessão do Supabase e injeta user + plan nos filhos via props.
 */
export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = createClient();
  const { data: userData } = await supabase.auth.getUser();
  const user = userData.user;

  if (!user) {
    redirect("/login");
  }

  const plan = await getCurrentPlan();

  return (
    <DashboardShell user={user} plan={plan}>
      {children}
    </DashboardShell>
  );
}
