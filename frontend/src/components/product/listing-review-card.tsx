'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Edit, 
  Check, 
  X, 
  ExternalLink,
  DollarSign,
  Tag,
  FileText,
  ShoppingBag
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { MarketplaceIcon } from '@/components/marketplace-icons';
import { cn } from '@/lib/utils';

interface ListingData {
  marketplace: string;
  title: string;
  description: string;
  short_description: string;
  price: number;
  currency: string;
  tags?: string[];
  specifications?: Record<string, string>;
  category?: string;
  brand?: string;
  condition?: string;
}

interface ListingReviewCardProps {
  listings: Record<string, ListingData>;
  onApprove: (approvedListings: Record<string, ListingData>) => void;
  onEdit: (marketplace: string, data: Partial<ListingData>) => void;
}

export function ListingReviewCard({
  listings,
  onApprove,
  onEdit
}: ListingReviewCardProps) {
  const [selectedMarketplace, setSelectedMarketplace] = useState<string>(
    Object.keys(listings)[0] || ''
  );
  const [approvedMarketplaces, setApprovedMarketplaces] = useState<Set<string>>(new Set());
  const [skippedMarketplaces, setSkippedMarketplaces] = useState<Set<string>>(new Set());

  const marketplaceIds = Object.keys(listings);
  const currentListing = listings[selectedMarketplace];

  const toggleApprove = (marketplace: string) => {
    setApprovedMarketplaces(prev => {
      const next = new Set(prev);
      if (next.has(marketplace)) {
        next.delete(marketplace);
      } else {
        next.add(marketplace);
        // Remove from skipped if exists
        setSkippedMarketplaces(prevSkipped => {
          const nextSkipped = new Set(prevSkipped);
          nextSkipped.delete(marketplace);
          return nextSkipped;
        });
      }
      return next;
    });
  };

  const toggleSkip = (marketplace: string) => {
    setSkippedMarketplaces(prev => {
      const next = new Set(prev);
      if (next.has(marketplace)) {
        next.delete(marketplace);
      } else {
        next.add(marketplace);
        // Remove from approved if exists
        setApprovedMarketplaces(prevApproved => {
          const nextApproved = new Set(prevApproved);
          nextApproved.delete(marketplace);
          return nextApproved;
        });
      }
      return next;
    });
  };

  const handlePublish = () => {
    const approvedListings: Record<string, ListingData> = {};
    approvedMarketplaces.forEach(marketplace => {
      if (listings[marketplace]) {
        approvedListings[marketplace] = listings[marketplace];
      }
    });

    if (Object.keys(approvedListings).length === 0) {
      alert('Please approve at least one listing to publish');
      return;
    }

    onApprove(approvedListings);
  };

  if (!currentListing) {
    return <div>No listings available</div>;
  }

  return (
    <Card className="glass-effect border-warmgold/20">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-darktext flex items-center gap-2">
          <ShoppingBag className="w-6 h-6 text-warmgold" />
          Review & Approve Listings
        </CardTitle>
        <p className="text-sm text-darktext/60 mt-2">
          Review AI-generated listings for each marketplace. Approve, edit, or skip.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Marketplace Tabs */}
        <div className="flex flex-wrap gap-2">
          {marketplaceIds.map(marketplace => {
            const isApproved = approvedMarketplaces.has(marketplace);
            const isSkipped = skippedMarketplaces.has(marketplace);
            const isSelected = marketplace === selectedMarketplace;

            return (
              <button
                key={marketplace}
                onClick={() => setSelectedMarketplace(marketplace)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all",
                  isSelected && "border-warmgold bg-warmgold/10 shadow-md",
                  !isSelected && "border-gray-200 hover:border-warmgold/50",
                  isApproved && !isSelected && "border-green-500 bg-green-50",
                  isSkipped && !isSelected && "border-gray-300 bg-gray-100 opacity-60"
                )}
              >
                <MarketplaceIcon name={marketplace} className="w-5 h-5" />
                <span className="font-medium capitalize">{marketplace}</span>
                {isApproved && (
                  <Check className="w-4 h-4 text-green-600" />
                )}
                {isSkipped && (
                  <X className="w-4 h-4 text-gray-500" />
                )}
              </button>
            );
          })}
        </div>

        <Separator />

        {/* Listing Preview */}
        <motion.div
          key={selectedMarketplace}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-6"
        >
          {/* Title */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-darktext flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Title
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  const newTitle = prompt('Edit title:', currentListing.title);
                  if (newTitle) {
                    onEdit(selectedMarketplace, { title: newTitle });
                  }
                }}
              >
                <Edit className="w-4 h-4" />
              </Button>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg border">
              <p className="text-sm font-medium text-darktext">{currentListing.title}</p>
            </div>
          </div>

          {/* Price & Category */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-darktext flex items-center gap-2 mb-2">
                <DollarSign className="w-4 h-4" />
                Price
              </label>
              <div className="p-3 bg-gray-50 rounded-lg border">
                <p className="text-lg font-bold text-warmgold">
                  ${currentListing.price.toFixed(2)}
                </p>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-darktext flex items-center gap-2 mb-2">
                <Tag className="w-4 h-4" />
                Category
              </label>
              <div className="p-3 bg-gray-50 rounded-lg border">
                <p className="text-sm font-medium text-darktext capitalize">
                  {currentListing.category || 'General'}
                </p>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-darktext">
                Description
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  const newDesc = prompt('Edit description:', currentListing.short_description);
                  if (newDesc) {
                    onEdit(selectedMarketplace, { short_description: newDesc, description: `<p>${newDesc}</p>` });
                  }
                }}
              >
                <Edit className="w-4 h-4" />
              </Button>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg border max-h-48 overflow-y-auto">
              <div 
                className="text-sm text-darktext prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: currentListing.description }}
              />
            </div>
          </div>

          {/* Tags */}
          {currentListing.tags && currentListing.tags.length > 0 && (
            <div>
              <label className="text-sm font-medium text-darktext mb-2 block">
                Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {currentListing.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Specifications */}
          {currentListing.specifications && Object.keys(currentListing.specifications).length > 0 && (
            <div>
              <label className="text-sm font-medium text-darktext mb-2 block">
                Specifications
              </label>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(currentListing.specifications).map(([key, value]) => (
                  <div key={key} className="p-2 bg-gray-50 rounded border text-sm">
                    <span className="font-medium text-darktext/70">{key}:</span>{' '}
                    <span className="text-darktext">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons for Current Listing */}
          <div className="flex gap-3">
            <Button
              onClick={() => toggleApprove(selectedMarketplace)}
              variant={approvedMarketplaces.has(selectedMarketplace) ? "default" : "outline"}
              className={cn(
                "flex-1",
                approvedMarketplaces.has(selectedMarketplace) && "bg-green-600 hover:bg-green-700"
              )}
            >
              <Check className="w-4 h-4 mr-2" />
              {approvedMarketplaces.has(selectedMarketplace) ? 'Approved' : 'Approve'}
            </Button>

            <Button
              onClick={() => toggleSkip(selectedMarketplace)}
              variant="outline"
              className="flex-1"
            >
              <X className="w-4 h-4 mr-2" />
              {skippedMarketplaces.has(selectedMarketplace) ? 'Skipped' : 'Skip'}
            </Button>
          </div>
        </motion.div>

        <Separator />

        {/* Publish All Button */}
        <div className="space-y-3">
          <div className="text-center text-sm text-darktext/60">
            {approvedMarketplaces.size} marketplace{approvedMarketplaces.size !== 1 ? 's' : ''} approved •{' '}
            {skippedMarketplaces.size} skipped
          </div>

          <Button
            onClick={handlePublish}
            disabled={approvedMarketplaces.size === 0}
            className="w-full bg-gradient-gold text-carbon font-semibold hover:opacity-90 disabled:opacity-50"
            size="lg"
          >
            Publish to {approvedMarketplaces.size} Marketplace{approvedMarketplaces.size !== 1 ? 's' : ''}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

