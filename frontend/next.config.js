/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['crossit-products.s3.amazonaws.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig

