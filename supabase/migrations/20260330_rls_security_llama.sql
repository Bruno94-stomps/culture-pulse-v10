-- Módulo de Segurança Cultural V9.9 (Supabase RLS)
-- ==========================================================
-- Garante isolamento total entre projetos e clientes.
-- O frontend só acessa sinais vinculados ao user_id ou org_id correto.

-- 1. Habilitar RLS em todas as tabelas críticas
ALTER TABLE public.cultural_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaign_match_history ENABLE ROW LEVEL SECURITY;

-- 2. Política de Isomento para Sinais Culturais
-- Permite que usuários vejam apenas sinais de seus próprios projetos (via user_id)
-- Ou sinais globais (se user_id for null) caso o plano permita.
DROP POLICY IF EXISTS "Users can only see their own signals" ON public.cultural_signals;
CREATE POLICY "Users can only see their own signals" ON public.cultural_signals
FOR SELECT 
TO authenticated 
USING (
    user_id = auth.uid() 
    OR 
    (user_id IS NULL AND (SELECT plan FROM public.user_profiles WHERE id = auth.uid()) = 'enterprise')
);

-- 3. Política para o Worker (Service Role)
-- O worker rodando no Mac Mini usa a SERVICE_ROLE_KEY, que ignora RLS.
-- Mas para segurança de auditoria, garantimos que o worker tenha acesso total.
CREATE POLICY "Service role full access" ON public.cultural_signals
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- 4. Proteção contra Injeção de Dados via API
-- Garante que um usuário não consiga "forjar" um sinal para outro usuário no ID alheio.
DROP POLICY IF EXISTS "Users can only insert their own signals" ON public.cultural_signals;
CREATE POLICY "Users can only insert their own signals" ON public.cultural_signals
FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());
