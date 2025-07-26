/** @type {import('next').NextConfig} */
const nextConfig = {
  // 移除 output: 'export' 以支持 API 路由
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // 配置部署 URL
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  basePath: '',
  // 如果需要跨域支持
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
}

module.exports = nextConfig
