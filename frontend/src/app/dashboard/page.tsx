'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  Package, 
  ShoppingCart, 
  DollarSign, 
  ArrowUpRight,
  Store,
  Sparkles,
  Activity
} from 'lucide-react';
import Link from 'next/link';
import { Bar, BarChart, Line, LineChart, CartesianGrid, XAxis } from "recharts";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

export default function DashboardPage() {
  // Mock data - à remplacer par des vraies données de l'API
  const stats = [
    {
      title: 'Total Products',
      value: '156',
      change: '+12.5%',
      trend: 'up',
      icon: Package,
      color: 'gold',
    },
    {
      title: 'Active Listings',
      value: '842',
      change: '+8.2%',
      trend: 'up',
      icon: ShoppingCart,
      color: 'electric',
    },
    {
      title: 'Marketplaces',
      value: '8',
      change: '+2',
      trend: 'up',
      icon: Store,
      color: 'gold',
    },
    {
      title: 'Monthly Revenue',
      value: '$24,560',
      change: '+18.7%',
      trend: 'up',
      icon: DollarSign,
      color: 'electric',
    },
  ];

  const recentActivity = [
    { action: 'Product listed', marketplace: 'Amazon', product: 'Premium Headphones', time: '2 min ago' },
    { action: 'Order received', marketplace: 'eBay', product: 'Wireless Mouse', time: '15 min ago' },
    { action: 'Product updated', marketplace: 'Etsy', product: 'Handmade Bag', time: '1 hour ago' },
    { action: 'Product delisted', marketplace: 'Amazon', product: 'Old Keyboard', time: '2 hours ago' },
  ];

  const topMarketplaces = [
    { name: 'Amazon', listings: 234, revenue: '$12,450', growth: '+15%' },
    { name: 'eBay', listings: 189, revenue: '$8,320', growth: '+22%' },
    { name: 'Etsy', listings: 156, revenue: '$3,790', growth: '+8%' },
  ];

  // Données pour le graphique de revenue
  const revenueData = [
    { month: "Jan", revenue: 18500 },
    { month: "Feb", revenue: 20100 },
    { month: "Mar", revenue: 19200 },
    { month: "Apr", revenue: 22300 },
    { month: "May", revenue: 23800 },
    { month: "Jun", revenue: 24560 },
  ];

  const chartConfig = {
    revenue: {
      label: "Revenue",
      color: "#DE8668", // coral terracotta
    },
  } satisfies ChartConfig;

  // Données pour le graphique de listings
  const listingsData = [
    { month: "Jan", amazon: 180, ebay: 150, etsy: 120 },
    { month: "Feb", amazon: 200, ebay: 165, etsy: 130 },
    { month: "Mar", amazon: 210, ebay: 170, etsy: 140 },
    { month: "Apr", amazon: 220, ebay: 180, etsy: 145 },
    { month: "May", amazon: 228, ebay: 185, etsy: 152 },
    { month: "Jun", amazon: 234, ebay: 189, etsy: 156 },
  ];

  const listingsChartConfig = {
    amazon: {
      label: "Amazon",
      color: "#FF9900",
    },
    ebay: {
      label: "eBay",
      color: "#E53238",
    },
    etsy: {
      label: "Etsy",
      color: "#F1641E",
    },
  } satisfies ChartConfig;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-darktext mb-2 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-warmgold" />
            Dashboard
          </h1>
          <p className="text-darktext/60">
            Welcome back! Here's your cross-listing overview.
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            asChild
            variant="outline"
            className="bg-lightgray/50 border-warmgold/20 text-darktext hover:bg-lightgray hover:border-warmgold/40"
          >
            <Link href="/dashboard/products/new">
              <Package className="mr-2 h-4 w-4" />
              Add Product
            </Link>
          </Button>
          <Button
            asChild
            className="bg-gradient-gold hover:opacity-90 text-carbon font-semibold shadow-premium"
          >
            <Link href="/dashboard/marketplaces">
              <Store className="mr-2 h-4 w-4" />
              Connect Marketplace
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card
              key={index}
              className="glass-effect border-warmgold/20 shadow-premium hover:shadow-electric transition-all duration-300 hover:scale-105 group"
            >
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-darktext/80">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.color === 'gold' ? 'bg-warmgold/20' : 'bg-skyblue/20'}`}>
                  <Icon className={`h-4 w-4 ${stat.color === 'gold' ? 'text-warmgold' : 'text-skyblue'}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-darktext group-hover:text-warmgold transition-colors">
                  {stat.value}
                </div>
                <div className="flex items-center text-xs text-darktext/60 mt-1">
                  <TrendingUp className="w-3 h-3 mr-1 text-green-500" />
                  <span className="text-green-500 font-medium">{stat.change}</span>
                  <span className="ml-1">from last month</span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <Card className="glass-effect border-warmgold/20 shadow-premium">
          <CardHeader>
            <CardTitle className="text-darktext flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-warmgold" />
              Revenue Overview
            </CardTitle>
            <CardDescription className="text-darktext/60">
              Monthly revenue for the last 6 months
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="h-[250px] w-full">
              <LineChart accessibilityLayer data={revenueData}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="month"
                  tickLine={false}
                  tickMargin={10}
                  axisLine={false}
                  className="text-xs"
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Line
                  dataKey="revenue"
                  type="monotone"
                  stroke="#DE8668"
                  strokeWidth={2}
                  dot={{ fill: "#DE8668", r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ChartContainer>
            <div className="flex items-center justify-center mt-4 text-sm text-darktext/60">
              <TrendingUp className="w-4 h-4 mr-2 text-green-500" />
              <span className="text-green-500 font-medium">+18.7%</span>
              <span className="ml-1">compared to last period</span>
            </div>
          </CardContent>
        </Card>

        {/* Listings Chart */}
        <Card className="glass-effect border-warmgold/20 shadow-premium">
          <CardHeader>
            <CardTitle className="text-darktext flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-warmgold" />
              Listings by Platform
            </CardTitle>
            <CardDescription className="text-darktext/60">
              Active listings across top marketplaces
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={listingsChartConfig} className="h-[250px] w-full">
              <BarChart accessibilityLayer data={listingsData}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="month"
                  tickLine={false}
                  tickMargin={10}
                  axisLine={false}
                  className="text-xs"
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="amazon" fill="#FF9900" radius={[4, 4, 0, 0]} />
                <Bar dataKey="ebay" fill="#E53238" radius={[4, 4, 0, 0]} />
                <Bar dataKey="etsy" fill="#F1641E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ChartContainer>
            <div className="flex items-center justify-center gap-4 mt-4 text-xs">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-sm bg-[#FF9900]"></div>
                <span className="text-darktext/60">Amazon</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-sm bg-[#E53238]"></div>
                <span className="text-darktext/60">eBay</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-sm bg-[#F1641E]"></div>
                <span className="text-darktext/60">Etsy</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="lg:col-span-2 glass-effect border-warmgold/20 shadow-premium">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-darktext flex items-center gap-2">
                  <Activity className="w-5 h-5 text-warmgold" />
                  Recent Activity
                </CardTitle>
                <CardDescription className="text-darktext/60">
                  Your latest cross-listing activities
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-warmgold hover:text-warmgold/80 hover:bg-warmgold/10"
              >
                View All
                <ArrowUpRight className="ml-1 w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg bg-lightgray/30 border border-warmgold/10 hover:border-warmgold/30 transition-all"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-electric flex items-center justify-center">
                      <Package className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-darktext">{activity.action}</p>
                      <div className="flex items-center text-xs text-darktext/60 space-x-2">
                        <span className="px-2 py-0.5 rounded bg-warmgold/20 text-warmgold">
                          {activity.marketplace}
                        </span>
                        <span>{activity.product}</span>
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-darktext/40">{activity.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Marketplaces */}
        <Card className="glass-effect border-warmgold/20 shadow-premium">
          <CardHeader>
            <CardTitle className="text-darktext flex items-center gap-2">
              <Store className="w-5 h-5 text-warmgold" />
              Top Marketplaces
            </CardTitle>
            <CardDescription className="text-darktext/60">
              Best performing platforms
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topMarketplaces.map((marketplace, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg bg-lightgray/30 border border-warmgold/10 hover:border-warmgold/30 transition-all group"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-darktext group-hover:text-warmgold transition-colors">
                      {marketplace.name}
                    </h4>
                    <span className="text-xs px-2 py-1 rounded bg-warmgold/20 text-warmgold">
                      {marketplace.growth}
                    </span>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-darktext/60">Listings</span>
                      <span className="text-darktext font-medium">{marketplace.listings}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-darktext/60">Revenue</span>
                      <span className="text-warmgold font-semibold">{marketplace.revenue}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

    </div>
  );
}
