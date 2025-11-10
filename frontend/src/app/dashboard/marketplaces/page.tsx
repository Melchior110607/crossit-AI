'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MarketplaceIcon } from '@/components/marketplace-icons';
import { 
  Store, 
  Search, 
  CheckCircle2, 
  Circle,
  Sparkles,
  Loader2,
  AlertCircle
} from 'lucide-react';

// En production Docker, utiliser URLs relatives pour bénéficier des rewrites Next.js
// En dev local, utiliser l'API directement
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface Marketplace {
  id: string;
  name: string;
  description?: string;
  auth_type: string;
  is_configured: boolean;
  requires_shop_domain: boolean;
  documentation_url?: string;
  connected?: boolean;
  listings?: number;
}

interface ConnectedMarketplace {
  id: string;
  marketplace_id: string;
  marketplace_name: string;
  status: string;
  created_at: number;
}

// Helper functions outside component to avoid initialization issues
const getMarketplaceDescription = (id: string): string => {
  const descriptions: Record<string, string> = {
    amazon: 'World\'s largest online marketplace',
    ebay: 'Leading online auction platform',
    etsy: 'Marketplace for unique & creative goods',
    bol: 'Leading e-commerce platform in Netherlands',
    allegro: 'Poland\'s largest online marketplace',
    kaufland: 'Major European marketplace',
    onbuy: 'Fast-growing UK marketplace',
    wish: 'Mobile-first shopping platform',
    joom: 'International e-commerce platform',
    zalando: 'Europe\'s leading fashion platform',
    aboutyou: 'European fashion & lifestyle marketplace',
    otto: 'Germany\'s largest online marketplace',
    cdiscount: 'Leading French e-commerce site',
    fnacdarty: 'French marketplace for tech & culture',
    vinted: 'Second-hand fashion marketplace',
    stockx: 'Marketplace for sneakers & streetwear',
    shopify: 'E-commerce platform for online stores',
    laredoute: 'French fashion & home marketplace',
    galerieslafayette: 'Premium French department store',
    asos: 'Global fashion destination',
    woocommerce: 'Open-source e-commerce platform',
  };
  return descriptions[id] || 'E-commerce marketplace';
};

const getMarketplaceColors = (id: string) => {
  const colors: Record<string, { gradient: string; border: string }> = {
    amazon: { gradient: 'from-orange-500/20 to-yellow-500/20', border: 'border-orange-500/30' },
    ebay: { gradient: 'from-blue-500/20 to-purple-500/20', border: 'border-blue-500/30' },
    etsy: { gradient: 'from-orange-400/20 to-pink-500/20', border: 'border-orange-400/30' },
    bol: { gradient: 'from-blue-600/20 to-cyan-500/20', border: 'border-blue-600/30' },
    allegro: { gradient: 'from-orange-500/20 to-red-500/20', border: 'border-orange-500/30' },
    kaufland: { gradient: 'from-red-600/20 to-blue-600/20', border: 'border-red-600/30' },
    stockx: { gradient: 'from-green-600/20 to-emerald-500/20', border: 'border-green-600/30' },
    shopify: { gradient: 'from-green-500/20 to-teal-500/20', border: 'border-green-500/30' },
    zalando: { gradient: 'from-orange-600/20 to-amber-500/20', border: 'border-orange-600/30' },
    vinted: { gradient: 'from-teal-600/20 to-cyan-500/20', border: 'border-teal-600/30' },
    asos: { gradient: 'from-slate-600/20 to-gray-500/20', border: 'border-slate-600/30' },
    woocommerce: { gradient: 'from-purple-500/20 to-indigo-500/20', border: 'border-purple-500/30' },
  };
  return colors[id] || { gradient: 'from-gray-500/20 to-slate-500/20', border: 'border-gray-500/30' };
};

export default function MarketplacesPage() {
  const searchParams = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [connectedMarketplaces, setConnectedMarketplaces] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [connectingId, setConnectingId] = useState<string | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  // Static list of all available marketplaces
  const allMarketplaces: Marketplace[] = [
    { id: 'amazon', name: 'Amazon', auth_type: 'oauth2', is_configured: false, requires_shop_domain: false },
    { id: 'ebay', name: 'eBay', auth_type: 'oauth2', is_configured: true, requires_shop_domain: false },
    { id: 'etsy', name: 'Etsy', auth_type: 'oauth2', is_configured: true, requires_shop_domain: false },
    { id: 'shopify', name: 'Shopify', auth_type: 'oauth2', is_configured: true, requires_shop_domain: true },
    { id: 'stockx', name: 'StockX', auth_type: 'oauth2', is_configured: true, requires_shop_domain: false },
    { id: 'bol', name: 'bol.com', auth_type: 'api_key', is_configured: true, requires_shop_domain: false },
    { id: 'allegro', name: 'Allegro', auth_type: 'oauth2', is_configured: false, requires_shop_domain: false },
    { id: 'kaufland', name: 'Kaufland', auth_type: 'api_key', is_configured: true, requires_shop_domain: false },
    { id: 'zalando', name: 'Zalando', auth_type: 'oauth2', is_configured: false, requires_shop_domain: false },
    { id: 'aboutyou', name: 'ABOUT YOU', auth_type: 'oauth2', is_configured: false, requires_shop_domain: false },
    { id: 'otto', name: 'OTTO Market', auth_type: 'basic_auth', is_configured: false, requires_shop_domain: false },
    { id: 'wish', name: 'Wish', auth_type: 'bearer_token', is_configured: false, requires_shop_domain: false },
    { id: 'joom', name: 'Joom', auth_type: 'bearer_token', is_configured: false, requires_shop_domain: false },
    { id: 'onbuy', name: 'OnBuy', auth_type: 'api_key', is_configured: false, requires_shop_domain: false },
    { id: 'vinted', name: 'Vinted Pro', auth_type: 'oauth2', is_configured: false, requires_shop_domain: false },
    { id: 'cdiscount', name: 'Cdiscount', auth_type: 'bearer_token', is_configured: false, requires_shop_domain: false },
    { id: 'fnacdarty', name: 'Fnac Darty', auth_type: 'api_key', is_configured: false, requires_shop_domain: false },
    { id: 'laredoute', name: 'La Redoute', auth_type: 'api_key', is_configured: false, requires_shop_domain: false },
    { id: 'galerieslafayette', name: 'Galeries Lafayette', auth_type: 'api_key', is_configured: false, requires_shop_domain: false },
    { id: 'asos', name: 'ASOS', auth_type: 'api_key', is_configured: false, requires_shop_domain: false },
    { id: 'woocommerce', name: 'WooCommerce', auth_type: 'api_key', is_configured: true, requires_shop_domain: true },
  ];

  // Enrich with descriptions and connection status
  const marketplaces = allMarketplaces.map(mp => ({
    ...mp,
    description: getMarketplaceDescription(mp.id),
    connected: connectedMarketplaces.has(mp.id),
  }));

  // Check for OAuth callback notification
  useEffect(() => {
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    const marketplace = searchParams.get('marketplace');
    
    if (success === 'true' && marketplace) {
      setNotification({
        type: 'success',
        message: `Successfully connected to ${marketplace}!`
      });
      // Clear notification after 5 seconds
      setTimeout(() => setNotification(null), 5000);
      // Refresh connected marketplaces
      fetchConnectedMarketplaces();
    } else if (error && marketplace) {
      setNotification({
        type: 'error',
        message: `Failed to connect to ${marketplace}: ${error}`
      });
      setTimeout(() => setNotification(null), 5000);
    }
  }, [searchParams]);

  // Fetch connected marketplaces from backend
  useEffect(() => {
    fetchConnectedMarketplaces();
  }, []);

  const fetchConnectedMarketplaces = async () => {
    try {
      setLoading(true);

      // Fetch connected marketplaces
      const connectedRes = await fetch(`${API_BASE_URL}/api/marketplaces/connected`, {
        headers: {
          'ngrok-skip-browser-warning': 'true',
        }
      });
      if (!connectedRes.ok) {
        console.warn('Could not fetch connected marketplaces, backend may be offline');
        setLoading(false);
        return;
      }
      
      const connectedData = await connectedRes.json();

      // Store connected IDs
      const connectedIds = new Set<string>(
        connectedData.connections.map((c: ConnectedMarketplace) => c.marketplace_id)
      );
      setConnectedMarketplaces(connectedIds);
    } catch (err) {
      console.warn('Error fetching connected marketplaces:', err);
      // Don't show error - just continue with empty connected list
    } finally {
      setLoading(false);
    }
  };


  const handleConnect = async (marketplace: Marketplace) => {
    if (marketplace.connected) {
      // Already connected - navigate to manage
      return;
    }

    try {
      setConnectingId(marketplace.id);

      if (marketplace.auth_type === 'oauth2') {
        // Check if marketplace requires shop_domain (Shopify, WooCommerce)
        let shopDomain = '';
        if (marketplace.requires_shop_domain) {
          if (marketplace.id === 'shopify') {
            shopDomain = prompt('Enter your Shopify store name (e.g., "my-store" for my-store.myshopify.com):');
            if (!shopDomain) {
              setConnectingId(null);
              return;
            }
            // Remove .myshopify.com if user added it
            shopDomain = shopDomain.replace('.myshopify.com', '').trim();
          } else if (marketplace.id === 'woocommerce') {
            shopDomain = prompt('Enter your WooCommerce store URL (e.g., "https://mystore.com"):');
            if (!shopDomain) {
              setConnectingId(null);
              return;
            }
          }
        }

        // OAuth flow
        const url = shopDomain 
          ? `${API_BASE_URL}/api/marketplaces/${marketplace.id}/auth-url?shop_domain=${encodeURIComponent(shopDomain)}`
          : `${API_BASE_URL}/api/marketplaces/${marketplace.id}/auth-url`;
          
        const res = await fetch(url, {
          headers: {
            'ngrok-skip-browser-warning': 'true',
          }
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || 'Failed to get authorization URL');
        }
        
        const data = await res.json();
        
        // Redirect to OAuth authorization page
        window.location.href = data.authorization_url;
      } else {
        // API Key flow - show modal (to implement later)
        alert(`${marketplace.name} uses API Key authentication. This feature is coming soon!`);
        setConnectingId(null);
      }
    } catch (err) {
      console.error('Error connecting marketplace:', err);
      alert(err instanceof Error ? err.message : 'Failed to connect marketplace');
      setConnectingId(null);
    }
  };

  const filteredMarketplaces = marketplaces.filter(mp =>
    mp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mp.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const connectedCount = marketplaces.filter(mp => mp.connected).length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-darktext mb-2 flex items-center gap-3">
          <Store className="w-8 h-8 text-warmgold" />
          Marketplaces
        </h1>
        <p className="text-darktext/60">
          Connect and manage your cross-listing channels
        </p>
      </div>

      {/* Notification */}
      {notification && (
        <div className={`p-4 rounded-lg border ${
          notification.type === 'success' 
            ? 'bg-green-500/10 border-green-500/30 text-green-600' 
            : 'bg-red-500/10 border-red-500/30 text-red-600'
        } flex items-center gap-3`}>
          {notification.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span className="font-medium">{notification.message}</span>
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="flex items-center gap-2 text-darktext/60 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Checking connected marketplaces...</span>
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-darktext/40 w-5 h-5" />
        <Input
          placeholder="Search marketplaces..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 bg-lightgray border-warmgold/20 text-darktext placeholder:text-darktext/40 focus:border-warmgold focus:ring-gold"
        />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="glass-effect border-warmgold/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-gold flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-carbon" />
              </div>
              <div>
                <p className="text-darktext/60 text-sm">Connected</p>
                <p className="text-2xl font-bold text-darktext">{connectedCount}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-effect border-warmgold/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-lightgray flex items-center justify-center">
                <Store className="w-6 h-6 text-warmgold" />
              </div>
              <div>
                <p className="text-darktext/60 text-sm">Available</p>
                <p className="text-2xl font-bold text-darktext">{marketplaces.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-effect border-warmgold/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-warmgold/20 flex items-center justify-center">
                <Circle className="w-6 h-6 text-warmgold" />
              </div>
              <div>
                <p className="text-darktext/60 text-sm">Not Connected</p>
                <p className="text-2xl font-bold text-darktext">{marketplaces.length - connectedCount}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Marketplaces Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredMarketplaces.map((marketplace) => {
          const colors = getMarketplaceColors(marketplace.id);
          return (
          <Card
            key={marketplace.id}
            className={`glass-effect ${colors.border} shadow-premium hover:shadow-electric transition-all duration-300 hover:scale-105 group relative overflow-hidden`}
          >
            {/* Background gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${colors.gradient} opacity-50 group-hover:opacity-70 transition-opacity`}></div>
            
            {/* Content */}
            <CardHeader className="relative">
              <div className="flex items-start justify-between mb-3">
                <div className="w-12 h-12 flex items-center justify-center">
                  <MarketplaceIcon name={marketplace.id} className="w-10 h-10" />
                </div>
                {marketplace.connected ? (
                  <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-warmgold/20 text-warmgold text-xs font-medium">
                    <CheckCircle2 className="w-3 h-3" />
                    Connected
                  </div>
                ) : (
                  <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-lightgray/50 text-darktext/60 text-xs font-medium">
                    <Circle className="w-3 h-3" />
                    Available
                  </div>
                )}
              </div>
              <CardTitle className="text-base text-darktext group-hover:text-warmgold transition-colors">
                {marketplace.name}
              </CardTitle>
              <CardDescription className="text-darktext/60 text-xs line-clamp-2">
                {marketplace.description}
              </CardDescription>
            </CardHeader>

            <CardContent className="relative space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-darktext/60">Auth Type</span>
                <span className="text-darktext font-medium capitalize">{marketplace.auth_type.replace('_', ' ')}</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-darktext/60">Status</span>
                <span className={`font-medium ${marketplace.is_configured ? 'text-green-600' : 'text-orange-500'}`}>
                  {marketplace.is_configured ? 'Configured' : 'Needs Setup'}
                </span>
              </div>

              <Button
                onClick={() => handleConnect(marketplace)}
                disabled={!marketplace.is_configured || connectingId === marketplace.id}
                className={`w-full ${
                  marketplace.connected
                    ? 'bg-lightgray/50 hover:bg-lightgray text-darktext border border-warmgold/20'
                    : 'bg-gradient-gold hover:opacity-90 text-carbon font-semibold disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
                size="sm"
              >
                {connectingId === marketplace.id ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Connecting...
                  </>
                ) : marketplace.connected ? (
                  <>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Connected
                  </>
                ) : !marketplace.is_configured ? (
                  <>
                    <AlertCircle className="mr-2 h-4 w-4" />
                    Not Configured
                  </>
                ) : (
                  <>
                    <Store className="mr-2 h-4 w-4" />
                    Connect
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )})}
      </div>

      {filteredMarketplaces.length === 0 && (
        <div className="text-center py-12">
          <Store className="w-16 h-16 text-darktext/40 mx-auto mb-4" />
          <p className="text-darktext/60">No marketplaces found matching your search.</p>
        </div>
      )}
    </div>
  );
}
