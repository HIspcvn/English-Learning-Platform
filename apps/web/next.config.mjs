const configuredUrl = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
const apiUrl = new URL(configuredUrl);

if (
  !["http:", "https:"].includes(apiUrl.protocol) ||
  apiUrl.username ||
  apiUrl.password ||
  apiUrl.pathname !== "/" ||
  apiUrl.search ||
  apiUrl.hash
) {
  throw new Error("API_INTERNAL_URL must be an HTTP(S) origin without credentials or a path");
}

/** @type {import("next").NextConfig} */
const nextConfig = {
  poweredByHeader: false,
  async rewrites() {
    return [
      { source: "/api/v1/:path*", destination: `${apiUrl.origin}/api/v1/:path*` },
      { source: "/health/live", destination: `${apiUrl.origin}/health/live` },
      { source: "/health/ready", destination: `${apiUrl.origin}/health/ready` },
    ];
  },
};

export default nextConfig;
