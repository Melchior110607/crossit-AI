'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';

const MARKETPLACE_INFO: Record<string, { logo: string; color: string }> = {
  amazon: { logo: '🔶', color: 'bg-orange-100 text-orange-800' },
  ebay: { logo: '🔴', color: 'bg-red-100 text-red-800' },
  etsy: { logo: '🟠', color: 'bg-amber-100 text-amber-800' },
  bol: { logo: '🔵', color: 'bg-blue-100 text-blue-800' },
  allegro: { logo: '🟣', color: 'bg-purple-100 text-purple-800' },
  kaufland: { logo: '🔴', color: 'bg-red-100 text-red-800' },
  onbuy: { logo: '🟢', color: 'bg-green-100 text-green-800' },
  wish: { logo: '💙', color: 'bg-sky-100 text-sky-800' },
  joom: { logo: '🟣', color: 'bg-violet-100 text-violet-800' },
  zalando: { logo: '🟠', color: 'bg-orange-100 text-orange-800' },
  aboutyou: { logo: '⚫', color: 'bg-gray-100 text-gray-800' },
  otto: { logo: '🔴', color: 'bg-red-100 text-red-800' },
  cdiscount: { logo: '🔵', color: 'bg-blue-100 text-blue-800' },
  fnac_darty: { logo: '🟡', color: 'bg-yellow-100 text-yellow-800' },
  vinted: { logo: '💚', color: 'bg-teal-100 text-teal-800' },
  stockx: { logo: '⚫', color: 'bg-black text-white' },
  shopify: { logo: '🟢', color: 'bg-green-100 text-green-800' },
  la_redoute: { logo: '🔴', color: 'bg-red-100 text-red-800' },
  galeries_lafayette: { logo: '🔵', color: 'bg-blue-100 text-blue-800' },
  asos: { logo: '⚫', color: 'bg-gray-900 text-white' },
};

export default function MarketplacesPage() {
  const [marketplaces, setMarketplaces] = useState<any[]>([]);
  const [connectedMarketplaces, setConnectedMarketplaces] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);

  useEffect(() => {
    fetchMarketplaces();
  }, []);

  const fetchMarketplaces = async () => {
    try {
      const [allMarketplaces, connected] = await Promise.all([
        apiClient.getMarketplaces(),
        apiClient.getConnectedMarketplaces(),
      ]);

      setMarketplaces(allMarketplaces.marketplaces || []);
      setConnectedMarketplaces(
        new Set(connected.connected_marketplaces?.map((m: any) => m.name) || [])
      );
    } catch (error) {
      console.error('Failed to fetch marketplaces:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (marketplaceName: string) => {
    setConnecting(marketplaceName);
    try {
      const result = await apiClient.connectMarketplace(marketplaceName);
      
      if (result.auth_url) {
        // Open OAuth URL in new window
        window.open(result.auth_url, '_blank', 'width=600,height=700');
        // TODO: Implement OAuth callback handling
        alert('OAuth flow initiated. Complete the authentication in the popup window.');
      } else {
        alert('Marketplace connection initiated. Check marketplace documentation for setup.');
      }
      
      // Refresh marketplace list
      await fetchMarketplaces();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to connect marketplace');
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async (marketplaceName: string) => {
    if (!confirm(`Are you sure you want to disconnect from ${marketplaceName}?`)) {
      return;
    }

    try {
      await apiClient.disconnectMarketplace(marketplaceName);
      await fetchMarketplaces();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to disconnect marketplace');
    }
  };

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Marketplaces</h1>
        <p className="mt-2 text-sm text-gray-600">
          Connect to marketplaces to start cross-listing your products
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {marketplaces.map((marketplace) => {
          const isConnected = connectedMarketplaces.has(marketplace.name);
          const info = MARKETPLACE_INFO[marketplace.name] || { logo: '🏪', color: 'bg-gray-100 text-gray-800' };

          return (
            <div
              key={marketplace.name}
              className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="p-5">
                <div className="flex items-center mb-3">
                  <div className={`text-3xl mr-3 ${info.color} p-2 rounded-lg`}>
                    {info.logo}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900">
                      {marketplace.display_name}
                    </h3>
                    {isConnected && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        Connected
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-4">{marketplace.description}</p>
                
                {isConnected ? (
                  <button
                    onClick={() => handleDisconnect(marketplace.name)}
                    className="w-full inline-flex justify-center items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
                  >
                    Disconnect
                  </button>
                ) : (
                  <button
                    onClick={() => handleConnect(marketplace.name)}
                    disabled={connecting === marketplace.name}
                    className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                  >
                    {connecting === marketplace.name ? 'Connecting...' : 'Connect'}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

