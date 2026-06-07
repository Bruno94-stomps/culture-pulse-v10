import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { getCurrentPlan } from "@/lib/plan";

/**
 * Middleware de autenticação Supabase + proteção de rotas por plano.
 *
 * Rotas protegidas:
 *   /dashboard/*        → qualquer plano autenticado
 *   /dashboard/pro/*    → plano pro ou enterprise
 *   /dashboard/enterprise/* → somente enterprise
 */
export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  // Se URL do Supabase estiver quebrada ou ausente, pula validação para permitir modo Demo
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL.includes("wsizqmnnicpgblopmxyv")) {
     return supabaseResponse;
  }

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
          cookiesToSet.forEach(({ name, value, options }) => {
            request.cookies.set(name, value);
            supabaseResponse.cookies.set(name, value, options);
          });
        },
      },
    }
  );

  // Atualiza sessão (obrigatório para @supabase/ssr)
  const { data: { user } } = await supabase.auth.getUser();
  const path = request.nextUrl.pathname;

  // Rotas que exigem autenticação
  if (path.startsWith("/dashboard")) {
    if (!user) {
      return NextResponse.redirect(new URL("/login", request.url));
    }

    // Resolve plano do usuário de forma centralizada via backend.
    const plan = await getCurrentPlan();

    // Proteção por plano
    if (path.startsWith("/dashboard/enterprise") && plan !== "enterprise") {
      return NextResponse.redirect(new URL("/dashboard/upgrade?required=enterprise", request.url));
    }
    if (path.startsWith("/dashboard/pro") && !["pro", "executive", "enterprise"].includes(plan)) {
      return NextResponse.redirect(new URL("/dashboard/upgrade?required=pro", request.url));
    }
  }

  // Redireciona usuário logado para fora da página de login
  if (path === "/login" && user) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return supabaseResponse;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
