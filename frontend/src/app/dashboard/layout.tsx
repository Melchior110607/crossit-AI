'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { ShoppingBag, LayoutDashboard, Package, Store, LogOut, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/signin');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-premium">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-electric shadow-electric mb-4 animate-pulse">
            <ShoppingBag className="w-8 h-8 text-white" />
          </div>
          <p className="text-darktext/60 animate-pulse">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/dashboard/products', label: 'Products', icon: Package },
    { href: '/dashboard/marketplaces', label: 'Marketplaces', icon: Store },
  ];

  return (
    <div className="min-h-screen bg-gradient-premium">
      {/* Navbar Premium */}
      <nav className="glass-effect border-b border-warmgold/10 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/dashboard" className="flex items-center space-x-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-electric shadow-electric flex items-center justify-center transition-transform group-hover:scale-110">
                <ShoppingBag className="w-6 h-6 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold text-darktext group-hover:text-warmgold transition-colors">
                  CrossIt
                </span>
                <span className="text-[10px] text-warmgold/60 -mt-1">Premium Platform</span>
              </div>
            </Link>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-darktext/70 hover:text-darktext hover:bg-lightgray/50 transition-all duration-200 group"
                  >
                    <Icon className="w-4 h-4 group-hover:text-warmgold transition-colors" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              {/* User Info */}
              <div className="hidden sm:flex items-center space-x-3 px-3 py-1.5 rounded-lg bg-lightgray/30 border border-warmgold/10">
                <div className="w-8 h-8 rounded-full bg-gradient-gold flex items-center justify-center">
                  <span className="text-xs font-bold text-white">
                    {user.email?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-darktext">{user.name || 'User'}</span>
                  <span className="text-xs text-darktext/50">{user.email}</span>
                </div>
              </div>

              {/* Logout Button */}
              <Button
                onClick={logout}
                variant="ghost"
                size="sm"
                className="text-darktext/60 hover:text-darktext hover:bg-lightgray/50 transition-all"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden border-t border-warmgold/10">
          <div className="flex justify-around py-2 px-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex flex-col items-center space-y-1 px-3 py-2 rounded-lg text-darktext/70 hover:text-darktext hover:bg-lightgray/50 transition-all"
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-xs font-medium">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-warmgold/10 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-darktext/40">
              © 2025 CrossIt. Premium cross-listing platform.
            </p>
            <div className="flex items-center space-x-2 text-xs text-darktext/40">
              <Sparkles className="w-3 h-3 text-warmgold" />
              <span>Powered by AI</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
