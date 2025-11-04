'use client';

import { useState } from 'react';
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
  TrendingUp,
  Users,
  Globe
} from 'lucide-react';

export default function MarketplacesPage() {
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data - les 20 marketplaces
  const marketplaces = [
    {
      id: 'amazon',
      name: 'Amazon',
      description: 'World\'s largest online marketplace',
      connected: true,
      region: 'Global',
      listings: 234,
      color: 'from-orange-500/20 to-yellow-500/20',
      borderColor: 'border-orange-500/30',
    },
    {
      id: 'ebay',
      name: 'eBay',
      description: 'Leading online auction platform',
      connected: true,
      region: 'Global',
      listings: 189,
      color: 'from-blue-500/20 to-purple-500/20',
      borderColor: 'border-blue-500/30',
    },
    {
      id: 'etsy',
      name: 'Etsy',
      description: 'Marketplace for unique & creative goods',
      connected: true,
      region: 'Global',
      listings: 156,
      color: 'from-orange-400/20 to-pink-500/20',
      borderColor: 'border-orange-400/30',
    },
    {
      id: 'bol',
      name: 'bol.com',
      description: 'Leading e-commerce platform in Netherlands',
      connected: false,
      region: 'Netherlands',
      listings: 0,
      color: 'from-blue-600/20 to-cyan-500/20',
      borderColor: 'border-blue-600/30',
    },
    {
      id: 'allegro',
      name: 'Allegro',
      description: 'Poland\'s largest online marketplace',
      connected: false,
      region: 'Poland',
      listings: 0,
      color: 'from-orange-500/20 to-red-500/20',
      borderColor: 'border-orange-500/30',
    },
    {
      id: 'kaufland',
      name: 'Kaufland',
      description: 'Major European marketplace',
      connected: false,
      region: 'Europe',
      listings: 0,
      color: 'from-red-600/20 to-blue-600/20',
      borderColor: 'border-red-600/30',
    },
    {
      id: 'onbuy',
      name: 'OnBuy',
      description: 'Fast-growing UK marketplace',
      connected: false,
      region: 'UK',
      listings: 0,
      color: 'from-purple-500/20 to-pink-500/20',
      borderColor: 'border-purple-500/30',
    },
    {
      id: 'wish',
      name: 'Wish',
      description: 'Mobile-first shopping platform',
      connected: false,
      region: 'Global',
      listings: 0,
      color: 'from-blue-400/20 to-cyan-400/20',
      borderColor: 'border-blue-400/30',
    },
    {
      id: 'joom',
      name: 'Joom',
      description: 'International e-commerce platform',
      connected: false,
      region: 'Global',
      listings: 0,
      color: 'from-teal-500/20 to-green-500/20',
      borderColor: 'border-teal-500/30',
    },
    {
      id: 'zalando',
      name: 'Zalando',
      description: 'Europe\'s leading fashion platform',
      connected: false,
      region: 'Europe',
      listings: 0,
      color: 'from-orange-600/20 to-amber-500/20',
      borderColor: 'border-orange-600/30',
    },
    {
      id: 'aboutyou',
      name: 'ABOUT YOU',
      description: 'European fashion & lifestyle marketplace',
      connected: false,
      region: 'Europe',
      listings: 0,
      color: 'from-pink-500/20 to-rose-500/20',
      borderColor: 'border-pink-500/30',
    },
    {
      id: 'otto',
      name: 'OTTO Market',
      description: 'Germany\'s largest online marketplace',
      connected: false,
      region: 'Germany',
      listings: 0,
      color: 'from-red-600/20 to-yellow-500/20',
      borderColor: 'border-red-600/30',
    },
    {
      id: 'cdiscount',
      name: 'Cdiscount',
      description: 'Leading French e-commerce site',
      connected: false,
      region: 'France',
      listings: 0,
      color: 'from-blue-600/20 to-red-500/20',
      borderColor: 'border-blue-600/30',
    },
    {
      id: 'fnac',
      name: 'Fnac Darty',
      description: 'French marketplace for tech & culture',
      connected: false,
      region: 'France',
      listings: 0,
      color: 'from-amber-600/20 to-orange-600/20',
      borderColor: 'border-amber-600/30',
    },
    {
      id: 'vinted',
      name: 'Vinted Pro',
      description: 'Second-hand fashion marketplace',
      connected: false,
      region: 'Europe',
      listings: 0,
      color: 'from-teal-600/20 to-cyan-500/20',
      borderColor: 'border-teal-600/30',
    },
    {
      id: 'stockx',
      name: 'StockX',
      description: 'Marketplace for sneakers & streetwear',
      connected: false,
      region: 'Global',
      listings: 0,
      color: 'from-green-600/20 to-emerald-500/20',
      borderColor: 'border-green-600/30',
    },
    {
      id: 'shopify',
      name: 'Shopify',
      description: 'E-commerce platform for online stores',
      connected: false,
      region: 'Global',
      listings: 0,
      color: 'from-green-500/20 to-teal-500/20',
      borderColor: 'border-green-500/30',
    },
    {
      id: 'laredoute',
      name: 'La Redoute',
      description: 'French fashion & home marketplace',
      connected: false,
      region: 'France',
      listings: 0,
      color: 'from-red-500/20 to-pink-500/20',
      borderColor: 'border-red-500/30',
    },
    {
      id: 'galerieslafayette',
      name: 'Galeries Lafayette',
      description: 'Premium French department store',
      connected: false,
      region: 'France',
      listings: 0,
      color: 'from-purple-600/20 to-fuchsia-500/20',
      borderColor: 'border-purple-600/30',
    },
    {
      id: 'asos',
      name: 'ASOS',
      description: 'Global fashion destination',
      connected: false,
      region: 'Global',
      listings: 0,
      color: 'from-slate-600/20 to-gray-500/20',
      borderColor: 'border-slate-600/30',
    },
  ];

  const filteredMarketplaces = marketplaces.filter(mp =>
    mp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mp.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const connectedCount = marketplaces.filter(mp => mp.connected).length;
  const totalListings = marketplaces.reduce((sum, mp) => sum + mp.listings, 0);

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

      {/* Marketplaces Grid - Plus compact */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {filteredMarketplaces.map((marketplace) => (
          <Card
            key={marketplace.id}
            className={`glass-effect ${marketplace.borderColor} shadow-premium hover:shadow-electric transition-all duration-300 hover:scale-105 group relative overflow-hidden`}
          >
            {/* Background gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${marketplace.color} opacity-50 group-hover:opacity-70 transition-opacity`}></div>
            
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
                <span className="text-darktext/60">Region</span>
                <span className="text-darktext font-medium">{marketplace.region}</span>
              </div>
              
              {marketplace.connected && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-darktext/60">Listings</span>
                  <span className="text-warmgold font-semibold">{marketplace.listings}</span>
                </div>
              )}

              <Button
                className={`w-full ${
                  marketplace.connected
                    ? 'bg-lightgray/50 hover:bg-lightgray text-darktext border border-warmgold/20'
                    : 'bg-gradient-gold hover:opacity-90 text-carbon font-semibold'
                }`}
                size="sm"
              >
                {marketplace.connected ? (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Manage
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
        ))}
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
