'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, ExternalLink, Home } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

interface PublishSuccessCardProps {
  publishedMarketplaces: string[];
  productId?: string;
}

export function PublishSuccessCard({
  publishedMarketplaces = [],
  productId
}: PublishSuccessCardProps) {
  const router = useRouter();

  return (
    <Card className="glass-effect border-green-500/20">
      <CardContent className="p-8 text-center space-y-6">
        {/* Success Animation */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{
            type: "spring",
            stiffness: 260,
            damping: 20
          }}
          className="flex justify-center"
        >
          <div className="w-24 h-24 rounded-full bg-green-100 flex items-center justify-center">
            <CheckCircle2 className="w-16 h-16 text-green-600" />
          </div>
        </motion.div>

        {/* Success Message */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-2"
        >
          <h2 className="text-3xl font-bold text-darktext">
            Successfully Published!
          </h2>
          <p className="text-darktext/60 max-w-md mx-auto">
            Your product has been published to {publishedMarketplaces.length} marketplace
            {publishedMarketplaces.length !== 1 ? 's' : ''}
          </p>
        </motion.div>

        {/* Published Marketplaces */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-3"
        >
          <p className="text-sm font-medium text-darktext">
            Published to:
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {publishedMarketplaces.map((marketplace) => (
              <div
                key={marketplace}
                className="px-4 py-2 bg-green-50 border border-green-200 rounded-lg text-green-700 font-medium capitalize"
              >
                {marketplace}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-3 pt-4"
        >
          <Button
            onClick={() => router.push('/dashboard/products')}
            variant="outline"
            className="flex-1"
          >
            <Home className="w-4 h-4 mr-2" />
            View All Products
          </Button>

          {productId && (
            <Button
              onClick={() => router.push(`/dashboard/products/${productId}`)}
              className="flex-1 bg-gradient-gold text-carbon font-semibold hover:opacity-90"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              View Product Details
            </Button>
          )}

          <Button
            onClick={() => router.push('/dashboard/products/new')}
            className="flex-1 bg-warmgold hover:bg-warmgold/90"
          >
            Add Another Product
          </Button>
        </motion.div>

        {/* Additional Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="pt-4 text-xs text-darktext/40"
        >
          <p>
            Your listings are now live. You can manage them from the Products page.
          </p>
        </motion.div>
      </CardContent>
    </Card>
  );
}

