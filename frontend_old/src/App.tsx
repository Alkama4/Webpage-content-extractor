import React, { useState, useEffect, useRef } from 'react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { ScrollArea } from './components/ui/scroll-area';
import { Separator } from './components/ui/separator';
import { 
  Globe, 
  Scissors, 
  Monitor, 
  Bookmark, 
  Star, 
  ExternalLink, 
  Trash2, 
  Clock,
  Loader2,
  AlertCircle,
  Target,
  Code,
  Copy,
  History,
  Settings,
  MousePointer,
  X,
  Database,
  Server,
  Play,
  Plus,
  Edit,
  Trash,
  Eye,
  RefreshCw,
  Home,
  Settings2
} from 'lucide-react';


interface Website {
  id: string;
  url: string;
  title: string;
  addedAt: Date;
  extractedElements: number;
}

interface RecentWebsite {
  id: string;
  url: string;
  title: string;
  lastVisited: Date;
}

interface ElementInfo {
  tagName: string;
  textContent: string;
  innerHTML: string;
  outerHTML: string;
  className: string;
  id: string;
  attributes: Array<{name: string, value: string}>;
  computedStyles: Array<{property: string, value: string}>;
}

interface Webpage {
  id: string;
  url: string;
  title?: string;
  created_at?: string;
  updated_at?: string;
  status?: string;
  description?: string;
}

interface Scrape {
  id: string;
  webpage_id: string;
  name?: string;
  selector?: string;
  created_at?: string;
  updated_at?: string;
  status?: string;
  last_run?: string;
  next_run?: string;
}

function App() {
  const [url, setUrl] = useState('');
  const [loadedUrl, setLoadedUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedElement, setSelectedElement] = useState<ElementInfo | null>(null);
  const [selectedElementInfo, setSelectedElementInfo] = useState<ElementInfo | null>(null);
  const [addedWebsites, setAddedWebsites] = useState<Website[]>([]);
  const [recentlyVisited, setRecentlyVisited] = useState<RecentWebsite[]>([]);
  const [bookmarks, setBookmarks] = useState<string[]>([]);
  const [proxyError, setProxyError] = useState('');
  const [isProxyMode, setIsProxyMode] = useState(true);
  const [browsingMode, setBrowsingMode] = useState<'normal' | 'select'>('normal');
  const [originalUrl, setOriginalUrl] = useState('');
  const [webpages, setWebpages] = useState<Webpage[]>([]);
  const [scrapes, setScrapes] = useState<Scrape[]>([]);
  const [isLoadingWebpages, setIsLoadingWebpages] = useState(false);
  const [isLoadingScrapes, setIsLoadingScrapes] = useState(false);
  const [activeTab, setActiveTab] = useState<'home' | 'api'>('home');
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Load saved websites from localStorage on component mount
  useEffect(() => {
    const savedWebsites = localStorage.getItem('addedWebsites');
    const savedRecent = localStorage.getItem('recentlyVisited');
    const savedBookmarks = localStorage.getItem('bookmarks');
    
    if (savedWebsites) {
      try {
        const parsed = JSON.parse(savedWebsites);
        setAddedWebsites(parsed.map((w: any) => ({
        ...w,
          addedAt: new Date(w.addedAt)
      })));
      } catch (error) {
        console.error('Error parsing saved websites:', error);
      }
    }
    
    if (savedRecent) {
      try {
        const parsed = JSON.parse(savedRecent);
        setRecentlyVisited(parsed.map((w: any) => ({
        ...w,
        lastVisited: new Date(w.lastVisited)
      })));
      } catch (error) {
        console.error('Error parsing recent websites:', error);
      }
    }
    
    if (savedBookmarks) {
      try {
        setBookmarks(JSON.parse(savedBookmarks));
      } catch (error) {
        console.error('Error parsing bookmarks:', error);
      }
    }
  }, []);

  // Listen for messages from iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'ELEMENT_SELECTED') {
        console.log('Received element selection:', event.data.data);
        setSelectedElement(event.data.data);
        setSelectedElementInfo(event.data.data);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [loadedUrl]);

  // Save to localStorage whenever websites change
  useEffect(() => {
    localStorage.setItem('addedWebsites', JSON.stringify(addedWebsites));
  }, [addedWebsites]);

  useEffect(() => {
    localStorage.setItem('recentlyVisited', JSON.stringify(recentlyVisited));
  }, [recentlyVisited]);

  useEffect(() => {
    localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
  }, [bookmarks]);

  const normalizeUrl = (inputUrl: string): string => {
    let normalized = inputUrl.trim();
    
    // Add protocol if missing
    if (!normalized.startsWith('http://') && !normalized.startsWith('https://')) {
      normalized = 'https://' + normalized;
    }
    
    return normalized;
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleScrape();
    }
  };

  const handleScrape = async () => {
    if (!url.trim()) return;
    
      setIsLoading(true);
    setProxyError('');
    setSelectedElement(null);
    setSelectedElementInfo(null);
    
    try {
      const normalizedUrl = normalizeUrl(url);
      console.log('Normalized URL:', normalizedUrl);
      
      // Store the original URL for mode switching
      setOriginalUrl(normalizedUrl);
      
      if (isProxyMode) {
        console.log('Using proxy mode');
        handleProxyLoad(normalizedUrl);
      } else {
        console.log('Using direct mode');
        setLoadedUrl(normalizedUrl);
      }
      
      // Add to recently visited
      const websiteTitle = new URL(normalizedUrl).hostname;
      const newRecent: RecentWebsite = {
      id: Date.now().toString(),
        url: normalizedUrl,
        title: websiteTitle,
        lastVisited: new Date()
      };
      
      setRecentlyVisited(prev => {
        const filtered = prev.filter(w => w.url !== normalizedUrl);
        return [newRecent, ...filtered].slice(0, 10);
      });
      
    } catch (error) {
      console.error('Error scraping website:', error);
      setProxyError('Failed to load website. Please check the URL and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProxyLoad = async (targetUrl: string) => {
    try {
      console.log('Loading via proxy:', targetUrl);
      const proxyUrl = `http://localhost:3001/api/proxy?url=${encodeURIComponent(targetUrl)}&mode=${browsingMode}`;
      console.log('Proxy URL:', proxyUrl);
      setLoadedUrl(proxyUrl);
    } catch (error) {
      console.error('Proxy error:', error);
      setProxyError('Failed to connect to proxy server. Make sure the backend is running.');
    }
  };

  const handleIframeLoad = () => {
    console.log('Iframe loaded with URL:', loadedUrl);
    console.log('Iframe element:', iframeRef.current);
    console.log('Iframe src attribute:', iframeRef.current?.src);
    setIsLoading(false);
    
    // Add click event listener to iframe content
    try {
      const iframe = iframeRef.current;
      if (iframe && iframe.contentDocument) {
        iframe.contentDocument.addEventListener('click', handleElementClick);
        
        // Add hover effects to make elements selectable
        const style = iframe.contentDocument.createElement('style');
        style.textContent = `
          * { cursor: pointer !important; }
          *:hover { 
            outline: 2px solid #3b82f6 !important; 
            background-color: oklch(0.9 0.08 180 / 0.1) !important;
          }
        `;
        iframe.contentDocument.head.appendChild(style);
      }
    } catch (error) {
      console.log('Cannot access iframe content due to CORS policy');
      // Try to load via proxy as fallback
      if (originalUrl) {
        handleProxyLoad(originalUrl);
      }
    }
  };

  const handleIframeError = () => {
    console.log('Iframe failed to load');
    setIsLoading(false);
    setProxyError('Failed to load website. This might be due to CORS restrictions or an invalid URL.');
  };

  const handleElementClick = (e: Event) => {
    if (browsingMode !== 'select') return;
    
    e.preventDefault();
    e.stopPropagation();
    
    const element = e.target as HTMLElement;
      const elementInfo = {
      tagName: element.tagName,
      textContent: element.textContent || '',
      innerHTML: element.innerHTML,
      outerHTML: element.outerHTML,
      className: element.className,
      id: element.id,
      attributes: Array.from(element.attributes).map(attr => ({
        name: attr.name,
        value: attr.value
      })),
      computedStyles: window.getComputedStyle ? 
        Array.from(window.getComputedStyle(element)).map(prop => ({
          property: prop,
          value: window.getComputedStyle(element).getPropertyValue(prop)
        })).filter(style => style.value) : []
    };
    
    setSelectedElement(elementInfo);
    setSelectedElementInfo(elementInfo);
  };

  const addWebsite = (websiteUrl: string) => {
    const websiteTitle = new URL(websiteUrl).hostname;
    const newWebsite: Website = {
      id: Date.now().toString(),
      url: websiteUrl,
      title: websiteTitle,
      addedAt: new Date(),
      extractedElements: 0
    };
    
    setAddedWebsites(prev => [newWebsite, ...prev]);
  };

  const removeWebsite = (id: string) => {
    setAddedWebsites(prev => prev.filter(w => w.id !== id));
  };

  const loadWebsiteFromSidebar = (websiteUrl: string) => {
    setUrl(websiteUrl);
    setOriginalUrl(websiteUrl);
    if (isProxyMode) {
      handleProxyLoad(websiteUrl);
    } else {
      setLoadedUrl(websiteUrl);
    }
  };

  const addToBookmarks = (websiteUrl: string) => {
    if (!bookmarks.includes(websiteUrl)) {
      setBookmarks(prev => [...prev, websiteUrl]);
    }
  };

  const removeFromBookmarks = (websiteUrl: string) => {
    setBookmarks(prev => prev.filter(url => url !== websiteUrl));
  };

  const clearRecentlyVisited = () => {
    setRecentlyVisited([]);
  };

  const handleModeSwitch = (newMode: 'normal' | 'select') => {
    if (!originalUrl) {
      console.log('No original URL available for mode switching');
      return;
    }

    console.log(`Switching mode from ${browsingMode} to ${newMode}`);
    setBrowsingMode(newMode);
    
    // Send message to iframe to toggle element selection mode
    try {
      const iframe = iframeRef.current;
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({
          type: 'TOGGLE_ELEMENT_SELECTION',
          enabled: newMode === 'select'
        }, '*');
        console.log(`Sent mode switch message to iframe: ${newMode}`);
      }
    } catch (error) {
      console.log('Cannot send message to iframe, falling back to reload');
      // Fallback to reload if postMessage fails
      if (isProxyMode) {
        const proxyUrl = `http://localhost:3001/api/proxy?url=${encodeURIComponent(originalUrl)}&mode=${newMode}`;
        console.log('Fallback: Reloading with new mode:', proxyUrl);
        setLoadedUrl(proxyUrl);
      }
    }
  };

  // API Functions
  const fetchWebpages = async () => {
    setIsLoadingWebpages(true);
    try {
      const response = await fetch('/webpages/webpages/');
      if (response.ok) {
        const data = await response.json();
        setWebpages(data);
      } else {
        console.error('Failed to fetch webpages:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching webpages:', error);
    } finally {
      setIsLoadingWebpages(false);
    }
  };

  const fetchScrapes = async () => {
    setIsLoadingScrapes(true);
    try {
      const response = await fetch('/scrapes/scrapes/');
      if (response.ok) {
        const data = await response.json();
        setScrapes(data);
      } else {
        console.error('Failed to fetch scrapes:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching scrapes:', error);
    } finally {
      setIsLoadingScrapes(false);
    }
  };

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      {/* Header Navigation */}
      <div className="sticky top-0 z-50 bg-background border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">Web Scraper Dashboard</h1>
            </div>
            
            <nav className="flex items-center gap-3 p-2">
              <a href="#home" onClick={(e) => { e.preventDefault(); setActiveTab('home'); }} style={{ cursor: 'pointer' }}>
                <Button
                  variant={activeTab === 'home' ? 'default' : 'ghost'}
                  size="sm"
                  className="h-8 px-4"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Home
                </Button>
              </a>
              <a href="#api" onClick={(e) => { e.preventDefault(); setActiveTab('api'); }} style={{ cursor: 'pointer' }}>
                <Button
                  variant={activeTab === 'api' ? 'default' : 'ghost'}
                  size="sm"
                  className="h-8 px-4"
                >
                  <Settings2 className="h-4 w-4 mr-2" />
                  API Manager
                </Button>
              </a>
            </nav>
          </div>
        </div>
      </div>

      <div className="p-2">
        <div className="max-w-7xl mx-auto space-y-2 w-full">
          {activeTab === 'home' && (
            <>
              {/* Main Row - Website Display (Left) and Scraper+Element Selector (Right) */}
        <div className="flex flex-row gap-6 min-w-0">
          {/* Left: Website Display */}
          <Card className="flex-1 min-w-0 border-2 border-primary/20">
              <CardHeader className="pb-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Monitor className="h-5 w-5 text-primary" />
                  <CardTitle>Website Display</CardTitle>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Globe className="h-4 w-4" />
                  <span>{loadedUrl ? 'Live Website Preview' : 'Ready for Website'}</span>
                </div>
              </div>
              <CardDescription>
                {loadedUrl 
                  ? 'Interactive website view • Click on any element to select it for data extraction'
                  : 'Enter a URL in the input box and click "Scrape Website" to load content here'
                }
              </CardDescription>
                
                {/* Browsing Mode Buttons */}
                <div className="mt-4 flex justify-center gap-4">
                  <Button
                    variant={browsingMode === 'normal' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleModeSwitch('normal')}
                    className="h-10 px-4"
                  >
                    <MousePointer className="mr-2 h-4 w-4" />
                    Normal Browsing
                  </Button>
                  <Button
                    variant={browsingMode === 'select' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleModeSwitch('select')}
                    className="h-10 px-4"
                  >
                    <Target className="mr-2 h-4 w-4" />
                    Element Selection
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col min-w-0">
                <div className="relative border-4 border-primary/30 rounded-lg flex-1 min-h-[80vh]">
                {!loadedUrl ? (
                    <div className="h-full flex items-center justify-center bg-muted/20">
                    <div className="text-center space-y-4">
                      <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
                        <Globe className="w-8 h-8 text-primary" />
                      </div>
                      <div className="space-y-2">
                        <h3 className="font-medium text-foreground">Website Display Area</h3>
                        <p className="text-sm text-muted-foreground max-w-md">
                          This area will show the live website when you enter a URL and click "Scrape Website". 
                          You'll be able to interact with elements directly.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <>
                    {isLoading && (
                        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-10">
                          <div className="text-center space-y-4">
                            <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
                            <div className="space-y-2">
                              <h3 className="font-medium">Loading Website...</h3>
                              <p className="text-sm text-muted-foreground">
                                Fetching content from {loadedUrl}
                              </p>
                            </div>
                        </div>
                      </div>
                    )}
                    
                    <iframe
                      ref={iframeRef}
                      src={loadedUrl}
                        className="w-full h-full"
                      onLoad={handleIframeLoad}
                      onError={handleIframeError}
                      sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
                      title={browsingMode === 'select' ? "Website Preview for Data Extraction" : "Website Preview"}
                    />
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Right: Website Scraper and Element Selector (Stacked Vertically) */}
          <div className="flex flex-col gap-2 w-96 flex-shrink-0">
          {/* Website Scraper */}
          <Card className="border-2 border-primary/20 min-w-0" style={{ width: '30em', maxWidth: '30em' }}>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-primary" />
                <CardTitle>Website Scraper</CardTitle>
              </div>
              <CardDescription>
                Enter a URL to scrape and load any website
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col space-y-4">
              <div className="space-y-2">
                  <Label htmlFor="url-input">Website URL</Label>
                  <div className="flex gap-2">
                <Input
                      id="url-input"
                  type="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleScrape()}
                      className="flex-1"
                    />
                            <Button onClick={handleScrape} disabled={isLoading || !url.trim()}>
                              {isLoading ? (
                                <>
                                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                  Scraping...
                                </>
                              ) : (
                                'Scrape Website'
                              )}
                            </Button>
                  </div>
                </div>

                {/* Connection Mode Toggle */}
                <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isProxyMode ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm font-medium">
                      {isProxyMode ? 'Proxy Mode' : 'Direct Mode'}
                    </span>
              </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsProxyMode(!isProxyMode)}
                  >
                    {isProxyMode ? 'Switch to Direct' : 'Switch to Proxy'}
                  </Button>
              </div>
              
                {/* Error Display */}
                {proxyError && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                    <div className="flex items-center gap-2 text-destructive">
                      <AlertCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">Connection Error</span>
                  </div>
                    <p className="text-sm text-destructive/80 mt-1">{proxyError}</p>
                </div>
              )}
              </div>
            </CardContent>
          </Card>

          {/* Element Inspector */}
          <Card className="border-2 border-primary/20 min-w-0" style={{ width: '30em', maxWidth: '30em' }}>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                <CardTitle>Element Inspector</CardTitle>
              </div>
              <CardDescription>
                Inspect and analyze selected elements from the website
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col min-w-0">
              <div className="flex flex-col space-y-4 min-w-0">
                {/* Selected Element Display */}
                {selectedElement ? (
                  <div className="space-y-4 min-w-0">
                    <div className="space-y-2 min-w-0">
                      <Label>Selected Element</Label>
                      <div className="p-3 bg-muted rounded border min-w-0">
                        <div className="space-y-2 min-w-0">
                          <div className="flex items-center gap-2">
                            <Target className="h-4 w-4 text-primary" />
                            <span className="text-sm font-medium">Element Type: {selectedElement.tagName}</span>
                          </div>
                          
                          {selectedElement.textContent && (
                            <div className="min-w-0">
                              <span className="text-xs text-muted-foreground">Text:</span>
                              <div className="text-sm mt-1 break-words">{selectedElement.textContent}</div>
                            </div>
                          )}
                          
                          {selectedElement.id && (
                            <div>
                              <span className="text-xs text-muted-foreground">ID:</span>
                              <code className="ml-2 px-1 py-0.5 bg-background rounded text-xs">#{selectedElement.id}</code>
                            </div>
                          )}
                          
                          {selectedElement.className && (
                            <div>
                              <span className="text-xs text-muted-foreground">Classes:</span>
                              <code className="ml-2 px-1 py-0.5 bg-background rounded text-xs">.{selectedElement.className.split(' ').join('.')}</code>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* All Attributes Display */}
                    <div className="space-y-2 min-w-0">
                      <Label>All Attributes</Label>
                      <div className="p-3 bg-muted rounded border min-w-0">
                        <div className="space-y-2 min-w-0">
                          {selectedElement.attributes && selectedElement.attributes.length > 0 ? (
                            Array.from(selectedElement.attributes).map((attr, index) => (
                              <div key={index} className="min-w-0">
                                <span className="text-xs text-muted-foreground">{attr.name}:</span>
                                <code className="ml-2 px-1 py-0.5 bg-background rounded text-xs break-words">
                                  {attr.value || '(empty)'}
                                </code>
                              </div>
                            ))
                          ) : (
                            <div className="text-xs text-muted-foreground">No attributes found</div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* HTML Structure Display */}
                    <div className="space-y-2 min-w-0">
                      <Label>HTML Structure</Label>
                      <div className="space-y-2 min-w-0">
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-muted-foreground">Outer HTML:</span>
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-6 px-2 text-xs flex items-center gap-1"
                              onClick={() => navigator.clipboard.writeText(selectedElement.outerHTML)}
                              title="Copy HTML"
                            >
                              <Copy className="h-3 w-3" />
                              Copy
                            </Button>
                          </div>
                          <div className="mt-1">
                            <pre className="p-2 bg-muted rounded text-xs overflow-y-auto font-mono whitespace-pre-wrap break-words max-w-full max-h-96">
                              {selectedElement.outerHTML}
                            </pre>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-muted-foreground">Inner HTML:</span>
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-6 px-2 text-xs flex items-center gap-1"
                              onClick={() => navigator.clipboard.writeText(selectedElement.innerHTML)}
                              title="Copy Inner HTML"
                            >
                              <Copy className="h-3 w-3" />
                              Copy
                            </Button>
                          </div>
                          <div className="mt-1">
                            <pre className="p-2 bg-muted rounded text-xs overflow-auto max-h-32 font-mono whitespace-pre-wrap">
                              {selectedElement.innerHTML}
                            </pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-muted rounded-lg">
                    <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-sm">No element selected</p>
                    <p className="text-xs mt-1">Click on an element in the website to see its information here</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          </div>
        </div>

        {/* Second Row - Website Manager */}
          <Card className="border-2 border-primary/20">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Bookmark className="h-5 w-5 text-primary" />
                <CardTitle>Website Manager</CardTitle>
              </div>
              <CardDescription>
              Manage your recently visited websites and bookmarks
              </CardDescription>
            </CardHeader>
          <CardContent>
            <div className="flex flex-row gap-6">
              {/* Left: Bookmarks */}
              <div className="flex-1 flex flex-col space-y-3">
                <div className="flex items-center gap-2">
                  <Bookmark className="h-4 w-4 text-primary" />
                  <h3 className="font-medium">Bookmarks</h3>
                    <Badge variant="secondary" className="text-xs">
                    {bookmarks.length}
                    </Badge>
                  </div>
                  
                {bookmarks.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-muted rounded-lg">
                    <Bookmark className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No bookmarks yet</p>
                    <p className="text-xs">Click the bookmark icon on recently visited sites to add them</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {bookmarks.map((website, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted/50 rounded hover:bg-muted/70 transition-colors">
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                          <Bookmark className="h-4 w-4 text-primary flex-shrink-0" />
                          <span className="text-sm truncate">{website}</span>
                        </div>
                        <div className="flex items-center gap-1">
                                <Button
                                  variant="ghost"
                                  size="sm"
                            onClick={() => loadWebsiteFromSidebar(website)}
                                  className="h-6 w-6 p-0"
                            title="Load website"
                                >
                                  <ExternalLink className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                            onClick={() => removeFromBookmarks(website)}
                                  className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                            title="Remove bookmark"
                                >
                            <X className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                    ))}
                  </div>
                      )}
                </div>

              {/* Right: Recently Visited Links */}
              <div className="flex-1 flex flex-col space-y-3">
                  <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <History className="h-4 w-4 text-primary" />
                    <h3 className="font-medium">Recently Visited</h3>
                    <Badge variant="secondary" className="text-xs">
                      {recentlyVisited.length}
                    </Badge>
                  </div>
                  {recentlyVisited.length > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearRecentlyVisited}
                      className="h-7 px-2 text-xs text-muted-foreground hover:text-destructive"
                      title="Clear all recently visited"
                    >
                      <Trash2 className="h-3 w-3 mr-1" />
                      Clear All
                    </Button>
                  )}
                  </div>
                  
                      {recentlyVisited.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-muted rounded-lg">
                    <History className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No websites visited yet</p>
                          <p className="text-xs">Start scraping websites to see them here</p>
                        </div>
                      ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {recentlyVisited.slice(0, 10).map((website, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted/50 rounded hover:bg-muted/70 transition-colors">
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                          <Globe className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium truncate">{website.title}</p>
                                <p className="text-xs text-muted-foreground truncate">{website.url}</p>
                          </div>
                              </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => loadWebsiteFromSidebar(website.url)}
                            className="h-6 w-6 p-0"
                            title="Load website"
                          >
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                            onClick={() => addToBookmarks(website.url)}
                                className="h-6 w-6 p-0"
                            title="Add to bookmarks"
                              >
                            <Bookmark className="h-3 w-3" />
                              </Button>
                            </div>
                    </div>
                    ))}
                  </div>
                )}
                </div>
              </div>
            </CardContent>
          </Card>
            </>
          )}

          {activeTab === 'api' && (
            <>
              {/* API Data Display */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Webpages Display */}
          <Card className="border-2 border-primary/20">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-primary" />
                  <CardTitle>Webpages Data</CardTitle>
                  <Badge variant="outline" className="text-xs">
                    {webpages.length} webpages
                  </Badge>
                </div>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={fetchWebpages}
                  disabled={isLoadingWebpages}
                >
                  {isLoadingWebpages ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-2" />
                  )}
                  Refresh
                </Button>
              </div>
              <CardDescription>
                Data from GET /webpages/webpages/ endpoint
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {webpages.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-muted rounded-lg">
                    <Globe className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-sm">No webpages data</p>
                    <p className="text-xs mt-1">Click "Test" on the GET /webpages/webpages/ endpoint to load data</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {webpages.map((webpage) => (
                      <div key={webpage.id} className="p-3 bg-muted/50 rounded-lg border">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Globe className="h-4 w-4 text-primary" />
                              <span className="font-medium text-sm">ID: {webpage.id}</span>
                            </div>
                            {webpage.status && (
                              <Badge variant="outline" className="text-xs">
                                {webpage.status}
                              </Badge>
                            )}
                          </div>
                          
                          <div className="space-y-1">
                            <div>
                              <span className="text-xs text-muted-foreground">URL:</span>
                              <p className="text-sm break-words">{webpage.url}</p>
                            </div>
                            
                            {webpage.title && (
                              <div>
                                <span className="text-xs text-muted-foreground">Title:</span>
                                <p className="text-sm">{webpage.title}</p>
                              </div>
                            )}
                            
                            {webpage.description && (
                              <div>
                                <span className="text-xs text-muted-foreground">Description:</span>
                                <p className="text-sm">{webpage.description}</p>
                              </div>
                            )}
                            
                            <div className="flex gap-4 text-xs text-muted-foreground">
                              {webpage.created_at && (
                                <span>Created: {new Date(webpage.created_at).toLocaleDateString()}</span>
                              )}
                              {webpage.updated_at && (
                                <span>Updated: {new Date(webpage.updated_at).toLocaleDateString()}</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Scrapes Display */}
          <Card className="border-2 border-primary/20">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Scissors className="h-5 w-5 text-primary" />
                  <CardTitle>Scrapes Data</CardTitle>
                  <Badge variant="outline" className="text-xs">
                    {scrapes.length} scrapes
                  </Badge>
                </div>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={fetchScrapes}
                  disabled={isLoadingScrapes}
                >
                  {isLoadingScrapes ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-2" />
                  )}
                  Refresh
                </Button>
              </div>
              <CardDescription>
                Data from GET /scrapes/scrapes/ endpoint
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {scrapes.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-muted rounded-lg">
                    <Scissors className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-sm">No scrapes data</p>
                    <p className="text-xs mt-1">Click "Test" on the GET /scrapes/scrapes/ endpoint to load data</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {scrapes.map((scrape) => (
                      <div key={scrape.id} className="p-3 bg-muted/50 rounded-lg border">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Scissors className="h-4 w-4 text-primary" />
                              <span className="font-medium text-sm">ID: {scrape.id}</span>
                            </div>
                            {scrape.status && (
                              <Badge variant="outline" className="text-xs">
                                {scrape.status}
                              </Badge>
                            )}
                          </div>
                          
                          <div className="space-y-1">
                            <div>
                              <span className="text-xs text-muted-foreground">Webpage ID:</span>
                              <p className="text-sm">{scrape.webpage_id}</p>
                            </div>
                            
                            {scrape.name && (
                              <div>
                                <span className="text-xs text-muted-foreground">Name:</span>
                                <p className="text-sm">{scrape.name}</p>
                              </div>
                            )}
                            
                            {scrape.selector && (
                              <div>
                                <span className="text-xs text-muted-foreground">Selector:</span>
                                <code className="text-xs bg-background px-1 py-0.5 rounded">
                                  {scrape.selector}
                                </code>
                              </div>
                            )}
                            
                            <div className="flex gap-4 text-xs text-muted-foreground">
                              {scrape.created_at && (
                                <span>Created: {new Date(scrape.created_at).toLocaleDateString()}</span>
                              )}
                              {scrape.updated_at && (
                                <span>Updated: {new Date(scrape.updated_at).toLocaleDateString()}</span>
                              )}
                            </div>
                            
                            <div className="flex gap-4 text-xs text-muted-foreground">
                              {scrape.last_run && (
                                <span>Last Run: {new Date(scrape.last_run).toLocaleDateString()}</span>
                              )}
                              {scrape.next_run && (
                                <span>Next Run: {new Date(scrape.next_run).toLocaleDateString()}</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Fourth Row - API Management */}
        <Card className="border-2 border-primary/20">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-primary" />
              <CardTitle>API Management</CardTitle>
            </div>
            <CardDescription>
              Manage webpages and scrapes through API endpoints
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Webpages API Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4 text-primary" />
                  <h3 className="font-medium">Webpages API</h3>
                  <Badge variant="outline" className="text-xs">8 endpoints</Badge>
                </div>
                
                <div className="space-y-3">
                  {/* GET ALL Webpages */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">GET</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/</code>
                      </div>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="h-7 px-2"
                        onClick={fetchWebpages}
                        disabled={isLoadingWebpages}
                      >
                        {isLoadingWebpages ? (
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <Eye className="h-3 w-3 mr-1" />
                        )}
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Get all webpages</p>
                  </div>

                  {/* POST Webpage */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" className="text-xs">POST</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Plus className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Create a new webpage</p>
                  </div>

                  {/* GET Specific Webpage */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">GET</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/&#123;id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Eye className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Get specific webpage by ID</p>
                  </div>

                  {/* PUT Webpage */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive" className="text-xs">PUT</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/&#123;id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Edit className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Replace entire webpage</p>
                  </div>

                  {/* PATCH Webpage */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">PATCH</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/&#123;id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Edit className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Update specific fields</p>
                  </div>

                  {/* DELETE Webpage */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive" className="text-xs">DELETE</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/&#123;id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Trash className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Delete webpage</p>
                  </div>

                  {/* GET Webpage Scrapes */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">GET</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/&#123;id&#125;/scrapes</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Eye className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Get all scrapes for webpage</p>
                  </div>

                  {/* GET Webpage Scrape Data */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">GET</Badge>
                        <code className="text-sm font-mono">/webpages/webpages/&#123;id&#125;/scrapes/data</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Eye className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Get all scraped data for webpage</p>
                  </div>
                </div>
              </div>

              {/* Scrapes API Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Scissors className="h-4 w-4 text-primary" />
                  <h3 className="font-medium">Scrapes API</h3>
                  <Badge variant="outline" className="text-xs">8 endpoints</Badge>
                </div>
                
                <div className="space-y-3">
                  {/* GET ALL Scrapes */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">GET</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/</code>
                      </div>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="h-7 px-2"
                        onClick={fetchScrapes}
                        disabled={isLoadingScrapes}
                      >
                        {isLoadingScrapes ? (
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                        ) : (
                          <Eye className="h-3 w-3 mr-1" />
                        )}
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Get all scrapes for every webpage</p>
                  </div>

                  {/* POST Run All Scrapes */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" className="text-xs">POST</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/run-all</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Play className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Trigger nightly batch scrape job</p>
                  </div>

                  {/* POST Create Scrape */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" className="text-xs">POST</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/&#123;webpage_id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Plus className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Create new scrape job for webpage</p>
                  </div>

                  {/* GET Specific Scrape */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">GET</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/&#123;scrape_id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Eye className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Get specific scrape by ID</p>
                  </div>

                  {/* PUT Scrape */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive" className="text-xs">PUT</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/&#123;scrape_id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Edit className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Replace entire scrape</p>
                  </div>

                  {/* PATCH Scrape */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">PATCH</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/&#123;scrape_id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Edit className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Update specific fields</p>
                  </div>

                  {/* DELETE Scrape */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive" className="text-xs">DELETE</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/&#123;scrape_id&#125;</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Trash className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Delete scrape</p>
                  </div>

                  {/* GET Scrape Data */}
                  <div className="p-3 bg-muted/50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">GET</Badge>
                        <code className="text-sm font-mono">/scrapes/scrapes/&#123;scrape_id&#125;/data</code>
                      </div>
                      <Button size="sm" variant="outline" className="h-7 px-2">
                        <Eye className="h-3 w-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Get all data for specific scrape</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;