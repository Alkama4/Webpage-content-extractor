// Simple test script to verify proxy functionality
const fetch = require('node-fetch');

async function testProxy() {
  try {
    console.log('Testing proxy server...');
    
    // Test health endpoint
    const healthResponse = await fetch('http://localhost:3001/api/health');
    const healthData = await healthResponse.json();
    console.log('Health check:', healthData);
    
    // Test proxy with google.com
    console.log('\nTesting proxy with google.com...');
    const proxyResponse = await fetch('http://localhost:3001/api/proxy?url=https://google.com');
    
    if (proxyResponse.ok) {
      const html = await proxyResponse.text();
      console.log('Proxy successful! HTML length:', html.length);
      console.log('First 200 characters:', html.substring(0, 200));
    } else {
      console.log('Proxy failed with status:', proxyResponse.status);
    }
    
  } catch (error) {
    console.error('Test failed:', error.message);
  }
}

testProxy();

