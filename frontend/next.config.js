const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || '';
    if (apiBase) {
      return [
        { source: '/api/:path*', destination: `${apiBase}/api/:path*` },
        { source: '/health', destination: `${apiBase}/health` },
        { source: '/docs', destination: `${apiBase}/docs` },
      ];
    }
    return [];
  },
};

module.exports = nextConfig;
