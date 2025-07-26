#!/usr/bin/env node

// 后端API交互测试脚本
const API_BASE_URL = 'http://demo.scruel.com:8000';

async function testAPI(endpoint, method = 'GET', data = null) {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`\n🔍 测试: ${method} ${url}`);
  
  try {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    if (data && method !== 'GET') {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    const responseData = await response.text();
    
    console.log(`   状态: ${response.status} ${response.statusText}`);
    console.log(`   响应: ${responseData.substring(0, 200)}${responseData.length > 200 ? '...' : ''}`);
    
    return {
      success: response.ok,
      status: response.status,
      data: responseData
    };
  } catch (error) {
    console.log(`   ❌ 错误: ${error.message}`);
    return {
      success: false,
      error: error.message
    };
  }
}

async function runTests() {
  console.log('🚀 开始测试后端API交互...\n');
  
  // 1. 测试健康检查
  await testAPI('/health');
  
  // 2. 测试产品列表
  await testAPI('/api/products');
  
  // 3. 测试产品详情
  await testAPI('/api/thread?tid=1');
  await testAPI('/api/thread?tid=2');
  
  // 4. 测试意图识别 (vibe)
  await testAPI('/api/vibe');
  await testAPI('/api/vibe?query=手机');
  await testAPI('/api/vibe?query=phone');
  
  // 5. 测试根路径
  await testAPI('/');
  
  console.log('\n✅ 测试完成！');
}

// 如果是直接运行这个脚本
if (require.main === module) {
  // Node.js 环境下需要 fetch polyfill
  if (typeof fetch === 'undefined') {
    console.log('安装 node-fetch...');
    try {
      global.fetch = require('node-fetch');
    } catch (e) {
      console.log('请先安装 node-fetch: npm install node-fetch');
      process.exit(1);
    }
  }
  
  runTests().catch(console.error);
}

module.exports = { testAPI, runTests };
