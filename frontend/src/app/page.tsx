'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  
  useEffect(() => {
    // Redirect to signin immediately
    router.push('/signin');
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="animate-pulse text-gray-400">Loading...</div>
    </div>
  );
}

