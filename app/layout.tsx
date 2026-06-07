import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { KeywordProvider } from "@/contexts/KeywordContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Culture Pulse — Inteligência Cultural Brasileira",
  description: "Análise de sinais culturais em tempo real. Entenda o Brasil antes da virada.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={inter.className}>
        <KeywordProvider>{children}</KeywordProvider>
      </body>
    </html>
  );
}
