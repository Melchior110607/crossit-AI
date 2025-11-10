'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

// En production Docker, utiliser URLs relatives pour bénéficier des rewrites Next.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface PageProps {
  params: {
    marketplace: string;
  };
}

export default function OAuthCallbackPage({ params }: PageProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const marketplace = params.marketplace;

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      // Check for errors from OAuth provider
      if (error) {
        setStatus('error');
        setMessage(errorDescription || error || 'Authorization failed');
        return;
      }

      if (!code) {
        setStatus('error');
        setMessage('No authorization code received');
        return;
      }

      try {
        // Exchange code for token
        const res = await fetch(
          `${API_BASE_URL}/api/marketplaces/${marketplace}/callback?code=${code}&state=${state || ''}`,
          {
            headers: {
              'ngrok-skip-browser-warning': 'true',
              'Content-Type': 'application/json',
            }
          }
        );

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || 'Failed to connect marketplace');
        }

        const data = await res.json();

        setStatus('success');
        setMessage(data.message || `Successfully connected to ${marketplace}!`);

        // Redirect to marketplaces page after 2 seconds
        setTimeout(() => {
          router.push('/dashboard/marketplaces');
        }, 2000);
      } catch (err) {
        console.error('Callback error:', err);
        setStatus('error');
        setMessage(err instanceof Error ? err.message : 'Connection failed');
      }
    };

    handleCallback();
  }, [marketplace, searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-carbon via-gray-900 to-carbon p-4">
      <Card className="w-full max-w-md glass-effect border-warmgold/20">
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            {status === 'loading' && (
              <>
                <Loader2 className="w-16 h-16 text-warmgold animate-spin mx-auto" />
                <h2 className="text-2xl font-bold text-darktext">Connecting...</h2>
                <p className="text-darktext/60">
                  Completing authentication with{' '}
                  <span className="text-warmgold capitalize">{marketplace}</span>
                </p>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-10 h-10 text-green-500" />
                </div>
                <h2 className="text-2xl font-bold text-darktext">Success!</h2>
                <p className="text-darktext/60">{message}</p>
                <p className="text-sm text-darktext/40">Redirecting to marketplaces...</p>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto">
                  <XCircle className="w-10 h-10 text-red-500" />
                </div>
                <h2 className="text-2xl font-bold text-darktext">Connection Failed</h2>
                <p className="text-darktext/60">{message}</p>
                <Button
                  onClick={() => router.push('/dashboard/marketplaces')}
                  className="bg-gradient-gold text-carbon font-semibold mt-4"
                >
                  Back to Marketplaces
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

