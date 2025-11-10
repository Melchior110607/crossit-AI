/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['crossit-products.s3.amazonaws.com'],
  },
  // Marquer pg comme external pour éviter de le bundler côté client
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Ne pas bundler ces packages côté client
      config.resolve.fallback = {
        ...config.resolve.fallback,
        pg: false,
        'pg-native': false,
      };
    }
    return config;
  },
  // Packages à exclure du bundling Next.js
  experimental: {
    serverComponentsExternalPackages: ['pg', 'pg-native', 'better-sqlite3'],
  },
  async rewrites() {
    return [
      // Proxy vers FastAPI backend SAUF /api/auth (utilisé par Better Auth)
      // FastAPI ajoute automatiquement /api via le prefix dans main.py
      // Donc on envoie /api/xxx vers backend/xxx (sans /api)
      {
        source: '/api/products/:path*',
        destination: 'http://backend:8000/products/:path*',
      },
      {
        source: '/api/listings/:path*',
        destination: 'http://backend:8000/listings/:path*',
      },
      {
        source: '/api/marketplaces/:path*',
        destination: 'http://backend:8000/marketplaces/:path*',
      },
      {
        source: '/api/webhooks/:path*',
        destination: 'http://backend:8000/webhooks/:path*',
      },
      {
        source: '/api/upload/:path*',
        destination: 'http://backend:8000/upload/:path*',
      },
      {
        source: '/api/users/:path*',
        destination: 'http://backend:8000/users/:path*',
      },
      // /api/auth reste dans Next.js pour Better Auth
    ]
  },
}

module.exports = nextConfig

