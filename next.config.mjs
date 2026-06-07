/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy para FastAPI — evita CORS em produção e centraliza a origem
  async rewrites() {
    return [
      {
        source: "/api/fastapi/:path*",
        destination: `${process.env.FASTAPI_URL ?? "http://localhost:8000"}/:path*`,
      },
    ];
  },
  // Headers de segurança
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
  images: {
    domains: ["avatars.githubusercontent.com", "lh3.googleusercontent.com"],
  },
};

export default nextConfig;
