const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for all routes
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Serve static files from the dist directory (for production)
app.use(express.static(path.join(__dirname, 'dist')));

// Proxy endpoint for scraping websites
app.get('/api/proxy', async (req, res) => {
  const { url, mode = 'normal' } = req.query;
  
  if (!url) {
    return res.status(400).json({ error: 'URL parameter is required' });
  }

  try {
    // Validate URL
    new URL(url);
    
    // Use a proxy service or fetch directly
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    let html = await response.text();
    
    // Always inject the element selection script, but make it toggleable
    const selectionScript = `
      <script>
        // Global variables for element selection
        let elementSelectionEnabled = ${mode === 'select' ? 'true' : 'false'};
        let selectionStyle = null;
        let clickHandler = null;
        
        function toggleElementSelection(enabled) {
          elementSelectionEnabled = enabled;
          console.log('Element selection toggled:', enabled);
          
          if (enabled) {
            enableElementSelection();
          } else {
            disableElementSelection();
          }
        }
        
        function enableElementSelection() {
          // Add global styles for element selection
          if (!selectionStyle) {
            selectionStyle = document.createElement('style');
            selectionStyle.id = 'element-selection-styles';
            selectionStyle.textContent = \`
              .element-selection-enabled * { 
                cursor: pointer !important; 
                transition: all 0.2s ease !important;
              }
              .element-selection-enabled *:hover { 
                outline: 2px solid #3b82f6 !important; 
                background-color: rgba(59, 130, 246, 0.1) !important;
                position: relative !important;
                z-index: 9999 !important;
              }
              .element-selected {
                outline: 3px solid #ef4444 !important;
                background-color: rgba(239, 68, 68, 0.2) !important;
              }
            \`;
            document.head.appendChild(selectionStyle);
          }
          
          // Add click handler
          if (!clickHandler) {
            clickHandler = function(e) {
              if (!elementSelectionEnabled) return;
              
              e.preventDefault();
              e.stopPropagation();
              
              // Remove previous selection
              document.querySelectorAll('.element-selected').forEach(el => {
                el.classList.remove('element-selected');
              });
              
              // Add selection to clicked element
              e.target.classList.add('element-selected');
              
              // Extract element information
              const elementInfo = {
                tagName: e.target.tagName,
                textContent: e.target.textContent?.trim(),
                innerHTML: e.target.innerHTML,
                outerHTML: e.target.outerHTML,
                className: e.target.className,
                id: e.target.id,
                attributes: Array.from(e.target.attributes).map(attr => ({
                  name: attr.name,
                  value: attr.value
                })),
                computedStyles: window.getComputedStyle ? 
                  Array.from(window.getComputedStyle(e.target)).map(prop => ({
                    property: prop,
                    value: window.getComputedStyle(e.target).getPropertyValue(prop)
                  })).filter(style => style.value) : []
              };
              
              // Send message to parent window
              if (window.parent && window.parent !== window) {
                window.parent.postMessage({
                  type: 'ELEMENT_SELECTED',
                  data: elementInfo
                }, '*');
              }
              
              console.log('Element selected:', elementInfo);
            };
            document.addEventListener('click', clickHandler, true);
          }
          
          // Enable selection mode
          document.body.classList.add('element-selection-enabled');
        }
        
        function disableElementSelection() {
          // Remove selection mode
          document.body.classList.remove('element-selection-enabled');
          
          // Remove any selected elements
          document.querySelectorAll('.element-selected').forEach(el => {
            el.classList.remove('element-selected');
          });
        }
        
        // Listen for messages from parent
        window.addEventListener('message', function(event) {
          if (event.data && event.data.type === 'TOGGLE_ELEMENT_SELECTION') {
            toggleElementSelection(event.data.enabled);
          }
        });
        
        // Initialize on DOM ready
        document.addEventListener('DOMContentLoaded', function() {
          if (elementSelectionEnabled) {
            enableElementSelection();
          }
        });
        
        // Also initialize if DOM is already loaded
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', function() {
            if (elementSelectionEnabled) {
              enableElementSelection();
            }
          });
        } else {
          if (elementSelectionEnabled) {
            enableElementSelection();
          }
        }
      </script>
    `;
    
    // Inject the script before closing body tag
    if (html.includes('</body>')) {
      html = html.replace('</body>', selectionScript + '</body>');
    } else {
      html += selectionScript;
    }
    
    // Return the HTML content
    res.setHeader('Content-Type', 'text/html');
    res.send(html);
    
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ 
      error: 'Failed to fetch website content',
      details: error.message 
    });
  }
});

// Alternative endpoint using a CORS proxy service
app.get('/api/cors-proxy', async (req, res) => {
  const { url, mode = 'normal' } = req.query;
  
  if (!url) {
    return res.status(400).json({ error: 'URL parameter is required' });
  }

  try {
    // Use a public CORS proxy service
    const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
    const response = await fetch(proxyUrl);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    let html = await response.text();
    
    // Always inject the element selection script, but make it toggleable
    const selectionScript = `
      <script>
        // Global variables for element selection
        let elementSelectionEnabled = ${mode === 'select' ? 'true' : 'false'};
        let selectionStyle = null;
        let clickHandler = null;
        
        function toggleElementSelection(enabled) {
          elementSelectionEnabled = enabled;
          console.log('Element selection toggled:', enabled);
          
          if (enabled) {
            enableElementSelection();
          } else {
            disableElementSelection();
          }
        }
        
        function enableElementSelection() {
          // Add global styles for element selection
          if (!selectionStyle) {
            selectionStyle = document.createElement('style');
            selectionStyle.id = 'element-selection-styles';
            selectionStyle.textContent = \`
              .element-selection-enabled * { 
                cursor: pointer !important; 
                transition: all 0.2s ease !important;
              }
              .element-selection-enabled *:hover { 
                outline: 2px solid #3b82f6 !important; 
                background-color: rgba(59, 130, 246, 0.1) !important;
                position: relative !important;
                z-index: 9999 !important;
              }
              .element-selected {
                outline: 3px solid #ef4444 !important;
                background-color: rgba(239, 68, 68, 0.2) !important;
              }
            \`;
            document.head.appendChild(selectionStyle);
          }
          
          // Add click handler
          if (!clickHandler) {
            clickHandler = function(e) {
              if (!elementSelectionEnabled) return;
              
              e.preventDefault();
              e.stopPropagation();
              
              // Remove previous selection
              document.querySelectorAll('.element-selected').forEach(el => {
                el.classList.remove('element-selected');
              });
              
              // Add selection to clicked element
              e.target.classList.add('element-selected');
              
              // Extract element information
              const elementInfo = {
                tagName: e.target.tagName,
                textContent: e.target.textContent?.trim(),
                innerHTML: e.target.innerHTML,
                outerHTML: e.target.outerHTML,
                className: e.target.className,
                id: e.target.id,
                attributes: Array.from(e.target.attributes).map(attr => ({
                  name: attr.name,
                  value: attr.value
                })),
                computedStyles: window.getComputedStyle ? 
                  Array.from(window.getComputedStyle(e.target)).map(prop => ({
                    property: prop,
                    value: window.getComputedStyle(e.target).getPropertyValue(prop)
                  })).filter(style => style.value) : []
              };
              
              // Send message to parent window
              if (window.parent && window.parent !== window) {
                window.parent.postMessage({
                  type: 'ELEMENT_SELECTED',
                  data: elementInfo
                }, '*');
              }
              
              console.log('Element selected:', elementInfo);
            };
            document.addEventListener('click', clickHandler, true);
          }
          
          // Enable selection mode
          document.body.classList.add('element-selection-enabled');
        }
        
        function disableElementSelection() {
          // Remove selection mode
          document.body.classList.remove('element-selection-enabled');
          
          // Remove any selected elements
          document.querySelectorAll('.element-selected').forEach(el => {
            el.classList.remove('element-selected');
          });
        }
        
        // Listen for messages from parent
        window.addEventListener('message', function(event) {
          if (event.data && event.data.type === 'TOGGLE_ELEMENT_SELECTION') {
            toggleElementSelection(event.data.enabled);
          }
        });
        
        // Initialize on DOM ready
        document.addEventListener('DOMContentLoaded', function() {
          if (elementSelectionEnabled) {
            enableElementSelection();
          }
        });
        
        // Also initialize if DOM is already loaded
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', function() {
            if (elementSelectionEnabled) {
              enableElementSelection();
            }
          });
        } else {
          if (elementSelectionEnabled) {
            enableElementSelection();
          }
        }
      </script>
    `;
    
    // Inject the script before closing body tag
    if (html.includes('</body>')) {
      html = html.replace('</body>', selectionScript + '</body>');
    } else {
      html += selectionScript;
    }
    
    // Return the HTML content
    res.setHeader('Content-Type', 'text/html');
    res.send(html);
    
  } catch (error) {
    console.error('CORS proxy error:', error);
    res.status(500).json({ 
      error: 'Failed to fetch website content via CORS proxy',
      details: error.message 
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Catch all handler: send back React's index.html file for client-side routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
  console.log(`Proxy endpoint: http://localhost:${PORT}/api/proxy?url=<website-url>`);
});

