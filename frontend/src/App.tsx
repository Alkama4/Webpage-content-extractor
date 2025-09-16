import { useState, useRef, useEffect } from 'react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { ScrollArea } from './components/ui/scroll-area';
import { Separator } from './components/ui/separator';
import { Globe, Monitor, MousePointer, Star, Clock, Trash2, ExternalLink, Bookmark } from 'lucide-react';

interface Website {
  id: string;
  url: string;
  title: string;
  addedAt: Date;
  lastVisited: Date;
  extractedElements: number;
}

export default function App() {
  const [url, setUrl] = useState('');
  const [loadedUrl, setLoadedUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedElement, setSelectedElement] = useState('');
  const [addedWebsites, setAddedWebsites] = useState<Website[]>([]);
  const [recentlyVisited, setRecentlyVisited] = useState<Website[]>([]);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Load saved websites from localStorage on component mount
  useEffect(() => {
    const savedWebsites = localStorage.getItem('addedWebsites');
    const savedRecent = localStorage.getItem('recentlyVisited');
    
    if (savedWebsites) {
      setAddedWebsites(JSON.parse(savedWebsites).map((w: any) => ({
        ...w,
        addedAt: new Date(w.addedAt),
        lastVisited: new Date(w.lastVisited)
      })));
    }
    
    if (savedRecent) {
      setRecentlyVisited(JSON.parse(savedRecent).map((w: any) => ({
        ...w,
        addedAt: new Date(w.addedAt),
        lastVisited: new Date(w.lastVisited)
      })));
    }
  }, []);

  // Save to localStorage whenever websites change
  useEffect(() => {
    localStorage.setItem('addedWebsites', JSON.stringify(addedWebsites));
  }, [addedWebsites]);

  useEffect(() => {
    localStorage.setItem('recentlyVisited', JSON.stringify(recentlyVisited));
  }, [recentlyVisited]);

  const getWebsiteTitle = async (websiteUrl: string): Promise<string> => {
    try {
      // For demo purposes, we'll extract a simple title from the URL
      const domain = new URL(websiteUrl).hostname.replace('www.', '');
      return domain.charAt(0).toUpperCase() + domain.slice(1);
    } catch {
      return 'Unknown Website';
    }
  };

  const addToRecentlyVisited = (websiteUrl: string, title: string) => {
    const existingIndex = recentlyVisited.findIndex(w => w.url === websiteUrl);
    const now = new Date();
    
    if (existingIndex >= 0) {
      // Update existing entry
      const updated = [...recentlyVisited];
      updated[existingIndex] = { ...updated[existingIndex], lastVisited: now };
      setRecentlyVisited([updated[existingIndex], ...updated.filter((_, i) => i !== existingIndex)]);
    } else {
      // Add new entry
      const newWebsite: Website = {
        id: Date.now().toString(),
        url: websiteUrl,
        title,
        addedAt: now,
        lastVisited: now,
        extractedElements: 0
      };
      setRecentlyVisited([newWebsite, ...recentlyVisited.slice(0, 9)]); // Keep only last 10
    }
  };

  const handleScrape = async () => {
    if (url.trim()) {
      setIsLoading(true);
      setLoadedUrl(url);
      setSelectedElement('');
      
      const title = await getWebsiteTitle(url);
      addToRecentlyVisited(url, title);
      
      console.log('Loading website:', url);
    }
  };

  const addWebsite = async (websiteUrl: string) => {
    const title = await getWebsiteTitle(websiteUrl);
    const existingIndex = addedWebsites.findIndex(w => w.url === websiteUrl);
    
    if (existingIndex >= 0) {
      return; // Already added
    }
    
    const newWebsite: Website = {
      id: Date.now().toString(),
      url: websiteUrl,
      title,
      addedAt: new Date(),
      lastVisited: new Date(),
      extractedElements: 0
    };
    
    setAddedWebsites([newWebsite, ...addedWebsites]);
  };

  const removeWebsite = (id: string) => {
    setAddedWebsites(addedWebsites.filter(w => w.id !== id));
  };

  const loadWebsiteFromSidebar = (websiteUrl: string) => {
    setUrl(websiteUrl);
    setLoadedUrl(websiteUrl);
    setIsLoading(true);
    setSelectedElement('');
    
    // Update recently visited
    const website = [...addedWebsites, ...recentlyVisited].find(w => w.url === websiteUrl);
    if (website) {
      addToRecentlyVisited(websiteUrl, website.title);
    }
  };

  const handleIframeLoad = () => {
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
            outline: 2px solid oklch(0.65 0.15 180) !important; 
            background-color: oklch(0.9 0.08 180 / 0.1) !important;
          }
        `;
        iframe.contentDocument.head.appendChild(style);
      }
    } catch (error) {
      console.log('Cannot access iframe content due to CORS policy');
    }
  };

  const handleElementClick = (e: Event) => {
    e.preventDefault();
    e.stopPropagation();
    
    const target = e.target as HTMLElement;
    if (target) {
      const elementInfo = {
        tagName: target.tagName,
        textContent: target.textContent?.trim(),
        className: target.className,
        id: target.id
      };
      
      setSelectedElement(target.textContent?.trim() || 'Element selected');
      
      // Update extracted elements count for current website
      if (loadedUrl) {
        setAddedWebsites(prev => prev.map(w => 
          w.url === loadedUrl 
            ? { ...w, extractedElements: w.extractedElements + 1 }
            : w
        ));
      }
      
      console.log('Selected element:', elementInfo);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleScrape();
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto flex gap-6 h-[calc(100vh-3rem)]">
        {/* Left Side - Website Display (50%) */}
        <div className="flex-1">
          <Card className="h-full border-2 border-primary/20">
            <CardHeader className="pb-3">
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
            </CardHeader>
            <CardContent className="pt-0 h-[calc(100%-8rem)]">
              {/* Browser-like URL bar */}
              <div className="mb-4 p-3 bg-muted/50 border border-border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-destructive/60"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500/60"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500/60"></div>
                  </div>
                  <div className="flex-1 bg-background border border-border rounded px-3 py-1.5">
                    <span className="text-sm text-muted-foreground break-all">
                      {loadedUrl || 'Website URL will appear here...'}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Website Frame */}
              <div className="relative border-4 border-primary/30 rounded-lg overflow-hidden h-[calc(100%-5rem)]">
                <div className="absolute top-0 left-0 right-0 h-8 bg-primary/10 border-b border-primary/20 flex items-center px-3 z-20">
                  <span className="text-xs text-primary font-medium">
                    {loadedUrl ? '🌐 Website Content - Click elements to extract data' : '📋 Website Preview Area'}
                  </span>
                </div>
                
                {!loadedUrl ? (
                  // Empty State
                  <div className="flex items-center justify-center h-full mt-8">
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
                      <div className="absolute inset-0 bg-background/90 flex items-center justify-center z-30 mt-8">
                        <div className="flex items-center gap-3 p-4 bg-card border border-border rounded-lg shadow-lg">
                          <div className="h-5 w-5 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                          <span>Loading website content...</span>
                        </div>
                      </div>
                    )}
                    
                    <iframe
                      ref={iframeRef}
                      src={loadedUrl}
                      className="w-full h-full mt-8"
                      onLoad={handleIframeLoad}
                      sandbox="allow-scripts allow-same-origin allow-forms"
                      title="Website Preview for Data Extraction"
                    />
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Side - Input Box and Website Manager (50%) */}
        <div className="flex-1 flex flex-col gap-6">
          {/* Top - Scraper Input Card */}
          <Card className="border-2 border-primary/20">
            <CardHeader className="text-center space-y-2">
              <div className="flex justify-center">
                <Globe className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>Web Scraper</CardTitle>
              <CardDescription>
                Enter a URL to scrape content from any website
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Input
                  type="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full"
                />
              </div>
              <div className="flex gap-2">
                <Button 
                  onClick={handleScrape}
                  disabled={!url.trim() || isLoading}
                  className="flex-1"
                >
                  {isLoading ? 'Loading...' : 'Scrape Website'}
                </Button>
                {loadedUrl && (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => addWebsite(loadedUrl)}
                    disabled={addedWebsites.some(w => w.url === loadedUrl)}
                    title="Add to saved websites"
                  >
                    <Star className={`h-4 w-4 ${addedWebsites.some(w => w.url === loadedUrl) ? 'fill-primary text-primary' : ''}`} />
                  </Button>
                )}
              </div>
              
              {selectedElement && (
                <div className="mt-4 p-3 bg-accent rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <MousePointer className="h-4 w-4 text-primary" />
                    <span className="font-medium">Selected Element:</span>
                  </div>
                  <p className="text-sm text-muted-foreground break-words">
                    "{selectedElement}"
                  </p>
                </div>
              )}

              {/* Instructions */}
              <div className="p-3 bg-accent/50 border border-primary/20 rounded-lg">
                <p className="text-sm text-accent-foreground">
                  💡 <strong>How to use:</strong> {loadedUrl 
                    ? 'Hover over elements in the left panel to highlight them, then click to select for data extraction.'
                    : 'Enter a website URL above and click "Scrape Website" to load it in the left panel for element selection.'
                  }
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Bottom - Website Manager */}
          <Card className="flex-1 border-2 border-primary/20">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Bookmark className="h-5 w-5 text-primary" />
                <CardTitle>Website Manager</CardTitle>
              </div>
              <CardDescription>
                Manage your scraped websites and recent visits
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-0 h-[calc(100%-6rem)]">
              <div className="flex flex-row gap-4 h-full">
                {/* Added Websites Section */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-foreground flex items-center gap-2">
                      <Star className="h-4 w-4 text-primary" />
                      Added Websites
                    </h3>
                    <Badge variant="secondary" className="text-xs">
                      {addedWebsites.length}
                    </Badge>
                  </div>
                  
                  <ScrollArea className="h-[calc(100%-2rem)]">
                    <div className="space-y-2 pr-4">
                      {addedWebsites.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          <Globe className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">No websites added yet</p>
                          <p className="text-xs">Load a website and click the star icon</p>
                        </div>
                      ) : (
                        addedWebsites.map((website) => (
                          <Card key={website.id} className="p-3 hover:bg-accent/50 transition-colors cursor-pointer border-primary/20">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0" onClick={() => loadWebsiteFromSidebar(website.url)}>
                                <p className="font-medium text-sm truncate">{website.title}</p>
                                <p className="text-xs text-muted-foreground truncate">{website.url}</p>
                                <div className="flex items-center gap-2 mt-1">
                                  <Badge variant="outline" className="text-xs px-1 py-0">
                                    {website.extractedElements} extracted
                                  </Badge>
                                  <span className="text-xs text-muted-foreground">
                                    {website.addedAt.toLocaleDateString()}
                                  </span>
                                </div>
                              </div>
                              <div className="flex flex-col gap-1">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0"
                                  onClick={() => window.open(website.url, '_blank')}
                                >
                                  <ExternalLink className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                                  onClick={() => removeWebsite(website.id)}
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          </Card>
                        ))
                      )}
                    </div>
                  </ScrollArea>
                </div>

                {/* Separator */}
                <Separator orientation="vertical" className="h-full mx-2" />

                {/* Recently Visited Section */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-foreground flex items-center gap-2">
                      <Clock className="h-4 w-4 text-primary" />
                      Recently Visited
                    </h3>
                    <Badge variant="secondary" className="text-xs">
                      {recentlyVisited.length}
                    </Badge>
                  </div>
                  
                  <ScrollArea className="h-[calc(100%-2rem)]">
                    <div className="space-y-2 pl-4">
                      {recentlyVisited.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">No recent visits</p>
                          <p className="text-xs">Start scraping websites to see them here</p>
                        </div>
                      ) : (
                        recentlyVisited.map((website) => (
                          <Card key={`recent-${website.id}`} className="p-3 hover:bg-accent/50 transition-colors cursor-pointer border-border">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0" onClick={() => loadWebsiteFromSidebar(website.url)}>
                                <p className="font-medium text-sm truncate">{website.title}</p>
                                <p className="text-xs text-muted-foreground truncate">{website.url}</p>
                                <span className="text-xs text-muted-foreground">
                                  {website.lastVisited.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => addWebsite(website.url)}
                                title="Add to saved websites"
                              >
                                <Star className="h-3 w-3" />
                              </Button>
                            </div>
                          </Card>
                        ))
                      )}
                    </div>
                  </ScrollArea>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}